#!/usr/bin/env python3
"""
generate_phonebook.py

Generates Yealink's Remote Phone Book XML format from a tenant's directory
data (extensions + any external contacts), served over HTTP so every phone
in a tenant's account shares one live-updating company directory instead
of static, per-phone contact lists that drift out of sync the moment
someone's extension changes.

Yealink phones poll the configured Remote Phone Book URL periodically and
on-demand (pressing the Directory key) - this script can run as a simple
Flask endpoint generating the XML on the fly from the same provisioning
database used elsewhere in this profile's repos, or as a one-shot script
writing a static file for a smaller, rarely-changing directory.

Usage (static file):
    python generate_phonebook.py --tenant acme --out acme_phonebook.xml

Usage (live Flask endpoint):
    python generate_phonebook.py --serve --port 8090
"""
import argparse
import xml.etree.ElementTree as ET
from xml.dom import minidom

# In a real deployment this comes from the provisioning database (the same
# one freeswitch-cloud-pbx's CDR/extension tables live in) - hardcoded here
# to keep this script runnable standalone without a DB dependency.
SAMPLE_DIRECTORY = {
    "acme": [
        {"name": "Reception", "phone": "1050", "type": "Work"},
        {"name": "Sales Team", "phone": "1100", "type": "Work"},
        {"name": "Support",   "phone": "1200", "type": "Work"},
        {"name": "Jane Smith", "phone": "1010", "type": "Work", "mobile": "14165550100"},
    ],
}


def build_phonebook_xml(tenant: str) -> str:
    contacts = SAMPLE_DIRECTORY.get(tenant, [])

    root = ET.Element("YealinkIPPhoneBook")
    for entry in contacts:
        contact = ET.SubElement(root, "Menu")
        ET.SubElement(contact, "Name").text = entry["name"]
        ET.SubElement(contact, "Telephone").text = entry["phone"]
        if "mobile" in entry:
            ET.SubElement(contact, "Mobile").text = entry["mobile"]
        ET.SubElement(contact, "Group").text = entry.get("type", "Work")

    raw = ET.tostring(root, encoding="utf-8")
    return minidom.parseString(raw).toprettyxml(indent="  ")


def write_static_file(tenant: str, out_path: str):
    xml_content = build_phonebook_xml(tenant)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(xml_content)
    print(f"Wrote {out_path} ({len(SAMPLE_DIRECTORY.get(tenant, []))} contacts)")


def serve(port: int):
    from flask import Flask, Response

    app = Flask(__name__)

    @app.route("/phonebook/<tenant>.xml")
    def phonebook(tenant):
        return Response(build_phonebook_xml(tenant), mimetype="text/xml")

    print(f"Serving phonebooks at http://0.0.0.0:{port}/phonebook/<tenant>.xml")
    app.run(host="0.0.0.0", port=port)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tenant", default="acme")
    parser.add_argument("--out", default="phonebook.xml")
    parser.add_argument("--serve", action="store_true", help="Run as a live HTTP endpoint instead of writing a file")
    parser.add_argument("--port", type=int, default=8090)
    args = parser.parse_args()

    if args.serve:
        serve(args.port)
    else:
        write_static_file(args.tenant, args.out)


if __name__ == "__main__":
    main()

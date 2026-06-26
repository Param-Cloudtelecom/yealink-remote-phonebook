# yealink-remote-phonebook

A live, server-generated company directory for Yealink desk phones —
every phone in a tenant's account shares one always-current contact list
instead of static, per-phone entries that go stale the moment someone's
extension changes.

## Why remote, not local, phonebook entries

Manually adding contacts to each phone (or worse, generating a one-time
import file) means every org change — a new hire, a changed extension, a
departed employee — requires re-touching every single handset. Yealink's
**Remote Phone Book** feature has every phone poll a URL on a schedule
(and on-demand via the Directory key); point that URL at a server that
generates the XML from the same provisioning data already driving the
rest of the deployment, and the directory simply can't drift out of sync.

## How it works

```
 Phone polls remote_phonebook.data.1.url every 6h (or on Directory key press)
                          │
                          ▼
            generate_phonebook.py (Flask endpoint)
                          │
              reads tenant's extension directory
           (same provisioning data as freeswitch-cloud-pbx)
                          │
                          ▼
              YealinkIPPhoneBook XML response
```

## Files

- [`generate_phonebook.py`](generate_phonebook.py) — generates the
  Yealink phonebook XML format, either as a one-shot static file or a
  live Flask endpoint serving per-tenant directories on demand.
- [`phone_config_snippet.cfg`](phone_config_snippet.cfg) — the
  provisioning config that points a phone at the remote phonebook URL
  (merge into the base config from
  [`voip-phone-provisioning-guides`](https://github.com/Param-Cloudtelecom/voip-phone-provisioning-guides)).

## Usage

```bash
# One-shot static file for a small, rarely-changing directory
python generate_phonebook.py --tenant acme --out acme_phonebook.xml

# Live endpoint - phones always get the current directory on each poll
pip install flask
python generate_phonebook.py --serve --port 8090
curl http://localhost:8090/phonebook/acme.xml
```

## Multi-vendor note

The XML schema here is Yealink-specific, but the underlying pattern
(generate a vendor's expected directory format server-side, from live
provisioning data, served over the same provisioning infrastructure)
applies equally to Cisco's XML directory format, Grandstream's, and
Snom's — only the schema changes, not the architecture.

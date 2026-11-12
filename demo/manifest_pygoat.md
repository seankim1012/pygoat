| ID | File | Marker | Language | CWE | Category | Severity | Description | Clean counterpart |
|---|---|---|---|---|---|---|---|---|
| P001 | `demo/seeded_vulns.py` | SEED-P001 | Python | CWE-89 | SQL injection | High | Query built by string concatenation with request arg | `seeded_clean.py` `/clean/user` |
| P002 | `demo/seeded_vulns.py` | SEED-P002 | Python | CWE-78 | OS command injection | Critical | `subprocess` with `shell=True` and unsanitized host | `seeded_clean.py` `/clean/ping` |
| P003 | `demo/seeded_vulns.py` | SEED-P003 | Python | CWE-22 | Path traversal | High | User-controlled filename joined into file path | `seeded_clean.py` `/clean/download` |
| P004 | `demo/seeded_vulns.py` | SEED-P004 | Python | CWE-94 | Code injection | Critical | `eval()` on request parameter | `seeded_clean.py` `/clean/calc` |
| P005 | `demo/seeded_vulns.py` | SEED-P005 | Python | CWE-79 | Reflected XSS | Medium | Unescaped request value written into HTML response | `seeded_clean.py` `/clean/greet` |
| P006 | `demo/seeded_vulns.py` | SEED-P006 | Python | CWE-798 | Hard-coded credentials | High | Flask secret key committed in source | `seeded_clean.py` `SECRET_KEY` |
| P007 | `demo/seeded_vulns.py` | SEED-P007 | Python | CWE-327 | Weak hashing algorithm | Medium | MD5 used for password hashing | `seeded_clean.py` `hash_password` |
| P008 | `demo/seeded_vulns.py` | SEED-P008 | Python | CWE-918 | Server-side request forgery | High | `requests.get()` on user-supplied URL | `seeded_clean.py` `/clean/fetch` |
| P009 | `demo/seeded_vulns.py` | SEED-P009 | Python | CWE-502 | Insecure deserialization | Critical | `pickle.loads()` on request body | `seeded_clean.py` `/clean/session` |
| P010 | `demo/seeded_vulns.py` | SEED-P010 | Python | CWE-502 | Unsafe YAML loading | High | `yaml.load()` with the full Loader on request body | `seeded_clean.py` `/clean/config` |

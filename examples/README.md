# Examples

Runnable scripts that demonstrate the connector against a real Google
Business Profile account. Each one expects the env vars from
[../docs/oauth-setup.md](../docs/oauth-setup.md) to be set.

```bash
export GBP_CLIENT_ID=...
export GBP_CLIENT_SECRET=...
export GBP_REFRESH_TOKEN=...

python examples/list_accounts.py
python examples/update_location_website.py --help
```

| Script                       | What it does                                                   |
|------------------------------|----------------------------------------------------------------|
| `list_accounts.py`           | Print every account the OAuth user manages, with role + state. |
| `update_location_website.py` | Patch a single location's `websiteUri`, with `--dry-run`.      |

These intentionally use only the public API — they are the kind of code an
end-user would write.

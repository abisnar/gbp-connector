"""List every Google Business Profile account the OAuth user manages.

Usage:
    python examples/list_accounts.py

Requires:
    GBP_CLIENT_ID, GBP_CLIENT_SECRET, GBP_REFRESH_TOKEN in the environment.
"""

from __future__ import annotations

from gbp_connector import GoogleBusinessProfileConnector


def main() -> None:
    with GoogleBusinessProfileConnector.from_env() as gbp:
        rows: list[tuple[str, str, str, str]] = []
        for account in gbp.accounts.list():
            rows.append(
                (
                    account.name,
                    account.account_name or "—",
                    account.role or "—",
                    account.verification_state or "—",
                )
            )

    if not rows:
        print("No accounts found for the current credentials.")
        return

    widths = [max(len(r[i]) for r in rows) for i in range(4)]
    header = ("RESOURCE NAME", "ACCOUNT NAME", "ROLE", "VERIFICATION")
    widths = [max(w, len(h)) for w, h in zip(widths, header, strict=True)]
    fmt = "  ".join(f"{{:<{w}}}" for w in widths)

    print(fmt.format(*header))
    print(fmt.format(*("-" * w for w in widths)))
    for row in rows:
        print(fmt.format(*row))


if __name__ == "__main__":
    main()

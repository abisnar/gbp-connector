"""Patch a single location's website URI.

Usage:
    python examples/update_location_website.py \\
        --location locations/9876543210 \\
        --website  https://example.com \\
        [--dry-run]

Requires:
    GBP_CLIENT_ID, GBP_CLIENT_SECRET, GBP_REFRESH_TOKEN in the environment.

The script always shows you the current value, asks for confirmation, and
only then performs the write — unless you pass --dry-run, which submits the
PATCH with validate_only=True so nothing on the live profile changes.
"""

from __future__ import annotations

import argparse
import sys

from gbp_connector import GBPApiError, GoogleBusinessProfileConnector


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--location",
        required=True,
        help="Resource name like 'locations/9876543210'.",
    )
    parser.add_argument(
        "--website",
        required=True,
        help="The new https:// URL.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Send PATCH with validate_only=True; the API checks but does not write.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip the interactive confirmation prompt.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()

    if not args.website.startswith("https://"):
        print("Refusing to set a non-HTTPS website.", file=sys.stderr)
        return 2

    with GoogleBusinessProfileConnector.from_env() as gbp:
        try:
            current = gbp.locations.get(args.location, read_mask="name,title,websiteUri")
        except GBPApiError as e:
            print(f"Could not fetch {args.location}: {e}", file=sys.stderr)
            return 1

        print(f"Location:    {current.name}")
        print(f"Title:       {current.title or '—'}")
        print(f"Current URL: {current.website_uri or '—'}")
        print(f"New URL:     {args.website}")
        print(f"Mode:        {'validate-only (dry run)' if args.dry_run else 'WRITE'}")

        if not args.yes and not args.dry_run:
            confirm = input("Proceed with write? [y/N] ").strip().lower()
            if confirm != "y":
                print("Aborted.")
                return 0

        try:
            updated = gbp.locations.patch(
                args.location,
                updates={"websiteUri": args.website},
                update_mask="websiteUri",
                validate_only=args.dry_run,
            )
        except GBPApiError as e:
            print(f"PATCH failed: {e}", file=sys.stderr)
            return 1

    print(f"OK. Returned websiteUri: {updated.website_uri or '—'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

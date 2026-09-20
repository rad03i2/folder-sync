from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from .core import apply, plan


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="folder-sync", description="Preview-first one-way folder synchronization")
    p.add_argument("source", type=Path)
    p.add_argument("destination", type=Path)
    p.add_argument("--delete", action="store_true", help="Delete destination-only files (dangerous; preview first)")
    p.add_argument("--include-hidden", action="store_true")
    p.add_argument("--apply", action="store_true", dest="execute", help="Execute the displayed plan")
    p.add_argument("--no-verify", action="store_true", help="Skip post-copy SHA-256 verification")
    p.add_argument("--manifest", type=Path, help="Write an execution manifest as JSON")
    p.add_argument("--json", action="store_true", help="Print the plan as JSON")
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        actions = plan(args.source, args.destination, delete=args.delete, include_hidden=args.include_hidden)
        if args.json:
            print(json.dumps([asdict(a) for a in actions], indent=2))
        else:
            if not actions:
                print("Already synchronized: no changes required.")
            for action in actions:
                print(f"{action.kind.upper():6} {action.relative_path} ({action.size} bytes)")
            print(f"\n{len(actions)} action(s). " + ("Applying..." if args.execute else "Preview only; add --apply to execute."))
        if args.execute and actions:
            apply(args.source, args.destination, actions, verify=not args.no_verify, manifest=args.manifest)
            print("Synchronization completed successfully.")
        return 0
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

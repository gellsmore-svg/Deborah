"""Allow ``python -m deborah`` (validate is the default entry)."""

from deborah.validate_cli import main

if __name__ == "__main__":
    raise SystemExit(main())

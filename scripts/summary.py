import argparse
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CFG_DIR = BASE_DIR / "CFG"
KEY_DIR = BASE_DIR / "KEY"
RYM_DIR = BASE_DIR / "RYM"


def load_json(path: Path):
    """Load a JSON file and return its data."""
    with path.open() as f:
        return json.load(f)


def summary_server() -> str:
    """Return a short summary string for the server configuration."""
    data = load_json(CFG_DIR / "SERVER.json")
    return f"{data['PROJECT_NAME']}: {data['DESCRIPTION']}"


def summary_key() -> str:
    """Return a summary of the Monday personality."""
    data = load_json(KEY_DIR / "MONDAY.JSON")
    identity = data["neural_imprint"]["identity"]
    return f"{identity['name']} – {identity['personality']}"


def list_styles() -> list[str]:
    """Return a list of musical style names."""
    data = load_json(RYM_DIR / "styles.json")
    return [style['name'] for style in data['styles']]


def main() -> None:
    parser = argparse.ArgumentParser(description="SOPHY config summary CLI")
    parser.add_argument(
        "section",
        choices=["server", "key", "styles"],
        help="Which configuration section to display",
    )
    args = parser.parse_args()
    if args.section == "server":
        print(summary_server())
    elif args.section == "key":
        print(summary_key())
    elif args.section == "styles":
        for name in list_styles():
            print(name)


if __name__ == "__main__":
    main()

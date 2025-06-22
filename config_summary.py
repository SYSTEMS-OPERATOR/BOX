import json
from pathlib import Path


def load_json(path: Path):
    with path.open() as f:
        return json.load(f)


def get_project_name(cfg_path: Path = Path('CFG') / 'SERVER.json') -> str:
    return load_json(cfg_path)['PROJECT_NAME']


def get_monday_name(key_path: Path = Path('KEY') / 'MONDAY.JSON') -> str:
    return load_json(key_path)['neural_imprint']['identity']['name']


def get_style_count(styles_path: Path = Path('RYM') / 'styles.json') -> int:
    return len(load_json(styles_path)['styles'])


def generate_summary() -> dict:
    return {
        'project_name': get_project_name(),
        'monday_name': get_monday_name(),
        'style_count': get_style_count(),
    }


if __name__ == '__main__':
    summary = generate_summary()
    print(json.dumps(summary, indent=2))

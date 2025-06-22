import json
import os

styles_path = os.path.join(os.path.dirname(__file__), '..', 'RYM', 'styles.json')

def load_styles(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return [entry['name'] for entry in data.get('styles', [])]

if __name__ == '__main__':
    styles = load_styles(styles_path)
    print("Available musical styles:")
    for style in styles:
        print(f"- {style}")


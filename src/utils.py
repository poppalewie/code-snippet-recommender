import json

def load_snippets(file_path="data/snippets.json"):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        return []
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {file_path}.")
        return []

def save_snippets(snippets, file_path="data/snippets.json"):
    try:
        with open(file_path, 'w') as f:
            json.dump(snippets, f, indent=2)
    except Exception as e:
        print(f"Error saving snippets to {file_path}: {e}")
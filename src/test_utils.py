from utils import load_snippets

def test_load_snippets():
    snippets = load_snippets()
    if not snippets:
        print("No snippets loaded.")
        return
    for snippet in snippets:
        print(f"ID: {snippet['id']}, Language: {snippet['language']}, Description: {snippet['description']}")

if __name__ == "__main__":
    test_load_snippets()
# ML-Powered Code Snippet Recommender
A Python-based tool to recommend code snippets using machine learning.


## Project Structure
- `src/`: Core code.
- `data/`: Snippet storage.
- `docs/`: Documentation.

## Data Model
Snippets are stored in `data/snippets.json` as a list of JSON objects with the following fields:
- `id`: Unique integer identifier for the snippet.
- `language`: Programming language (e.g., "python", "javascript", "java").
- `description`: Brief description of the snippet’s functionality.
- `tags`: List of keywords for matching (e.g., ["sort", "list"]).
- `code`: The code snippet as a string, with `\n` for line breaks.

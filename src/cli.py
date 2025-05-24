from recommender import CodeRecommender

def main():
    recommender = CodeRecommender()
    print("Welcome to the Code Snippet Recommender!")
    print("Enter a query (e.g., 'sort list in python') or 'quit' to exit.")
    print("Optionally, add :language:mode (e.g., 'sort list:python:embeddings').")
    print("Modes: 'tfidf' (default), 'embeddings'.")
    
    while True:
        user_input = input("\nQuery: ")
        if user_input.lower() == 'quit':
            break
        if not user_input.strip():
            print("Please enter a valid query.")
            continue
            
        # Split input into query, language, mode
        parts = user_input.split(':')
        query = parts[0].strip()
        language = parts[1].strip() if len(parts) > 1 else None
        mode = parts[2].strip() if len(parts) > 2 else 'tfidf'
        
        results = recommender.recommend(query, language=language, mode=mode)
        if isinstance(results, dict) and 'error' in results:
            print(results['error'])
            continue
        if not results:
            print(f"No matching snippets found{' for language ' + language if language else ''}.")
            continue
            
        for i, result in enumerate(results, 1):
            print(f"\nResult {i} (Score: {result['score']:.4f})")
            print(f"Language: {result['snippet']['language']}")
            print(f"Description: {result['snippet']['description']}")
            print(f"Code:\n{result['snippet']['code']}\n")

if __name__ == "__main__":
    main()
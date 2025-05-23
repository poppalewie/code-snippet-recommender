from recommender import CodeRecommender

def main():
    recommender = CodeRecommender()
    print("Welcome to the Code Snippet Recommender!")
    print("Enter a query (e.g., 'sort list in python') or 'quit' to exit.")
    print("Optionally, specify a language (e.g., 'python') after the query with a colon (e.g., 'sort list:python').")
    
    while True:
        user_input = input("\nQuery: ")
        if user_input.lower() == 'quit':
            break
        if not user_input.strip():
            print("Please enter a valid query.")
            continue
            
        # Split input into query and language (if provided)
        query, language = user_input, None
        if ':' in user_input:
            query, language = [part.strip() for part in user_input.split(':', 1)]
            
        results = recommender.recommend(query, language=language)
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
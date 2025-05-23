from recommender import CodeRecommender

def main():
    recommender = CodeRecommender()
    print("Welcome to the Code Snippet Recommender!")
    print("Enter a query (e.g., 'sort list in python') or 'quit' to exit.")
    
    while True:
        query = input("\nQuery: ")
        if query.lower() == 'quit':
            break
        if not query.strip():
            print("Please enter a valid query.")
            continue
            
        results = recommender.recommend(query)
        if not results:
            print("No matching snippets found.")
            continue
            
        for i, result in enumerate(results, 1):
            print(f"\nResult {i} (Score: {result['score']:.4f})")
            print(f"Language: {result['snippet']['language']}")
            print(f"Tags: {', '.join(result['snippet']['tags'])}")
            print(f"Description: {result['snippet']['description']}")
            print(f"Code:\n{result['snippet']['code']}\n")

if __name__ == "__main__":
    main()
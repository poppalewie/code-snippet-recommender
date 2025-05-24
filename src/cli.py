from recommender import CodeRecommender
import json
import os

def main():
    recommender = CodeRecommender()
    print("Welcome to the Code Snippet Recommender!")
    print("Enter a query (e.g., 'sort list in python') or 'quit' to exit.")
    print("Optionally, add :language:mode:top_k:save:file (e.g., 'sort list:python:embeddings:3:save:output.json').")
    print("Modes: 'tfidf' (default), 'embeddings'. Top_k: number of results (default 2).")
    
    while True:
        user_input = input("\nQuery: ")
        if user_input.lower() == 'quit':
            break
        if not user_input.strip():
            print("Please enter a valid query.")
            continue
            
        # Split input into parts
        parts = user_input.split(':')
        query = parts[0].strip()
        language = parts[1].strip() if len(parts) > 1 else None
        mode = parts[2].strip() if len(parts) > 2 else 'tfidf'
        top_k = parts[3].strip() if len(parts) > 3 else '2'
        save = parts[4].strip() if len(parts) > 4 else None
        save_file = parts[5].strip() if len(parts) > 5 else 'output.json'
        
        # Validate top_k
        try:
            top_k = int(top_k)
            if top_k < 1:
                print("top_k must be at least 1.")
                continue
        except ValueError:
            print("top_k must be a number.")
            continue
            
        # Get recommendations
        results = recommender.recommend(query, language=language, mode=mode, top_k=top_k)
        if isinstance(results, dict) and 'error' in results:
            print(results['error'])
            continue
        if not results:
            print(f"No matching snippets found{' for language ' + language if language else ''}.")
            continue
            
        # Display results
        for i, result in enumerate(results, 1):
            print(f"\nResult {i} (Score: {result['score']:.4f})")
            print(f"Language: {result['snippet']['language']}")
            print(f"Description: {result['snippet']['description']}")
            print(f"Code:\n{result['snippet']['code']}\n")
            
        # Save results if requested
        if save == 'save':
            try:
                if os.path.exists(save_file):
                    overwrite = input(f"File {save_file} exists. Overwrite? (y/n): ").lower()
                    if overwrite != 'y':
                        print("Results not saved.")
                        continue
                result_data = [
                    {
                        'id': r['snippet']['id'],
                        'language': r['snippet']['language'],
                        'description': r['snippet']['description'],
                        'tags': r['snippet']['tags'],
                        'code': r['snippet']['code'],
                        'score': float(r['score'])
                    } for r in results
                ]
                with open(save_file, 'w') as f:
                    json.dump(result_data, f, indent=4)
                print(f"Results saved to {save_file}")
            except Exception as e:
                print(f"Error saving results: {e}")

if __name__ == "__main__":
    main()
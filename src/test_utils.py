from recommender import CodeRecommender

def test_recommender():
    recommender = CodeRecommender()
    queries = [
        "sort list in python",
        "filter array javascript",
        "find max java",
        "reverse string python",
        "http request javascript"
    ]
    for query in queries:
        print(f"\nQuery: {query}")
        results = recommender.recommend(query, top_k=2)
        if not results:
            print("No results found.")
            continue
        for i, result in enumerate(results, 1):
            print(f"Result {i} (Score: {result['score']:.4f})")
            print(f"Language: {result['snippet']['language']}")
            print(f"Description: {result['snippet']['description']}")
            print(f"Code:\n{result['snippet']['code']}\n")

if __name__ == "__main__":
    test_recommender()
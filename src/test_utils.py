
from recommender import CodeRecommender

def test_recommender():
    recommender = CodeRecommender()
    query = "sort list in python"
    results = recommender.recommend(query)
    for result in results:
        print(f"Score: {result['score']:.4f}")
        print(f"Language: {result['snippet']['language']}")
        print(f"Description: {result['snippet']['description']}")
        print(f"Code:\n{result['snippet']['code']}\n")

if __name__ == "__main__":
    test_recommender()
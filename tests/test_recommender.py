import unittest
import json
import os
from recommender import CodeRecommender

class TestCodeRecommender(unittest.TestCase):
    def setUp(self):
        self.recommender = CodeRecommender()
        # Create a temporary snippets file for testing
        self.test_snippets = [
            {"id": 1, "language": "python", "description": "Test snippet", "tags": ["test"], "code": "print('test')"}
        ]
        with open("tests/test_snippets.json", "w") as f:
            json.dump(self.test_snippets, f)
        self.recommender.load_snippets("tests/test_snippets.json")

    def tearDown(self):
        # Clean up the temporary file
        if os.path.exists("tests/test_snippets.json"):
            os.remove("tests/test_snippets.json")

    def test_empty_query(self):
        result = self.recommender.recommend("", language="python", mode="tfidf", top_k=2)
        self.assertEqual(result, [], "Empty query should return empty results")

    def test_language_filter(self):
        result = self.recommender.recommend("test", language="javascript", mode="tfidf", top_k=2)
        self.assertEqual(result, [], "No snippets in javascript should return empty results")

    def test_tfidf_recommendation(self):
        result = self.recommender.recommend("test", language="python", mode="tfidf", top_k=2)
        self.assertEqual(len(result), 1, "Should return 1 result for TF-IDF mode")

    # Add other test methods as needed...

if __name__ == "__main__":
    unittest.main()
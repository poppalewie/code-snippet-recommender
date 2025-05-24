import unittest
import os
import json
from recommender import CodeRecommender

class TestCodeRecommender(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a temporary snippet file for testing
        cls.test_snippets_file = "tests/test_snippets.json"
        test_snippets = [
            {
                "id": 1,
                "language": "python",
                "description": "Sort a list in ascending order",
                "tags": ["sort", "list", "python"],
                "code": "def sort_list(arr):\n    return sorted(arr)"
            },
            {
                "id": 2,
                "language": "javascript",
                "description": "Filter even numbers from array",
                "tags": ["array", "filter", "javascript"],
                "code": "function filterEvens(arr) {\n    return arr.filter(num => num % 2 === 0);\n}"
            }
        ]
        with open(cls.test_snippets_file, 'w') as f:
            json.dump(test_snippets, f)
        cls.recommender = CodeRecommender(snippets_file=cls.test_snippets_file)

    @classmethod
    def tearDownClass(cls):
        # Clean up temporary file
        if os.path.exists(cls.test_snippets_file):
            os.remove(cls.test_snippets_file)

    def test_tfidf_recommendation(self):
        results = self.recommender.recommend("sort list python", mode="tfidf")
        self.assertGreaterEqual(len(results), 1)
        self.assertEqual(results[0]['snippet']['id'], 1)
        self.assertGreater(results[0]['score'], 0)

    def test_embeddings_recommendation(self):
        results = self.recommender.recommend("arrange list python", mode="embeddings")
        self.assertGreaterEqual(len(results), 1)
        self.assertEqual(results[0]['snippet']['id'], 1)
        self.assertGreater(results[0]['score'], 0)

    def test_language_filter(self):
        results = self.recommender.recommend("sort list", language="python", mode="tfidf")
        self.assertGreaterEqual(len(results), 1)
        self.assertEqual(results[0]['snippet']['language'], "python")
        results = self.recommender.recommend("sort list", language="javascript", mode="tfidf")
        self.assertEqual(len(results), 0)  # No matching snippets after filter

    def test_invalid_mode(self):
        results = self.recommender.recommend("sort list", mode="invalid")
        self.assertIsInstance(results, dict)
        self.assertIn("error", results)
        self.assertIn("Invalid mode", results['error'])

    def test_invalid_language(self):
        results = self.recommender.recommend("sort list", language="go")
        self.assertIsInstance(results, dict)
        self.assertIn("error", results)
        self.assertIn("Language 'go' not found", results['error'])

    def test_empty_query(self):
        results = self.recommender.recommend("", mode="tfidf")
        self.assertEqual(len(results), 0)

    def test_top_k(self):
        results = self.recommender.recommend("sort list python", top_k=2, mode="tfidf")
        self.assertEqual(len(results), 2)
        results = self.recommender.recommend("sort list python", top_k=1, mode="tfidf")
        self.assertEqual(len(results), 1)

if __name__ == '__main__':
    unittest.main()
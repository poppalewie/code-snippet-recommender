from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils import load_snippets
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string

class CodeRecommender:
    def __init__(self, snippets_file="data/snippets.json"):
        self.snippets = load_snippets(snippets_file)
        self.vectorizer = TfidfVectorizer()
        self.documents = self._prepare_documents()
        self.tfidf_matrix = self._fit_vectorizer()

    def _prepare_documents(self):
        # Combine description and tags into a single string for each snippet
        return [
            f"{snippet['description']} {' '.join(snippet['tags'])}"
            for snippet in self.snippets
        ]

    def _fit_vectorizer(self):
        # Convert documents to TF-IDF matrix
        return self.vectorizer.fit_transform(self.documents)

    def _preprocess_query(self, query):
        # Tokenize, lowercase, remove stopwords and punctuation
        stop_words = set(stopwords.words('english'))
        tokens = word_tokenize(query.lower())
        tokens = [t for t in tokens if t not in stop_words and t not in string.punctuation]
        return ' '.join(tokens)

    def recommend(self, query, top_k=2):
        # Preprocess query and convert to TF-IDF vector
        processed_query = self._preprocess_query(query)
        query_vector = self.vectorizer.transform([processed_query])
        # Compute cosine similarity between query and snippets
        similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
        # Get top-k snippet indices
        top_indices = similarities.argsort()[-top_k:][::-1]
        # Return matching snippets with similarity scores
        return [
            {'snippet': self.snippets[i], 'score': similarities[i]}
            for i in top_indices
        ]
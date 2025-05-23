from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils import load_snippets
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import string

class CodeRecommender:
    def __init__(self, snippets_file="data/snippets.json"):
        self.snippets = load_snippets(snippets_file)
        self.vectorizer = TfidfVectorizer()
        self.lemmatizer = WordNetLemmatizer()
        self.documents = self._prepare_documents()
        self.tfidf_matrix = self._fit_vectorizer()

    def _prepare_documents(self):
        stop_words = set(stopwords.words('english'))
        return [
            ' '.join([
                self.lemmatizer.lemmatize(t)
                for t in word_tokenize(f"{snippet['description']} {' '.join(snippet['tags'])}".lower())
                if t not in stop_words and t not in string.punctuation
            ])
            for snippet in self.snippets
        ]

    def _fit_vectorizer(self):
        return self.vectorizer.fit_transform(self.documents)

    def _preprocess_query(self, query):
        stop_words = set(stopwords.words('english'))
        tokens = word_tokenize(query.lower())
        tokens = [
            self.lemmatizer.lemmatize(t)
            for t in tokens
            if t not in stop_words and t not in string.punctuation
        ]
        return ' '.join(tokens)

    def recommend(self, query, top_k=2, language=None):
        processed_query = self._preprocess_query(query)
        query_vector = self.vectorizer.transform([processed_query])
        
        # Filter snippets by language if specified
        if language:
            language = language.lower()
            indices = [i for i, s in enumerate(self.snippets) if s['language'].lower() == language]
            if not indices:
                return []  # No snippets in the specified language
            filtered_matrix = self.tfidf_matrix[indices]
            filtered_snippets = [self.snippets[i] for i in indices]
        else:
            indices = list(range(len(self.snippets)))
            filtered_matrix = self.tfidf_matrix
            filtered_snippets = self.snippets

        # Compute cosine similarity
        similarities = cosine_similarity(query_vector, filtered_matrix).flatten()
        # Get top-k indices
        top_indices = similarities.argsort()[-top_k:][::-1]
        # Return matching snippets with scores
        return [
            {'snippet': filtered_snippets[i], 'score': similarities[i]}
            for i in top_indices
            if similarities[i] > 0  # Only return non-zero similarity results
        ]
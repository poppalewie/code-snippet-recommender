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
        self.lemmatizer = WordNetLemmatizer()  # Initialize lemmatizer
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
        # Lemmatize tokens and remove stopwords/punctuation
        tokens = [
            self.lemmatizer.lemmatize(t)
            for t in tokens
            if t not in stop_words and t not in string.punctuation
        ]
        return ' '.join(tokens)

    def recommend(self, query, top_k=2):
        processed_query = self._preprocess_query(query)
        query_vector = self.vectorizer.transform([processed_query])
        similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
        top_indices = similarities.argsort()[-top_k:][::-1]
        return [
            {'snippet': self.snippets[i], 'score': similarities[i]}
            for i in top_indices
        ]
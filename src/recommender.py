from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils import load_snippets
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import string
from sentence_transformers import SentenceTransformer
import numpy as np

class CodeRecommender:
    def __init__(self, snippets_file="data/snippets.json"):
        self.snippets = load_snippets(snippets_file)
        self.vectorizer = TfidfVectorizer()
        self.lemmatizer = WordNetLemmatizer()
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.documents = self._prepare_documents()
        self.tfidf_matrix = self._fit_vectorizer()
        self.embedding_matrix = self._fit_embeddings()

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

    def _fit_embeddings(self):
        # Generate embeddings for documents
        return self.embedding_model.encode(self.documents, convert_to_numpy=True)

    def _preprocess_query(self, query):
        stop_words = set(stopwords.words('english'))
        tokens = word_tokenize(query.lower())
        tokens = [
            self.lemmatizer.lemmatize(t)
            for t in tokens
            if t not in stop_words and t not in string.punctuation
        ]
        return ' '.join(tokens)

    def recommend(self, query, top_k=2, language=None, mode='tfidf'):
        if mode not in ['tfidf', 'embeddings']:
            return {'error': f"Invalid mode '{mode}'. Use 'tfidf' or 'embeddings'."}
            
        processed_query = self._preprocess_query(query)
        
        # Filter snippets by language if specified
        available_languages = sorted(set(s['language'].lower() for s in self.snippets))
        if language:
            language = language.lower()
            if language not in available_languages:
                return {'error': f"Language '{language}' not found. Available: {', '.join(available_languages)}"}
            indices = [i for i, s in enumerate(self.snippets) if s['language'].lower() == language]
            if not indices:
                return []
            filtered_snippets = [self.snippets[i] for i in indices]
        else:
            indices = list(range(len(self.snippets)))
            filtered_snippets = self.snippets

        if mode == 'tfidf':
            query_vector = self.vectorizer.transform([processed_query])
            filtered_matrix = self.tfidf_matrix[indices]
        else:  # mode == 'embeddings'
            query_vector = self.embedding_model.encode([processed_query], convert_to_numpy=True)
            filtered_matrix = self.embedding_matrix[indices]

        similarities = cosine_similarity(query_vector, filtered_matrix).flatten()
        top_indices = similarities.argsort()[-top_k:][::-1]
        return [
            {'snippet': filtered_snippets[i], 'score': similarities[i]}
            for i in top_indices
            if similarities[i] > 0
        ]
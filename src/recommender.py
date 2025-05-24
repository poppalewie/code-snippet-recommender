import json
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk

class CodeRecommender:
    def __init__(self, snippets_file='data/snippets.json'):
        self.snippets = []
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.vectorizer = TfidfVectorizer()
        self.load_snippets(snippets_file)

    def load_snippets(self, snippets_file):
        with open(snippets_file, 'r') as f:
            self.snippets = json.load(f)

    def recommend(self, query, language=None, mode='tfidf', top_k=2):
        if not query:
            return []
        
        filtered_snippets = [s for s in self.snippets if language is None or s['language'].lower() == language.lower()]
        if not filtered_snippets:
            return []
        
        if mode == 'embeddings':
            query_embedding = self.model.encode(query)
            snippet_embeddings = self.model.encode([s['description'] for s in filtered_snippets])
            similarities = cosine_similarity([query_embedding], snippet_embeddings)[0]
            scored_snippets = [(score, snippet) for score, snippet in zip(similarities, filtered_snippets)]
            scored_snippets.sort(key=lambda x: x[0], reverse=True)
            return [{"score": score, "snippet": snippet} for score, snippet in scored_snippets[:top_k]]
        else:
            documents = [s['description'] for s in filtered_snippets]
            tfidf_matrix = self.vectorizer.fit_transform(documents + [query])
            similarities = cosine_similarity(tfidf_matrix[-1:], tfidf_matrix[:-1])[0]
            scored_snippets = [(score, snippet) for score, snippet in zip(similarities, filtered_snippets)]
            scored_snippets.sort(key=lambda x: x[0], reverse=True)
            return [{"score": score, "snippet": snippet} for score, snippet in scored_snippets[:top_k]]
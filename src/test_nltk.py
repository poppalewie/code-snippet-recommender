import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

def test_nltk():
    # Test tokenization
    text = "Sort a list in Python"
    tokens = word_tokenize(text.lower())
    print(f"Tokens: {tokens}")
    
    # Test stopwords
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [t for t in tokens if t not in stop_words]
    print(f"Filtered tokens: {filtered_tokens}")

if __name__ == "__main__":
    test_nltk()
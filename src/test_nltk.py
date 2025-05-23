import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

def test_nltk():
    # Test tokenization
    text = "Sorting arrays in Python and JavaScript"
    tokens = word_tokenize(text.lower())
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [t for t in tokens if t not in stop_words]
    print(f"Original: {text}")
    print(f"Tokens: {tokens}")
    print(f"Filtered tokens: {filtered_tokens}")
    
if __name__ == "__main__":
    test_nltk()
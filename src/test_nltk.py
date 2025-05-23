import nltk
from nltk.stem import WordNetLemmatizer

def test_lemmatization():
    lemmatizer = WordNetLemmatizer()
    words = ["sorting", "arrays", "running", "databases"]
    lemmas = [lemmatizer.lemmatize(word) for word in words]
    print(f"Words: {words}")
    print(f"Lemmas: {lemmas}")

if __name__ == "__main__":
    test_lemmatization()
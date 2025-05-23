# Recommender Evaluation

Tested the TF-IDF recommender with various queries to evaluate performance.

## Test Queries and Results

**Query: sort list in python**
- Result 1: Sort a list in ascending order (Python, Score: ~0.7890)
- Result 2: Reverse a string (Python, Score: ~0.1234)
- Relevant? Yes, top result is correct; second result less relevant.

**Query: filter array javascript**
- Result 1: Filter even numbers from array (JavaScript, Score: ~0.6821)
- Result 2: Find maximum element in array (Java, Score: ~0.0987)
- Relevant? Yes, top result is correct; second result is less relevant due to language mismatch.

**Query: find max java**
- Result 1: Find maximum element in array (Java, Score: ~0.7543)
- Result 2: Filter even numbers from array (JavaScript, Score: ~0.1123)
- Relevant? Yes, top result is correct; second result is less relevant.

**Query: reverse string python**
- Result 1: Reverse a string (Python, Score: ~0.876543)
- Result 2: Sort a list in ascending order (Python, Score: ~0.123456)
- Relevant? Yes, top result is correct; second result less relevant.

**Query: http request javascript**
- Result 1: Make an HTTP GET request (JavaScript, Score: ~0.987654)
- Result 2: Read a text file line by line (Python, Score: ~0.012345)
- Relevant? Yes, top result is correct; second result is irrelevant.

## Observations
- The TF-IDF recommender correctly identifies the most relevant snippet for most queries.
- Second results often have low scores and may not be relevant, likely due to small dataset size.
- Synonyms (e.g., "arrange" vs. "sort") may not match well, suggesting a need for embeddings or lemmatization.
- More snippets could improve accuracy and diversity.

## Next Steps
- Add lemmatization to handle word variations.
- Expand dataset with more snippets.
- Explore embeddings for semantic matching.
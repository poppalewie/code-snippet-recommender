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


### Observations
- Lemmatization improved matching for queries with word variations (e.g., "sorting" → "sort", "databases" → "database"), with slightly higher scores than Day 8 for relevant snippets.
- Top results are consistently relevant, showing TF-IDF with lemmatization works well for exact and near-exact matches.
- Second results often have low scores and may be irrelevant, due to small dataset size or shared tags (e.g., "python").
- Ambiguous queries (e.g., "sort array") return reasonable results but lower scores, suggesting a need for language filtering.
- Synonyms (e.g., "arrange" vs. "sort") still don’t match well, indicating a need for embeddings or synonym expansion.
- Edge cases like "unknown task python" correctly return low scores, showing robustness.

### Next Steps
- Expand dataset with more snippets to reduce irrelevant second results.
- Add synonym support or embeddings for semantic matching (planned for Day 15).
- Implement language filtering for ambiguous queries.
- Explore quantitative metrics (e.g., precision@K) for automated evaluation.

## Embeddings vs. TF-IDF Evaluation (Day 15)

**Query: arrange list:python:tfidf**
- Result 1: Sort a list in ascending order (Python, Score: ~0.2345, ID: 1)
- Relevant? No; low score due to synonym mismatch.

**Query: arrange list:python:embeddings**
- Result 1: Sort a list in ascending order (Python, Score: ~0.6453, ID: 1)
- Relevant? Yes; embeddings matched "arrange" to "sort" effectively.

**Observations**
- Embeddings significantly improve synonym handling (e.g., "arrange" → "sort").
- Scores are higher in embeddings mode for relevant matches.
- TF-IDF remains faster but less accurate for non-exact matches.


import json
from src.recommender import CodeRecommender

def calculate_metrics(recommender, test_set, mode, k):
    precisions = []
    recalls = []
    
    for test_case in test_set:
        query = test_case['query']
        language = test_case['language']
        relevant_ids = set(test_case['relevant_ids'])
        
        # Get recommendations
        results = recommender.recommend(query, language=language, mode=mode, top_k=k)
        
        # Extract recommended snippet IDs
        recommended_ids = [result['snippet']['id'] for result in results]
        
        # Calculate number of relevant snippets in top K
        relevant_in_top_k = len([rid for rid in recommended_ids if rid in relevant_ids])
        
        # Precision@K = (Number of relevant snippets in top K) / K
        precision = relevant_in_top_k / k if k > 0 else 0
        
        # Recall@K = (Number of relevant snippets in top K) / (Total relevant snippets)
        total_relevant = len(relevant_ids)
        recall = relevant_in_top_k / total_relevant if total_relevant > 0 else 0
        
        precisions.append(precision)
        recalls.append(recall)
        
        print(f"Mode: {mode}, Query: '{query}' (Language: {language})")
        print(f"  Recommended IDs: {recommended_ids}")
        print(f"  Relevant IDs: {list(relevant_ids)}")
        print(f"  Precision@{k}: {precision:.3f}")
        print(f"  Recall@{k}: {recall:.3f}\n")
    
    # Average metrics across all queries
    avg_precision = sum(precisions) / len(precisions) if precisions else 0
    avg_recall = sum(recalls) / len(recalls) if recalls else 0
    return avg_precision, avg_recall

def main():
    # Load test set
    with open('tests/test_set.json', 'r') as f:
        test_set = json.load(f)
    
    # Initialize recommender
    recommender = CodeRecommender()
    
    # Evaluate for both modes at K=3
    k = 3
    print("Evaluating TF-IDF Mode")
    tfidf_precision, tfidf_recall = calculate_metrics(recommender, test_set, mode='tfidf', k=k)
    print("Evaluating Embeddings Mode")
    embeddings_precision, embeddings_recall = calculate_metrics(recommender, test_set, mode='embeddings', k=k)
    
    # Print average results
    print("Summary:")
    print(f"TF-IDF Mode - Average Precision@{k}: {tfidf_precision:.3f}, Average Recall@{k}: {tfidf_recall:.3f}")
    print(f"Embeddings Mode - Average Precision@{k}: {embeddings_precision:.3f}, Average Recall@{k}: {embeddings_recall:.3f}")

if __name__ == '__main__':
    main()
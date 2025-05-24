from flask import Flask, render_template, request
from recommender import CodeRecommender

app = Flask(__name__)
recommender = CodeRecommender()

@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    error = None
    query = language = mode = top_k = save = save_file = None
    
    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        language = request.form.get('language', '').strip() or None
        mode = request.form.get('mode', 'tfidf').strip()
        top_k = request.form.get('top_k', '2').strip()
        
        try:
            top_k = int(top_k)
            if top_k < 1:
                error = "Number of results must be at least 1."
        except ValueError:
            error = "Number of results must be a number."
            
        if not error and query:
            results = recommender.recommend(query, language=language, mode=mode, top_k=top_k)
            if isinstance(results, dict) and 'error' in results:
                error = results['error']
                results = []
    
    return render_template('index.html', results=results, error=error, 
                         query=query, language=language, mode=mode, top_k=top_k or '2')

if __name__ == '__main__':
    app.run(debug=True)
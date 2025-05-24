from flask import Flask, render_template, request, send_file
from recommender import CodeRecommender
import json
import os
import uuid

app = Flask(__name__, template_folder='/home/siwel/Documents/code-snippet-recommender/templates')
recommender = CodeRecommender()

@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    error = None
    query = language = mode = top_k = save_results = results_filename = None
    
    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        language = request.form.get('language', '').strip() or None
        mode = request.form.get('mode', 'tfidf').strip()
        top_k = request.form.get('top_k', '2').strip()
        save_results = request.form.get('save_results') == 'on'
        
        try:
            top_k = int(top_k)
            if top_k < 1:
                error = "Number of results must be at least 1."
            elif top_k > 50:
                top_k = 50
                error = "Number of results capped at 50 for performance."
        except ValueError:
            error = "Number of results must be a number."
            
        if not error and query:
            results = recommender.recommend(query, language=language, mode=mode, top_k=top_k)
            if isinstance(results, dict) and 'error' in results:
                error = results['error']
                results = []
            elif save_results and results:
                # Save results to a JSON file
                results_filename = f"results_{uuid.uuid4()}.json"
                results_path = os.path.join('/home/siwel/Documents/code-snippet-recommender', 'downloads', results_filename)
                os.makedirs(os.path.dirname(results_path), exist_ok=True)
                with open(results_path, 'w') as f:
                    json.dump([{
                        "score": result["score"],
                        "language": result["snippet"]["language"],  # Use dictionary access
                        "description": result["snippet"]["description"],
                        "code": result["snippet"]["code"]
                    } for result in results], f, indent=4)
    
    return render_template('index.html', results=results, error=error,
                         query=query, language=language, mode=mode, top_k=top_k or '2',
                         save_results=save_results, results_filename=results_filename)

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join('/home/siwel/Documents/code-snippet-recommender', 'downloads', filename)
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
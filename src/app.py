from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from recommender import CodeRecommender
import json
import os
import uuid
from glob import glob
from datetime import datetime, timedelta
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from math import ceil
from collections import Counter
import shutil

app = Flask(__name__, template_folder='/home/siwel/Documents/code-snippet-recommender/templates')
app.secret_key = 'supersecretkey'
recommender = CodeRecommender(snippets_file='/home/siwel/Documents/code-snippet-recommender/data/snippets.json')

# Database setup
DATABASE = '/home/siwel/Documents/code-snippet-recommender/users.db'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL
            )
        ''')
        try:
            cursor.execute('ALTER TABLE users ADD COLUMN created_at TEXT')
        except sqlite3.OperationalError:
            pass
        try:
            cursor.execute('ALTER TABLE users ADD COLUMN theme_preference TEXT')
        except sqlite3.OperationalError:
            pass
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS password_reset_tokens (
                username TEXT NOT NULL,
                token TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                PRIMARY KEY (username, token),
                FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS login_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                attempt_time TEXT NOT NULL,
                FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
            )
        ''')
        cursor.execute('''
            UPDATE users
            SET created_at = ?
            WHERE created_at IS NULL
        ''', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'),))
        cursor.execute('''
            UPDATE users
            SET theme_preference = ?
            WHERE theme_preference IS NULL
        ''', ('light',))
        conn.commit()

# Call init_db when the app starts
init_db()

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Set up Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, username):
        self.id = username
        self.username = username

@login_manager.user_loader
def load_user(username):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    if user:
        return User(username)
    return None

def get_user_theme():
    if current_user.is_authenticated:
        conn = get_db_connection()
        user = conn.execute('SELECT theme_preference FROM users WHERE username = ?', (current_user.username,)).fetchone()
        conn.close()
        return user['theme_preference'] if user else 'light'
    return 'light'

def check_login_attempts(username):
    conn = get_db_connection()
    try:
        # Define rate limiting parameters
        ATTEMPT_LIMIT = 5
        TIME_WINDOW_MINUTES = 15
        
        # Calculate the time window (last 15 minutes)
        time_threshold = (datetime.now() - timedelta(minutes=TIME_WINDOW_MINUTES)).strftime('%Y-%m-%d %H:%M:%S')
        
        # Get failed login attempts within the time window
        attempts = conn.execute('''
            SELECT COUNT(*) as attempt_count, MIN(attempt_time) as first_attempt
            FROM login_attempts
            WHERE username = ? AND attempt_time >= ?
        ''', (username, time_threshold)).fetchone()
        
        attempt_count = attempts['attempt_count']
        first_attempt = attempts['first_attempt']
        
        if attempt_count >= ATTEMPT_LIMIT:
            # Calculate when the lockout will expire (15 minutes after the first failed attempt)
            if first_attempt:
                first_attempt_time = datetime.strptime(first_attempt, '%Y-%m-%d %H:%M:%S')
                reset_time = first_attempt_time + timedelta(minutes=TIME_WINDOW_MINUTES)
                if datetime.now() < reset_time:
                    remaining_seconds = (reset_time - datetime.now()).total_seconds()
                    minutes = int(remaining_seconds // 60)
                    seconds = int(remaining_seconds % 60)
                    return False, f"Too many login attempts. Please try again in {minutes} minute(s) and {seconds} second(s)."
                else:
                    # Reset attempts if the lockout period has expired
                    conn.execute('DELETE FROM login_attempts WHERE username = ? AND attempt_time < ?', 
                               (username, time_threshold))
                    conn.commit()
                    return True, None
        return True, None
    finally:
        conn.close()

def log_failed_login_attempt(username):
    conn = get_db_connection()
    try:
        attempt_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        conn.execute('INSERT INTO login_attempts (username, attempt_time) VALUES (?, ?)', 
                    (username, attempt_time))
        conn.commit()
    finally:
        conn.close()

def generate_reset_token(username):
    token = str(uuid.uuid4())
    expires_at = (datetime.now() + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO password_reset_tokens (username, token, expires_at) VALUES (?, ?, ?)',
                     (username, token, expires_at))
        conn.commit()
    finally:
        conn.close()
    return token

def validate_reset_token(token):
    conn = get_db_connection()
    try:
        token_data = conn.execute('SELECT * FROM password_reset_tokens WHERE token = ?', (token,)).fetchone()
        if not token_data:
            return None, "Invalid or expired token."
        expires_at = datetime.strptime(token_data['expires_at'], '%Y-%m-%d %H:%M:%S')
        if datetime.now() > expires_at:
            conn.execute('DELETE FROM password_reset_tokens WHERE token = ?', (token,))
            conn.commit()
            return None, "Token has expired."
        return token_data['username'], None
    finally:
        conn.close()

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if not user:
            flash('Username not found.', 'error')
            return render_template('forgot_password.html', theme='light')
        
        token = generate_reset_token(username)
        reset_link = url_for('reset_password', token=token, _external=True)
        flash(f'Password reset link (simulated email): {reset_link}', 'success')
        return redirect(url_for('login'))
    
    return render_template('forgot_password.html', theme='light')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    username, error = validate_reset_token(token)
    if error:
        flash(error, 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not new_password or not confirm_password:
            flash('All fields are required.', 'error')
            return render_template('reset_password.html', token=token, theme='light')
        if new_password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('reset_password.html', token=token, theme='light')
        if len(new_password) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return render_template('reset_password.html', token=token, theme='light')
        
        conn = get_db_connection()
        try:
            password_hash = generate_password_hash(new_password)
            conn.execute('UPDATE users SET password_hash = ? WHERE username = ?', (password_hash, username))
            conn.execute('DELETE FROM password_reset_tokens WHERE token = ?', (token,))
            conn.commit()
            flash('Password reset successfully! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.Error as e:
            flash(f'Failed to reset password: {str(e)}', 'error')
            return render_template('reset_password.html', token=token, theme='light')
        finally:
            conn.close()
    
    return render_template('reset_password.html', token=token, theme='light')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Username and password are required.', 'error')
            return render_template('register.html', theme='light')
        
        if len(username) < 3 or len(password) < 6:
            flash('Username must be at least 3 characters and password at least 6 characters.', 'error')
            return render_template('register.html', theme='light')
        
        conn = get_db_connection()
        existing_user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        
        if existing_user:
            conn.close()
            flash('Username already exists. Please choose a different one.', 'error')
            return render_template('register.html', theme='light')
        
        password_hash = generate_password_hash(password)
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            conn.execute('INSERT INTO users (username, password_hash, created_at, theme_preference) VALUES (?, ?, ?, ?)', 
                       (username, password_hash, created_at, 'light'))
            conn.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.Error as e:
            conn.close()
            flash(f'Registration failed: {str(e)}', 'error')
            return render_template('register.html', theme='light')
        finally:
            conn.close()
    
    return render_template('register.html', theme='light')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Check rate limiting
        can_attempt, error_message = check_login_attempts(username)
        if not can_attempt:
            flash(error_message, 'error')
            return render_template('login.html', theme='light')
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        
        if user and check_password_hash(user['password_hash'], password):
            # Successful login, clear any previous failed attempts
            conn.execute('DELETE FROM login_attempts WHERE username = ?', (username,))
            conn.commit()
            conn.close()
            
            user_obj = User(username)
            login_user(user_obj)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        else:
            # Failed login, log the attempt
            log_failed_login_attempt(username)
            conn.close()
            flash('Invalid username or password.', 'error')
    
    return render_template('login.html', theme='light')

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (current_user.username,)).fetchone()
    
    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not old_password or not new_password or not confirm_password:
            flash('All fields are required.', 'error')
        elif not check_password_hash(user['password_hash'], old_password):
            flash('Old password is incorrect.', 'error')
        elif new_password != confirm_password:
            flash('New password and confirmation do not match.', 'error')
        elif len(new_password) < 6:
            flash('New password must be at least 6 characters.', 'error')
        else:
            new_password_hash = generate_password_hash(new_password)
            try:
                conn.execute('UPDATE users SET password_hash = ? WHERE username = ?', 
                           (new_password_hash, current_user.username))
                conn.commit()
                flash('Password updated successfully!', 'success')
            except sqlite3.Error as e:
                flash(f'Password update failed: {str(e)}', 'error')
    
    conn.close()
    return render_template('profile.html', user=user, theme=get_user_theme())

@app.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    username = current_user.username
    conn = get_db_connection()
    try:
        conn.execute('DELETE FROM users WHERE username = ?', (username,))
        conn.commit()
        history_dir = os.path.join('/home/siwel/Documents/code-snippet-recommender', 'history', username)
        if os.path.exists(history_dir):
            shutil.rmtree(history_dir)
        downloads_dir = os.path.join('/home/siwel/Documents/code-snippet-recommender', 'downloads', username)
        if os.path.exists(downloads_dir):
            shutil.rmtree(downloads_dir)
        logout_user()
        flash('Your account has been deleted successfully.', 'success')
        return redirect(url_for('login'))
    except sqlite3.Error as e:
        flash(f'Failed to delete account: {str(e)}', 'error')
        return redirect(url_for('profile'))
    finally:
        conn.close()

@app.route('/analytics')
@login_required
def analytics():
    history_file = os.path.join('/home/siwel/Documents/code-snippet-recommender', 'history', current_user.username, 'history.json')
    history = []
    if os.path.exists(history_file):
        with open(history_file, 'r') as f:
            history = json.load(f)
    
    total_searches = len(history)
    languages = [entry['language'].lower() if entry['language'] else 'any' for entry in history]
    language_counts = Counter(languages)
    most_searched_languages = language_counts.most_common(5)
    modes = [entry['mode'].lower() for entry in history]
    mode_counts = Counter(modes)
    most_used_modes = mode_counts.most_common(5)
    
    return render_template('analytics.html', 
                         total_searches=total_searches,
                         most_searched_languages=most_searched_languages,
                         most_used_modes=most_used_modes,
                         theme=get_user_theme())

@app.route('/toggle_theme', methods=['POST'])
@login_required
def toggle_theme():
    conn = get_db_connection()
    current_theme = conn.execute('SELECT theme_preference FROM users WHERE username = ?', (current_user.username,)).fetchone()['theme_preference']
    new_theme = 'dark' if current_theme == 'light' else 'light'
    try:
        conn.execute('UPDATE users SET theme_preference = ? WHERE username = ?', (new_theme, current_user.username))
        conn.commit()
    except sqlite3.Error as e:
        flash(f'Failed to update theme: {str(e)}', 'error')
    finally:
        conn.close()
    return redirect(request.referrer or url_for('index'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
@login_required
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
            else:
                history_dir = os.path.join('/home/siwel/Documents/code-snippet-recommender', 'history', current_user.username)
                history_file = os.path.join(history_dir, 'history.json')
                os.makedirs(history_dir, exist_ok=True)
                search_entry = {
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'query': query,
                    'language': language,
                    'mode': mode,
                    'top_k': top_k,
                    'num_results': len(results),
                    'saved': save_results
                }
                history = []
                if os.path.exists(history_file):
                    with open(history_file, 'r') as f:
                        history = json.load(f)
                history.append(search_entry)
                with open(history_file, 'w') as f:
                    json.dump(history, f, indent=4)
                
                if save_results and results:
                    results_filename = f"results_{uuid.uuid4()}.json"
                    user_dir = os.path.join('/home/siwel/Documents/code-snippet-recommender', 'downloads', current_user.username)
                    results_path = os.path.join(user_dir, results_filename)
                    os.makedirs(user_dir, exist_ok=True)
                    with open(results_path, 'w') as f:
                        json.dump([{
                            "score": result["score"],
                            "language": result["snippet"]["language"],
                            "description": result["snippet"]["description"],
                            "code": result["snippet"]["code"],
                            "query": query,
                            "language_filter": language,
                            "mode": mode,
                            "top_k": top_k
                        } for result in results], f, indent=4)
    
    return render_template('index.html', results=results, error=error,
                         query=query, language=language, mode=mode, top_k=top_k or '2',
                         save_results=save_results, results_filename=results_filename,
                         theme=get_user_theme())

@app.route('/download/<filename>')
@login_required
def download_file(filename):
    file_path = os.path.join('/home/siwel/Documents/code-snippet-recommender', 'downloads', current_user.username, filename)
    return send_file(file_path, as_attachment=True)

@app.route('/saved_results')
@login_required
def saved_results():
    user_dir = os.path.join('/home/siwel/Documents/code-snippet-recommender', 'downloads', current_user.username)
    saved_files = glob(os.path.join(user_dir, "results_*.json"))
    saved_results = []
    
    for file_path in saved_files:
        with open(file_path, 'r') as f:
            results = json.load(f)
            if results:
                metadata = {
                    "filename": os.path.basename(file_path),
                    "query": results[0].get("query", "Unknown"),
                    "language": results[0].get("language_filter", "Any"),
                    "mode": results[0].get("mode", "Unknown"),
                    "top_k": results[0].get("top_k", "Unknown"),
                    "num_results": len(results)
                }
                saved_results.append(metadata)
    
    ITEMS_PER_PAGE = 10
    page = request.args.get('page', 1, type=int)
    total_items = len(saved_results)
    total_pages = ceil(total_items / ITEMS_PER_PAGE)
    start = (page - 1) * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    paginated_results = saved_results[start:end]
    
    return render_template('saved_results.html', saved_results=paginated_results,
                         page=page, total_pages=total_pages,
                         theme=get_user_theme())

@app.route('/delete_result/<filename>', methods=['POST'])
@login_required
def delete_result(filename):
    file_path = os.path.join('/home/siwel/Documents/code-snippet-recommender', 'downloads', current_user.username, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        flash('Saved result deleted successfully!', 'success')
    else:
        flash('Saved result not found.', 'error')
    return redirect(url_for('saved_results'))

@app.route('/search_history')
@login_required
def search_history():
    history_file = os.path.join('/home/siwel/Documents/code-snippet-recommender', 'history', current_user.username, 'history.json')
    history = []
    if os.path.exists(history_file):
        with open(history_file, 'r') as f:
            history = json.load(f)
    
    sort_by = request.args.get('sort_by', 'timestamp_desc')
    filter_language = request.args.get('filter_language', '').strip().lower() or None
    filter_mode = request.args.get('filter_mode', '').strip().lower() or None
    
    filtered_history = history
    if filter_language:
        filtered_history = [entry for entry in filtered_history if entry['language'] and entry['language'].lower() == filter_language]
    if filter_mode:
        filtered_history = [entry for entry in filtered_history if entry['mode'].lower() == filter_mode]
    
    if sort_by == 'timestamp_asc':
        filtered_history.sort(key=lambda x: x['timestamp'])
    elif sort_by == 'timestamp_desc':
        filtered_history.sort(key=lambda x: x['timestamp'], reverse=True)
    elif sort_by == 'query_asc':
        filtered_history.sort(key=lambda x: x['query'].lower())
    elif sort_by == 'query_desc':
        filtered_history.sort(key=lambda x: x['query'].lower(), reverse=True)
    elif sort_by == 'num_results_asc':
        filtered_history.sort(key=lambda x: x['num_results'])
    elif sort_by == 'num_results_desc':
        filtered_history.sort(key=lambda x: x['num_results'], reverse=True)
    
    ITEMS_PER_PAGE = 10
    page = request.args.get('page', 1, type=int)
    total_items = len(filtered_history)
    total_pages = ceil(total_items / ITEMS_PER_PAGE)
    start = (page - 1) * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    paginated_history = filtered_history[start:end]
    
    languages = sorted(set(entry['language'].lower() for entry in history if entry['language']))
    modes = sorted(set(entry['mode'].lower() for entry in history))
    
    return render_template('search_history.html', history=paginated_history, sort_by=sort_by,
                         filter_language=filter_language, filter_mode=filter_mode,
                         languages=languages, modes=modes,
                         page=page, total_pages=total_pages,
                         theme=get_user_theme())

@app.route('/export_search_history')
@login_required
def export_search_history():
    history_file = os.path.join('/home/siwel/Documents/code-snippet-recommender', 'history', current_user.username, 'history.json')
    if os.path.exists(history_file):
        return send_file(history_file, as_attachment=True, download_name=f"search_history_{current_user.username}.json")
    else:
        flash('No search history found to export.', 'error')
        return redirect(url_for('search_history'))

@app.route('/clear_search_history', methods=['POST'])
@login_required
def clear_search_history():
    history_file = os.path.join('/home/siwel/Documents/code-snippet-recommender', 'history', current_user.username, 'history.json')
    if os.path.exists(history_file):
        os.remove(history_file)
        flash('Search history cleared successfully!', 'success')
    else:
        flash('No search history found.', 'error')
    return redirect(url_for('search_history'))

if __name__ == '__main__':
    app.run(debug=True)
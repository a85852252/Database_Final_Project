from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from database import connect_db, create_user, verify_user

app = Flask(__name__)
app.secret_key = 'qwertyuiop'

@app.route('/')
def index():
    username = session.get('username')
    return render_template('index.html', username=username)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        password2 = request.form.get('password2', '')

        if not username or not email or not password or not password2:
            flash('請填寫所有欄位', 'danger')
            return redirect(url_for('register'))
        if password != password2:
            flash('兩次輸入的密碼不一致', 'danger')
            return redirect(url_for('register'))

        conn = connect_db()
        if not conn:
            flash('無法連接資料庫，請稍後再試', 'danger')
            return redirect(url_for('register'))

        result = create_user(conn, username, email, password)
        conn.close()

        if result is True:
            flash('註冊成功，請登入', 'success')
            return redirect(url_for('login'))
        else:
            if '1062' in result:
                flash('使用者名稱或 Email 已被註冊', 'danger')
            else:
                flash('註冊失敗：' + result, 'danger')
            return redirect(url_for('register'))

    return render_template('register.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('請輸入帳號與密碼', 'warning')
            return redirect(url_for('login'))

        conn = connect_db()
        user = verify_user(conn, username, password)
        conn.close()

        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash(f'歡迎回來，{user["username"]}！', 'success')
            return redirect(url_for('index'))
        else:
            flash('帳號或密碼錯誤', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear() 
    flash('已成功登出', 'info')
    return redirect(url_for('index'))

@app.route('/api/search')
def search():
    query = request.args.get('q', '').strip()
    mode = request.args.get('mode', 'name')

    if not query:
        return jsonify([])

    conn = connect_db()
    cursor = conn.cursor(dictionary=True)

    if mode == 'series':
        sql = """
        SELECT name, code, price, stock, image_url
        FROM cards
        WHERE code LIKE %s
        LIMIT 100
        """
        cursor.execute(sql, (f"{query}%",)) 
    else:
        sql = """
        SELECT c.name, c.code, c.price, c.stock, c.image_url 
        FROM cards c
        WHERE name LIKE %s OR code LIKE %s
        LIMIT 100
        """
        cursor.execute(sql, (f"%{query}%", f"%{query}%"))

    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(result)

@app.route('/api/series_list')
def get_series_list():
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT code, name FROM series ORDER BY name")
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)

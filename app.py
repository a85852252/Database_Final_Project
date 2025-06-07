import os
from flask import Flask, Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app
from werkzeug.utils import secure_filename
from database import connect_db, verify_user, create_user

app = Flask(__name__)
app.secret_key = 'qwertyuiop'

auction_bp = Blueprint('auction', __name__)

@auction_bp.route('/auction')
def auction_list():
    tag_id = request.args.get('tag')
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT code, name FROM series ORDER BY name")
    all_series = cursor.fetchall()

    if tag_id:
        cursor.execute("""
            SELECT i.*, u.username,
                   (SELECT image_path FROM auction_images WHERE item_id = i.id LIMIT 1) AS image_path
              FROM auction_items i
              JOIN users u ON i.user_id = u.id
              JOIN auction_item_series ais ON i.id = ais.item_id
             WHERE ais.series_code = %s
             ORDER BY i.created_at DESC
        """, (tag_id,))
    else:
        cursor.execute("""
            SELECT i.*, u.username,
                   (SELECT image_path FROM auction_images WHERE item_id = i.id LIMIT 1) AS image_path
              FROM auction_items i
              JOIN users u ON i.user_id = u.id
             ORDER BY i.created_at DESC
        """)
    items = cursor.fetchall()

    for item in items:
        cursor.execute("""
            SELECT s.code, s.name FROM series s
            JOIN auction_item_series ais ON s.code = ais.series_code
           WHERE ais.item_id = %s
        """, (item['id'],))
        item['series'] = cursor.fetchall()

    conn.close()
    return render_template('auction_list.html', items=items, all_series=all_series, cur_tag=tag_id)

@auction_bp.route('/auction/upload', methods=['GET', 'POST'])
def auction_upload():
    if 'user_id' not in session:
        flash('請先登入', 'warning')
        return redirect(url_for('login'))

    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT code, name FROM series ORDER BY name")
    all_tags = cursor.fetchall()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        price = request.form.get('price', '').strip()
        tags = request.form.getlist('tags')
        images = request.files.getlist('images')

        if not name or not price or not images or images[0].filename == '':
            flash('請填寫商品名稱、價格，並至少上傳一張圖片', 'danger')
            return redirect(url_for('auction.auction_upload'))

        cursor.execute("INSERT INTO auction_items (user_id, name, description, price) VALUES (%s, %s, %s, %s)",
                       (session['user_id'], name, description, price))
        item_id = cursor.lastrowid

        upload_folder = os.path.join(current_app.static_folder, 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        for img in images:
            if img and img.filename:
                filename = secure_filename(img.filename)
                save_path = os.path.join(upload_folder, filename)
                img.save(save_path)
                cursor.execute("INSERT INTO auction_images (item_id, image_path) VALUES (%s, %s)", (item_id, f'uploads/{filename}'))

        series_codes = request.form.getlist('tags') 
        for code in series_codes:
            cursor.execute(
                "INSERT INTO auction_item_series (item_id, series_code) VALUES (%s, %s)", 
                (item_id, code)
            )

        conn.commit()
        conn.close()
        flash('商品已成功上架！', 'success')
        return redirect(url_for('auction.auction_upload'))

    conn.close()
    return render_template('auction_upload.html', all_tags=all_tags)

@auction_bp.route('/auction/my-items')
def user_items():
    if 'user_id' not in session:
        flash('請先登入', 'warning')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT i.*, 
               (SELECT image_path FROM auction_images WHERE item_id = i.id LIMIT 1) AS image_path,
               CASE 
                   WHEN i.is_sold = 1 THEN '已售出'
                   ELSE '待售'
               END AS status_label
          FROM auction_items i
         WHERE i.user_id = %s
         ORDER BY i.created_at DESC
    """, (user_id,))
    items = cursor.fetchall()

    for item in items:
        cursor.execute("""
            SELECT t.* FROM auction_tags t
            JOIN auction_item_tags ait ON t.id = ait.tag_id
           WHERE ait.item_id = %s
        """, (item['id'],))
        item['tags'] = cursor.fetchall()

    conn.close()
    return render_template('user_items.html', items=items)

@app.route('/api/create_tag', methods=['POST'])
def create_tag():
    tag_name = request.json.get('name', '').strip()
    if not tag_name:
        return jsonify({'success': False, 'error': '標籤名稱不可空白'}), 400

    conn = connect_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM auction_tags WHERE name = %s", (tag_name,))
    if cursor.fetchone():
        conn.close()
        return jsonify({'success': False, 'error': '標籤已存在'}), 409

    cursor.execute("INSERT INTO auction_tags (name) VALUES (%s)", (tag_name,))
    conn.commit()
    tag_id = cursor.lastrowid
    conn.close()
    return jsonify({'success': True, 'id': tag_id, 'name': tag_name})

@app.route('/')
def index():
    username = session.get('username')
    return render_template('index.html', username=username)

@app.before_request
def make_session_not_permanent():
    session.permanent = False

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
            session.permanent = False    
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

app.register_blueprint(auction_bp)

if __name__ == "__main__":
    app.run(debug=True)

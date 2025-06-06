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

    # 查詢所有標籤（for 篩選用）
    cursor.execute("SELECT * FROM auction_tags ORDER BY name")
    all_tags = cursor.fetchall()

    # 查詢商品（如有篩選就只撈該標籤）
    if tag_id:
        cursor.execute("""
            SELECT i.*, u.username,
                   (SELECT image_path FROM auction_images WHERE item_id = i.id LIMIT 1) AS image_path
              FROM auction_items i
              JOIN users u ON i.user_id = u.id
              JOIN auction_item_tags ait ON i.id = ait.item_id
             WHERE ait.tag_id = %s
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

    # 對每個商品查標籤
    for item in items:
        cursor.execute("""
            SELECT t.* FROM auction_tags t
            JOIN auction_item_tags ait ON t.id = ait.tag_id
           WHERE ait.item_id = %s
        """, (item['id'],))
        item['tags'] = cursor.fetchall()

    conn.close()
    return render_template('auction_list.html', items=items, all_tags=all_tags, cur_tag=tag_id)

    tag_id = request.args.get('tag')
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    
    # 查詢所有標籤（for 篩選用）
    cursor.execute("SELECT * FROM auction_tags ORDER BY name")
    all_tags = cursor.fetchall()
    
    # 查詢商品（如有篩選就只撈該標籤）
    if tag_id:
        cursor.execute("""
            SELECT i.*, u.username,
                   (SELECT image_path FROM auction_images WHERE item_id = i.id LIMIT 1) AS image_path
              FROM auction_items i
              JOIN users u ON i.user_id = u.id
              JOIN auction_item_tags ait ON i.id = ait.item_id
             WHERE ait.tag_id = %s
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
    
    # 對每個商品查標籤（優化可再合併查詢，這邊先 for 迴圈寫法）
    for item in items:
        cursor.execute("""
            SELECT t.* FROM auction_tags t
            JOIN auction_item_tags ait ON t.id = ait.tag_id
           WHERE ait.item_id = %s
        """, (item['id'],))
        item['tags'] = cursor.fetchall()
    
    conn.close()
    return render_template('auction_list.html', items=items, all_tags=all_tags, cur_tag=tag_id)

@auction_bp.route('/auction/upload', methods=['GET', 'POST'])
def auction_upload():
    if 'user_id' not in session:
        flash('請先登入', 'warning')
        return redirect(url_for('login'))

    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM auction_tags ORDER BY name")
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

        for tag_id in tags:
            cursor.execute("INSERT INTO auction_item_tags (item_id, tag_id) VALUES (%s, %s)", (item_id, tag_id))

        conn.commit()
        conn.close()
        flash('商品已成功上架！', 'success')
        return redirect(url_for('auction.auction_upload'))

    conn.close()
    return render_template('auction_upload.html', all_tags=all_tags)

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

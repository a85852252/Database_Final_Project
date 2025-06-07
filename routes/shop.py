#shop.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app
import os
from werkzeug.utils import secure_filename
from utils.database import connect_db

shop_bp = Blueprint('shop', __name__)

@shop_bp.route('/auction')
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
             WHERE ais.series_code = %s AND i.stock > 0
             ORDER BY i.created_at DESC
        """, (tag_id,))
    else:
        cursor.execute("""
            SELECT i.*, u.username,
                   (SELECT image_path FROM auction_images WHERE item_id = i.id LIMIT 1) AS image_path
              FROM auction_items i
              JOIN users u ON i.user_id = u.id
             WHERE i.stock > 0
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

@shop_bp.route('/auction/upload', methods=['GET', 'POST'])
def auction_upload():
    if 'user_id' not in session:
        flash('請先登入', 'warning')
        return redirect(url_for('auth.login'))

    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    # 用 series 做商品標籤（多選）
    cursor.execute("SELECT code, name FROM series ORDER BY name")
    all_series = cursor.fetchall()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        price = request.form.get('price', '').strip()
        series_codes = request.form.getlist('series_codes')  # <--- 取多選
        images = request.files.getlist('images')

        if not name or not price or not images or images[0].filename == '':
            flash('請填寫商品名稱、價格，並至少上傳一張圖片', 'danger')
            return redirect(url_for('shop.auction_upload'))  # <--- 修正

        cursor.execute(
            "INSERT INTO auction_items (user_id, name, description, price) VALUES (%s, %s, %s, %s)",
            (session['user_id'], name, description, price)
        )
        item_id = cursor.lastrowid

        upload_folder = os.path.join(current_app.static_folder, 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        for img in images:
            if img and img.filename:
                filename = secure_filename(img.filename)
                save_path = os.path.join(upload_folder, filename)
                img.save(save_path)
                cursor.execute(
                    "INSERT INTO auction_images (item_id, image_path) VALUES (%s, %s)",
                    (item_id, f'uploads/{filename}')
                )

        # 寫入商品-系列關聯（多選）
        for code in series_codes:
            cursor.execute(
                "INSERT INTO auction_item_series (item_id, series_code) VALUES (%s, %s)", 
                (item_id, code)
            )

        conn.commit()
        conn.close()
        flash('商品已成功上架！', 'success')
        return redirect(url_for('shop.auction_upload'))

    conn.close()
    # 對應前端用 all_series
    return render_template('auction_upload.html', all_series=all_series)

@shop_bp.route('/auction/my-items')
def user_items():
    if 'user_id' not in session:
        flash('請先登入', 'warning')
        return redirect(url_for('auth.login'))  # <--- 修正
    
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

@shop_bp.route('/auction/edit/<int:item_id>', methods=['GET', 'POST'])
def auction_edit(item_id):
    if 'user_id' not in session:
        flash('請先登入', 'warning')
        return redirect(url_for('auth.login'))

    conn = connect_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM auction_items WHERE id=%s AND user_id=%s", (item_id, session['user_id']))
    item = cursor.fetchone()
    if not item:
        conn.close()
        flash('找不到商品或沒有權限', 'danger')
        return redirect(url_for('shop.user_items'))  

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        price = request.form.get('price', '').strip()
        stock = request.form.get('stock', '').strip()

        if not name or not price or not stock:
            flash('名稱、價格、庫存不可空白', 'danger')
            return redirect(request.url)

        cursor.execute("""
            UPDATE auction_items
            SET name=%s, description=%s, price=%s, stock=%s
            WHERE id=%s AND user_id=%s
        """, (name, description, price, stock, item_id, session['user_id']))
        conn.commit()
        conn.close()
        flash('商品資訊已更新', 'success')
        return redirect(url_for('shop.user_items'))

    conn.close()
    return render_template('auction_edit.html', item=item)

@shop_bp.route('/api/create_tag', methods=['POST'])
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

@shop_bp.route('/api/search')
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

@shop_bp.route('/api/series_list')
def get_series_list():
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT code, name FROM series ORDER BY name")
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(result)

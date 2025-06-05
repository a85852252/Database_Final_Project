from flask import Flask, render_template, request, jsonify
from database import connect_db

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/search')
def search():
    query = request.args.get('q', '').strip()
    mode = request.args.get('mode', 'card')  # 預設為 card 模式

    conn = connect_db()
    cursor = conn.cursor(dictionary=True)

    if mode == 'series':
        sql = """
        SELECT * FROM series
        WHERE name LIKE %s OR unique_code LIKE %s
        """
        like_query = f"%{query}%"
        cursor.execute(sql, (like_query, like_query))
        data = cursor.fetchall()

    else:  # 預設卡片搜尋
        sql = """
        SELECT * FROM cards
        WHERE name LIKE %s OR code LIKE %s
        """
        like_query = f"%{query}%"
        cursor.execute(sql, (like_query, like_query))
        data = cursor.fetchall()

    conn.close()
    return jsonify(data)



if __name__ == "__main__":
    app.run(debug=True)

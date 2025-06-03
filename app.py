from flask import Flask, render_template, request, jsonify
from database import connect_db

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/search")
def search_cards():
    keyword = request.args.get("q", "").strip().lower()
    mode = request.args.get("mode", "name")

    if not keyword:
        return jsonify([])

    conn = connect_db()
    if not conn:
        return jsonify([])

    cursor = conn.cursor(dictionary=True)

    if mode == "series":
        # 你之後可以另外實作 series 搜尋條件
        query = "SELECT name, price, image_url, stock, code FROM cards WHERE LOWER(name) LIKE %s"
        cursor.execute(query, (f"%{keyword}%",))
    else:
        # 同時搜尋 name 和 code 欄位
        query = """
            SELECT name, price, image_url, stock, code
            FROM cards
            WHERE LOWER(name) LIKE %s OR LOWER(code) LIKE %s
        """
        cursor.execute(query, (f"%{keyword}%", f"%{keyword}%"))

    results = cursor.fetchall()
    conn.close()
    return jsonify(results)



if __name__ == "__main__":
    app.run(debug=True)

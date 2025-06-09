from flask import Flask
from routes.auth import auth_bp
from routes.shop import shop_bp

app = Flask(__name__)

# ⚠️ 正式專案建議使用環境變數存放 secret key，不要寫死在程式碼裡
app.secret_key = 'qwertyuiop'

# 註冊 Blueprint
app.register_blueprint(auth_bp)
app.register_blueprint(shop_bp)

# ====== 首頁路由 ======
@app.route('/')
def index():
    """
    首頁：若已登入則顯示 username，否則為訪客
    """
    from flask import session, render_template
    username = session.get('username')
    return render_template('index.html', username=username)

# ====== 每次請求前設置 Session 為非永久 ======
@app.before_request
def make_session_not_permanent():
    """
    每次請求前讓 session 不永久（瀏覽器關閉即登出）
    """
    from flask import session
    session.permanent = False

if __name__ == "__main__":
    # ⚠️ 建議生產環境關掉 debug=True
    app.run(debug=True)

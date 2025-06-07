from flask import Flask
from routes.auth import auth_bp
from routes.shop import shop_bp

app = Flask(__name__)
app.secret_key = 'qwertyuiop'

app.register_blueprint(auth_bp)
app.register_blueprint(shop_bp)

@app.route('/')
def index():
    from flask import session, render_template
    username = session.get('username')
    return render_template('index.html', username=username)

@app.before_request
def make_session_not_permanent():
    from flask import session
    session.permanent = False

if __name__ == "__main__":
    app.run(debug=True)

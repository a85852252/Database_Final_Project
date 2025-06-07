from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.database import connect_db, verify_user, create_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        password2 = request.form.get('password2', '')

        if not username or not email or not password or not password2:
            flash('請填寫所有欄位', 'danger')
            return redirect(url_for('auth.register'))  
        if password != password2:
            flash('兩次輸入的密碼不一致', 'danger')
            return redirect(url_for('auth.register'))  

        conn = connect_db()
        if not conn:
            flash('無法連接資料庫，請稍後再試', 'danger')
            return redirect(url_for('auth.register'))

        result = create_user(conn, username, email, password)
        conn.close()

        if result is True:
            flash('註冊成功，請登入', 'success')
            return redirect(url_for('auth.login'))   
        else:
            if '1062' in result:
                flash('使用者名稱或 Email 已被註冊', 'danger')
            else:
                flash('註冊失敗：' + result, 'danger')
            return redirect(url_for('auth.register'))  .

    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('請輸入帳號與密碼', 'warning')
            return redirect(url_for('auth.login'))   

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
            return redirect(url_for('auth.login'))  

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('已成功登出', 'info')
    return redirect(url_for('index'))   

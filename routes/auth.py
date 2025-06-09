from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.database import connect_db, verify_user, create_user

# 建立 Auth 藍圖 (模組化註冊/登入/登出功能)
auth_bp = Blueprint('auth', __name__)

# ========= 註冊 =========
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    使用者註冊流程
    - 前端表單驗證
    - 資料庫寫入（不可重複）
    """
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        password2 = request.form.get('password2', '')

        # 表單欄位檢查
        if not username or not email or not password or not password2:
            flash('請填寫所有欄位', 'danger')
            return redirect(url_for('auth.register'))
        if password != password2:
            flash('兩次輸入的密碼不一致', 'danger')
            return redirect(url_for('auth.register'))

        # 嘗試連接資料庫
        conn = connect_db()
        if not conn:
            flash('無法連接資料庫，請稍後再試', 'danger')
            return redirect(url_for('auth.register'))

        # 建立新用戶
        result = create_user(conn, username, email, password)
        conn.close()

        if result is True:
            flash('註冊成功，請登入', 'success')
            return redirect(url_for('auth.login'))
        else:
            # 1062: Duplicate entry（MySQL錯誤碼）
            if '1062' in str(result):
                flash('使用者名稱或 Email 已被註冊', 'danger')
            else:
                flash('註冊失敗：' + str(result), 'danger')
            return redirect(url_for('auth.register'))

    return render_template('auth/register.html')

# ========= 登入 =========
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    使用者登入流程
    - 前端表單驗證
    - 資料庫密碼比對
    """
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('請輸入帳號與密碼', 'warning')
            return redirect(url_for('auth.login'))

        # 查詢/比對密碼
        conn = connect_db()
        user = verify_user(conn, username, password)
        conn.close()

        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session.permanent = False    # session 不永久，瀏覽器關閉即登出
            flash(f'歡迎回來，{user["username"]}！', 'success')
            return redirect(url_for('index'))
        else:
            flash('帳號或密碼錯誤', 'danger')
            return redirect(url_for('auth.login'))

    return render_template('auth/login.html')

# ========= 登出 =========
@auth_bp.route('/logout')
def logout():
    """
    使用者登出流程
    - 清空 session
    """
    session.clear()
    flash('已成功登出', 'info')
    return redirect(url_for('index'))


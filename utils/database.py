import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash

# 連接資料庫
def connect_db():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='AkaYu1030',
            database='yuyutei',
            charset='utf8mb4'
        )
        print("正在嘗試連接 MySQL...")
        return conn
    except Error as e:
        print(f"資料庫連線錯誤：{e}")
        return None

# 清空 cards 資料表
def clear_table(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("TRUNCATE TABLE cards")
        conn.commit()
        print("資料表 cards 已清空")
    except Error as e:
        print(f"清空 cards 資料表失敗：{e}")

# 插入 card資料
def insert_card(conn, name, price, image_url, stock, code):
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO cards (name, price, image_url, stock, code)
            VALUES (%s, %s, %s, %s, %s)
            """, (name, price, image_url, stock, code))
        conn.commit()
    except Error as e:
        print(f"插入卡片資料失敗：{e}")

# 清空 series 資料表
def clear_series_table(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("TRUNCATE TABLE series")
        conn.commit()
        print("系列資料表已清空")
    except Error as e:
        print(f"清空系列資料表失敗：{e}")

# 插入 serie 資料
def insert_series(conn, name, code):
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT IGNORE INTO series (name, code)
            VALUES (%s, %s)
        """, (name, code))
        conn.commit()
    except Error as e:
        print(f"插入系列資料失敗：{e}")

# 清空 yuyutei_series_links 資料表
def clear_yuyutei_series_links(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("TRUNCATE TABLE yuyutei_series_links")
        conn.commit()
        print("yuyutei_series_links 資料表已清空")
    except Error as e:
        print(f"清空 yuyutei_series_links 失敗：{e}")

# 插入 yuyutei_series_links 資料
def insert_yuyutei_series_link(conn, name, url):
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT IGNORE INTO yuyutei_series_links (name, url)
            VALUES (%s, %s)
        """, (name, url))
        conn.commit()
    except Error as e:
        print(f"插入 yuyutei_series_links 失敗：{e}")

def create_user(conn, username, email, password_plaintext):
    try:
        pw_hash = generate_password_hash(password_plaintext)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (username, email, password_hash)
            VALUES (%s, %s, %s)
        """, (username, email, pw_hash))
        conn.commit()
        return True
    except Error as e:
        return str(e)

def get_user_by_username(conn, username):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    return user

def get_user_by_email(conn, email):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()
    return user

def verify_user(conn, username, password_plaintext):
    user = get_user_by_username(conn, username)
    if not user:
        return None
    if check_password_hash(user['password_hash'], password_plaintext):
        return user
    return None

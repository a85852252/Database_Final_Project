# DATABASE_FINAL_PROJECT

本專題致力於打造一個整合主流卡牌市場資訊、並結合二手交易/搜尋功能的全方位平台。  
玩家可以即時查詢卡片價格、拍賣商品、並比對悠遊亭等實時行情，協助卡牌蒐集與交易更便利。

---

## 🎯 主要功能

1. **卡牌即時查詢**  
   - 依卡片名稱或系列搜尋，可直接比對市場價格（以悠悠亭行情為主）。
2. **自建拍賣賣場**  
   - 註冊登入後可上架/管理自己的商品，支援多圖、標籤、系列分類。
3. **專屬爬蟲同步資料**  
   - 定期同步官方 WS 官網與悠悠亭卡片數據，維持最新行情。
4. **彈性標籤與多條件搜尋**  
   - 商品可標記多個標籤、支援複合搜尋、查詢更快速。

---

## 📁 專案目錄結構

```text
專案根目錄/
├── app.py                  # Flask 主應用程式
├── utils/
│   └── database.py         # 資料庫操作模組
├── routes/
│   ├── auth.py             # 登入註冊相關路由
│   └── shop.py             # 拍賣/搜尋相關路由
├── scraper/
│   ├── card_scraper.py         # 悠悠亭單卡資料爬蟲
│   ├── series_scraper.py       # WS 官網系列列表爬蟲
│   └── yuyutei_top_scraper.py  # 悠悠亭系列頁連結爬蟲
│   └── __init__.py
├── scraper_main.py         # 一鍵啟動所有爬蟲的主程式
├── static/                 # 靜態檔案（CSS、JS、圖片、上傳）
│   ├── CSS/
│   ├── JS/
│   ├── img/
│   └── uploads/
├── templates/              # 前端頁面模板
│   ├── base.html
│   ├── index.html
│   └── ...（細分各功能頁）
├── sql_commend.txt         # 資料庫建表指令
├── README.md
└── .pyc, __pycache__       # 編譯暫存（自動產生，可忽略）
```

## 🚀 安裝與執行方式

### 1. 環境需求

- Python 3.10+

- MySQL 8 或 5.7 以上

### 2. 安裝套件

```bash
pip install requests beautifulsoup4 mysql-connector-python flask Werkzeug
```

### 3. 初始化資料庫

1. 建立 MySQL 資料庫（建議名稱 yuyutei）

2. 使用 sql_commend.txt 內所有 SQL 指令建立資料表：

``` SQL
CREATE DATABASE yuyutei CHARACTER SET utf8mb4;
USE yuyutei;
-- 複製 sql_commend.txt 所有內容貼上執行
```

3. 編輯 utils/database.py 連線設定（帳號/密碼/資料庫）

### 4. 爬蟲資料同步

依序自動擷取所有官方/悠悠亭數據，請執行：

```bash
python scraper_main.py
```

### 5. 啟動網站服務

```bash
python app.py
```

．開啟瀏覽器訪問 http://localhost:5000
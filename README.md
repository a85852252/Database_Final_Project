# DATABASE_FINAL_PROJECT

此專題的目標是建立一個能夠將目前市面較主流的卡牌交易市場去做全面性的統合。以下為其功能

1. 具有可依關鍵字完成單卡/卡表的查詢並提供玩家常用於作為價格標準的悠悠亭價格以方便了解市場行情
2. 提供買賣服務並加強特定商品的搜尋能力

## 📁 專案結構

<pre> 專案根目錄/ ├── __pycache__/ # Python 編譯後快取檔案 ├── scraper/ # 網路爬蟲模組 ├── static/ # 靜態檔案（如 CSS、JS、圖片等） ├── templates/ # HTML 模板（用於網頁渲染） ├── app.py # Flask 應用程式主入口 ├── database.py # 資料庫操作相關程式碼 ├── scraper_main.py # 網路爬蟲模組整合及執行 ├── README.md # 專案說明文件 └── sql_commend.txt # SQL 指令記錄 </pre>


## 🚀 安裝與執行方式

### 1. 環境需求

- Python 3.10+

### 2. 安裝套件

```bash
pip install requests beautifulsoup4 mysql-connector-python flask pandas schedule
```

### 3. 執行方式

```bash
python scraper_main.py 
python app.py
```
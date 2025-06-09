# scraper/series_scraper.py
# 用途：爬取卡片官網所有系列名稱與系列代號，存進本地資料庫

import requests
from bs4 import BeautifulSoup
from utils.database import connect_db, clear_series_table, insert_series

def scrape_series():
    """
    從卡片官網首頁抓取所有系列資料（名稱＋系列代號）
    :return: list of (name, code) tuple
    """
    url = 'https://ws-tcg.com/cardlist/'
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    print(f"狀態碼：{response.status_code}")
    response.encoding = 'utf-8'

    soup = BeautifulSoup(response.text, 'html.parser')
    # 找出所有含有 showTitleNumberDetail 的系列連結
    series_links = soup.select("a[onclick^=showTitleNumberDetail]")
    print(f"抓到系列數：{len(series_links)}")

    series_data = []
    for a in series_links:
        onclick = a.get('onclick')
        name = a.text.strip()
        if not onclick or not name:
            continue

        # 解析 onclick 內容，例如 showTitleNumberDetail('##abc##def##...')
        try:
            raw_codes = onclick.split("'")[1]  # 取得 '##abc##def##...' 這段
            code_list = [code for code in raw_codes.split('##') if code]  # 分離出所有代號
        except IndexError:
            print(f"無法解析 onclick: {onclick}")
            continue

        for code in code_list:
            series_data.append((name, code))

    return series_data

def run_series_scraper():
    """
    主流程：連線資料庫、清空原有系列、批次寫入新系列資料
    """
    print("啟動系列爬蟲程式")
    conn = connect_db()
    if not conn:
        print("資料庫連線失敗")
        return

    clear_series_table(conn)      # 清空舊的系列表，確保不重複
    series = scrape_series()
    print(f"實際抓到 {len(series)} 筆系列資料")

    for name, code in series:
        insert_series(conn, name, code)

    conn.close()
    print("系列資料寫入完成，資料庫連線已關閉")

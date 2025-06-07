# scraper/series_scraper.py
import requests
from bs4 import BeautifulSoup
from utils.database import connect_db, clear_series_table, insert_series

def scrape_series():
    url = 'https://ws-tcg.com/cardlist/'
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    print(f"狀態碼：{response.status_code}")
    response.encoding = 'utf-8'

    soup = BeautifulSoup(response.text, 'html.parser')
    series_links = soup.select("a[onclick^=showTitleNumberDetail]")
    print(f"抓到系列數：{len(series_links)}")

    series_data = []
    for a in series_links:
        onclick = a.get('onclick')
        name = a.text.strip()
        if not onclick or not name:
            continue

        # 擷取 showTitleNumberDetail('##ABC##') 中所有代號
        try:
            raw_codes = onclick.split("'")[1]  # e.g. '##abc##def##ghi##'
            code_list = [code for code in raw_codes.split('##') if code]  # 去除空白，分離代號
        except IndexError:
            print(f"無法解析 onclick: {onclick}")
            continue

        for code in code_list:
            series_data.append((name, code))

    return series_data

def run_series_scraper():
    print("啟動系列爬蟲程式")
    conn = connect_db()
    if not conn:
        print("資料庫連線失敗")
        return

    clear_series_table(conn)
    series = scrape_series()
    print(f"實際抓到 {len(series)} 筆系列資料")

    for name, code in series:
        insert_series(conn, name, code)

    conn.close()
    print("系列資料寫入完成，資料庫連線已關閉")

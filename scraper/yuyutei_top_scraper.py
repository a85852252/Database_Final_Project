# yuyutei_top_scraper.py
# 用途：爬取 yuyu-tei.jp 官方 WS 卡牌分類所有「#kana」賣場連結，寫入本地資料庫

import requests
from bs4 import BeautifulSoup

def scrape_yuyutei_series_links():
    """
    從 YUYU-TEI 官網爬出所有系列分類連結
    :return: list of dict，每筆 {'name':..., 'url':...}
    """
    url = 'https://yuyu-tei.jp/top/ws'
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    print(f"狀態碼：{response.status_code}")
    response.encoding = 'utf-8'

    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.select('a[href*="/sell/ws/s/"]')

    series_list = []
    for a in links:
        name = a.text.strip()
        href = a.get('href')

        # 只保留含有 '#kana' 的連結（官方有分類效果）
        if not href or '#kana' not in href:
            continue

        # 統一補齊為絕對路徑
        full_url = f"https://yuyu-tei.jp{href}" if href.startswith("/") else href
        series_list.append({'name': name, 'url': full_url})

    # 避免重複：以 url 做唯一 key，覆蓋名稱
    unique = {}
    for item in series_list:
        unique[item['url']] = item['name']
    deduped = [{'name': name, 'url': url} for url, name in unique.items()]

    return deduped

def run_yuyutei_top_scraper():
    """
    主流程：連線資料庫、清空表格、批次寫入新抓到的系列連結
    """
    from utils.database import connect_db, clear_yuyutei_series_links, insert_yuyutei_series_link

    print("開始爬取 YUYU-TEI 系列連結")
    conn = connect_db()
    if not conn:
        return

    clear_yuyutei_series_links(conn)    # 清空表
    data = scrape_yuyutei_series_links()
    print(f"擷取 {len(data)} 筆資料")

    for item in data:
        insert_yuyutei_series_link(conn, item['name'], item['url'])

    conn.close()
    print("系列連結已寫入完成")

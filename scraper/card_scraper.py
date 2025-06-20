# card_scraper.py
# 用途：從系列連結批次爬取卡牌資料，清空後寫入 MySQL 資料庫

import requests
from bs4 import BeautifulSoup
from utils.database import connect_db, insert_card, clear_table

def scrape_cards_from_url(url):
    """
    抓取單一系列頁面的所有卡片資料
    :param url: 系列商品頁面網址
    :return: list[dict] 各卡片基本資料
    """
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    print(f"正在抓取：{url}，狀態碼：{response.status_code}")

    soup = BeautifulSoup(response.text, 'html.parser')
    cards = soup.select('#card-lits .card-product')  # 注意：若網頁結構有異需同步修正
    print(f"抓到卡片數量：{len(cards)}")

    card_list = []
    for card in cards:
        # 各區塊資料皆防呆
        name_tag = card.select_one('h4.text-primary')
        price_tag = card.select_one('strong.text-end')
        img_tag = card.select_one('.product-img img')
        stock_tag = card.select_one('.cart_sell_zaiko')
        code_tag = card.select_one('span.border-dark')

        name = name_tag.text.strip() if name_tag else 'N/A'
        price = price_tag.text.replace("円", "").replace(",", "").strip() if price_tag else '0'
        image_url = img_tag['src'] if img_tag else 'N/A'
        stock = stock_tag.text.replace("在庫 :", "").strip() if stock_tag else 'N/A'
        card_code = code_tag.text.strip() if code_tag else 'N/A'

        card_list.append({
            'name': name,
            'price': price,
            'image_url': image_url,
            'stock': stock,
            'code': card_code
        })
    return card_list

def run_card_scraper():
    """
    主流程：連接資料庫，清空舊卡片資料，依系列連結批次爬卡寫入
    """
    print("啟動卡片爬蟲程式")
    conn = connect_db()
    if not conn:
        print("資料庫連線失敗")
        return

    # 清空原本 cards 資料表，避免重複或殘留
    clear_table(conn)

    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT url FROM yuyutei_series_links")
    urls = [row[0] for row in cursor.fetchall()]
    print(f"準備處理 {len(urls)} 筆系列連結")

    for url in urls:
        cards = scrape_cards_from_url(url)
        print(f"從 {url} 抓取 {len(cards)} 張卡片")
        for card in cards:
            insert_card(conn, card['name'], card['price'], card['image_url'], card['stock'], card['code'])

    conn.close()
    print("卡片資料寫入完成，資料庫連線已關閉")

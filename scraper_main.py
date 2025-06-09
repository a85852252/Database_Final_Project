# scraper_main.py
# 用途：統一管理所有卡牌資料爬蟲，依流程順序自動執行

from scraper.series_scraper import run_series_scraper           # 1. 抓 WS 官網系列資料
from scraper.yuyutei_top_scraper import run_yuyutei_top_scraper # 2. 抓 YUYU-TEI 官網分類連結
from scraper.card_scraper import run_card_scraper               # 3. 抓 YUYU-TEI 每張卡片資料

def main():
    print("==============================")
    print("啟動爬蟲流程")
    print("==============================")

    print("\n[1/3] 擷取 WS 系列資料（官網）...")
    run_series_scraper()  # 先取得系列名稱＋代號

    print("\n[2/3] 擷取 YUYU-TEI 系列連結...")
    run_yuyutei_top_scraper()  # 取得分類連結

    print("\n[3/3] 擷取 YUYU-TEI 卡片資料...")
    run_card_scraper()    # 依所有連結爬每張卡片、寫入資料庫

    print("\n所有流程執行完畢！")

if __name__ == "__main__":
    main()

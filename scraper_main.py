# main.py
from scraper.series_scraper import run_series_scraper
from scraper.yuyutei_top_scraper import run_yuyutei_top_scraper
from scraper.card_scraper import run_card_scraper


def main():
    print("==============================")
    print("啟動爬蟲流程")
    print("==============================")

    print("\n[1/3] 擷取 WS 系列資料（官網）...")
    run_series_scraper()

    print("\n[2/3] 擷取 YUYU-TEI 系列連結...")
    run_yuyutei_top_scraper()

    print("\n[3/3] 擷取 YUYU-TEI 卡片資料...")
    run_card_scraper()

    print("\n所有流程執行完畢！")


if __name__ == "__main__":
    main()

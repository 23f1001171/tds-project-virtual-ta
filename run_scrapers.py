
import os
from scrape.scrape_tds import scrape_tds_site
from scrape.scrape_discourse import scrape_forum

def ensure_data_folder():
    if not os.path.exists("data"):
        os.makedirs("data")

def main():
    print("🚀 Starting scraping pipeline...\n")

    ensure_data_folder()

    print("🔍 Scraping TDS site content...")
    try:
        scrape_tds_site()
    except Exception as e:
        print(f"❌ TDS site scraping failed: {e}")

    print("\n🔍 Scraping Discourse forum content...")
    try:
        scrape_forum()
    except Exception as e:
        print(f"❌ Discourse forum scraping failed: {e}")

    print("\n✅ All scraping complete. JSON files saved in 'data/' folder.")

if __name__ == "__main__":
    main()

# import requests
# res = requests.get("https://discourse.onlinedegree.iitm.ac.in/c/courses/tds-kb/34.json")
# print(res.status_code)
# print(res.headers["Content-Type"])
# print(res.text[:1000])  # Print first 1000 chars of the response

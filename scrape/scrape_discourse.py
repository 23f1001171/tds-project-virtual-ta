from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from datetime import datetime
import json
import time
import os

BASE_URL     = "https://discourse.onlinedegree.iitm.ac.in"
LOGIN_URL    = f"{BASE_URL}/login"
CATEGORY_URL = f"{BASE_URL}/c/courses/tds-kb/34"
START_DATE   = datetime(2025, 1, 1)
END_DATE     = datetime(2025, 4, 14)

def parse_created_at(date_str):
    try:
        return datetime.strptime(date_str, "%b %d, %Y %I:%M %p")
    except ValueError:
        return None

def is_within_range(dt):
    return dt and START_DATE <= dt <= END_DATE

def scrape_forum():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
        context = browser.new_context()
        page = context.new_page()

        # 1) Go to login page
        page.goto(LOGIN_URL)
        print("🔐 Please log in manually with your username and password.")
        # 2) Wait for navigation away from /login (timeout after 2 minutes)
        page.wait_for_url(lambda url: not url.startswith(LOGIN_URL), timeout=120_000)
        print("✅ Detected successful login, starting scrape.")

        result = []
        for page_num in range(1, 10):
            paged_url = f"{CATEGORY_URL}?page={page_num}"
            print(f"\n📄 Scraping category page: {paged_url}")
            page.goto(paged_url)
            time.sleep(2)

            soup = BeautifulSoup(page.content(), "html.parser")
            topics = soup.select("tr.topic-list-item")
            if not topics:
                print("No more topics, stopping.")
                break

            for topic_row in topics:
                link = topic_row.select_one("a.title.raw-link")
                if not link:
                    continue
                href = link["href"]
                if not href.startswith("/t/"):
                    continue
                topic_url = BASE_URL + href

                age_td = topic_row.select_one("td.activity.num.topic-list-data.age")
                created_dt = None
                if age_td and age_td.has_attr("title"):
                    created_line = next(
                        (l for l in age_td["title"].splitlines() if l.startswith("Created:")),
                        None
                    )
                    if created_line:
                        created_dt = parse_created_at(created_line.replace("Created:", "").strip())

                if not is_within_range(created_dt):
                    continue

                print(f"→ Fetching {topic_url} (created {created_dt})")
                page.goto(topic_url)
                time.sleep(1)
                # scroll to ensure all posts load
                for _ in range(5):
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    time.sleep(1)

                topic_soup = BeautifulSoup(page.content(), "html.parser")
                posts = topic_soup.select("div.topic-post")
                print(f"   {len(posts)} posts")

                for post in posts:
                    date_tag = post.select_one("span.relative-date")
                    created_at = date_tag and date_tag.get("title")
                    if not created_at or not is_within_range(parse_created_at(created_at)):
                        continue
                    author = post.get("data-user-card", "unknown")
                    content = post.select_one(".cooked")
                    text = content.get_text("\n", strip=True) if content else ""
                    result.append({
                        "topic_url": topic_url,
                        "author": author,
                        "created_at": created_at,
                        "content": text
                    })

        browser.close()

    os.makedirs("data", exist_ok=True)
    with open("data/discourse_forum_posts.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("✅ Scraping complete – results in data/discourse_forum_posts.json")

if __name__ == "__main__":
    scrape_forum()

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import requests, json, time, os, re
from datetime import datetime
from urllib.parse import urljoin

# --- Cấu hình ---
BASE_URL = "https://thanhnien.vn/giao-duc.htm"
DOMAIN = "thanhnien.vn"
OUTPUT_DIR = "articles_json"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Selenium ---
options = Options()
driver = webdriver.Chrome(options=options)
driver.get(BASE_URL)
time.sleep(3)

# --- Auto scroll ---
last_height = driver.execute_script("return document.body.scrollHeight")
scroll_round = 0
while scroll_round < 40:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height
    scroll_round += 1
    print(f"✅ Scroll {scroll_round}")

# --- Parse toàn bộ danh sách ---
soup = BeautifulSoup(driver.page_source, "html.parser")
articles = soup.find_all("a", class_="box-category-link-title")

links = []
for a in articles:
    href = a.get("href")
    if href and href.startswith("/"):
        href = urljoin(BASE_URL, href)
    if href and DOMAIN in href:
        links.append(href)

print(f"🔹 Tổng cộng {len(links)} link hợp lệ")
driver.quit()

# --- Hàm lấy chi tiết từng bài ---
def get_article_data(url):
    try:
        res = requests.get(url, timeout=10)
        if res.status_code != 200:
            return None
        page = BeautifulSoup(res.text, "html.parser")

        title_tag = page.find("h1")
        title = title_tag.text.strip() if title_tag else ""

        desc_tag = page.find("meta", {"name": "description"})
        description = desc_tag.get("content", "").strip() if desc_tag else ""

        img_tag = page.find("meta", {"property": "og:image"})
        image_url = img_tag.get("content", "").strip() if img_tag else ""

        time_tag = page.find("time")
        date_publish = time_tag.get("datetime", "").strip() if time_tag else None

        paragraphs = [p.get_text(strip=True) for p in page.find_all("p") if len(p.get_text(strip=True)) > 30]
        maintext = "\n\n".join(paragraphs)

        filename = re.sub(r'[^a-zA-Z0-9]', '_', url) + ".json"

        data = {
            "authors": [],
            "date_download": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "date_modify": None,
            "date_publish": date_publish,
            "description": description,
            "filename": filename,
            "image_url": image_url,
            "language": "vi",
            "localpath": None,
            "maintext": maintext,
            "source_domain": DOMAIN,
            "title": title,
            "title_page": None,
            "title_rss": None,
            "url": url
        }

        with open(os.path.join(OUTPUT_DIR, filename), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        print(f"💾 Saved: {filename}")
        return data
    except Exception as e:
        print(f"❌ Error at {url}: {e}")
        return None


# --- Crawl từng bài ---
for i, link in enumerate(links, start=1):
    print(f"📄 [{i}/{len(links)}] {link}")
    get_article_data(link)
    time.sleep(1)

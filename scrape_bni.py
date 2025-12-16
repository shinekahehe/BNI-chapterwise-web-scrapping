from playwright.sync_api import sync_playwright
import json

URL = "https://bnimadurai.in/madurai-bni-maduras/en-IN/memberlist?chapterName=40692&regionIds=26740$isChapterwebsite"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto(URL, timeout=60000)

    # Wait for the table to load
    page.wait_for_selector("table.listtables tbody tr", timeout=60000)

    rows = page.query_selector_all("table.listtables tbody tr")

    members = []

    for row in rows:
        cells = row.query_selector_all("td")

        if len(cells) < 3:
            continue

        name = cells[0].inner_text().strip()
        business = cells[1].inner_text().strip()
        category = cells[2].inner_text().strip()

        members.append({
            "name": name,
            "business": business,
            "category": category
        })

    browser.close()

with open("bni_members.json", "w", encoding="utf-8") as f:
    json.dump(members, f, indent=4, ensure_ascii=False)

print(f"Saved {len(members)} members")

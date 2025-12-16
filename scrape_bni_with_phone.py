from playwright.sync_api import sync_playwright
import json
import time

URL = "https://bnimadurai.in/madurai-bni-maduras/en-IN/memberlist?chapterName=40692&regionIds=26740$isChapterwebsite"

def scrape_members():
    members = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(URL, timeout=60000)

        while True:
            page.wait_for_selector("table.listtables tbody tr", timeout=60000)
            rows = page.query_selector_all("table.listtables tbody tr")

            for i in range(len(rows)):
                page.wait_for_selector("table.listtables tbody tr")
                rows = page.query_selector_all("table.listtables tbody tr")  # Re-query each time
                row = rows[i]

                cells = row.query_selector_all("td")
                if len(cells) < 3:
                    continue

                name_link = cells[0].query_selector("a")
                name = name_link.inner_text().strip()
                business = cells[1].inner_text().strip()
                category = cells[2].inner_text().strip()

                # Click member link and scrape phone
                name_link.click()
                try:
                    page.wait_for_selector('a[href^="tel:"]', timeout=15000)
                    phone_link = page.query_selector('a[href^="tel:"]')
                    phone = phone_link.get_attribute("href").replace("tel:", "") if phone_link else None
                except:
                    phone = None

                members.append({
                    "name": name,
                    "business": business,
                    "category": category,
                    "phone": phone
                })

                page.go_back()
                time.sleep(1)  # wait for table to reload

            # Pagination: check if next button exists
            next_button = page.query_selector('a[title="Next"]')
            if next_button and "disabled" not in next_button.get_attribute("class"):
                next_button.click()
                time.sleep(2)
            else:
                break

        browser.close()

    # Save to JSON
    with open("bni_members_with_phone.json", "w", encoding="utf-8") as f:
        json.dump(members, f, indent=4, ensure_ascii=False)

    print(f"Saved {len(members)} members with phone numbers")

if __name__ == "__main__":
    scrape_members()

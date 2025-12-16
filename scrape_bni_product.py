from playwright.sync_api import sync_playwright
import json
import time

URL = "https://bnimadurai.in/madurai-bni-maduras/en-IN/memberlist?chapterName=40692&regionIds=26740$isChapterwebsite"

TARGET_SECTIONS = {
    "My Business",
    "Top Product",
    "Ideal Referral",
    "Top Problem Solved",
    "My Favourite BNI Story"
}

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
                rows = page.query_selector_all("table.listtables tbody tr")
                row = rows[i]

                cells = row.query_selector_all("td")
                if len(cells) < 3:
                    continue

                name_link = cells[0].query_selector("a")
                name = name_link.inner_text().strip()
                business = cells[1].inner_text().strip()
                category = cells[2].inner_text().strip()

                # Open member profile
                name_link.click()

                # --- PHONE ---
                try:
                    page.wait_for_selector('a[href^="tel:"]', timeout=15000)
                    phone_link = page.query_selector('a[href^="tel:"]')
                    phone = phone_link.get_attribute("href").replace("tel:", "") if phone_link else None
                except:
                    phone = None

                # --- PROFILE SECTIONS ---
                section_data = {
                    "My Business": None,
                    "Top Product": None,
                    "Ideal Referral": None,
                    "Top Problem Solved": None,
                    "My Favourite BNI Story": None
                }

                try:
                    page.wait_for_selector(".widgetProfile .rowTwoCol h3", timeout=15000)
                    headings = page.query_selector_all(".widgetProfile .rowTwoCol h3")

                    for h3 in headings:
                        title = h3.inner_text().strip()

                        if title in TARGET_SECTIONS:
                            value = h3.evaluate(
                                "el => el.nextElementSibling ? el.nextElementSibling.innerText : ''"
                            )
                            section_data[title] = value.strip()

                except:
                    pass

                members.append({
                    "name": name,
                    "business": business,
                    "category": category,
                    "phone": phone,
                    "my_business": section_data["My Business"],
                    "top_product": section_data["Top Product"],
                    "ideal_referral": section_data["Ideal Referral"],
                    "top_problem_solved": section_data["Top Problem Solved"],
                    "my_favourite_bni_story": section_data["My Favourite BNI Story"]
                })

                page.go_back()
                time.sleep(1)

            # Pagination
            next_button = page.query_selector('a[title="Next"]')
            if next_button and "disabled" not in next_button.get_attribute("class"):
                next_button.click()
                time.sleep(2)
            else:
                break

        browser.close()

    with open("bni_members_full_profile.json", "w", encoding="utf-8") as f:
        json.dump(members, f, indent=4, ensure_ascii=False)

    print(f"Saved {len(members)} members with full profiles")

if __name__ == "__main__":
    scrape_members()

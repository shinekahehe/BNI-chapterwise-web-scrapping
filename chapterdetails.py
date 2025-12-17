from playwright.sync_api import sync_playwright
import json
import time

URL = "https://bni-chennaisouth.in/en-IN/chapterdetail?chapterId=TjL4JeuSRTtYFcvz0eH4Og%3D%3D&name=Brilliance"

def scrape_bni_members():
    members = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        print("📍 Navigating to BNI chapter page...")
        page.goto(URL, timeout=60000)
        page.wait_for_load_state("networkidle")
        
        print("🖱️  Clicking 'Show Members' button...")
        page.evaluate("""
        () => {
            const el = [...document.querySelectorAll('*')]
              .find(e => e.textContent.trim() === 'Show Members');
            if (el) el.click();
        }
        """)
        
        # Wait for members table
        page.wait_for_selector("table tbody tr", timeout=30000)
        time.sleep(2)
        
        # Collect member profile links
        member_links = page.eval_on_selector_all(
            "table tbody tr td a",
            "els => els.map(e => e.href)"
        )
        
        print(f"✅ Found {len(member_links)} members\n")
        
        for idx, link in enumerate(member_links, 1):
            print(f"[{idx}/{len(member_links)}] Scraping member profile...")
            
            mp = context.new_page()
            
            try:
                mp.goto(link, timeout=60000)
                mp.wait_for_load_state("networkidle")
                time.sleep(1)
                
                # ========== BASIC INFORMATION ==========
                def safe_text(sel):
                    try:
                        return mp.locator(sel).inner_text().strip()
                    except:
                        return ""
                
                # Extract name
                name = safe_text(".widgetMemberProfileTop .memberProfileInfo h2")
                print(f"   👤 Name: {name}")
                
                # Extract category (in <h6> tag)
                category = safe_text(".widgetMemberProfileTop .memberProfileInfo h6")
                
                # Extract phone from memberContactDetails section
                phone = ""
                try:
                    phone_links = mp.query_selector_all(".memberContactDetails a[href^='tel:']")
                    if phone_links:
                        phone = phone_links[0].inner_text().strip()
                except Exception as e:
                    print(f"   ⚠️  Error extracting phone: {e}")
                
                # ========== SECTION SCRAPING (IMPROVED) ==========
                def get_section(title):
                    try:
                        # For "My Business" section - it's in widgetMemberTxtVideo
                        if title == "My Business":
                            content = mp.evaluate("""
                                () => {
                                    const section = document.querySelector('.widgetMemberTxtVideo');
                                    if (section) {
                                        const h2 = section.querySelector('h2');
                                        if (h2 && h2.textContent.includes('My Business')) {
                                            const p = section.querySelector('p');
                                            return p ? p.textContent.trim() : '';
                                        }
                                    }
                                    return '';
                                }
                            """)
                            return content if content else ""
                        
                        # For other sections in widgetProfile
                        content = mp.evaluate(f"""
                            () => {{
                                const h3s = document.querySelectorAll('.widgetProfile .rowTwoCol h3');
                                for (let h3 of h3s) {{
                                    const h3Text = h3.textContent.trim();
                                    if (h3Text.includes('{title}')) {{
                                        let next = h3.nextElementSibling;
                                        if (next) {{
                                            return next.textContent.trim();
                                        }}
                                    }}
                                }}
                                return '';
                            }}
                        """)
                        return content if content else ""
                    except Exception as e:
                        print(f"   ⚠️  Error getting section '{title}': {e}")
                        return ""
                
                my_business = get_section("My Business")
                top_product = get_section("Top Product")
                ideal_referral = get_section("Ideal Referral")
                top_problem = get_section("Top Problem Solved")
                favourite_story = get_section("My Favourite BNI Story")
                
                # ========== SAVE MEMBER DATA ==========
                member_data = {
                    "name": name,
                    "category": category,
                    "phone": phone,
                    "my_business": my_business,
                    "top_product": top_product,
                    "ideal_referral": ideal_referral,
                    "top_problem_solved": top_problem,
                    "my_favourite_bni_story": favourite_story,
                    "chapter": "BNI Chennai South"
                }
                
                members.append(member_data)
                
                # Save to JSON after each member
                output_file = "bni_chennai_south.json"
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(members, f, indent=2, ensure_ascii=False)
                
                print(f"   ✅ Successfully scraped: {name}\n")
                
            except Exception as e:
                print(f"   ❌ Error scraping member: {e}\n")
            
            finally:
                mp.close()
        
        browser.close()
    
    print(f"\n🎉 Scraping completed successfully!")
    print(f"📁 Saved {len(members)} members to {output_file}")
    
    # Print summary
    print("\n📊 Summary:")
    print(f"   Total members scraped: {len(members)}")
    print(f"   Members with my_business info: {sum(1 for m in members if m['my_business'])}")
    print(f"   Members with phone: {sum(1 for m in members if m['phone'])}")

if __name__ == "__main__":
    scrape_bni_members()
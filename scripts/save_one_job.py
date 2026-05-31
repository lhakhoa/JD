import os, re, requests, sys
from datetime import date
from pathlib import Path
from bs4 import BeautifulSoup

def slugify(text):
    text = text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text[:80]

def scrape_linkedin_job(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    # If LinkedIn blocks you, add: headers["Cookie"] = f"li_at={os.getenv('LI_AT_COOKIE')}"
    
    res = requests.get(url, headers=headers, timeout=15)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "lxml")

    title_el = soup.select_one("h1.top-card-layout__title")
    company_el = soup.select_one("a.topcard__org-name-link") or soup.select_one(".topcard__flavor")
    desc_el = soup.select_one("div.show-more-less-html__markup")

    title = title_el.get_text(strip=True) if title_el else "Unknown Role"
    company = company_el.get_text(strip=True) if company_el else "Unknown Company"
    desc = str(desc_el) if desc_el else ""

    return {"title": title, "company": company, "description": desc, "url": url}

def main():
    url = os.environ["JOB_URL"]
    job = scrape_linkedin_job(url)

    company_slug = slugify(job["company"]) or "unknown-company"
    title_slug = slugify(job["title"]) or "unknown-role"
    today = date.today().isoformat()

    folder = Path("jobs") / company_slug
    folder.mkdir(parents=True, exist_ok=True)
    fp = folder / f"{today}_{title_slug}.md"

    # Skip if we already saved this company+title today
    if fp.exists():
        print(f"Already exists: {fp}. Skipping.")
        sys.exit(0)  # exit with 0 so Actions doesn't fail

    content = f"# {job['title']}\n\n"
    content += f"**Company:** {job['company']}  \n"
    content += f"**URL:** {job['url']}  \n"
    content += f"**Saved:** {today}\n\n---\n\n"
    content += job["description"].strip() + "\n"

    fp.write_text(content, encoding="utf-8")
    print(f"Saved {fp}")

if __name__ == "__main__":
    main()

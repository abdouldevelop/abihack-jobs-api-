import json
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

BASE_URL = "https://www.novojob.com"
PAGES = [0, 1]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
}

def fetch(url: str) -> BeautifulSoup:
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")

def parse_card(card_tag) -> dict:
    title_tag = card_tag.find("a", class_="job-title")
    company_tag = card_tag.find(class_="job-company")
    url_tag = title_tag if title_tag else None
    date_tag = card_tag.find("time")
    contract_tag = card_tag.find(class_="job-contract")
    education_tag = card_tag.find(class_="job-education")
    experience_tag = card_tag.find(class_="job-experience")
    region_tag = card_tag.find(class_="job-region")
    skill_tags = card_tag.select(".job-skill")

    url = None
    if url_tag and url_tag.has_attr("href"):
        href = url_tag["href"]
        url = href if href.startswith("http") else f"{BASE_URL}{href}"

    return {
        "title": title_tag.get_text(strip=True) if title_tag else None,
        "company": company_tag.get_text(strip=True) if company_tag else None,
        "url": url,
        "date": date_tag.get_text(strip=True) if date_tag else None,
        "contract_type": contract_tag.get_text(strip=True) if contract_tag else None,
        "education_level": education_tag.get_text(strip=True) if education_tag else None,
        "experience_level": experience_tag.get_text(strip=True) if experience_tag else None,
        "region": region_tag.get_text(strip=True) if region_tag else None,
        "skills": [s.get_text(strip=True) for s in skill_tags],
    }

def main() -> int:
    offers = []
    for page in tqdm(PAGES, desc="pages"):
        url = f"{BASE_URL}/ci/offres?query=it&location=Abidjan&page={page}"
        soup = fetch(url)
        cards = soup.select(".job-card")
        for card in tqdm(cards, desc="offers", leave=False):
            offers.append(parse_card(card))
            if len(offers) >= 40:
                break
        if len(offers) >= 40:
            break
    Path("offers.json").write_text(
        json.dumps(offers, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return len(offers)

if __name__ == "__main__":
    count = main()
    print(f"Saved {count} offers to offers.json")

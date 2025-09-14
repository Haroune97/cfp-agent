# agent_cfp.py
import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime

KEYWORDS = [
    "international economics", "global logistics", "supply chain", 
    "trade policy", "international trade", "logistics management",
    "global supply chains", "transportation economics", "port logistics",
    "cross-border logistics", "world economy"
]

CSV_FILE = "cfp_found.csv"
SEEN_CFP = set()

# Charger les CFP déjà vus
try:
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            SEEN_CFP.add(row[0])
except FileNotFoundError:
    pass

def scrape_wikicfp():
    url = "https://web.archive.org/web/20240101000000*/http://www.wikicfp.com/cfp/servlet/event.showcfp?eventid=90000"
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        cfp_list = []
        for row in soup.select('table tr'):
            cells = row.find_all('td')
            if len(cells) >= 5:
                title = cells[0].get_text(strip=True)
                date = cells[1].get_text(strip=True)
                location = cells[2].get_text(strip=True)
                link_tag = cells[0].find('a')
                if link_tag and link_tag.get('href'):
                    url = "https://wikicfp.com" + link_tag['href']
                    if any(kw.lower() in title.lower() for kw in KEYWORDS):
                        if url not in SEEN_CFP:
                            cfp_list.append({
                                'title': title,
                                'date': date,
                                'location': location,
                                'url': url
                            })
                            SEEN_CFP.add(url)
        return cfp_list
    except Exception as e:
        print(f"⚠️ WikiCFP error: {e}")
        return []

def scrape_conferenceradar():
    url = "https://www.conferenceradar.com/search?q=international+economics+OR+logistics"
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        cfp_list = []
        for item in soup.select('.event-item'):
            title = item.select_one('.title').get_text(strip=True) if item.select_one('.title') else ""
            date = item.select_one('.date').get_text(strip=True) if item.select_one('.date') else ""
            link = item.select_one('a')['href'] if item.select_one('a') else ""
            if any(kw.lower() in title.lower() for kw in KEYWORDS) and link:
                if link not in SEEN_CFP:
                    cfp_list.append({
                        'title': title,
                        'date': date,
                        'location': "",
                        'url': link
                    })
                    SEEN_CFP.add(link)
        return cfp_list
    except Exception as e:
        print(f"⚠️ ConferenceRadar error: {e}")
        return []

def save_to_csv(cfp_list):
    with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for cfp in cfp_list:
            writer.writerow([cfp['url'], cfp['title'], cfp['date'], cfp['location'], datetime.now().strftime("%Y-%m-%d")])

# ==== MAIN ====
print("🔍 Lancement du scraper...")
all_cfp = scrape_wikicfp() + scrape_conferenceradar()
if all_cfp:
    save_to_csv(all_cfp)
    print(f"✅ {len(all_cfp)} nouveaux CFP ajoutés au fichier CSV.")
else:
    print("❌ Aucun nouveau CFP trouvé.")
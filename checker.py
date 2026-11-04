import os
import requests
from bs4 import BeautifulSoup

NTFY_TOPIC = "NuNoticebd24"
TARGET_URL = "https://www.nu.ac.bd/recent-news-notice.php"

def check_notice():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(TARGET_URL, headers=headers, timeout=25)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        notice_link_tag = None
        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.get_text(strip=True)
            if ('notice' in href.lower() or 'upload' in href.lower() or '.pdf' in href.lower()) and len(text) > 5:
                notice_link_tag = a
                break

        if not notice_link_tag:
            table = soup.find('table')
            if table:
                rows = table.find_all('tr')
                for row in rows:
                    a = row.find('a')
                    if a and len(a.get_text(strip=True)) > 5:
                        notice_link_tag = a
                        break

        if not notice_link_tag:
            print("Notice element not found.")
            return

        title = notice_link_tag.get_text(strip=True)
        link = notice_link_tag['href']
        if not link.startswith('http'):
            link = "https://www.nu.ac.bd/" + link.lstrip('/')

        last_title = ""
        if os.path.exists("last_notice.txt"):
            with open("last_notice.txt", "r", encoding="utf-8") as f:
                last_title = f.read().strip()

        if title and title != last_title:
            requests.post(
                f"https://ntfy.sh/{NTFY_TOPIC}",
                data=title.encode('utf-8'),
                headers={
                    "Title": "National University Notice",
                    "Click": link,
                    "Priority": "high",
                    "Tags": "loudspeaker,scroll"
                }
            )
            with open("last_notice.txt", "w", encoding="utf-8") as f:
                f.write(title)
            print("Alert sent successfully!")
        else:
            print("No new notice.")

    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    check_notice()

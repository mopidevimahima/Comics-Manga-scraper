import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

print("🦸‍♂️ Comics New Releases FINAL - Amazon.in")
url = "https://www.amazon.in/gp/new-releases/books/1318104031/ref=zg_bs_tab_t_books_bsnr"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"}

os.makedirs("comics_thumbs", exist_ok=True)
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

items = soup.find_all('div', {'id': 'gridItemRoot'})
print(f"Found {len(items)} items!")

comics = []
for i, item in enumerate(items[:25]):
    try:
        # Title from image alt or spans
        title = "N/A"
        img_elem = item.find('img')
        if img_elem:
            title = img_elem.get('alt', title).strip()
        span_title = item.find('span', class_='a-size-base-plus') or item.find('h5')
        if span_title:
            title = span_title.text.strip()

        author = "N/A"
        author_elem = item.find('span', class_='contributorNameID') or item.find('a', class_='a-link-normal')
        if author_elem:
            author = author_elem.text.strip()

        price_elem = item.find('span', class_='a-price-whole') or item.find(string=lambda x: x and '₹' in x)
        price = price_elem.strip() if price_elem else "N/A"

        kindle_flag = "🔥 KINDLE" if price != "N/A" and len(price.replace('₹', '').replace(',', '')) < 4 else ""

        img_path = f"comics_thumbs/comic_{i + 1}.jpg"
        try:
            if img_elem:
                img_resp = requests.get(img_elem['src'], headers=headers)
                from PIL import Image
                from io import BytesIO

                Image.open(BytesIO(img_resp.content)).save(img_path)
        except:
            pass

        rating_elem = item.find('span', class_='a-icon-alt')
        rating = rating_elem.text.strip() if rating_elem else "N/A"

        comics.append({
            "Rank": i + 1,
            "Title": title,
            "Author": author,
            "Price": price,
            "Rating": rating,
            "Kindle": kindle_flag,
            "Image": img_path
        })
        print(f"{i + 1:2d}. {title[:65]} | {price} | {author[:20]} {kindle_flag}")
        time.sleep(1)
    except Exception as e:
        print(f"Error {i + 1}: {str(e)[:40]}")

df = pd.DataFrame(comics)
df.to_excel("comics_final.xlsx", index=False)

# Fixed HTML (no f-string quote issues)
html_template = '''
<html><body style="background:#000;color:#fff;font-family:Arial">
<h1 style="color:lime">🦸 Comics New Releases Gallery</h1>
<style>div{{display:inline-block;margin:20px;background:#111;padding:20px;border-radius:20px;width:220px}}img{{max-width:200px;border-radius:15px;border:2px #0f0 solid}}</style>
{}
</body></html>
'''
gallery_items = ""
for c in comics:
    gallery_items += f'<div><img src="{c["Image"]}" style="width:200px"><h3>{c["Title"][:50]}</h3><p>{c["Author"][:30]}<br><b style="color:lime">{c["Price"]}</b> {c["Kindle"]}</p></div>'

html = html_template.format(gallery_items)
with open("comics_gallery.html", "w", encoding="utf-8") as f:
    f.write(html)


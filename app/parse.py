import requests
from bs4 import BeautifulSoup

url = "https://kolejemalopolskie.com.pl/pl/utrudnienia?trains_category=1&bus_category=0&current_day=&this_week=&current_plan=undefined&future_plane=undefined"

params = {
    "trains_category": 1,
    "bus_category": 0,
    "current_day": "",
    "this_week": "",
    "current_plan": "undefined",
    "future_plane": "undefined"
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/140 Safari/537.36",
    "Referer": "https://kolejemalopolskie.com.pl/",
}

# створюємо сесію
s = requests.Session()
s.headers.update(headers)

# крок 1: отримати cookies
s.get("https://kolejemalopolskie.com.pl/")

# крок 2: реальний запит на utrudnienia
resp = s.get(url, params=params)
print("Status:", resp.status_code, "Length:", len(resp.text))

with open("debug.html", "w", encoding="utf-8") as f:
    f.write(resp.text)

# крок 3: парсимо HTML
soup = BeautifulSoup(resp.text, "html.parser")

# приклад: шукаємо блоки з труднощами
items = soup.select("p .tag .obstruction .title .problem_desc")
result = []
for item in items:
    title = item.get_text(strip=True)
    result.append(title)

print(result)
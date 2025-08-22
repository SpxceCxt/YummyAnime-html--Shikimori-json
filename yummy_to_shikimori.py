# -*- coding: cp1251 -*-
from html.parser import HTMLParser
import requests
import json

# === Пути к файлам ===
html_path = "html.html"
json_out_shikimori = "all_animes_shikimori.json"

# === Парсинг из HTML и перевод в JSON ===
print("Читаю HTML и формирую JSON...\n")
def parse_animes_from_html(html_content):
    animes = []

    class LocalParser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.in_li = False
            self.current_li = ""

        def handle_starttag(self, tag, attrs):
            if tag == "li":
                self.in_li = True
                self.current_li = ""

        def handle_endtag(self, tag):
            if tag == "li" and self.in_li:
                self.in_li = False
                title_ru = self.current_li.strip()
                if title_ru:
                    animes.append({
                        "target_title": None,
                        "target_title_ru": title_ru,
                        "target_id": None,
                        "target_type": "Anime",
                        "score": 0,
                        "status": "planned",
                        "rewatches": 0,
                        "episodes": 0,
                        "text": None
                    })

        def handle_data(self, data):
            if self.in_li:
                self.current_li += data

    parser = LocalParser()
    parser.feed(html_content)
    return animes

with open(html_path, "r", encoding="utf-8") as f:
    html_content = f.read()

all_animes = parse_animes_from_html(html_content)

# === Поиск в Shikimori ===
print("Начинаю поиск на Shikimori...\n")
def search_shikimori(anime_ru_name):
    url = "https://shikimori.one/api/animes"
    params = {"search": anime_ru_name}
    headers = {"User-Agent": "AnimeListBot/1.0"}
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data:
                best_match = data[0]
                return {
                    "id": best_match.get("id"),
                    "title": best_match.get("name"),
                    "russian": best_match.get("russian")
                }
    except Exception as e:
        print(f"Ошибка при запросе {anime_ru_name}: {e}")
    return None

updated_animes = []
for anime in all_animes:
    ru_name = anime["target_title_ru"]
    print(f"Ищу: {ru_name}")
    result = search_shikimori(ru_name)
    if result:
        anime["target_id"] = result["id"]
        anime["target_title"] = result["title"]
        anime["target_title_ru"] = result["russian"] or ru_name
    updated_animes.append(anime)

# === Сохранение финального результата ===
with open(json_out_shikimori, "w", encoding="utf-8") as f:
    json.dump(updated_animes, f, ensure_ascii=False, indent=4)

print(f"\nФайл готов: {json_out_shikimori}\n")
# -*- coding: cp1251 -*-
from bs4 import BeautifulSoup
import requests
import json

# === Пути к файлам ===
html_path = "html.html"
json_out_shikimori = "all_animes_shikimori.json"

# === Парсинг из HTML и перевод в JSON ===
print("Читаю HTML и формирую JSON...\n")
with open(html_path, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

all_animes = []
for sec in soup.find_all("h3"):
    ul = sec.find_next("ul")
    if not ul:
        continue
    for li in ul.find_all("li"):
        title_ru = li.get_text(strip=True)
        all_animes.append({
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
    return None

updated_animes = []
for anime in all_animes:
    ru_name = anime["target_title_ru"]
    print(f"Ищу: {ru_name}")

    try:
        result = search_shikimori(ru_name)
        if result:
            anime["target_id"] = result["id"]
            anime["target_title"] = result["title"]
            anime["target_title_ru"] = result["russian"] or ru_name
    except Exception as e:
        print(f"Ошибка при обработке '{ru_name}': {e}")

    updated_animes.append(anime)

# === Сохранение финального результата ===
with open(json_out_shikimori, "w", encoding="utf-8") as f:
    json.dump(updated_animes, f, ensure_ascii=False, indent=4)

print(f"\nФайл готов: {json_out_shikimori}\n")
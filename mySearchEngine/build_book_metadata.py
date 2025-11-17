import os
import json
import requests

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LIB_DIR = os.path.join(BASE_DIR, "library")

INDEX_PATH = os.path.join(LIB_DIR, "index.json")
BOOKS_PATH = os.path.join(LIB_DIR, "books.json")


def get_metadata(book_id):
    url = f"https://gutendex.com/books/{book_id}"
    r = requests.get(url)

    if r.status_code != 200:
        print(f"Impossible de récupérer metadata pour {book_id}")
        return None

    data = r.json()

    title = data.get("title", "Unknown title")

    authors = [a["name"] for a in data.get("authors", [])]

    languages = data.get("languages", [])

    formats = data.get("formats", {})

    text_url = (
        formats.get("text/plain; charset=utf-8")
        or formats.get("text/plain; charset=us-ascii")
        or formats.get("text/plain")
    )

    cover_url = formats.get("image/jpeg")

    download_count = data.get("download_count", None)

    return {
        "title": title,
        "authors": authors,
        "languages": languages,
        "text_url": text_url,
        "cover_url": cover_url,
        "download_count": download_count,
    }

def main():
    # Charger l’index pour récupérer tous les doc_id utilisés
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        index = json.load(f)

    all_docs = set()
    for docs in index.values():
        for doc_id in docs.keys():
            all_docs.add(doc_id)

    print(f"Total de documents dans l'index : {len(all_docs)}")

    books = {}

    for doc_id in sorted(all_docs, key=lambda x: int(x)):
        print(f"Récupération metadata pour livre {doc_id}...")
        meta = get_metadata(doc_id)
        if meta:
            books[doc_id] = meta

    with open(BOOKS_PATH, "w", encoding="utf-8") as f:
        json.dump(books, f, indent=2, ensure_ascii=False)

    print(f"Metadata sauvegardées dans {BOOKS_PATH}")


if __name__ == "__main__":
    main()
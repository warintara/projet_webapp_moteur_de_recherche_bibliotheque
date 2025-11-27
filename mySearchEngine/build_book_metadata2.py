import os
import json
import time
import re
import requests
from bs4 import BeautifulSoup

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LIB_DIR = os.path.join(BASE_DIR, "library")
VOCAB_PATH = os.path.join(LIB_DIR, "vocab.json")
METADATA_PATH = os.path.join(LIB_DIR, "metadata.json")

GUTENBERG_PAGE = "https://www.gutenberg.org/ebooks/{doc_id}"
COVER_URL = "https://www.gutenberg.org/cache/epub/{doc_id}/pg{doc_id}.cover.medium.jpg"


def safe_get(url, retries=5, timeout=15):
    """
    GET robuste avec retries.
    """
    for attempt in range(retries):
        try:
            r = requests.get(url, timeout=timeout)
            return r
        except requests.exceptions.RequestException:
            print(f"  Tentative {attempt+1}/{retries} échouée, retry...")
            time.sleep(1 + attempt)
    return None


def parse_metadata_from_html(doc_id: str, html: str):
    """
    Extrait :
      - titre
      - auteur
      - année
      - downloads
      - cover_url
    depuis la page HTML Gutenberg.
    """

    soup = BeautifulSoup(html, "html.parser")

    # ============== Titre ==============
    # <td itemprop="headline">The 1994 CIA World Factbook</td>
    title_elem = soup.find("td", itemprop="headline")
    if title_elem:
        title = title_elem.get_text(strip=True)
    else:
        # fallback
        title = f"Document #{doc_id}"

    # ============== Auteur ==============
    # <th>Author</th> <td> <a>NAME</a> </td>
    author = "Unknown author"
    tr_author = soup.find("th", string="Author")
    if tr_author:
        td = tr_author.find_next("td")
        if td:
            author = td.get_text(strip=True)

    # ============== Année (Release Date) ==============
    # <th>Release Date</th> <td>1 nov. 1994</td>
    year = None
    tr_rel = soup.find("th", string="Release Date")
    if tr_rel:
        td = tr_rel.find_next("td")
        if td:
            match = re.search(r"(\d{4})", td.get_text())
            if match:
                year = int(match.group(1))

    # ============== Downloads ==============
    # <th>Downloads</th> <td>1392 downloads in the last 30 days.</td>
    downloads = None
    tr_dl = soup.find("th", string="Downloads")
    if tr_dl:
        td = tr_dl.find_next("td")
        if td:
            m = re.search(r"([\d,]+)", td.get_text())
            if m:
                downloads = int(m.group(1).replace(",", ""))

    # ============== Cover URL ==============
    cover_url = COVER_URL.format(doc_id=doc_id)

    return {
        "title": title,
        "author": author,
        "year": year,
        "downloads": downloads,
        "cover_url": cover_url,
        "gutenberg_page": GUTENBERG_PAGE.format(doc_id=doc_id),
    }


def build_metadata_scrape():
    # Charger vocab.json
    if not os.path.exists(VOCAB_PATH):
        raise FileNotFoundError(f"vocab.json introuvable : {VOCAB_PATH}")

    with open(VOCAB_PATH, "r", encoding="utf-8") as f:
        vocab = json.load(f)

    all_doc_ids = sorted(vocab.keys(), key=lambda x: int(x))
    print(f"Nombre total de documents indexés : {len(all_doc_ids)}")

    # Charger metadata existantes (si script relancé)
    metadata = {}
    if os.path.exists(METADATA_PATH):
        with open(METADATA_PATH, "r", encoding="utf-8") as f:
            try:
                metadata = json.load(f)
                print(f"Métadonnées déjà récupérées : {len(metadata)}")
            except json.JSONDecodeError:
                metadata = {}

    processed = 0

    for doc_id in all_doc_ids:
        # Skip déjà récupérés
        if doc_id in metadata:
            continue

        url = GUTENBERG_PAGE.format(doc_id=doc_id)
        print(f"Doc {doc_id}: récupération {url} ...")
        r = safe_get(url)

        if r is None or r.status_code != 200:
            print(f"  -> Erreur réseau ou HTTP {getattr(r, 'status_code', '??')}")
            continue

        meta = parse_metadata_from_html(doc_id, r.text)
        metadata[doc_id] = meta
        processed += 1

        print(f"  OK - {meta['title']} | {meta['author']} | {meta['year']} | DL={meta['downloads']}")

        # Sauvegarde avancée tous les 20 livres
        if processed % 20 == 0:
            print("  Sauvegarde intermédiaire...")
            with open(METADATA_PATH, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2)

        # pause pour ne pas se faire bloquer (mode A)
        time.sleep(0.5)

    # Sauvegarde finale
    print("\nSauvegarde finale...")
    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"\nTerminé : {len(metadata)} documents ont des métadonnées.")


if __name__ == "__main__":
    try:
        build_metadata_scrape()
    except KeyboardInterrupt:
        print("\nInterrompu (Ctrl+C). Les données déjà récupérées sont sauvegardées.")

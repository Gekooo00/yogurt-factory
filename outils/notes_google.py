"""
Met à jour la note Google, le nombre d'avis et le lien Google Maps de chaque boutique
(champs note_google, nombre_avis, lien_google de contenu/boutiques/*.json).

Source : API officielle Google Places (la copie manuelle ou automatique depuis Google Maps
est interdite par les conditions de Google). Il faut une clé d'API :
    1. https://console.cloud.google.com : créer un projet, activer « Places API (New) »,
       créer une clé d'API (restreinte à Places API). Le quota gratuit mensuel suffit largement.
    2. Lancer :
         Windows (PowerShell) : $env:GOOGLE_PLACES_API_KEY="la-cle"; python outils/notes_google.py
         macOS / Linux        : GOOGLE_PLACES_API_KEY=la-cle python outils/notes_google.py
       Option --essai : affiche ce qui serait modifié sans rien écrire.
    3. Relancer python build.py (ou pousser sur GitHub).

Sur GitHub, le workflow « Notes Google » le fait automatiquement chaque mois si la clé est
enregistrée dans Settings > Secrets and variables > Actions sous le nom GOOGLE_PLACES_API_KEY.

La boutique est cherchée par « Yogurt Factory + centre + adresse + ville », autour de ses
coordonnées GPS. Un résultat dont le nom ne contient pas « Yogurt Factory » est ignoré :
aucune note d'un autre établissement ne peut être attribuée par erreur.
"""
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STORES = ROOT / "contenu" / "boutiques"
API = "https://places.googleapis.com/v1/places:searchText"
FIELDS = "places.displayName,places.rating,places.userRatingCount,places.googleMapsUri,places.formattedAddress"


def search(key, store):
    body = {"textQuery": " ".join(filter(None, ["Yogurt Factory", store.get("centre"), store["adresse"], store["ville"]])),
            "languageCode": "fr", "maxResultCount": 3}
    if "lat" in store:
        body["locationBias"] = {"circle": {"center": {"latitude": store["lat"], "longitude": store["lng"]}, "radius": 1500.0}}
    req = urllib.request.Request(API, data=json.dumps(body).encode(), method="POST", headers={
        "Content-Type": "application/json", "X-Goog-Api-Key": key, "X-Goog-FieldMask": FIELDS})
    with urllib.request.urlopen(req, timeout=20) as r:
        places = json.load(r).get("places", [])
    for p in places:
        name = p.get("displayName", {}).get("text", "").lower().replace(" ", "")
        if "yogurtfactory" in name or "yogourtfactory" in name:
            return p
    return None


def main():
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8", errors="replace")
    key = os.environ.get("GOOGLE_PLACES_API_KEY", "").strip()
    if not key:
        sys.exit("Clé manquante : définissez la variable d'environnement GOOGLE_PLACES_API_KEY (voir en tête de ce fichier).")
    dry = "--essai" in sys.argv
    changed = missing = 0
    for path in sorted(STORES.glob("*.json")):
        if path.name.startswith("_"):
            continue
        store = json.loads(path.read_text(encoding="utf-8"))
        try:
            place = search(key, store)
        except urllib.error.HTTPError as e:
            sys.exit(f"Erreur de l'API Google ({e.code}) : {e.read().decode(errors='replace')[:300]}")
        if not place or "rating" not in place:
            missing += 1
            print(f"  ? {path.stem} : pas de fiche Google trouvée")
            continue
        new = {"note_google": round(float(place["rating"]), 1), "nombre_avis": int(place.get("userRatingCount", 0)),
               "lien_google": place.get("googleMapsUri", store.get("lien_google", ""))}
        if all(store.get(k) == v for k, v in new.items()):
            continue
        print(f"  ✓ {path.stem} : {new['note_google']} ★ ({new['nombre_avis']} avis)")
        store.update({k: v for k, v in new.items() if v})
        changed += 1
        if not dry:
            path.write_text(json.dumps(store, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\n{changed} boutique(s) mise(s) à jour, {missing} sans fiche trouvée." + (" (essai : rien n'a été écrit)" if dry else ""))


if __name__ == "__main__":
    main()

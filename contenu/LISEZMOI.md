# Contenu du site : ce qu'on modifie le plus souvent

Tout ce dossier est lu par `python build.py`. Vous modifiez un fichier, vous relancez le build (ou vous poussez sur GitHub : le site se reconstruit tout seul), et le site est à jour **en français et en anglais**.

Le format est du JSON. Les règles à respecter :

- des guillemets droits `"` autour des textes ;
- une virgule entre deux lignes, mais jamais après la dernière ;
- les nombres (points, coordonnées GPS, notes) s'écrivent sans guillemets.

En cas d'erreur, le build s'arrête et indique **le fichier, la ligne et la cause** : rien de cassé n'est mis en ligne.

Un texte traduit s'écrit `{ "fr": "Fraise", "en": "Strawberry" }`. Un texte identique dans les deux langues s'écrit simplement `"Kit Kat"`.

---

## Ajouter une boutique — `boutiques/`

1. Copiez `boutiques/_modele.json`. Renommez la copie en minuscules, sans accent ni espace, par exemple `lyon-part-dieu.json`.
2. Remplissez les champs.
   - **Obligatoires :** `nom`, `adresse`, `ville`, `region`, `pays`, `horaires`.
   - **Facultatifs :** `centre`, `code_postal`, `telephone`, `lat`, `lng`, `note_google`, `nombre_avis`, `lien_google`, `photo`, `fuseau_horaire`, `uber_eats`, `deliveroo`, `takeaway`. Un champ inutile peut être supprimé.
   - **Livraison :** collez l'adresse de la page de la boutique sur Uber Eats, Deliveroo ou Takeaway (Belgique). La fiche affiche alors ses boutons de commande et la boutique apparaît avec le filtre « 🛵 Livraison ».
   - **Notes Google :** inutile de les saisir à la main, voir « Notes Google automatiques » plus bas.
3. **Photo :** déposez-la dans `images/boutiques/` avec le **même nom** que le fichier JSON, par exemple `images/boutiques/lyon-part-dieu.jpg`.
   - Formats acceptés : JPG, PNG ou WebP.
   - Le build la convertit et la redimensionne automatiquement.
   - Sans photo, une photo générique est affichée.
4. **Coordonnées GPS :** dans Google Maps, faites un clic droit sur la boutique et cliquez sur les chiffres pour les copier. Le premier nombre va dans `lat`, le second dans `lng`.

**Horaires :** respectez ce format pour que le site affiche « Ouvert / Fermé » :

- `"Tous les jours 10h–20h"`
- `"Lun–sam 10h–20h · dim 11h–19h"`
- `"Lun–jeu 11h–19h · ven–dim 11h–minuit"`

Utilisez le tiret long `–` et le point médian `·`, comme dans les exemples. `"Horaires du centre"` est aussi accepté.

**Fermer une boutique :** supprimez son fichier (et sa photo).

**Masquer une boutique temporairement :** renommez son fichier pour qu'il commence par `_`, par exemple `_lyon-part-dieu.json`.

Tout est recalculé automatiquement : compteurs (« 88 adresses dans 79 villes »), carte interactive, filtres, données Google et liste pour les IA.

## Actualités — `actualites/`

Une actualité = un fichier nommé `AAAA-MM-JJ-titre-court.json` (la date du nom est la date affichée). Copiez `actualites/_modele.json`.

- `titre` et `resume` sont obligatoires ; `texte` (paragraphes supplémentaires), `image` (ou `emoji`) et `lien` sont facultatifs.
- Les 3 plus récentes s'affichent sur l'accueil, toutes sur la page Actus.
- Un fichier qui commence par `_` est un brouillon : il n'est pas publié.

## Notes Google automatiques

`outils/notes_google.py` récupère la note, le nombre d'avis et le lien Google Maps de chaque boutique grâce à l'API officielle Google Places (la copie depuis Google Maps est interdite). Il faut une clé d'API gratuite : la marche à suivre est en tête du fichier.

Sur GitHub, enregistrez la clé dans *Settings › Secrets and variables › Actions* sous le nom `GOOGLE_PLACES_API_KEY` : les notes sont alors mises à jour **automatiquement chaque mois**, et le site republié.

## Un nouveau pays — `pays.json`

Ajoutez une ligne avec :

- le nom du pays en français ;
- `en` : son nom en anglais ;
- `fuseau_horaire` : son fuseau, par exemple `"Europe/Rome"`, `"Africa/Casablanca"` ou `"Asia/Dubai"`.

L'ordre des lignes est l'ordre des pastilles sur la page Boutiques.

Pour « Outre-mer », le fuseau se met dans la fiche de chaque boutique (`"fuseau_horaire": "Indian/Reunion"`, `"America/Martinique"`…).

## La carte — `carte/`

Chaque rubrique de la page « La carte » est un fichier `<numéro>-<ancre>.json`. Le numéro donne l'ordre d'affichage ; l'ancre donne l'adresse de la rubrique (`carte.html#boissons`).

| Je veux… | Où |
|---|---|
| Ajouter / retirer un topping ou un coulis | `2-toppings.json`, dans la liste `elements` concernée |
| Signaler un topping de saison ou contenant du porc | ajouter `"saison": true` ou `"porc": true` sur l'élément |
| Changer un sirop, une perle de bubble tea, un granité… | `listes.json` : la modification s'applique partout où la liste est utilisée |
| Ajouter un produit (boisson, gaufre…) | copier un bloc de la liste `produits` du fichier concerné |
| Mettre une étiquette « Nouveau » | `"badge": { "fr": "Nouveau", "en": "New" }` (ajouter `"badge_couleur": "bleu"` pour la version bleue) |
| Ajouter une rubrique | créer `6-ma-rubrique.json` sur le modèle de `5-cafes.json` |

**Produits :**

- **Avec photo :** mettez le chemin dans `"image"`, par exemple `"images/menu/ma-photo.webp"`. Les dimensions sont lues automatiquement.
- **Sans photo :** mettez `"emoji"` et `"fond"` (deux couleurs `#rrggbb`).
- **Utiliser une liste partagée :** écrivez `{{liste:nom-de-la-liste}}` dans un texte, ou `{{Liste:…}}` pour une majuscule au début.

Les chiffres « 34 toppings et 11 coulis » affichés sur tout le site sont **comptés automatiquement**.

## Programme de fidélité — `fidelite.json`

Une ligne par récompense, **du plus petit au plus grand nombre de points**. Le simulateur de la page Fidélité s'adapte tout seul.

## Réglages — `reglages.json`

- **`formulaires`** : adresse e-mail de réception de chaque formulaire (contact, franchise, recrutement).
  - Si `endpoint` est vide, le formulaire ouvre la messagerie du visiteur avec un message pré-rempli.
  - Avec l'adresse `https://…` d'un service d'envoi (Formspree, Basin…), le message est envoyé directement. Cette adresse est ajoutée automatiquement à la politique de sécurité du site.
- **`proteger_le_texte`** : `true` empêche la sélection et la copie du texte ; `false` les autorise.
- **`boutiques_par_page`** : nombre de fiches affichées avant le bouton « Afficher plus ».

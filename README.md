# Site Yogurt Factory

Site statique (HTML/CSS/JS), sans CMS ni base de données : rapide, sûr, et hébergeable partout
(OVH, o2switch, Ionos, Netlify, Cloudflare Pages…). Aucun cookie publicitaire, aucun service Google :
polices et librairie de carte sont hébergées sur le site.

## En bref

```bash
python build.py
```

génère le dossier **`dist/`** : c'est **le seul dossier à mettre en ligne** (contenu de `dist/` à la racine
de l'hébergement). Prérequis : Python 3 et Pillow (`pip install pillow`).

Aperçu local :

```bash
python -m http.server 8765 --directory dist
```

puis ouvrir http://localhost:8765

## Organisation

| Dossier / fichier | Rôle |
|---|---|
| `_src/pages/` | Contenu des pages (une page = un fichier) |
| `_src/partials/` | Bandeau, menu, pied de page, menu accessibilité (communs à toutes les pages) |
| `_src/static/` | `.htaccess` (Apache), `_headers` / `_redirects` (Netlify), `robots.txt` |
| `assets/css/style.css` | Styles (couleurs et polices en haut du fichier) |
| `assets/js/main.js` | Fonctionnalités ; **configuration en haut du fichier** (`YF_CONFIG`) |
| `assets/js/stores.js` | **Liste des boutiques** (modifiable sans connaissance technique) |
| `images/` | Photos ; `images/menu/` produits ; `images/boutiques/` photos des boutiques ; `images/src/` originaux (non publiés) |
| `dist/` | Site généré, prêt à publier (ne pas modifier à la main) |

## Pages

Accueil · Le concept · La carte (onglets, recherche de toppings) · Fidélité (simulateur de points) ·
Boutiques (carte interactive, « Autour de moi », « Ouvert maintenant », favori « Ma Facto ») · Franchise ·
Recrutement · Contact & FAQ · Mentions légales · Confidentialité · Cookies · Conditions d'utilisation ·
Accessibilité · 404.

La carte **n'affiche aucun prix** : chaque boutique fixe les siens (les franchisés sont libres de leurs prix).

## Tâches courantes

- **Ajouter / modifier une boutique** : `assets/js/stores.js`, puis `python build.py`.
  - `hours` au format `"Lun–sam 10h–20h · dim 11h–19h"` ou `"Tous les jours 10h–20h"` (sinon « Horaires variables »).
  - `lat` / `lng` : clic droit sur le lieu dans Google Maps → cliquer sur les coordonnées pour les copier.
  - **Photo** : déposer l'image dans `images/boutiques/` (format paysage, 800 px de large, `.webp` ou `.jpg`)
    et ajouter `photo: "images/boutiques/nom.webp"`. Sans photo, une photo générique s'affiche.
  - **Note Google** : ajouter `rating: 4.6, reviews: 1234` et `googleUrl: "lien de la fiche Google Maps"`.
    Sans note, un bouton « Voir les avis Google » s'affiche.
- **Modifier un texte** : fichier correspondant dans `_src/pages/`, puis `python build.py`.
- **Protection du texte** (anti-sélection / anti-copie) : `protectContent` dans `YF_CONFIG` (`true` / `false`).
  Les champs de formulaire restent utilisables. Cette protection décourage la copie, sans pouvoir l'empêcher totalement.

## À faire avant la mise en ligne

1. **E-mails des formulaires** (`YF_CONFIG.forms` dans `assets/js/main.js`) : adresses provisoires à remplacer.
   Pour recevoir les demandes directement (sans ouvrir la messagerie du visiteur), créer un formulaire
   Formspree et coller son URL dans `endpoint`, **puis** ajouter `https://formspree.io` à `connect-src`
   dans la Content-Security-Policy (`_src/static/.htaccess` et `_headers`).
2. **Pages légales** : compléter les passages surlignés en jaune (raison sociale, SIREN, hébergeur,
   médiateur de la consommation, contact RGPD, validité des points fidélité…) et faire relire par un juriste.
3. **« Le plus gros bar à toppings de France »** : c'est une allégation comparative ; gardez de quoi la justifier
   (comparatif du nombre de toppings) en cas de contestation.
4. **Boutiques** : 88 adresses (voir « Boutiques à confirmer » plus bas) ; ajouter les nouvelles,
   retirer les fermées, ajouter photos et notes.
5. **Photos** manquantes : granités, matcha, ube (emoji pour l'instant).
6. **Carte OpenStreetMap** : les tuiles gratuites d'OpenStreetMap conviennent pour un trafic modéré.
   Si le site reçoit beaucoup de visites, passer à un fournisseur (MapTiler, Stadia Maps…) : changer l'URL des tuiles
   dans `main.js` (`tileLayer`) et le domaine dans la CSP.
7. **Accessibilité** : faire réaliser un audit RGAA pour afficher un taux de conformité.
8. Après la mise en ligne : déclarer `https://yogurtfactory.fr/sitemap.xml` dans Google Search Console
   et vérifier les redirections des anciennes pages.

## Déjà en place pour la production

- HTTPS forcé, domaine sans `www`, redirections 301 des anciennes URL WordPress.
- En-têtes de sécurité (CSP stricte sans script externe, HSTS, anti-iframe, Permissions-Policy).
- Compression et cache long des CSS/JS/polices, avec numéro de version automatique à chaque build.
- CSS minifié, images WebP en chargement différé, polices préchargées.
- SEO : titres et descriptions uniques, canonical, Open Graph + image de partage 1200×630, sitemap,
  données structurées (organisation + 84 boutiques), liste des boutiques lisible sans JavaScript.
- Favicon, icônes mobiles et manifest.
- Formulaires : anti-spam invisible, brouillon conservé si la page est fermée par erreur.
- Accessibilité : navigation clavier, lien d'évitement, menu d'adaptation (texte, contraste, dyslexie…).

## Référencement : moteurs de recherche et agents IA

Généré automatiquement à chaque build :

| Fichier / balise | Pour qui |
|---|---|
| `sitemap.xml` (avec images et priorités) | Google, Bing, Yandex, Apple, Qwant… |
| `robots.txt` | Autorise explicitement moteurs **et** agents IA (GPTBot, ClaudeBot, PerplexityBot, Google-Extended…) |
| `llms.txt` | Résumé de la marque pour les assistants IA (ChatGPT, Claude, Perplexity, Gemini) |
| `llms-full.txt` | Tout le contenu du site + les 84 boutiques en texte brut, pour les agents IA |
| Données structurées JSON-LD | Organization + WebSite (accueil), Menu (carte), 84 × IceCreamShop (boutiques), FAQPage (contact, fidélité, franchise), fil d'Ariane (toutes les pages) |
| Open Graph / Twitter Card | Aperçus sur WhatsApp, Facebook, LinkedIn, X, iMessage… |
| IndexNow (`python build.py --indexnow`) | Indexation instantanée sur Bing, Yandex, Seznam, Naver (et donc DuckDuckGo, Qwant, Ecosia, Yahoo) |

**Après la mise en ligne :**
1. Créer les comptes **Google Search Console** et **Bing Webmaster Tools**, coller leurs codes de validation
   dans `build.py` (`GOOGLE_SITE_VERIFICATION`, `BING_SITE_VERIFICATION`), rebuild, puis y déclarer `sitemap.xml`.
2. Lancer `python build.py --indexnow` après chaque mise à jour importante.
3. Tester avec le [test des résultats enrichis Google](https://search.google.com/test/rich-results)
   et [PageSpeed Insights](https://pagespeed.web.dev/).

## Compatibilité

- Navigateurs : Chrome, Edge, Firefox, Safari (Mac, iPhone, iPad depuis iOS 13), Opera, Samsung Internet.
  Le JavaScript et le CSS sont automatiquement convertis pour ces navigateurs (esbuild, nécessite Node.js ;
  sans Node, le build fonctionne quand même avec une minification simple).
- Écrans : testés de 320 px (petits téléphones) à 2560 px (grands écrans), téléphones en paysage,
  écrans tactiles (zones de clic agrandies), iPhone à encoche.

## Aperçus de liens (Discord, WhatsApp, Slack, LinkedIn…)

Chaque page a sa propre image de partage 1200×630 (`dist/images/og/`), générée au build avec son titre
et une photo produit. Titre et sous-titre personnalisables dans l'en-tête de chaque page :
`og_title:` et `og_sub:` (photo : dictionnaire `OG_PRODUCT` dans `build.py`).
La couleur rouge de la barre latérale des aperçus Discord vient de `theme-color`.
Slack affiche en plus deux lignes d'infos (boutiques, fidélité).
Après publication, tester un lien sur https://www.opengraph.xyz. Discord et Facebook gardent les
aperçus en cache : utiliser https://developers.facebook.com/tools/debug/ pour forcer la mise à jour.

## Écrans pliables et doubles

Testé sur l'écran extérieur du Galaxy Z Fold (280 px), les pliables dépliés (format presque carré) et les
tablettes. Sur les appareils à deux écrans (Surface Duo, pliables en mode livre ou ordinateur), le contenu se
répartit de part et d'autre de la charnière. Pour tester : Chrome → outils de développement → mode appareil →
« Surface Duo » ou « Galaxy Z Fold 5 ».

## 🥚 Easter egg

Code Konami (↑ ↑ ↓ ↓ ← → ← → B A) sur ordinateur, ou 5 tapotements rapides sur le logo du pied de page :
pluie de toppings. Un petit message attend aussi les curieux dans la console du navigateur.

## Formulaires : que se passe-t-il après l'envoi ?

- **Actuellement (sans `endpoint`)** : le clic sur « Envoyer » ouvre la messagerie du visiteur (Gmail, Outlook,
  Mail…) avec un e-mail pré-rempli adressé à `contact@`, `franchise@` ou `recrutement@`. **Rien n'est envoyé tant
  que le visiteur ne clique pas sur « Envoyer » dans sa messagerie.** Si aucune messagerie n'est configurée
  (fréquent sur ordinateur), rien ne s'ouvre et le visiteur doit écrire lui-même à l'adresse affichée.
  Le CV ne peut pas être joint automatiquement.
- **Recommandé** : brancher un service de formulaires (Formspree, Web3Forms, Netlify Forms, ou un CRM) via
  `endpoint` dans `YF_CONFIG`. Le visiteur reste alors sur le site et voit « Merci ! », vous recevez un e-mail
  et/ou une ligne dans un tableau, avec la possibilité de joindre un CV et d'envoyer une réponse automatique.

## Boutiques : sources et boutiques à confirmer

La liste (`assets/js/stores.js`, 88 boutiques) croise, en septembre 2026 :
les fiches boutiques du site officiel (dont 71 photos de boutiques), OpenStreetMap (positions GPS précises,
boutiques fermées) et les annuaires / plateformes de livraison. Google Maps n'a pas été aspiré :
c'est interdit par ses conditions d'utilisation.

Ajoutées (confirmées par plusieurs sources) : Paris Gare Montparnasse, Toulouse Centre (58 rue Léon Gambetta),
Antibes (6 traverse Lacan), La Rochelle Centre (14 rue du Temple).

**À confirmer par le réseau** (présentes dans des annuaires, statut incertain, non ajoutées) :
Montpellier centre (25 Grand Rue Jean Moulin), Charleroi Ville 2, Annecy (8 quai Eustache Chappuis),
Clermont-Ferrand Jaude 2, Saint-Étienne Steel, Cannes (rue d'Antibes), Épagny.
Fermées (non listées) : Bordeaux rue Sainte-Catherine, SQY Ouest, Marseille.

## Pages annexes

| Page | Rôle |
|---|---|
| `404.html` | Page introuvable (avec recherche de boutique) |
| `403.html` | Accès interdit |
| `500.html` | Erreur serveur |
| `maintenance.html` | Maintenance (erreur 503) — mode d'emploi en commentaire dans `.htaccess` |
| `hors-ligne.html` | Affichée sans connexion (service worker `sw.js`), recharge automatique au retour du réseau |
| `merci.html` | Confirmation après un formulaire, avec message adapté (`?f=contact`, `franchise` ou `recrutement`) |
| `plan-du-site.html` | Plan du site (exigé par le RGAA) |

Les pages d'erreur et utilitaires ne sont pas indexées par les moteurs.

## Animations et petits plus

Transitions douces entre les pages, barre de progression de lecture, chiffres qui défilent,
toppings flottants et parallaxe sur l'accueil, cartes qui s'inclinent au survol, reflet sur les boutons,
suggestions qui s'écrivent dans les champs de recherche, pastille « Ouvert » qui pulse, épingles qui tombent
sur la carte, pot de glace qui fond sur les pages d'erreur. Tout se coupe automatiquement si le visiteur
préfère réduire les animations (réglage système ou menu accessibilité).

## Version anglaise

Le site complet existe en anglais dans `/en/` (adresses anglaises : `/en/menu.html`, `/en/stores.html`,
`/en/loyalty.html`, `/en/careers.html`…). Bouton FR / EN dans le menu ; les visiteurs dont le navigateur
n'est pas en français voient une petite suggestion « View in English » (et inversement).

- Pages anglaises : `_src/pages-en/`, **même nom de fichier** que la page française correspondante
  (ex. `_src/pages-en/carte.html` → `/en/menu.html`). Correspondance des noms : `SLUGS_EN` dans `build.py`.
- En-tête / pied de page : `_src/partials/header-en.html` et `footer-en.html`.
- Textes générés par le JavaScript (horaires, boutiques, messages…) : dictionnaire `I18N` en haut de
  `assets/js/main.js` (`fr` et `en`).
- Référencement : balises `hreflang`, sitemap bilingue, aperçus de partage en anglais, `llms.txt` bilingue.
- Pages légales anglaises = traductions de courtoisie : la version française fait foi.
- **Quand vous modifiez un texte en français, pensez à mettre à jour la page anglaise correspondante.**

## Curseur et barre de défilement

Curseur aux couleurs de la marque (flèche rouge, petite glace sur les liens et boutons), désactivable dans le
menu accessibilité (« Curseur classique »). Barre de défilement rouge assortie (Chrome, Edge, Safari, Firefox).

## Publication sur GitHub Pages

Le dépôt contient une automatisation (`.github/workflows/deploy-pages.yml`) qui construit le site et le
publie à chaque push sur `main`.

1. **Une seule fois** : sur GitHub, **Settings → Pages → Build and deployment → Source : « Deploy from a branch »,
   Branch : `gh-pages`, dossier `/ (root)`**, puis Save. (Le réglage « GitHub Actions » fonctionne aussi.)
2. Chaque push publie le site sur `https://<utilisateur>.github.io/<dépôt>/` en 2 minutes environ
   (suivi dans l'onglet **Actions**).

Sur cette adresse, le site vit dans un sous-dossier : le build adapte les chemins (`BASE_PATH`) et marque les
pages « noindex » pour qu'elles ne concurrencent pas le futur site officiel dans Google.
**Avec un domaine personnalisé** (ex. yogurtfactory.fr) : dans le workflow, mettre `BASE_PATH: ""`, puis
configurer le domaine dans Settings → Pages. Le site est alors servi à la racine et indexé normalement.

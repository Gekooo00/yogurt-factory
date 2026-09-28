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
| **`contenu/`** | **Tout ce qui change souvent** : boutiques, carte, fidélité, pays, réglages. Mode d'emploi : [`contenu/LISEZMOI.md`](contenu/LISEZMOI.md) |
| `_src/pages/`, `_src/pages-en/` | Texte des pages en français / en anglais (même nom de fichier) |
| `_src/partials/` | En-tête, pied de page, panneau d'accessibilité, données structurées communes |
| `_src/static/` | `.htaccess` (Apache), `_headers` / `_redirects` (Netlify), `security.txt` |
| `assets/css/style.css` | Styles ; plan du fichier et variables de couleurs en tête |
| `assets/js/main.js` | Comportements du site, textes affichés par le script (FR / EN) |
| `build.py` | Générateur : lit et **vérifie** `contenu/`, fabrique les pages, la sécurité, le référencement |
| `images/` | Photos ; `images/menu/` produits ; `images/boutiques/` photos des boutiques ; `images/src/` originaux (non publiés) |
| `dist/` | Site généré, prêt à publier (ne jamais modifier à la main) |

## Pages

Accueil · Le concept · La carte (rubriques générées depuis `contenu/carte/`, recherche) · Fidélité (simulateur de points) ·
Boutiques (carte interactive, « Autour de moi », « Ouvert maintenant », favori « Ma Facto ») · Franchise ·
Recrutement · Contact & FAQ · Mentions légales · Confidentialité · Cookies · Conditions d'utilisation ·
Accessibilité · Plan du site · 404 / 403 / 500 · Maintenance · Hors connexion · Merci.

La carte **n'affiche aucun prix** : chaque boutique fixe les siens (les franchisés sont libres de leurs prix).

## Tâches courantes

| Je veux… | Je modifie… |
|---|---|
| Ajouter, modifier, fermer une boutique | `contenu/boutiques/` (un fichier par boutique, modèle `_modele.json`) + photo du même nom dans `images/boutiques/` |
| Ajouter / retirer un topping, un coulis, un sirop, une perle | `contenu/carte/2-toppings.json` ou `contenu/carte/listes.json` |
| Ajouter un produit à la carte | le fichier de la rubrique dans `contenu/carte/` |
| Changer les récompenses fidélité | `contenu/fidelite.json` |
| Changer l'adresse de réception d'un formulaire | `contenu/reglages.json` |
| Modifier un texte de page | `_src/pages/…` **et** `_src/pages-en/…` |
| Autoriser un service externe (vidéo, statistiques…) | dictionnaire `CSP` en haut de `build.py` |

Puis `python build.py` (ou un simple push sur GitHub : le site se reconstruit tout seul).
Le build refuse de générer le site si un fichier de `contenu/` est mal rempli et dit exactement où est l'erreur.

**Protection du texte** (anti-sélection / anti-copie) : `proteger_le_texte` dans `contenu/reglages.json`.
Les champs de formulaire restent utilisables. Cette protection décourage la copie sans pouvoir l'empêcher totalement.

## À faire avant la mise en ligne

1. **E-mails des formulaires** (`contenu/reglages.json`) : adresses provisoires à remplacer.
   Pour recevoir les demandes directement (sans ouvrir la messagerie du visiteur), créer un formulaire
   Formspree et coller son URL dans `endpoint` : la politique de sécurité est mise à jour automatiquement.
2. **Pages légales** : compléter les passages surlignés en jaune (raison sociale, SIREN, hébergeur,
   médiateur de la consommation, contact RGPD, validité des points fidélité…) et faire relire par un juriste.
3. **« Le plus gros bar à toppings de France »** : c'est une allégation comparative ; gardez de quoi la justifier
   (comparatif du nombre de toppings) en cas de contestation.
4. **Boutiques** : 88 adresses (voir « Boutiques à confirmer » plus bas) ; ajouter les nouvelles,
   retirer les fermées, ajouter photos et notes.
5. **Photos** manquantes : granités, matcha, ube (emoji pour l'instant).
6. **Carte OpenStreetMap** : les tuiles gratuites d'OpenStreetMap conviennent pour un trafic modéré.
   Si le site reçoit beaucoup de visites, passer à un fournisseur (MapTiler, Stadia Maps…) : changer l'URL des tuiles
   dans `main.js` (`tileLayer`) et le domaine dans `CSP` (`build.py`).
7. **Accessibilité** : faire réaliser un audit RGAA pour afficher un taux de conformité.
8. Après la mise en ligne : déclarer `https://yogurtfactory.fr/sitemap.xml` dans Google Search Console
   et vérifier les redirections des anciennes pages.

## Déjà en place pour la production

- HTTPS forcé, domaine sans `www`, redirections 301 des anciennes URL WordPress.
- En-têtes de sécurité (CSP stricte sans script externe, HSTS, anti-iframe, Permissions-Policy).
- CSP aussi présente dans chaque page (balise meta) : protège même sur un hébergeur sans en-têtes (GitHub Pages).
- Données de `contenu/` vérifiées au build (liens Google Maps et endpoints en https uniquement, couleurs, nombres) ;
  toute donnée affichée par le script est échappée (pas d'injection de code possible via une fiche boutique).
- Formulaires : champ piège invisible + envoi refusé s'il arrive moins de 3 s après l'ouverture de la page (robots).
- Aucun commentaire de travail publié : HTML nettoyé, CSS/JS minifiés.
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
  `endpoint` dans `contenu/reglages.json`. Le visiteur reste alors sur le site et voit « Merci ! », vous recevez un e-mail
  et/ou une ligne dans un tableau, avec la possibilité de joindre un CV et d'envoyer une réponse automatique.

## Boutiques : sources et boutiques à confirmer

La liste (`contenu/boutiques/`, 88 boutiques) croise, en septembre 2026 :
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

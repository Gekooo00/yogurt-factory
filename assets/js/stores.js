/* ==========================================================================
   Liste des boutiques Yogurt Factory
   --------------------------------------------------------------------------
   Pour ajouter / modifier une boutique : copiez une ligne et adaptez-la.
   Champs : name (nom affiché), center (centre commercial / quartier),
            address, zip, city, region, country, hours, phone (optionnel),
            lat / lng (coordonnées GPS pour la carte : clic droit sur Google Maps > copier)
   Champs optionnels :
            photo     : image de la boutique, ex. "images/boutiques/lyon-confluence.webp"
                        (format 16/9, 800 px de large ; sinon photo générique)
            rating    : note Google, ex. 4.6       reviews : nombre d'avis, ex. 1234
            googleUrl : lien de la fiche Google Maps de la boutique (bouton « avis »)
   Format des horaires (lu par le site pour afficher « Ouvert / Fermé ») :
            "Tous les jours 10h–20h"  ou  "Lun–sam 10h–20h · dim 11h–19h"
   Sources (sept. 2026) : fiches boutiques de l'ancien site officiel, OpenStreetMap,
   annuaires et plateformes de livraison. Photos : fiches boutiques officielles.
   ========================================================================== */
window.YF_STORES = [
  // --- Paris ---------------------------------------------------------------
  { name: "Paris Les Halles", center: "Westfield Forum des Halles", address: "101 rue Berger", zip: "75001", city: "Paris", region: "Île-de-France", country: "France", hours: "Tous les jours 10h–20h", phone: "01 40 28 01 51", lat: 48.85902, lng: 2.35351, photo: "images/boutiques/paris-les-halles.webp" },
  { name: "Paris Carrousel du Louvre", center: "Carrousel du Louvre", address: "99 rue de Rivoli", zip: "75001", city: "Paris", region: "Île-de-France", country: "France", hours: "Tous les jours 10h–20h", lat: 48.85902, lng: 2.35351, photo: "images/boutiques/paris-carrousel-du-louvre.webp" },
  { name: "Paris Le Marais", center: "Le Marais", address: "3 rue Saint-Merri", zip: "75004", city: "Paris", region: "Île-de-France", country: "France", hours: "Tous les jours 13h–minuit", phone: "09 80 51 35 73", lat: 48.85902, lng: 2.35351, photo: "images/boutiques/paris-le-marais.webp" },
  { name: "Paris Passage du Havre", center: "Passage du Havre", address: "109 rue Saint-Lazare", zip: "75009", city: "Paris", region: "Île-de-France", country: "France", hours: "Lun–sam 10h–20h · dim 10h–19h", lat: 48.87535, lng: 2.327, photo: "images/boutiques/paris-passage-du-havre.webp" },
  { name: "Paris Italie 2", center: "Italie Deux", address: "30 avenue d'Italie", zip: "75013", city: "Paris", region: "Île-de-France", country: "France", hours: "Tous les jours 10h–20h", phone: "01 45 89 35 42", lat: 48.82973, lng: 2.35491, photo: "images/boutiques/paris-italie-2.webp" },
  { name: "Paris Beaugrenelle", center: "Beaugrenelle", address: "12 rue Linois", zip: "75015", city: "Paris", region: "Île-de-France", country: "France", hours: "Tous les jours 10h–21h", phone: "09 83 76 53 52", lat: 48.84857, lng: 2.2825, photo: "images/boutiques/paris-beaugrenelle.webp" },

  { name: "Paris Gare Montparnasse", center: "Gare Montparnasse, hall 1, niveau 2", address: "17 boulevard de Vaugirard", zip: "75015", city: "Paris", region: "Île-de-France", country: "France", hours: "Lun–sam 7h–20h · dim 10h–20h", lat: 48.84048, lng: 2.32084 },

  // --- Île-de-France -------------------------------------------------------
  { name: "Argenteuil", center: "Côté Seine", address: "50 avenue du Maréchal Foch", zip: "95100", city: "Argenteuil", region: "Île-de-France", country: "France", hours: "Lun–sam 10h–20h", lat: 48.94469, lng: 2.25417 },
  { name: "Aulnay-sous-Bois", center: "O'Parinor", address: "Haut de Galy", zip: "93606", city: "Aulnay-sous-Bois", region: "Île-de-France", country: "France", hours: "Tous les jours 10h–20h", lat: 48.95698, lng: 2.47513 },
  { name: "Boulogne-Billancourt", center: "Les Passages", address: "5 rue Tony Garnier", zip: "92100", city: "Boulogne-Billancourt", region: "Île-de-France", country: "France", hours: "Lun–sam 10h–20h", lat: 48.83673, lng: 2.23828, photo: "images/boutiques/boulogne-billancourt.webp" },
  { name: "Claye-Souilly", center: "Shopping Promenade", address: "3 rue Robert Schuman", zip: "77410", city: "Claye-Souilly", region: "Île-de-France", country: "France", hours: "Tous les jours 12h–20h", lat: 48.94509, lng: 2.65571 },
  { name: "Collégien", center: "Bay 2", address: "Rue du Général de Gaulle", zip: "77090", city: "Collégien", region: "Île-de-France", country: "France", hours: "Lun–sam 9h30–20h · dim 10h–19h", lat: 48.83713, lng: 2.6595 },
  { name: "Créteil", center: "Créteil Soleil", address: "Avenue de la France Libre", zip: "94000", city: "Créteil", region: "Île-de-France", country: "France", hours: "Lun–sam 10h–20h30", phone: "01 43 77 21 64", lat: 48.77829, lng: 2.45514, photo: "images/boutiques/creteil.webp" },
  { name: "Évry", center: "Évry 2", address: "2 boulevard de l'Europe", zip: "91000", city: "Évry-Courcouronnes", region: "Île-de-France", country: "France", hours: "Lun–sam 10h–21h", phone: "01 78 05 09 79", lat: 48.62814, lng: 2.42788, photo: "images/boutiques/evry.webp" },
  { name: "La Défense – 4 Temps", center: "Westfield Les 4 Temps", address: "15 parvis de La Défense", zip: "92092", city: "Puteaux", region: "Île-de-France", country: "France", hours: "Tous les jours 10h–20h30", phone: "01 47 67 07 93", lat: 48.88415, lng: 2.23689, photo: "images/boutiques/la-defense-4-temps.webp" },
  { name: "La Défense – Le Dôme", center: "Le Dôme, Les 4 Temps", address: "Parvis de La Défense", zip: "92092", city: "Puteaux", region: "Île-de-France", country: "France", hours: "Tous les jours 10h–22h30", lat: 48.88415, lng: 2.23689, photo: "images/boutiques/la-defense-le-dome.webp" },
  { name: "Levallois-Perret", center: "So Ouest", address: "30 rue d'Alsace", zip: "92300", city: "Levallois-Perret", region: "Île-de-France", country: "France", hours: "Lun–sam 10h–20h30", phone: "09 83 00 47 57", lat: 48.89268, lng: 2.29721, photo: "images/boutiques/levallois-perret.webp" },
  { name: "Lieusaint", center: "Carré Sénart", address: "3 allée du Préambule", zip: "77127", city: "Lieusaint", region: "Île-de-France", country: "France", hours: "Lun–sam 11h–20h30 · dim 11h–19h", phone: "09 84 45 72 92", lat: 48.61545, lng: 2.54031, photo: "images/boutiques/lieusaint.webp" },
  { name: "Serris", center: "Val d'Europe", address: "14 cours du Danube", zip: "77700", city: "Serris", region: "Île-de-France", country: "France", hours: "Tous les jours 10h–22h", phone: "09 83 48 57 98", lat: 48.85553, lng: 2.77622, photo: "images/boutiques/serris.webp" },
  { name: "Roissy", center: "Aéroville", address: "30 rue des Buissons", zip: "95700", city: "Roissy-en-France", region: "Île-de-France", country: "France", hours: "Lun–sam 9h–20h", phone: "01 48 62 03 85", lat: 48.99059, lng: 2.52207, photo: "images/boutiques/roissy.webp" },
  { name: "Rosny-sous-Bois", center: "Rosny 2", address: "Avenue du Général de Gaulle", zip: "93110", city: "Rosny-sous-Bois", region: "Île-de-France", country: "France", hours: "Mar–sam 10h–21h · dim–lun 10h–20h", phone: "01 48 94 32 02", lat: 48.88622, lng: 2.47231, photo: "images/boutiques/rosny-sous-bois.webp" },
  { name: "Thiais", center: "Belle Épine", address: "Rue du Luxembourg", zip: "94320", city: "Thiais", region: "Île-de-France", country: "France", hours: "Lun–sam 10h–20h30 · dim 11h–19h", phone: "01 75 37 23 15", lat: 48.75723, lng: 2.37214, photo: "images/boutiques/thiais.webp" },
  { name: "Vélizy", center: "Vélizy 2", address: "Centre commercial Vélizy 2", zip: "78140", city: "Vélizy-Villacoublay", region: "Île-de-France", country: "France", hours: "Lun–sam 10h–21h · dim 10h–19h", phone: "01 39 46 24 96", lat: 48.78262, lng: 2.21797, photo: "images/boutiques/velizy.webp" },
  { name: "Villeneuve-la-Garenne", center: "Qwartz", address: "4 boulevard Gallieni", zip: "92390", city: "Villeneuve-la-Garenne", region: "Île-de-France", country: "France", hours: "Tous les jours 9h30–20h30", phone: "01 47 90 33 04", lat: 48.92669, lng: 2.32993, photo: "images/boutiques/villeneuve-la-garenne.webp" },

  // --- Provence-Alpes-Côte d'Azur -----------------------------------------
  { name: "Aix-en-Provence", center: "Jas de Bouffan", address: "210 avenue de Bredasque", zip: "13090", city: "Aix-en-Provence", region: "Provence-Alpes-Côte d'Azur", country: "France", hours: "Lun–sam 9h30–20h", lat: 43.53292, lng: 5.42005 },
  { name: "Avignon – Le Pontet", center: "Auchan Le Pontet", address: "533 avenue Louis Braille", zip: "84130", city: "Le Pontet", region: "Provence-Alpes-Côte d'Azur", country: "France", hours: "Lun–sam 12h–19h30", lat: 43.9806, lng: 4.87987, photo: "images/boutiques/avignon-le-pontet.webp" },
  { name: "Antibes", center: "Vieil Antibes", address: "6 traverse Lacan", zip: "06600", city: "Antibes", region: "Provence-Alpes-Côte d'Azur", country: "France", hours: "Tous les jours 13h–19h", lat: 43.58167, lng: 7.12355 },
  { name: "Cabriès", center: "Avant Cap – Plan de Campagne", address: "CD6", zip: "13480", city: "Cabriès", region: "Provence-Alpes-Côte d'Azur", country: "France", hours: "Tous les jours 9h30–19h30", lat: 43.41985, lng: 5.36121, photo: "images/boutiques/cabries.webp" },
  { name: "Cagnes-sur-Mer", center: "Polygone Riviera", address: "137 avenue des Alpes", zip: "06800", city: "Cagnes-sur-Mer", region: "Provence-Alpes-Côte d'Azur", country: "France", hours: "Lun–sam 10h–20h · dim 10h–19h", phone: "04 97 02 19 81", lat: 43.6637, lng: 7.12838, photo: "images/boutiques/cagnes-sur-mer.webp" },
  { name: "Nice – Cap 3000", center: "Cap 3000", address: "217 avenue Eugène Donadeï", zip: "06700", city: "Saint-Laurent-du-Var", region: "Provence-Alpes-Côte d'Azur", country: "France", hours: "Lun–sam 10h–21h · dim 10h–20h", lat: 43.65737, lng: 7.19794, photo: "images/boutiques/nice-cap-3000.webp" },
  { name: "Nice TNL", center: "Nice TNL", address: "15 boulevard Général Louis Delfino", zip: "06300", city: "Nice", region: "Provence-Alpes-Côte d'Azur", country: "France", hours: "Lun–sam 10h–20h", phone: "09 63 56 65 84", lat: 43.70546, lng: 7.28503, photo: "images/boutiques/nice-tnl.webp" },
  { name: "Saint-Raphaël", center: "Front de mer", address: "101 promenade René Coty", zip: "83700", city: "Saint-Raphaël", region: "Provence-Alpes-Côte d'Azur", country: "France", hours: "Tous les jours 11h–19h30", phone: "04 94 82 01 39", lat: 43.42197, lng: 6.76796, photo: "images/boutiques/saint-raphael.webp" },
  { name: "Toulon – La Valette", center: "Avenue 83", address: "300 avenue de l'Université", zip: "83160", city: "La Valette-du-Var", region: "Provence-Alpes-Côte d'Azur", country: "France", hours: "Lun–sam 11h–20h", phone: "06 02 05 11 92", lat: 43.13643, lng: 6.00748, photo: "images/boutiques/toulon-la-valette.webp" },

  // --- Auvergne-Rhône-Alpes ------------------------------------------------
  { name: "Grenoble – Grand Place", center: "Grand Place", address: "55 Grand Place", zip: "38100", city: "Grenoble", region: "Auvergne-Rhône-Alpes", country: "France", hours: "Lun–sam 10h–20h", phone: "07 61 88 87 36", lat: 45.15837, lng: 5.73113, photo: "images/boutiques/grenoble-grand-place.webp" },
  { name: "Grenoble – Neyrpic", center: "Neyrpic", address: "9 avenue Benoît Frachon", zip: "38400", city: "Saint-Martin-d'Hères", region: "Auvergne-Rhône-Alpes", country: "France", hours: "Lun–sam 10h–20h", lat: 45.18596, lng: 5.75635, photo: "images/boutiques/grenoble-neyrpic.webp" },
  { name: "Lyon Confluence", center: "Confluence", address: "112 cours Charlemagne", zip: "69002", city: "Lyon", region: "Auvergne-Rhône-Alpes", country: "France", hours: "Tous les jours 10h–20h", lat: 45.74069, lng: 4.8188, photo: "images/boutiques/lyon-confluence.webp" },
  { name: "Lyon Part-Dieu", center: "Westfield La Part-Dieu", address: "17 rue du Docteur Bouchut", zip: "69003", city: "Lyon", region: "Auvergne-Rhône-Alpes", country: "France", hours: "Lun–sam 10h–20h", lat: 45.76001, lng: 4.85544, photo: "images/boutiques/lyon-part-dieu.webp" },
  { name: "Vichy", center: "Les 4 Chemins", address: "35 rue Lucas", zip: "03200", city: "Vichy", region: "Auvergne-Rhône-Alpes", country: "France", hours: "Mar–sam 9h30–19h · dim–lun 14h–19h", lat: 46.1266, lng: 3.42204, photo: "images/boutiques/vichy.webp" },

  // --- Bourgogne-Franche-Comté ---------------------------------------------
  { name: "Besançon", center: "Châteaufarine", address: "Rue André Breton", zip: "25000", city: "Besançon", region: "Bourgogne-Franche-Comté", country: "France", hours: "Lun–sam 10h–20h", lat: 47.21478, lng: 5.94688, photo: "images/boutiques/besancon.webp" },
  { name: "Dijon", center: "Toison d'Or", address: "Route de Langres", zip: "21000", city: "Dijon", region: "Bourgogne-Franche-Comté", country: "France", hours: "Lun–sam 10h–20h", lat: 47.36725, lng: 5.04738 },

  // --- Nouvelle-Aquitaine --------------------------------------------------
  { name: "Bordeaux – Bègles", center: "Rives d'Arcins", address: "Rue des Frères Lumière", zip: "33130", city: "Bègles", region: "Nouvelle-Aquitaine", country: "France", hours: "Horaires du centre", phone: "05 54 52 04 87", lat: 44.79604, lng: -0.53479, photo: "images/boutiques/bordeaux-begles.webp" },
  { name: "Anglet", center: "BAB2", address: "Avenue Jean Léon Laporte", zip: "64600", city: "Anglet", region: "Nouvelle-Aquitaine", country: "France", hours: "Lun–sam 10h–20h", lat: 43.48773, lng: -1.49859, photo: "images/boutiques/anglet.webp" },
  { name: "Bayonne", center: "Centre-ville", address: "81 rue d'Espagne", zip: "64100", city: "Bayonne", region: "Nouvelle-Aquitaine", country: "France", hours: "Lun–sam 12h–19h", lat: 43.49014, lng: -1.47681, photo: "images/boutiques/bayonne.webp" },
  { name: "La Rochelle – Beaulieu", center: "Beaulieu", address: "ZAC de Beaulieu", zip: "17138", city: "Puilboreau", region: "Nouvelle-Aquitaine", country: "France", hours: "Lun–sam 9h30–19h30", phone: "09 82 20 61 94", lat: 46.17583, lng: -1.11646, photo: "images/boutiques/la-rochelle.webp" },
  { name: "La Rochelle – Centre", center: "Centre-ville", address: "14 rue du Temple", zip: "17000", city: "La Rochelle", region: "Nouvelle-Aquitaine", country: "France", hours: "Lun–sam 12h–18h45", phone: "05 46 55 43 11", lat: 46.15883, lng: -1.15246 },
  { name: "Poitiers", center: "Passage des Cordeliers", address: "4 rue Henri Oudin", zip: "86000", city: "Poitiers", region: "Nouvelle-Aquitaine", country: "France", hours: "Lun–sam 10h–20h", phone: "06 61 24 78 02", lat: 46.5824, lng: 0.34164, photo: "images/boutiques/poitiers.webp" },

  // --- Bretagne ------------------------------------------------------------
  { name: "Brest", center: "Coat Ar Gueven", address: "50 rue Jean Jaurès", zip: "29200", city: "Brest", region: "Bretagne", country: "France", hours: "Lun–sam 10h–19h30", lat: 48.39307, lng: -4.4827, photo: "images/boutiques/brest.webp" },
  { name: "Quimper", center: "La Galerie", address: "163 route de Bénodet", zip: "29000", city: "Quimper", region: "Bretagne", country: "France", hours: "Lun–sam 9h–19h30", lat: 47.97547, lng: -4.09536, photo: "images/boutiques/quimper.webp" },
  { name: "Rennes", center: "Colombia", address: "40 place du Colombier", zip: "35000", city: "Rennes", region: "Bretagne", country: "France", hours: "Lun–sam 10h–20h", phone: "02 99 65 10 86", lat: 48.10479, lng: -1.68107, photo: "images/boutiques/rennes.webp" },

  // --- Normandie -----------------------------------------------------------
  { name: "Caen – Mondeville 2", center: "Mondeville 2", address: "ZA de l'Étoile", zip: "14120", city: "Mondeville", region: "Normandie", country: "France", hours: "Lun–sam 9h30–20h", phone: "09 72 55 26 93", lat: 49.16425, lng: -0.297, photo: "images/boutiques/caen-mondeville-2.webp" },
  { name: "Caen – Rives de l'Orne", center: "Les Rives de l'Orne", address: "Quai Amiral Hamelin", zip: "14000", city: "Caen", region: "Normandie", country: "France", hours: "Lun–sam 10h–20h", lat: 49.17766, lng: -0.35087, photo: "images/boutiques/caen-rives-de-l-orne.webp" },
  { name: "Cherbourg", center: "Les Eléis", address: "Quai de l'Entrepôt", zip: "50100", city: "Cherbourg-en-Cotentin", region: "Normandie", country: "France", hours: "Lun–sam 10h30–18h30", phone: "02 33 45 07 45", lat: 49.63516, lng: -1.61982 },
  { name: "Granville", center: "Centre-ville", address: "6 rue de l'Abreuvoir", zip: "50400", city: "Granville", region: "Normandie", country: "France", hours: "Horaires saisonniers", phone: "02 33 69 86 24", lat: 48.83741, lng: -1.59737, photo: "images/boutiques/granville.webp" },
  { name: "Le Havre", center: "Docks Vauban", address: "70 quai Frissard", zip: "76600", city: "Le Havre", region: "Normandie", country: "France", hours: "Tous les jours 10h–20h", phone: "09 81 45 65 27", lat: 49.49019, lng: 0.13014, photo: "images/boutiques/le-havre.webp" },
  { name: "Rouen", center: "Docks 76", address: "5-7 rue Netien", zip: "76000", city: "Rouen", region: "Normandie", country: "France", hours: "Lun–sam 10h–20h", phone: "02 79 90 13 32", lat: 49.44596, lng: 1.06533, photo: "images/boutiques/rouen.webp" },

  // --- Hauts-de-France -----------------------------------------------------
  { name: "Beauvais", center: "Jeu de Paume", address: "21 boulevard Saint-André", zip: "60000", city: "Beauvais", region: "Hauts-de-France", country: "France", hours: "Lun–sam 10h–20h", phone: "03 44 07 53 79", lat: 49.43308, lng: 2.08908, photo: "images/boutiques/beauvais.webp" },
  { name: "Calais – Coquelles", center: "Cité Europe", address: "1001 boulevard du Kent", zip: "62231", city: "Coquelles", region: "Hauts-de-France", country: "France", hours: "Lun–sam 10h–20h", lat: 50.93394, lng: 1.81029, photo: "images/boutiques/calais-coquelles.webp" },
  { name: "Dunkerque", center: "Centre Marine", address: "Centre Marine", zip: "59140", city: "Dunkerque", region: "Hauts-de-France", country: "France", hours: "Horaires du centre", lat: 51.03454, lng: 2.37435 },
  { name: "Lille", center: "Euralille", address: "100 avenue Willy Brandt", zip: "59777", city: "Lille", region: "Hauts-de-France", country: "France", hours: "Lun–sam 10h–20h", phone: "09 67 00 51 56", lat: 50.63777, lng: 3.07434, photo: "images/boutiques/lille.webp" },
  { name: "Noyelles-Godault", center: "Auchan Noyelles", address: "Route Nationale 43", zip: "62950", city: "Noyelles-Godault", region: "Hauts-de-France", country: "France", hours: "Lun–sam 10h–20h30", lat: 50.41225, lng: 2.97734, photo: "images/boutiques/noyelles-godault.webp" },

  // --- Centre-Val de Loire / Pays de la Loire ------------------------------
  { name: "Tours", center: "L'Heure Tranquille", address: "59 avenue Marcel Mérieux", zip: "37200", city: "Tours", region: "Centre-Val de Loire", country: "France", hours: "Lun–sam 10h–20h · dim 11h–19h", lat: 47.36627, lng: 0.67745, photo: "images/boutiques/tours.webp" },
  { name: "Angers – Beaucouzé", center: "L'Atoll", address: "Écoparc du Buisson", zip: "49070", city: "Beaucouzé", region: "Pays de la Loire", country: "France", hours: "Lun–sam 10h–20h", lat: 47.4853, lng: -0.6271, photo: "images/boutiques/angers-beaucouze.webp" },
  { name: "La Roche-sur-Yon", center: "Les Flâneries", address: "181 rue Philippe Lebon", zip: "85000", city: "La Roche-sur-Yon", region: "Pays de la Loire", country: "France", hours: "Lun–jeu 9h30–21h30 · ven–sam 9h30–22h", lat: 46.69922, lng: -1.4324, photo: "images/boutiques/la-roche-sur-yon.webp" },
  { name: "Le Mans", center: "Auchan – ZAC du Moulin aux Moines", address: "ZAC du Moulin aux Moines", zip: "72650", city: "La Chapelle-Saint-Aubin", region: "Pays de la Loire", country: "France", hours: "Lun–sam 10h–21h", lat: 48.03667, lng: 0.1783, photo: "images/boutiques/le-mans.webp" },
  { name: "Nantes Beaulieu", center: "Beaulieu", address: "1 boulevard Général de Gaulle", zip: "44200", city: "Nantes", region: "Pays de la Loire", country: "France", hours: "Lun–sam 9h30–20h", lat: 47.20563, lng: -1.53481, photo: "images/boutiques/nantes-beaulieu.webp" },
  { name: "Nantes – Basse-Goulaine", center: "Pôle Sud", address: "Route de Clisson", zip: "44115", city: "Basse-Goulaine", region: "Pays de la Loire", country: "France", hours: "Lun–sam 8h30–21h", lat: 47.18745, lng: -1.46734, photo: "images/boutiques/nantes-basse-goulaine.webp" },

  // --- Grand Est -----------------------------------------------------------
  { name: "Metz", center: "Muse", address: "2 rue des Messageries", zip: "57000", city: "Metz", region: "Grand Est", country: "France", hours: "Lun–sam 10h–20h", phone: "03 72 59 55 99", lat: 49.10569, lng: 6.18236, photo: "images/boutiques/metz.webp" },
  { name: "Nancy", center: "Saint-Sébastien", address: "Rue des Ponts", zip: "54000", city: "Nancy", region: "Grand Est", country: "France", hours: "Lun–sam 10h–20h", phone: "03 83 23 82 50", lat: 48.68675, lng: 6.18307, photo: "images/boutiques/nancy.webp" },
  { name: "Strasbourg", center: "Les Halles", address: "24 place des Halles", zip: "67000", city: "Strasbourg", region: "Grand Est", country: "France", hours: "Lun–sam 10h–20h", lat: 48.58663, lng: 7.74157, photo: "images/boutiques/strasbourg.webp" },
  { name: "Thionville", center: "Carrefour Geric", address: "Centre commercial Geric", zip: "57100", city: "Thionville", region: "Grand Est", country: "France", hours: "Tous les jours 9h–20h", lat: 49.37674, lng: 6.13673 },

  // --- Occitanie -----------------------------------------------------------
  { name: "Béziers", center: "Polygone", address: "3 carrefour de l'Hours", zip: "34500", city: "Béziers", region: "Occitanie", country: "France", hours: "Lun–sam 10h–20h", lat: 43.33601, lng: 3.2252, photo: "images/boutiques/beziers.webp" },
  { name: "Montpellier", center: "Odysseum", address: "2 place de Lisbonne", zip: "34000", city: "Montpellier", region: "Occitanie", country: "France", hours: "Tous les jours 12h–19h", phone: "09 67 13 29 90", lat: 43.60354, lng: 3.91671, photo: "images/boutiques/montpellier.webp" },
  { name: "Perpignan – Claira", center: "Carrefour Claira", address: "Route du Barcarès", zip: "66530", city: "Claira", region: "Occitanie", country: "France", hours: "Lun–sam 9h30–20h", phone: "06 62 14 71 93", lat: 42.77516, lng: 2.91331, photo: "images/boutiques/perpignan-claira.webp" },
  { name: "Toulouse Centre", center: "Centre-ville", address: "58 rue Léon Gambetta", zip: "31000", city: "Toulouse", region: "Occitanie", country: "France", hours: "Tous les jours 12h–22h", phone: "09 63 62 39 94", lat: 43.60366, lng: 1.44254 },
  { name: "Toulouse – Blagnac", center: "Centre commercial Blagnac", address: "2 allée Émile Zola", zip: "31700", city: "Blagnac", region: "Occitanie", country: "France", hours: "Lun–sam 9h30–20h", lat: 43.64486, lng: 1.37321, photo: "images/boutiques/toulouse-blagnac.webp" },

  // --- Outre-mer -----------------------------------------------------------
  { name: "Matoury", center: "Family Plaza", address: "CC Family Plaza", zip: "97351", city: "Matoury", region: "Guyane", country: "Outre-mer", hours: "Tous les jours 9h30–19h30", lat: 4.88771, lng: -52.33176, photo: "images/boutiques/matoury.webp" },
  { name: "Nouméa – Baie des Citrons", center: "Baie des Citrons", address: "Promenade Roger Laroque", zip: "98800", city: "Nouméa", region: "Nouvelle-Calédonie", country: "Outre-mer", hours: "Lun–jeu 11h–19h · ven–dim 11h–20h", phone: "+687 31 14 77", lat: -22.29889, lng: 166.43871 },
  { name: "Nouméa – Mirage Plaza", center: "Mirage Plaza", address: "27 promenade Roger Laroque", zip: "98800", city: "Nouméa", region: "Nouvelle-Calédonie", country: "Outre-mer", hours: "Horaires du centre", lat: -22.29889, lng: 166.43871, photo: "images/boutiques/noumea-mirage-plaza.webp" },
  { name: "Dumbéa", center: "Dumbéa Mall", address: "Centre commercial Dumbéa Mall", zip: "98835", city: "Dumbéa-sur-Mer", region: "Nouvelle-Calédonie", country: "Outre-mer", hours: "Lun–jeu 10h–19h30 · ven 10h–20h · sam 9h–20h · dim 9h–18h", lat: -22.1497, lng: 166.4432, photo: "images/boutiques/dumbea.webp" },

  // --- International -------------------------------------------------------
  { name: "Charleroi", center: "Rive Gauche", address: "Place Verte 20", zip: "6000", city: "Charleroi", region: "Wallonie", country: "Belgique", hours: "Lun–sam 10h–19h", lat: 50.40785, lng: 4.44242 },
  { name: "Liège", center: "Médiacité", address: "Boulevard Raymond Poincaré 7", zip: "4020", city: "Liège", region: "Wallonie", country: "Belgique", hours: "Lun–sam 10h–20h", lat: 50.63449, lng: 5.58086, photo: "images/boutiques/liege.webp" },
  { name: "Luxembourg", center: "Cloche d'Or", address: "25 boulevard F. W. Raiffeisen", zip: "2411", city: "Luxembourg", region: "Luxembourg", country: "Luxembourg", hours: "Lun–sam 10h–21h", lat: 49.58417, lng: 6.11619, photo: "images/boutiques/luxembourg.webp" },
  { name: "Saint-Sébastien", center: "Garbera", address: "Garbera Zeharbidea 1", zip: "20017", city: "Donostia-San Sebastián", region: "Pays basque", country: "Espagne", hours: "Tous les jours 12h–22h30", lat: 43.30877, lng: -1.94368, photo: "images/boutiques/saint-sebastien.webp" },
  { name: "Saly", center: "Saly", address: "Route de Saly, croisement allée des Milliardaires", zip: "", city: "Saly", region: "Mbour", country: "Sénégal", hours: "Tous les jours 10h–20h", lat: 14.44414, lng: -17.01131, photo: "images/boutiques/saly.webp" },
  { name: "Libreville", center: "Mbolo", address: "Boulevard Triomphal", zip: "", city: "Libreville", region: "Estuaire", country: "Gabon", hours: "Tous les jours 9h–18h30", phone: "060 22 28 28", lat: 0.40433, lng: 9.43606, photo: "images/boutiques/libreville.webp" },
  { name: "Putrajaya – IOI City Mall", center: "IOI City Mall", address: "Level 3A, IOI City Tower Two", zip: "62502", city: "Putrajaya", region: "Kuala Lumpur", country: "Malaisie", hours: "Horaires du centre", lat: 2.92335, lng: 101.68849 },
  { name: "Kuala Lumpur – Mid Valley", center: "Mid Valley Megamall", address: "Lingkaran Syed Putra, Mid Valley City", zip: "59200", city: "Kuala Lumpur", region: "Kuala Lumpur", country: "Malaisie", hours: "Tous les jours 10h–22h", phone: "+60 13-432 6765", lat: 3.12009, lng: 101.67692 },
  { name: "Tachkent", center: "Tashkent City Mall", address: "Tashkent City", zip: "", city: "Tachkent", region: "Tachkent", country: "Ouzbékistan", hours: "Tous les jours 12h–minuit", lat: 41.31541, lng: 69.24816, photo: "images/boutiques/tachkent.webp" }
];

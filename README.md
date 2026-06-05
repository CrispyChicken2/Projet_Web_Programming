# Générateur de CV en ligne — Vue utilisateur

Qu'est‑ce que c'est ?
- Une application web simple qui permet de créer, organiser et prévisualiser un CV directement depuis votre navigateur.

Ce que vous pouvez faire
- Créer un compte et vous connecter.
- Saisir vos informations personnelles, expériences, formations et compétences via des formulaires clairs.
- Réorganiser et compléter les sections de votre CV.
- Voir un aperçu immédiat du CV en version web adaptée à l'impression.
- Imprimer ou enregistrer votre CV au format PDF depuis la fonction d'impression du navigateur.

Usage rapide (côté utilisateur)
- Inscription : créez un compte depuis la page d'inscription.
- Édition : remplissez les champs du formulaire pour chaque section (Expériences, Formation, Compétences, etc.).
- Prévisualisation : cliquez sur "Aperçu" pour voir le rendu final et le télécharger/imprimer.

Accessibilité
- L'interface est conçue pour être simple et responsive afin de fonctionner sur ordinateur et tablette.

Informations techniques (très succinct)
- Outils utilisés : Flask (serveur web léger, idéal pour prototypage rapide) ; Apache en reverse proxy pour assurer l'accès public et TLS sur la VM d'hébergement.
- Déploiement : l'application est hébergée sur une VM et accessible publiquement à l'adresse suivante : https://k2vm-101.mde.epf.fr/

Fichiers utiles (pour les développeurs)
- Entrée de l'application : `test/main.py`
- Pages et gabarits : le dossier `templates/`
- Ressources statiques : le dossier `static/`

## Côté IT (très bref)
- Base de données : SQLite via SQLAlchemy (fichier `cv_app.db`) pour une persistance légère et simple à déployer.
- Authentification : mots de passe hachés avec PBKDF2 ; gestion de session côté serveur pour garder l'identifiant utilisateur.
- Framework : l'application utilise FastAPI pour les routes et Jinja2 pour les templates.
- Interaction côté client : `htmx` est utilisé pour sauvegarder et prévisualiser le CV sans recharger la page (requêtes partielles vers `/generate-cv`).
- Déploiement : la VM héberge l'application derrière un reverse proxy Apache (TLS et routage), accessible sur https://k2vm-101.mde.epf.fr/
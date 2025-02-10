# Gmail to Discord Bot

Ce bot permet de récupérer des emails sur Gmail (en filtrant par différents labels) et de les envoyer sur différents channels Discord selon la configuration.

## Configuration

- **config.json**  
  Ce fichier contient la configuration du bot (token Discord, chemin vers le fichier credentials Gmail et mapping entre labels et channels Discord).

  Exemple :
  ```json
  {
    "discord_token": "TON_TOKEN_DISCORD",
    "gmail_credentials": "credentials.json",
    "label_channel_mapping": {
      "Label1": channel1,
      "label2": channel2,
      "label3": channel3
    }
  }
  ```

- **credentials.json**  
  Fichier obtenu depuis la Google Cloud Console pour l'accès à l'API Gmail.

- **token.json**  
  Fichier généré automatiquement lors de la première authentification OAuth. **Ne pas versionner ce fichier !**

## Installation

1. **Installer les dépendances :**

   ```bash
   pip install -r requirements.txt
   ```

2. **Exécuter le bot en local :**

   ```bash
   python gmail_discord_bot.py
   ```

3. **Ou utiliser Docker :**

   Construire l'image :
   ```bash
   docker build -t gmail-discord-bot .
   ```
   
   Lancer le conteneur :
   ```bash
   docker run --name my-bot gmail-discord-bot
   ```

## TODO

- [ ] **Améliorer la pagination des embeds :**  
  Implémenter un système de pagination avec des réactions pour les très longs emails.

- [ ] **Gestion des erreurs et des reconnections :**  
  Mettre en place une gestion plus robuste des erreurs (p.ex. en cas de perte de connexion à l'API Gmail ou Discord).

- [ ] **Optimisation de l'extraction des emails :**  
  Mieux gérer les différentes structures MIME (HTML, multipart/mixed) pour extraire le contenu de l'email.

- [ ] **Configurer un système de logging :**  
  Ajouter des logs détaillés pour faciliter le débogage et la maintenance.

- [ ] **Déploiement continu :**  
  Configurer un pipeline CI/CD pour déployer automatiquement le bot.

---

Ce projet reste à améliorer, je m'en sers surtout pour faire de la veille sur des newletter sur un email dedié ! 
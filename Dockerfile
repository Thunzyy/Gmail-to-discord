# Utilisation de l'image officielle Python en version slim
FROM python:3.9-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier le fichier de dépendances dans le conteneur
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copier tous les fichiers de ton projet dans le conteneur
COPY . .

# Lancer le bot
CMD ["python", "gmail_discord_bot.py"] 
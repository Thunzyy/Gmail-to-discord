import os
import time
import asyncio
import base64
import json
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from discord.ext import commands
import discord
from google_auth_oauthlib.flow import InstalledAppFlow

# Chargement du fichier de configuration
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

# Configuration lue depuis le fichier JSON
DISCORD_TOKEN = config["discord_token"]
GMAIL_CREDENTIALS = config["gmail_credentials"]
LABEL_CHANNEL_MAPPING = config["label_channel_mapping"]

# Initialisation Discord
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

# Fonction d'authentification Gmail
def gmail_authenticate():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json')
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                GMAIL_CREDENTIALS,
                ['https://www.googleapis.com/auth/gmail.modify']
            )
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

# Récupérer les emails non lus selon la requête
def get_unread_emails(service, query):
    results = service.users().messages().list(
        userId='me',
        q=query
    ).execute()
    return results.get('messages', [])

# Extraction du corps de l'email (en parcourant les parties)
def extract_email_body(email_data):
    body = ""
    # Si le payload contient directement du texte
    if email_data['payload'].get('body') and email_data['payload']['body'].get('data'):
        data = email_data['payload']['body']['data']
        body += base64.urlsafe_b64decode(data).decode('utf-8', errors='replace')
    # Sinon, si le payload contient plusieurs parties
    elif 'parts' in email_data['payload']:
        for part in email_data['payload']['parts']:
            if part['mimeType'] == 'text/plain' and part['body'].get('data'):
                data = part['body'].get('data')
                body += base64.urlsafe_b64decode(data).decode('utf-8', errors='replace')
            elif part['mimeType'].startswith('multipart/'):
                for subpart in part.get('parts', []):
                    if subpart['mimeType'] == 'text/plain' and subpart['body'].get('data'):
                        data = subpart['body'].get('data')
                        body += base64.urlsafe_b64decode(data).decode('utf-8', errors='replace')
    return body.strip() or "Aucun contenu textuel trouvé"

# Boucle principale de vérification
@bot.event
async def on_ready():
    print(f'Connecté en tant que {bot.user}')
    await check_emails_loop()

async def check_emails_loop():
    service = gmail_authenticate()
    while True:
        # Pour chaque label personnalisé dans la config, on lance une requête spécifique
        for label, channel_id in LABEL_CHANNEL_MAPPING.items():
            query = f'is:unread label:{label}'
            messages = get_unread_emails(service, query=query)
            if messages:
                channel = bot.get_channel(channel_id)
                if channel is None:
                    print(f"Channel avec l'ID {channel_id} non trouvé.")
                    continue
                for msg in messages:
                    # Récupération des headers (format metadata)
                    email_meta = service.users().messages().get(
                        userId='me', id=msg['id'], format='metadata'
                    ).execute()
                    headers = {h['name']: h['value'] for h in email_meta['payload']['headers']}
                    
                    # Récupération du contenu complet du mail (format full)
                    email_data = service.users().messages().get(
                        userId='me', id=msg['id'], format='full'
                    ).execute()
                    
                    # Extraction et découpage du corps de l'email.
                    body = extract_email_body(email_data)
                    # Découpage en morceaux de 1000 caractères
                    chunks = [body[i:i+1000] for i in range(0, len(body), 1000)] or ["Aucun contenu textuel trouvé"]
                    
                    # Premier embed avec les informations principales
                    main_embed = discord.Embed(
                        title=headers.get('Subject', 'Pas de sujet')[:256],
                        description=chunks[0],
                        color=0x00ff00
                    )
                    main_embed.set_author(name=headers.get('From', 'Expéditeur inconnu')[:256])
                    main_embed.add_field(name="Date", value=headers.get('Date', 'Inconnue'), inline=True)
                    
                    # Ajout des pièces jointes si présentes
                    if 'parts' in email_data['payload']:
                        attachments = [p['filename'] for p in email_data['payload']['parts'] if p.get('filename')]
                        if attachments:
                            main_embed.add_field(name="Pièces jointes", value="\n".join(attachments[:5])[:1024], inline=False)
                    
                    embeds = [main_embed]
                    # Embeds supplémentaires pour les parties suivantes
                    for i, chunk in enumerate(chunks[1:], start=2):
                        embeds.append(
                            discord.Embed(
                                description=f"**Suite du message ({i}/{len(chunks)})**\n{chunk}",
                                color=0x00ff00
                            )
                        )
                    
                    # Envoi des embeds par paquets (max 5 embeds par envoi)
                    for i in range(0, len(embeds), 5):
                        await channel.send(embeds=embeds[i:i+5])
                    
                    # Marquer l'email comme lu
                    service.users().messages().modify(
                        userId='me',
                        id=msg['id'],
                        body={'removeLabelIds': ['UNREAD']}
                    ).execute()
        await asyncio.sleep(60)

bot.run(DISCORD_TOKEN) 
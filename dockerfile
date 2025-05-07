 Utiliser une image Python officielle
FROM python:3.11-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier le fichier requirements.txt dans le conteneur
COPY requirements.txt /app/

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste des fichiers du projet
COPY . /app/

# Exposer le port sur lequel Django fonctionne
EXPOSE 8000

# Définir la commande pour démarrer l'application Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

ENV DJANGO_SETTINGS_MODULE=artist_network.settings


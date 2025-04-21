# Étape 1 : image de base
FROM python:3.10-slim

# Étape 2 : définir le répertoire de travail
WORKDIR /app

# Étape 3 : copier les fichiers
COPY . /app

# Étape 4 : installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Étape 5 : exposer le port Flask
EXPOSE 5000

# Étape 6 : lancer l’application
CMD ["python", "app.py"]

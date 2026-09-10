# Basis-Image
FROM python:3.10-slim

# Arbeitsverzeichnis
WORKDIR /app

# Requirements installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Bot-Code kopieren
COPY . .

# Startbefehl
CMD ["python", "Personalbot.py"]

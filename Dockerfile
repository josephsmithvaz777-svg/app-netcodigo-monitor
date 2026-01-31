FROM python:3.12-slim

# Instalar dependencias del sistema necesarias para lxml
RUN apt-get update && apt-get install -y \
    gcc \
    libxml2-dev \
    libxslt-dev \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Crear archivos de configuración si no existen
RUN if [ ! -f accounts.json ]; then echo '{"accounts": []}' > accounts.json; fi && \
    if [ ! -f settings.json ]; then echo '{"check_interval": 300, "days_back": 7, "auto_mark_read": false, "notification_enabled": true}' > settings.json; fi

# Exponer puerto
EXPOSE 5000

# Variables de entorno por defecto
ENV PORT=5000
ENV PYTHONUNBUFFERED=1

# Comando para ejecutar la aplicación
CMD ["python", "app.py"]

# Guardian del Diván

Este bot de Telegram gestiona suscripciones y requiere un token para funcionar.

## Instalación

1. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

2. Copia `.env.example` a `.env` y define `BOT_TOKEN` y `ADMIN_IDS`:
   ```bash
   cp .env.example .env
   echo "BOT_TOKEN=TU_TOKEN_AQUI" >> .env
   echo "ADMIN_IDS=123456789" >> .env
   ```

## Ejecución

Inicia el bot ejecutando `python main.py`. Si `BOT_TOKEN` o `ADMIN_IDS` no están
definidos se mostrará un error indicando cómo configurarlos.


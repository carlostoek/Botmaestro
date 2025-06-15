# Botmaestro

Este repositorio contiene un ejemplo b\u00e1sico de un bot de Telegram con tres flujos principales:

1. **Men\u00fa de Administrador** para usuarios con privilegios.
2. **Men\u00fa de suscriptores VIP** que incluye la base de un sistema de gamificaci\u00f3n.
3. **Men\u00fa de suscripci\u00f3n** para usuarios del canal gratuito.

El bot est\u00e1 desarrollado con `python-telegram-bot`. Para probarlo localmente sigue estos pasos:

```bash
pip install python-telegram-bot==13.15
python bot.py
```

Antes de ejecutar, reemplaza `YOUR_TELEGRAM_BOT_TOKEN` en `bot.py` con el token real de tu bot y actualiza las listas `ADMIN_IDS` y `VIP_USERS` con los identificadores correspondientes.

FROM python:3.10

WORKDIR /app

# Копируем файлы бота
COPY . .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Если нужен доступ к Django
ENV PYTHONPATH "${PYTHONPATH}:/app/hourgraph"
ENV DJANGO_SETTINGS_MODULE=backend.settings

CMD ["python", "telegram_bot.py"]
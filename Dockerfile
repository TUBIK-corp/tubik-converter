FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все содержимое приложения
COPY ./app .

# Убедитесь, что статические файлы доступны
RUN chmod -R 755 /app/static

CMD ["python", "app.py"]
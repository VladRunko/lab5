
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Копіювання коду
COPY . /app

# Відкриття порту
EXPOSE 5000

# Запуск Flask-застосунку
CMD ["python", "lab4.py"]

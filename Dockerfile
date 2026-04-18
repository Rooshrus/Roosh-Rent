# Використовуємо офіційний образ Python
FROM python:3.10-slim

# Встановлюємо системні залежності для psycopg2 та pillow
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    python3-dev \
    libjpeg-dev \
    zlib1g-dev \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

# Встановлюємо робочу директорію
WORKDIR /app

# Копіюємо файл залежностей та встановлюємо їх
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо весь проект
COPY . .

# Збираємо статику (можна закоментувати, якщо будете робити це вручну)
# RUN python manage.py collectstatic --noinput

# Команда для запуску (використовуємо gunicorn або стандартний runserver для розробки)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

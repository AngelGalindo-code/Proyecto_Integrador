FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Exponemos el puerto 10599
EXPOSE 10599
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Forzamos a Flask a correr en el puerto 10599
CMD ["flask", "run", "--port", "10599"]
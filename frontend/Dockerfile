FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Cambiamos al puerto 8080
EXPOSE 8080
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Le indicamos a Flask que escuche en el 8080
CMD ["flask", "run", "--port", "8080"]
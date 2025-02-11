FROM python:3.9-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

CMD ["waitress-serve", "--host", "0.0.0.0", "--port", "8080", "main:app"]

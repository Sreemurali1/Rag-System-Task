FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 10000 8000

CMD ["supervisord", "-c", "supervisord.conf"]
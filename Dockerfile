FROM python:3.11.8-slim

WORKDIR /app

RUN apt-get update && apt-get install -y python3-pip && \
    pip3 install --no-cache-dir -r requirements.txt

COPY . /app

CMD ["python3", "bot.py"]
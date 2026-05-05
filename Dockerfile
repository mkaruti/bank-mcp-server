FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY data/ ./data/

RUN python src/setup_database.py

COPY start.sh .
RUN chmod +x start.sh

CMD ["./start.sh"]
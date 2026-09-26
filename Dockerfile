FROM python:3.14.7-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY mastofeed/ ./mastofeed/

EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "mastofeed.feed_server:app"]

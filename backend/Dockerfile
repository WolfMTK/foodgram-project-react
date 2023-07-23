FROM python:3.9

RUN apt-get update && apt-get install -y fontconfig

WORKDIR /app

RUN pip install gunicorn==20.1.0

COPY requirements.txt .
COPY --chmod=0755 entrypoint.sh /usr/local/bin/
COPY . .

RUN pip install -r requirements.txt --no-cache-dir

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "foodgram.wsgi"]

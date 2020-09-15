FROM python:3.7.7

WORKDIR /app
COPY requirements.txt /app/

VOLUME /app/logs
VOLUME /app/vfs

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "app.py"]

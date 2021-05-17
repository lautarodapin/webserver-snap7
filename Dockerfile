FROM python:3.9.5-slim-buster

WORKDIR /app

COPY requeriments.txt .

RUN pip3 install -r requeriments.txt

COPY . .

RUN python3 manage.py migrate

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
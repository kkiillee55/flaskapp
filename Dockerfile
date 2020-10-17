FROM python:3.7-buster

USER root

WORKDIR /app

ADD . /app

RUN apt-get update && apt-get install -y libpq-dev |  pip install -r requirements.txt

EXPOSE 80

CMD ["python","run.py"]
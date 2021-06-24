FROM python:3

ENV PYTHONUNBUFFERED=0

RUN apt-get update && apt-get -y install \
    libpq-dev


WORKDIR /app
ADD    ./django_src/django.requirements.txt   /app/
RUN    pip install -r django.requirements.txt

CMD python manage.py migrate && \
    python manage.py runserver 0:8000
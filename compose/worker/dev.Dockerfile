FROM python:3

ENV PYTHONUNBUFFERED=0

RUN apt-get update && apt-get -y install \
    libpq-dev


WORKDIR /app
ADD    ./django_src/worker.requirements.txt   /app/
RUN    pip install -r worker.requirements.txt

CMD watchmedo auto-restart --directory=./ --pattern=*.py --recursive -- celery -A walk_data_processing worker -l info --concurrency=10 -Q default
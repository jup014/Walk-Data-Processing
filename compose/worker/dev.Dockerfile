FROM python:3

ENV PYTHONUNBUFFERED=0

RUN apt-get update && apt-get -y install \
    libpq-dev


WORKDIR /app
ADD    ./django_src/worker.requirements.txt   /app/
RUN    pip install -r worker.requirements.txt

CMD [ "python", "worker.py"]
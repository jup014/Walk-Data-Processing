FROM python:3

ENV PYTHONUNBUFFERED=0

RUN apt-get update && apt-get -y install \
    libpq-dev


WORKDIR /app
ADD    ./django_src/requirements.txt   /app/
RUN    pip install -r requirements.txt

CMD [ "python", "manage.py", "runserver", "0:8000" ]
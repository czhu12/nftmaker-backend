FROM python:3.8
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

RUN apt-get update \
    && apt-get install postgresql-13 -y

WORKDIR /app
COPY ./requirements.txt /app/
RUN pip install -r requirements.txt
RUN pip install cython
COPY ./app /app/
CMD PYTHONPATH=/app python manage.py migrate && PYTHONPATH=/app python manage.py runserver 0.0.0.0:$PORT

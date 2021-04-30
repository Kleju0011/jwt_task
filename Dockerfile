FROM python:3.9

EXPOSE 8000

WORKDIR /jwt_task

COPY jwt_url_task /jwt_task
COPY requirements.txt /jwt_task/requirements.txt
COPY uwsgi.ini /jwt_task/uwsgi.ini

RUN pip install -r requirements.txt
RUN python3 manage.py makemigrations shorter_url
RUN python3 manage.py migrate

CMD uwsgi --ini uwsgi.ini
# Python with Debian. bookworm or bullseye tags indicate Debian.
FROM python:3.12.0-bookworm

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

#COPY ./startup.sh /code/startup.sh # This command might be required if deployed on Azure.

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

CMD ["gunicorn", "--config", "app/gunicorn.conf.py", "app.app:app"]
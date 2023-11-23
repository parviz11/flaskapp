# Use an official Python runtime as a parent image. bookworm or bullseye tags indicate Debian.
FROM python:3.12.0-bookworm

# Set the working directory to /code
WORKDIR /code

# Copy the current directory contents into the container at /code
COPY ./requirements.txt /code/requirements.txt

# This command might be required if deployed on Azure.
#COPY ./startup.sh /code/startup.sh

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the app directory into the container at /code/app
COPY ./app /code/app

# Define the command to run on container start
CMD ["gunicorn", "--config", "app/gunicorn.conf.py", "app.app:app"]
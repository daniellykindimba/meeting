# pull official base image
FROM python:3.8.5

# set working directory
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install system dependencies
# RUN apt-get update \
#   && apt-get -y install netcat gcc \
#   && apt-get clean

# install python dependencies
RUN pip install --upgrade pip
RUN pip install watchdog
COPY ./requirements.txt .
RUN pip install -r requirements.txt


ADD entrypoint.sh .
RUN chmod 766 /etc/passwd

# ENTRYPOINT ./entrypoint.sh
# add app
COPY . .

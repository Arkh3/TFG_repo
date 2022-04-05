FROM ubuntu:20.04

## Installing Python dependencies
RUN apt upgrade
RUN apt update
RUN apt install -y git
RUN apt install -y vim
#RUN apt install -y postgresql
RUN apt install -y python3.8
RUN apt install -y python3-pip
RUN apt install -y libpq-dev
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/
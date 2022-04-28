FROM python:3

## Installing Python dependencies
RUN apt upgrade
RUN apt update && apt install -y vim libpq-dev cmake ffmpeg libsm6 libxext6
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
COPY requirements.txt /
RUN pip install -r requirements.txt
WORKDIR /code
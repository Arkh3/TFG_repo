FROM ubuntu:20.04

## Installing Python dependencies
# Maybe we need sudo for this
RUN apt upgrade
RUN apt update
RUN apt install -y git 
RUN apt install -y vim
RUN apt install -y python3.8
RUN apt install -y python3-pip
RUN pip install django
RUN alias python=python3
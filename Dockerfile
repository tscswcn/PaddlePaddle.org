############################################################
# Dockerfile to run a Django-based web application
# Based on an AMI
# https://medium.com/@rohitkhatana/deploying-django-app-on-aws-ecs-using-docker-gunicorn-nginx-c90834f76e21
############################################################
# Set the base image to use to Ubuntu
FROM ubuntu:14.04

# Set the file maintainer (your name - the file's author)
MAINTAINER Thuan Nguyen

ENV EXTERNAL_TEMPLATE_DIR=/templates

# Update the default application repository sources list
RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y python python-pip
RUN apt-get install -y python-dev
RUN apt-get install -y libmysqlclient-dev
RUN apt-get install -y git
RUN apt-get install -y vim
RUN apt-get install -y mysql-server
RUN apt-get install -y nginx

# Create application subdirectories
WORKDIR /var
RUN mkdir www logs

WORKDIR /var/www
COPY portal .

# Port to expose
EXPOSE 8000

RUN pip install -r requirements.txt

COPY ./docker-entrypoint.sh .
COPY ./django_nginx.conf /etc/nginx/sites-available/
RUN ln -s /etc/nginx/sites-available/django_nginx.conf /etc/nginx/sites-enabled
RUN echo "daemon off;" >> /etc/nginx/nginx.conf
ENTRYPOINT ["./docker-entrypoint.sh"]
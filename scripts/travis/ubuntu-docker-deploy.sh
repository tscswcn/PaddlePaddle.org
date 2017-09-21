#!/bin/bash
set -e

sudo bash
eval $(aws ecr get-login --no-include-email --region ap-southeast-1)
docker pull 330323714104.dkr.ecr.ap-southeast-1.amazonaws.com/paddlepaddle.org:latest
docker stop paddlepaddle.org
docker rm paddlepaddle.org
docker run --name=paddlepaddle.org -d -p 80:8000 --env-file portal.env -v /var/content:/var/content 330323714104.dkr.ecr.ap-southeast-1.amazonaws.com/paddlepaddle.org:latest
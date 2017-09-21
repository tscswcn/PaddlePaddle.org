# PaddlePaddle.org Install Guide

## Run from Docker

##### Clone repo
```
git clone https://github.com/PaddlePaddle/PaddlePaddle.org.git
```

##### Building Image

```
cd <project-dir>
docker build -t paddlepaddle.org .
```

##### Run Docker Image
**Note:**  Please contact product team (Varun, Jeff, Daming, Thuan) for the external_template_dir

###### Create portal.env file with the following variables

```
ENV=development
SECRET_KEY="my_secret_key"
```

###### Run Docker Image
```
docker run -d -p 8000:8000 --env-file portal.env -v <external_template_dir>:/var/content paddlepaddle.org:latest
```

## Local Development

##### Clone repo
```
git clone https://github.com/PaddlePaddle/PaddlePaddle.org.git
```

##### Install compass
```
gem update --system
gem install compass
```

##### Setup virtual environment and install requirements
```
cd paddlepaddle-portal/portal
virtualenv venv
```

##### Add environment variables in venv/bin/activate
```
export ENV="development"
export SECRET_KEY="my_secret_key"
export EXTERNAL_TEMPLATE_DIR="<dir where external templates reside>"
```

##### Source virtualenv
```
source venv/bin/activate
```

##### Install requirements

###### Install gettext
```
[macOS]: brew install gettext
[Ubuntu]: apt-get install gettext
```

```
pip install -r requirements.txt
```

#### Build localization files

```
python manage.py compilemessages -l zh
```

##### Startup server
```
python manage.py runserver
```

##### Open up another terminal and run compass (to rebuild css files)
```
cd <project-dir>/portal
compass watch ./static/
```

#### Manual Deployment

##### Generate temporary login for AWS ECR

```
aws ecr get-login --no-include-email --region ap-southeast-1
```

##### Login to AWS registry from Docker CLI

```
docker login -u AWS -p <AWS_PASSWORD> https://330323714104.dkr.ecr.ap-southeast-1.amazonaws.com
```

##### Build, tag, and push image

```
cd <project-dir>
docker build -t paddlepaddle.org .
docker tag paddlepaddle.org:latest 330323714104.dkr.ecr.ap-southeast-1.amazonaws.com/paddlepaddle.org:latest
docker push 330323714104.dkr.ecr.ap-southeast-1.amazonaws.com/paddlepaddle.org:latest
``` 

##### Login to VM

```
ssh -i ubuntu.pem ubuntu@52.76.173.135
```

##### From VM, login to AWS Registry from Docker CLI, then pull latest image

```
docker login -u AWS -p <AWS_PASSWORD> https://330323714104.dkr.ecr.ap-southeast-1.amazonaws.com
docker pull 330323714104.dkr.ecr.ap-southeast-1.amazonaws.com/paddlepaddle.org:latest
```

##### Deploy Docker image from within VM

```
docker run --name=paddlepaddle.org -d -p 80:8000 --env-file portal.env -v /var/content:/var/content 330323714104.dkr.ecr.ap-southeast-1.amazonaws.com/paddlepaddle.org:latest
```

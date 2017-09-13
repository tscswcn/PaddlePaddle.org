# paddlepaddle-portal

## Setup

### 1) Clone repo
```
git clone git@github.svail.baidu.com:baidu-research/paddlepaddle-portal.git
```

### 2) Install compass
```
gem update --system
gem install compass
```

### 3) Setup virtual environment and install requirements
```
cd paddlepaddle-portal
virtualenv venv
```

### 4) Add environment variables in venv/bin/activate
```
export ENV="development"
export SECRET_KEY="<secret_key>"
export EXTERNAL_TEMPLATE_DIR="<dir where external templates reside>"
```

### 5) Source virtualenv
```
source venv/bin/activate
```

### 5)  Install requirements
```
pip install -r requirements.txt
```

### 5) Startup server
```
python manage.py runserver
```

### 6) Open up another terminal and run compass (to rebuild css files)
```
cd <project-dir>
compass watch portal/static/
```

## Docker

### Building Image

```
cd <project-dir>
docker build -t paddlepaddle-portal .
```

### Run Docker Image

#### 1) Create portal.env file with the following variables

```
ENV=development
SECRET_KEY=<secret_key>
```

#### 2) Run Docker Image
```
docker run -d -p 8000:8000 --env-file portal.env -v <external_template_dir>:/templates paddlepaddle-portal:latest
```

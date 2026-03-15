# Steps to deploy in EC2 with Docker Compose

## Take EC2 instance and add the ports in security groups

- ports are defined in Dockerfile and docker-compose.yml file

```markdown
- add port 8000 for backend
- add port 3000 for frontend
```

## Basic setup and installation

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install docker.io
sudo usermod -aG docker $USER
sudo reboot
sudo apt install docker-compose -y

# check docker and docker-compose
docker --version
docker-compose --version

```

## Clone repo

```bash
git clone https://github.com/ripon1995/grocery-management.git
```

## Setup .env files

```bash
# setup backend env file
cd backend
cp .env.sample .env
# setup frontend env file
cd frontend
cp .env.sample .env
```

## Allow all origins

```markdown
set allow_origins = ["*"] in backend main.py file 
```

## Run the docker-compose file

```bash
# from project root directory
docker-compose up -d --build
```

## Check the docker containers and images and network

```bash
docker images
docker ps -a
docker network ls
docker-compose ps
```
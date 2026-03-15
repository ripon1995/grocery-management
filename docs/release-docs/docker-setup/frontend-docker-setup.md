# DOCKER setup for Monthly Grocery Frontend App

Requirement:

- Create a Dockerfile in frontend/

## 1. Update system & install basics

```bash
# basic linux setup
sudo apt update
sudo apt upgrade -y
# install docker
sudo apt install docker.io
# permission
sudo usermod -aG docker $USER
# reboot
sudo reboot
# check docker 
docker ps -a
```

## 2. Clone the repo

```bash
git clone https://github.com/ripon1995/grocery-management.git
```

## 3. Build docker image

```bash
# navigate to frontend
cd frontend
# build the image in the current directory
docker build -t grocery-frontend .
```

## 4. Run the container

```bash
# option 1 : not dtouch mode
docker run -p 3000:3000 grocery-frontend
# option 2 : dtouch mode
docker run -d --rm -p 3000:5173 grocery-frontend
```

# DOCKER setup for Monthly Grocery Backend App

Requirement:

- Create a Dockerfile in backend/


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
# navigate to backend
cd backend
# build the image in the current directory
docker build -t grocery-backend .
```

## 4. Run the container

```bash
# option 1 : not dtouch mode
docker run -p 8000:8000 grocery-backend
# option 2 : dtouch mode
docker run -d --rm -p 8000:8000 grocery-backend
# option 3 : with a custom name
docker run -d --rm --name grocery-api -p 8000:8000 grocery-backend
```

## 5. Useful commands
```bash
# to stop the container
docker stop grocery-api
# to see the logs
docker logs -f grocery-api
# to enter into it
docker exec -it grocery-api bash
```
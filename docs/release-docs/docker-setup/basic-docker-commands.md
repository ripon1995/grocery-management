# DOCKER Basic Commands That Might Be Useful

# 1. Base commands
## Check status
```bash
# option - 1: running containers
docker ps
# option -2 : all containers
docker ps -a
```

# 2. Image related commands

## Build an image

```bash
# <image name> -> can be anything
# . -> refers the current directory
docker build -t <image_name> .
```

## List images

```bash
docker images
```

## Remove dangling images

```bash
docker image prune
```

## Remove image manually

```bash
docker rmi <image_id>
```


# 3. Container related commands

## Build a container from the image
```bash
# -d -> refers detached mode
# --rm -> refers container will be auto removed when its stopped
# --name <container_name> -> add a specific name to that container
# <image_name> -> refers the image name from which the container will be created
# <host_port> -> refers the port of the host machine like EC2
# <container_port> -> refers the port of the container. Generally in Dockerfile ex -> EXPOSE xxxx
docker run -d --rm --name <container_name> -p <host_port>:<container_port> <image_name>
```
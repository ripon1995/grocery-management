# DOCKER Basic Commands That Might Be Useful

---

# 1. Base commands

## Check status

```bash
# option - 1: running containers
docker ps
# option -2 : all containers
docker ps -a
```

---

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

---

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

---

# 4. Docker compose related commands

- File must be named 'docker-compose.yml' in the root directory.
- Orchestrates multiple containers as a single system.
- Automatically handles internal networking between services.

## Run a docker compose

```bash
# Starts everything in the background (Detached)
docker compose up -d
# Force a rebuild of images before starting (Use after code changes/git pull)
docker-compose up -d --build
```

# View status of all services in the project

```bash
docker compose ps
```

# View live logs of all services

```bash
docker compose logs -f
```

# View only backend logs

```bash
# option 1 : snapshot
docker compose logs backend
# option 2 : will follow the logs
docker compose logs -f backend
```

# View only frontend logs

```bash
# option 1 : snapshot
docker compose logs frontend
# option 2 : will follow the logs
docker compose logs -f frontend
```

---

# Stop Project

```bash
# OPTION 1: Stop and REMOVE containers + networks (Cleanest)
docker compose down

# OPTION 2: Stop/Pause (Keeps containers in 'Exited' state)
docker compose stop

```
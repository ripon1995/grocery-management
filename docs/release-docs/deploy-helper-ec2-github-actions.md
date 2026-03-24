# Steps to deploy in EC2 with Docker Compose with GitHubAction

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
# install docker
sudo apt install docker.io
sudo usermod -aG docker $USER
sudo reboot
# install docker compose
sudo apt-get update
sudo apt-get install docker-compose-plugin -y
mkdir -p ~/.docker/cli-plugins/
curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 -o ~/.docker/cli-plugins/docker-compose
chmod +x ~/.docker/cli-plugins/docker-compose
# check docker and docker-compose
docker --version
docker compose version
```

## Create PR on Branch Main

## Update AWS_KEY & AWS_HOST

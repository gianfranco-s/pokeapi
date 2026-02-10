#!/bin/bash
yum update -y
yum install -y docker curl
systemctl enable docker && systemctl start docker
usermod -aG docker ec2-user

# Install docker compose plugin for all users
# https://docs.docker.com/compose/install/linux/
DOCKER_CLI_PLUGINS_DIR=/usr/local/lib/docker/cli-plugins
sudo mkdir -p $DOCKER_CLI_PLUGINS_DIR
sudo curl -SL https://github.com/docker/compose/releases/download/v2.32.0/docker-compose-linux-x86_64 -o $DOCKER_CLI_PLUGINS_DIR/docker-compose
sudo chmod +x $DOCKER_CLI_PLUGINS_DIR/docker-compose

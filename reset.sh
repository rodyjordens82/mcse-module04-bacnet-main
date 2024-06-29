#!/bin/bash
echo "DELETING ALL DOCKER FILES"

sudo systemctl restart docker.socket docker.service

sudo docker image rm -f $(sudo docker image ls -q)

yes | docker system prune

yes | docker volume rm $(docker volume ls -q)


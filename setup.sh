#!/bin/bash

echo "Starting up the application..."

#1. Create the docker networks
docker network create --subnet=172.20.0.0/24 dbbms
docker network create --subnet=172.20.2.0/24 dbwebapp
docker network create --subnet=192.168.123.0/24 wg-network

#2. Start the MySQL container
docker run -d --name mysql --network dbwebapp --ip 172.20.2.100 -e MYSQL_ROOT_PASSWORD=Pass123 -e MYSQL_USER=beheer -e MYSQL_PASSWORD=Geheim123! -e MYSQL_DATABASE=db mysql:5.7
docker network connect dbbms mysql --ip 172.20.0.100

sleep 3

#3. Build and start the create container
docker build -t createi database/
docker run -d --name create -it --network dbwebapp --ip 172.20.2.102 createi

sleep 1

#4. Build and start the webapp container
docker build -t webappi webapp/
docker run -d --name webapp -it -p 5000:5000 --network dbwebapp --ip 172.20.2.101 webappi

sleep 1

#5. Build and start the controller container
docker build -t controlleri controller/
docker run -d --name controller -it --network dbbms --ip 172.20.0.102 controlleri

sleep 1

#6. Build and start the bms container
docker build -t bmsi bms/
docker run -d --name bms -it --network dbbms --ip 172.20.0.101 bmsi

sleep 1

#7. change network too internal network
#docker network rm dbbms
docker stop controller
docker stop webapp
docker stop bms
docker stop mysql
docker rm create

docker network rm dbbms
docker network rm dbwebapp
docker network disconnect dbbms mysql
docker network disconnect dbbms controller
docker network disconnect dbbms bms
docker network disconnect dbwebapp mysql
docker network disconnect dbwebapp webapp
docker network create --internal --subnet=172.20.0.0/24 dbbms
docker network create --internal --subnet=172.20.2.0/24 dbwebapp

sleep 1

docker network connect dbbms bms --ip 172.20.0.101
docker network connect dbbms controller --ip 172.20.0.102
docker network connect dbbms mysql --ip 172.20.0.100
docker network connect dbwebapp mysql --ip 172.20.2.100
docker network connect dbwebapp webapp --ip 172.20.2.101
docker network connect --ip 192.168.123.2 wg-network webapp
iptables -I DOCKER-USER -i wg0 -d 192.168.123.0/24 -j ACCEPT
cp vpn/wg0.conf /etc/wireguard/
wg-quick up wg0

docker start mysql

sleep 1

docker start webapp
docker start controller

sleep 1

docker start bms

#Done
echo "All services started or already running!"

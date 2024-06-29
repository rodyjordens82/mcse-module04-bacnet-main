#!/bin/bash

# Prompt the user for Docker container names (space-separated)
read -p "Enter Docker container names to stop (space-separated): " container_names

# Split the space-separated input into an array
IFS=' ' read -ra containers <<< "$container_names"

# Iterate through the container names and stop each one
for container in "${containers[@]}"; do
    # Check if the container exists
    if docker ps -a --format '{{.Names}}' | grep -wq "$container"; then
        # Stop the container
        docker stop "$container"
        echo "Container '$container' has been stopped."
    else
        echo "Container '$container' not found."
    fi
done

#Prompt the user to stop the vpn
read -p "Stop the VPN (Y/n): " vpnStop

if [[ "$vpnStop" == "y" || "$vpnStop" == "Y" ]]; then
    wg-quick down wg0
fi

#Prompt the user to make the network devices external
read -p "Network devices external access allowed (Y/n): " networkOpen

if [[ "$networkOpen" == "y" || "$networkOpen" == "Y" ]]; then
    docker stop controller
    docker stop webapp
    docker stop bms
    docker stop mysql

    docker network rm dbbms
    docker network rm dbwebapp
    docker network disconnect dbbms mysql
    docker network disconnect dbbms controller
    docker network disconnect dbbms bms
    docker network disconnect dbwebapp mysql
    docker network disconnect dbwebapp webapp
    docker network create --subnet=172.20.0.0/24 dbbms
    docker network create --subnet=172.20.2.0/24 dbwebapp

    sleep 1

    docker network connect dbbms bms --ip 172.20.0.101
    docker network connect dbbms controller --ip 172.20.0.102
    docker network connect dbbms mysql --ip 172.20.0.100
    docker network connect dbwebapp mysql --ip 172.20.2.100
    docker network connect dbwebapp webapp --ip 172.20.2.101
    docker network connect --ip 192.168.123.2 wg-network webapp

    docker start mysql

    sleep 1

    docker start webapp
    docker start controller

    sleep 1

    docker start bms
fi

#Prompt the user to change all the admin mfa's to the same
read -p "Change all MFA secret too JJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJ (32*J) (Y/n): " secretEasy

if [[ "$secretEasy" == "y" || "$secretEasy" == "Y" ]]; then
    docker exec -it mysql mysql -u beheer -pGeheim123! -e "update db.users set secret_key = 'JJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJ'"
fi

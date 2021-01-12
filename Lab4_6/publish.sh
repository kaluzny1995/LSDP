#!/usr/bin/env bash
sudo docker build -t webspark .
sudo docker tag webspark kaluzny1995/webspark:latest
sudo docker login
sudo docker push kaluzny1995/webspark:latest

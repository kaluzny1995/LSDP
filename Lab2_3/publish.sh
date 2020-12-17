#!/usr/bin/env bash
sudo docker build -t worker .
sudo docker tag worker kaluzny1995/worker:latest
sudo docker login
sudo docker push kaluzny1995/worker:latest

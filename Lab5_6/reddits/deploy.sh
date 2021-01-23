kubectl apply -f rabbitmq.yaml
kubectl apply -f worker.yaml
kubectl apply -f influxdb.yaml
kubectl apply -f mongodb.yaml
kubectl apply -f grafana.yaml
kubectl apply -f redash.yaml
bash deploy.webspark.sh

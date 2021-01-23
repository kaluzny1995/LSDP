bash undeploy.webspark.sh
kubectl delete deploy/redash-deploy sts/postgres-sts svc/postgres svc/redash-svc svc/redis job/redash-job cm/postgres-cm cm/redash-cm pvc/postgres-pvc pv/postgres-pv
kubectl delete deploy/grafana-deploy svc/grafana-svc pvc/grafana-pvc pv/grafana-pv
kubectl delete sts/mongodb-sts svc/mongodb-svc pvc/mongodb-pvc pv/mongodb-pv
kubectl delete sts/influxdb-sts svc/influxdb-svc pvc/influxdb-pvc pv/influxdb-pv
kubectl delete deploy/worker-deploy cm/worker-cm
kubectl delete sts/rabbitmq-sts svc/rabbitmq-svc

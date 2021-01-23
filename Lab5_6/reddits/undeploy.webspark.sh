kubectl delete ing/web-ing
kubectl delete deploy/web-deploy svc/web-redis svc/web-svc cm/web-cm
kubectl delete deploy/spark-deploy svc/spark-worker svc/spark-master pvc/webspark-pvc pv/webspark-pv cm/spark-cm

VU=100

for j in {1..10}
do
  echo "======== VU: $VU and this is round $j ========="
  for i in {1..10}
  do
    cd /home/ansible/load-test-http/http-request/scripts
    # sudo k6 run --vus $VU --duration 5m --out influxdb=http://localhost:8086/k6 ./getProduct.js
    sudo k6 run --vus $VU --duration 5m ./getProduct.js | grep -E "status|http_req_duration|http_reqs|iterations|vus" | tee -a result.txt
    
    sleep 30s
    ssh cfliao@140.119.163.226 "k3s kubectl scale deployment jpetstore-backend-deployment --replicas=0 -n jpetstore"
    ssh cfliao@140.119.163.226 "k3s kubectl scale deployment jpetstore-backend-deployment --replicas=1 -n jpetstore"
    sleep 150s
  done
  VU=$((VU+100))
done

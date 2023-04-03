VU=100

for j in {1..10}
do
  echo "======== VU: $VU and this is round $j ========="
  for i in {1..10}
  do
    cd /home/ansible/load-test-http/http-request/scripts
    # sudo k6 run --vus $VU --duration 5m --out influxdb=http://localhost:8086/k6 ./getProduct.js
    sudo k6 run --vus $VU --duration 5m ./getProduct.js
    
    sleep 30s
    ssh cfliao@140.119.163.226 "k3s kubectl restart deployment jpetstore-backend-deployment -n jpetstore"
    sleep 60s
  done
  VU=$((VU+100))
done


VU=100

for j in {1..10}
do
  echo "======== VU: $VU and this is round $j ========="
  for i in {1..10}
  do
    cd /home/ansible/load-test-http/http-request/scripts
    sudo k6 run --vus $VU --duration 5m --out influxdb=http://localhost:8086/k6 ./getProduct.js
    sleep 30s
  done
  VU=$((VU+100))
done


VU=500

for j in {1..10}
do
  echo "======== VU: $VU and this is round $j ========="
  for i in {1..10}
  do
    # cd /home/brandon/k6
    # docker compose down
    # docker compose up -d grafana influxdb
    # sleep 10s

    cd /home/ansible/load-test-http/http-request/scripts
    # sudo k6 run --vus $VU --duration 5m --out influxdb=http://localhost:8086/k6 ./register.js 
    sudo k6 run --vus $VU --duration 5m ./register.js 
    sleep 10s

    mysql -h 140.119.163.226 --port=30360 -u root -p'brandon' -e 'DELETE FROM jpetstore.ACCOUNT WHERE 1=1;'
    
    ssh cfliao@140.119.163.226 "k3s kubectl restart deployment jpetstore-backend-deployment -n jpetstore"
    sleep 60s
  done
  VU=$((VU+100))
done


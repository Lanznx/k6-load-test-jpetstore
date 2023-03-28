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
    sudo k6 run --vus $VU --duration 5m --out influxdb=http://localhost:8086/k6 ./register.js 
    sleep 30s

    mysql -h 140.119.163.226 --port=30360 -u root -p'brandon' -e 'DELETE FROM jpetstore.ACCOUNT WHERE 1=1;'
  done
  VU=$((VU+100))
done


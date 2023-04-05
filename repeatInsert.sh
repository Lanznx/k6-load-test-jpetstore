VU=300

for j in {1..10}
do
  echo "========== round $j VUs $VU ========== " >> ./output/data.txt
  for i in {1..10}
  do
    # cd /home/brandon/k6
    # docker compose down
    # docker compose up -d grafana influxdb
    # sleep 10s

    cd /home/ansible/load-test-http/http-request/scripts
    # sudo k6 run --vus $VU --duration 5m --out influxdb=http://localhost:8086/k6 ./register.js 
    sudo k6 run --vus $VU --duration 1s ./register.js | grep -E "checks|http_req_duration" | tee -a ./output/data.txt
    sleep 10s

    mysql -h 140.119.163.226 --port=30360 -u root -p'brandon' -e 'DELETE FROM jpetstore.ACCOUNT WHERE 1=1;'
    
    ssh cfliao@140.119.163.226 "k3s kubectl scale deployment jpetstore-backend-deployment --replicas=0 -n jpetstore"
    ssh cfliao@140.119.163.226 "k3s kubectl scale deployment jpetstore-backend-deployment --replicas=1 -n jpetstore"
    sleep 150s
  done
  python3 ./extract.py
  VU=$((VU+100))
done


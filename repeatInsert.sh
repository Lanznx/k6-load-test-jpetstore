ENV_ID=3
VU=100
TIME_RANGE=2
PATH_TO_TXT='./output/data_3.txt'

IP=140.119.163.226

sudo chmod 777 $PATH_TO_TXT

for j in {1..50}
do
  echo "========== round $j VUs $VU ========== " >> $PATH_TO_TXT
  for i in {1..10}
  do
    # cd /home/brandon/k6
    # docker compose down
    # docker compose up -d grafana influxdb
    # sleep 10s

    cd /home/ansible/load-test-http/http-request/scripts
    sudo k6 run --vus $VU --duration 2m ./register.js | grep -E "checks|http_req_duration" | tee -a $PATH_TO_TXT

    mysql -h $IP --port=30360 -u root -p'brandon' -e 'DELETE FROM jpetstore.ACCOUNT WHERE 1=1;'
    mysql -h $IP --port=30360 -u root -p'brandon' -e 'DELETE FROM jpetstore.PROFILE WHERE 1=1;'
    mysql -h $IP --port=30360 -u root -p'brandon' -e 'DELETE FROM jpetstore.SIGNON WHERE 1=1;'
    
    /home/brandon/miniconda3/bin/python ./extract.py $ENV_ID $i $VU $TIME_RANGE $PATH_TO_TXT

    ssh cfliao@$IP "k3s kubectl scale deployment jpetstore-backend-deployment --replicas=0 -n jpetstore"
    ssh cfliao@$IP "k3s kubectl scale deployment jpetstore-backend-deployment --replicas=3 -n jpetstore"
    sleep 150s
  done
  VU=$((VU+100))
done


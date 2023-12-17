source .env

touch $PATH_TO_TXT
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
    /home/brandon/miniconda3/bin/python ./extract.py $ENV_ID $i $VU $TIME_RANGE $PATH_TO_TXT

    mysql -h $REMOTE_MYSQL_HOST --port=$REMOTE_MYSQL_PORT -u $REMOTE_MYSQL_USER -p"$REMOTE_MYSQL_PASSWORD" -e 'DELETE FROM jpetstore.ACCOUNT WHERE 1=1;'
    mysql -h $REMOTE_MYSQL_HOST --port=$REMOTE_MYSQL_PORT -u $REMOTE_MYSQL_USER -p"$REMOTE_MYSQL_PASSWORD" -e 'DELETE FROM jpetstore.PROFILE WHERE 1=1;'
    mysql -h $REMOTE_MYSQL_HOST --port=$REMOTE_MYSQL_PORT -u $REMOTE_MYSQL_USER -p"$REMOTE_MYSQL_PASSWORD" -e 'DELETE FROM jpetstore.SIGNON WHERE 1=1;' 

    ssh $SSH_USER@$SSH_HOST "k3s kubectl scale deployment jpetstore-backend-deployment --replicas=0 -n jpetstore"
    ssh $SSH_USER@$SSH_HOST "k3s kubectl scale deployment jpetstore-backend-deployment --replicas=$SUT_REPLICAS -n jpetstore"
    sleep 150s
  done
  VU=$((VU+100))
done


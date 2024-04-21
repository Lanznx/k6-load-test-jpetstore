source .env

touch $PATH_TO_TXT
sudo chmod 777 $PATH_TO_TXT

for j in {1..7}
do
  if [ $j -eq 1 ]
  then
    TXT_SIZE="16MB"
    SLEEP_TIME=80
    ENV_ID=100
  if [ $j -eq 2 ]
  then
    TXT_SIZE="32MB" 
    SLEEP_TIME=80
    ENV_ID=110
  if [ $j -eq 3 ]
  then
    TXT_SIZE="64MB"
    SLEEP_TIME=80
    ENV_ID=120
  if [ $j -eq 4 ]
  then
    TXT_SIZE="128MB"
    SLEEP_TIME=100
    ENV_ID=130
  if [ $j -eq 5 ]
  then
    TXT_SIZE="256MB"
    SLEEP_TIME=120
    ENV_ID=140
  if [ $j -eq 6 ]
  then
    TXT_SIZE="512MB"
    SLEEP_TIME=200
    ENV_ID=150
  fi

  for i in {1..10}
  echo "========== TXT_SIZE $TXT_SIZE round $i ========== " >> $PATH_TO_TXT
  do
    cd ~/k6-load-test-jpetstore
    ~/miniconda3/bin/python ~/k6-load-test-jpetstore/batch_promql.py $ENV_ID $i $TXT_SIZE 


    mysql -h $REMOTE_MYSQL_HOST --port=$REMOTE_MYSQL_PORT -u $REMOTE_MYSQL_USER -p"$REMOTE_MYSQL_PASSWORD" -e 'DELETE FROM jpetstore.batch WHERE 1=1;' 

    ssh $SSH_USER@$SSH_HOST "k3s kubectl scale deployment jpetstore-backend-deployment --replicas=0 -n jpetstore"
    ssh $SSH_USER@$SSH_HOST "k3s kubectl scale deployment jpetstore-backend-deployment --replicas=$SUT_REPLICAS -n jpetstore"
    
    sleep $SLEEP_TIME
  done
done
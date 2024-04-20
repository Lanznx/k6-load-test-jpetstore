source .env

touch $PATH_TO_TXT
sudo chmod 777 $PATH_TO_TXT

for j in {1..5}
do
  if [ $j -eq 1 ]
  then
    TXT_SIZE="2MB"
  if [ $j -eq 2 ]
  then
    TXT_SIZE="16MB" 
  if [ $j -eq 3 ]
  then
    TXT_SIZE="128MB"
  if [ $j -eq 4 ]
  then
    TXT_SIZE="512MB"
  if [ $j -eq 5 ]
  then
    TXT_SIZE="1024MB"
  fi

  for i in {1..10}
  echo "========== round $j VUs $VU ========== " >> $PATH_TO_TXT
  do
    cd ~/k6-load-test-jpetstore
    curl --location 'http://jpetstore.cerana.tech' --header 'Content-Type: application/json' --data "{\"file_path\": \"./${TXT_SIZE}.txt\"}"

    mysql -h $REMOTE_MYSQL_HOST --port=$REMOTE_MYSQL_PORT -u $REMOTE_MYSQL_USER -p"$REMOTE_MYSQL_PASSWORD" -e 'DELETE FROM jpetstore.batch WHERE 1=1;' 

    ssh $SSH_USER@$SSH_HOST "k3s kubectl scale deployment jpetstore-backend-deployment --replicas=0 -n jpetstore"
    ssh $SSH_USER@$SSH_HOST "k3s kubectl scale deployment jpetstore-backend-deployment --replicas=$SUT_REPLICAS -n jpetstore"
    if [ $TXT_SIZE -eq "2MB" ]
    then
      sleep 30
    if [ $TXT_SIZE -eq "16MB" ]
    then
      sleep 120
    if [ $TXT_SIZE -eq "128MB" ]
    then
      sleep 600
    if [ $TXT_SIZE -eq "512MB" ]
    then
      sleep 2500
    if [ $TXT_SIZE -eq "1024MB" ]
    then
      sleep 5000
    fi
  done
done
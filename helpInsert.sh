source .env

touch $PATH_TO_TXT
sudo chmod 777 $PATH_TO_TXT

for j in {1..50}
do
  echo "========== round $j VUs $VU ========== " >> $PATH_TO_TXT
  for i in {1..10}
  do
    cd ~/k6-load-test-jpetstore
    k6 run --vus $VU --duration 2m ~/k6-load-test-jpetstore/register.js | grep -E "checks|http_req_duration" | tee -a $PATH_TO_TXT

    sleep 150s
  done
  VU=$((VU+100))
done


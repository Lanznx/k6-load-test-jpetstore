import { sleep, check, group } from 'k6'
import http from 'k6/http'

export const options = {
  ext: {
    loadimpact: {
      distribution: { 'amazon:us:ashburn': { loadZone: 'amazon:us:ashburn', percent: 100 } },
      apm: [],
    },
  },
  thresholds: {},
  scenarios: {
    Scenario_1: {
      executor: 'constant-vus',
      vus: 100,
      exec: 'addToCart',
      duration: '5m',
    },
  },
}



export function addToCart() {
  let response
  const data = generateRandomString(10)
  group('addToCart', function () {
    response = http.get( 
      'http://140.119.163.226:32635/jpetstore/actions/Cart.action?addItemToCart=&workingItemId=EST-6',
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'Cookie': 'JSESSIONID=A3F68A89BB83EA009ACD5BB42F01C0D1'
        },
      }
    )
    check(response, { 'status equals 200': response => response.status.toString() === '200' })
  })

  // Automatically added sleep
  sleep(1)
}

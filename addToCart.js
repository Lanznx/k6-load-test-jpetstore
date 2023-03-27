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
      vus: 1,
      exec: 'addToCart',
      duration: '5s',
    },
  },
}



export function addToCart() {
  let response
  group('addToCart', function () {
    response = http.get(
      'http://jpetstore.cerana.tech/jpetstore/actions/Cart.action?addItemToCart=&workingItemId=EST-6',
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'Cookie': 'JSESSIONID=A3F68A89BB83EA009ACD5BB42F01C0D1'
        },
      }
    )
    check(response, {
      'is inserted': (r) => r.body.includes(' name="EST-6" type="text" value='),
      'is status 200': (r) => r.status === 200,
    }
    );
  })

  // Automatically added sleep
  sleep(1)
}

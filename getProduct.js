import { parseHTML } from 'k6/html';
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
      exec: 'GetProduct',
    },
  },
}



export default function GetProduct() {
  let response
  group('GetProduct', function () {
    response = http.get( 
      'http://jpetstore.cerana.tech/jpetstore/actions/Catalog.action?viewCategory=&categoryId=CATS',
    )
    check(response, { 'status equals 200': response => response.status.toString() === '200' })
    const doc = parseHTML(response.body)
    const catName = doc.find('#Catalog > table > tbody > tr:nth-child(2) > td:nth-child(2)').text()
    check(catName, { 'catName equals Persian': catName => catName === 'Persian' })
  })

  // Automatically added sleep
  sleep(1)
}



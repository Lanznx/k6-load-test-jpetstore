import { sleep, check, group } from 'k6';
import http from 'k6/http';

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
      exec: 'Register',
    },
  },
};

export default function Register() {
  let response;
  const data = generateRandomString();
  group('Register', function () {
    response = http.post(
      'http://jpetstore.cerana.tech/jpetstore/actions/Account.action',
      `username=${data}&password=j2ee&repeatedPassword=j2ee&account.firstName=${data}&account.lastName=${data}&account.email=${data}@example.com&account.phone=123-456-7890&account.address1=123 Main St&account.address2=Apt 4&account.city=Anytown&account.state=Anystate&account.zip=12345&account.country=USA&account.languagePreference=english&account.favouriteCategoryId=FISH&newAccount=Save Account Information`,
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      }
    );
    check(response, { 'status is 200': (r) => r.status === 200 });
  });

  // Automatically added sleep
  sleep(1);
}

function generateRandomString() {
  // Fixed part of the username
  const fixedPart = 'User_';

  // Random part of the username
  var randomPart = '';
  var characters = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ';
  var charactersLength = characters.length;
  for (var i = 0; i < 7; i++) {
    randomPart += characters.charAt(Math.floor(Math.random() * charactersLength));
  }

  return fixedPart + randomPart;
}

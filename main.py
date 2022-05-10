from selenium import webdriver
import requests
import time
import datetime
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

chrome_options = Options()
chrome_options.add_argument('--headless')

TARGET_PAGE_URL = 'https://czech-craft.eu/server/epes/vote/'
CAPTCHA_KEY = "6LdG2UkUAAAAALt2hHRqE7k0-9GR7XKYJKGaiqC6"

with open("api_key.txt", "r") as r:
    CAPTCHA_API_KEY = r.read()

CAPTCHA_DATA = {
    "method": "userrecaptcha",
    "googlekey": CAPTCHA_KEY,
    "key": CAPTCHA_API_KEY,
    "pageurl": TARGET_PAGE_URL,
    "json": 1
}

print('enter your username below:')
USERNAME = input()

webdriver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

while True:
    try:
        # start chrome client
        webdriver.get(TARGET_PAGE_URL)

        # get cookies from page
        ccs = webdriver.get_cookie('ccs')['value']
        session = webdriver.get_cookie('session')['value']

        # pass captcha to 2captcha for solving
        response = requests.post('https://2captcha.com/in.php', data=CAPTCHA_DATA)
        request_id = response.json()['request']

        captcha_url = f"https://2captcha.com/res.php?key={CAPTCHA_API_KEY}&action=get&id={request_id}&json=1"

        print(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] voting for "{USERNAME}" every 2 hours')

        solved = False
        while not solved:
            # retrieve solved captcha
            captcha_response = requests.get(captcha_url)
            if captcha_response.json()['status'] == 0:
                print(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] [{captcha_response.json()["status"]}] '
                      f'didnt solve captcha, retrying')
                time.sleep(3)
            else:
                key = captcha_response.json()['request']
                solved = True

                headers = {
                    'content-type': 'application/x-www-form-urlencoded',
                    'cookie': f'ccs={ccs}; session={session}',
                    'referer': 'https://czech-craft.eu/server/epes/vote/',
                    'user-agent': 'Mozilla/5.0'
                                  ' (Windows NT 10.0; Win64; x64)'
                                  ' AppleWebKit/537.36 (KHTML, like Gecko)'
                                  ' Chrome/100.0.4896.127 Safari/537.36'
                }

                gettoken = f'return document.getElementById("csrf_token").value;'
                csrf_token = webdriver.execute_script(gettoken)

                vote_data = {
                    'username': USERNAME,
                    'privacy': 'y',
                    'g-recaptcha-response': key,
                    'csrf_token': csrf_token
                }

                response = requests.post(TARGET_PAGE_URL, data=vote_data, headers=headers)
                print(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] [{captcha_response.json()["status"]}] '
                      f'success solving captcha')
                print(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]'
                      f' waiting 2 hours before submitting another request')
                time.sleep(7200)  # sleep for 2 hours
    except Exception as e:
        print(e)
        print(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]'
              f' an exception occurred, trying again in 20 seconds')
        time.sleep(20)

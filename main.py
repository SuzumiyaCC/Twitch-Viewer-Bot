import os
import json
import time
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver

PROXY_FILE = os.getenv('PROXY_FILE', '/home/a.zubrev/proxy/proxy.json')
CHANNEL = os.getenv('CHANNEL', 'kichi779')
VIEWERS = int(os.getenv('VIEWERS', '1'))


def load_proxies(path):
    with open(path, 'r') as f:
        data = json.load(f)
    return data


def start_viewer(proxy):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.add_argument('--disable-logging')
    chrome_options.add_argument('--log-level=3')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--mute-audio')
    chrome_options.add_argument('--disable-dev-shm-usage')
    extension_path = 'adblock.crx'
    if os.path.exists(extension_path):
        chrome_options.add_extension(extension_path)
    chrome_options.add_argument(f"--proxy-server={proxy['type']}://{proxy['ip']}:{proxy['port']}")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(f"https://www.twitch.tv/{CHANNEL}")
    return driver


def main():
    proxies = load_proxies(PROXY_FILE)
    drivers = []
    with ThreadPoolExecutor(max_workers=VIEWERS) as executor:
        for i in range(VIEWERS):
            proxy = proxies[i % len(proxies)]
            drivers.append(executor.submit(start_viewer, proxy))
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        for driver_future in drivers:
            try:
                driver_future.result().quit()
            except Exception:
                pass


if __name__ == '__main__':
    main()

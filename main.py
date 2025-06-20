import os
import json
import time
import logging
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver

PROXY_FILE = os.getenv('PROXY_FILE', '/home/a.zubrev/proxy/proxy.json')
CHANNEL = os.getenv('CHANNEL', 'kichi779')
VIEWERS = int(os.getenv('VIEWERS', '1'))
LOG_FILE = os.getenv('LOG_FILE', 'bot.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def load_proxies(path):
    with open(path, 'r') as f:
        data = json.load(f)
    return data


def start_viewer(proxy):
    logger.info(
        "Starting viewer with proxy %s://%s:%s",
        proxy.get('type'), proxy.get('ip'), proxy.get('port')
    )
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.add_argument('--disable-logging')
    chrome_options.add_argument('--log-level=3')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--mute-audio')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--no-sandbox')
    extension_path = 'adblock.crx'
    if os.path.exists(extension_path):
        chrome_options.add_extension(extension_path)
    chrome_options.add_argument(f"--proxy-server={proxy['type']}://{proxy['ip']}:{proxy['port']}")
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(f"https://www.twitch.tv/{CHANNEL}")
        logger.info("Viewer launched for channel %s", CHANNEL)
        return driver
    except Exception:
        logger.exception(
            "Failed to launch viewer with proxy %s://%s:%s",
            proxy.get('type'), proxy.get('ip'), proxy.get('port')
        )
        raise


def main():
    proxies = load_proxies(PROXY_FILE)
    logger.info(
        "Loaded %d proxies from %s", len(proxies), PROXY_FILE
    )
    logger.info(
        "Launching %d viewers for channel %s", VIEWERS, CHANNEL
    )
    drivers = []
    with ThreadPoolExecutor(max_workers=VIEWERS) as executor:
        for i in range(VIEWERS):
            proxy = proxies[i % len(proxies)]
            drivers.append(executor.submit(start_viewer, proxy))
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("Stopping viewers...")
        for driver_future in drivers:
            try:
                driver_future.result().quit()
            except Exception:
                logger.exception("Error while closing viewer")


if __name__ == '__main__':
    main()

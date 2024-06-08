from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
import asyncio, re

options = webdriver.FirefoxOptions()
options.add_argument("--headless")
options.binary_location = "/usr/bin/firefox"
options.set_preference("javascript.enabled", True)
options.set_preference('network.dns.disableIPv6', True)

r = re.compile(
      r'^(?:http)s?://'
      r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
      r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
      r'(?::\d+)?'
      r'(?:/?|[/?]\S+)$', re.IGNORECASE)

async def take_screenshot(url):
    if not re.match(r, url):
        return False
    try:
        driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)
        driver.get(url)
        print("Connected !")
        driver.implicitly_wait(10)
        driver.save_screenshot("team_score.png")
        driver.quit()
        return True
    
    except Exception as e:
        print(e)
        driver.quit()
        return False
        

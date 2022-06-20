import os
import datetime
import time
import json
import random

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException

from webdriver import get_webdriver
from elem_module import Elem

from helper.utilities import get_config


class TwitterCrawlingBot:

    BASE_URL = 'https://twitter.com'

    def __init__(self, headless: bool):
        self.webdriver = get_webdriver(headless)
        self.__set_login_config()
        self.cookies_jar = f'{self.username}.json'

    def __set_login_config(self):
        config = get_config('twitter')
        self.username = config.get('username')
        self.password = config.get('password')
        self.name = config.get('name')

    def __random_waiting(self, secs: int = 10):
        secs = 0 if secs-5 < 0 else secs
        wait = random.randint(secs-5, secs)
        time.sleep(wait)
    
    def get(self, url: str):
        try:
            self.webdriver.get(url)
            self.__random_waiting(5)
        except TimeoutException as e:
            print(datetime.datetime.now(), 'TimeoutException, try again...')
            self.webdriver.refresh()
            self.__random_waiting(5)
            self.webdriver.get(url)
            self.__random_waiting(5)
    
    def __exists(self, xpath: str):
        elem = self.webdriver.find_elements(By.XPATH, xpath)
        if len(elem) > 0:
            return True
        else:
            return False
    
    def __locate(self, xpath: str):
        if self.__exists(xpath):
            elem = self.webdriver.find_element(By.XPATH, xpath)
            return Elem(elem)
    
    def loop_locate(self, xpath: str):
        list_ = list()
        if self.__exists(xpath):
            elems = self.webdriver.find_elements(By.XPATH, xpath)
            for elem in elems:
                obj = Elem(elem)
                list_.append(obj)
            return list_
    
    def scroll(self, up: bool, px: int):
        if up:
            self.webdriver.execute_script(f'window.scroll(0, -{px});')
        else:
            self.webdriver.execute_script(f'window.scroll(0, {px});')
        self.__random_waiting()
    
    def scroll_bottom(self):
        self.webdriver.execute_script('window.scroll(0, document.body.scrollHeight);')
        self.__random_waiting()
    
    def get_current_url(self) -> str:
        return self.webdriver.current_url
    
    def quit(self):
        self.webdriver.quit()

    def __get_cookies(self):
        self.cookies = self.webdriver.get_cookies()
    
    def __store_cookies(self):
        data = dict()
        data['cookies'] = list()
        for cookie in self.cookies:
            data['cookies'].append(cookie)
        with open(self.cookies_jar, 'w') as f:
            json.dump(data, f)
    
    def store_cookies(self):
        self.__get_cookies()
        self.__store_cookies()
        
    def prepare_cookies(self):
        print('Preparing cookies.')
        with open(self.cookies_jar) as f:
            data = json.load(f)
            for cookie in data.get('cookies'):
                self.webdriver.add_cookie(cookie)
        self.webdriver.refresh()

    def __input_login_info(self):
        if self.__exists('//input[@autocomplete="username"]'):
            self.__locate('//input[@autocomplete="username"]').input(self.username)
            self.__locate('//input[@autocomplete="username"]').send_keys(Keys.ENTER)

        elif self.__exists('//input[@name="password"]'):
            self.__locate('//input[@name="password"]').input(self.password)
            self.__locate('//input[@name="password"]').send_keys(Keys.ENTER)
        
        elif self.__exists('//input[@autocomplete="on" and not(@name="password")]'):
            self.__locate('//input[@autocomplete="on" and not(@name="password")]').input(self.name)
            self.__locate('//input[@autocomplete="on" and not(@name="password")]').send_keys(Keys.ENTER)

        self.__random_waiting()
        if self.__exists('//a[@aria-label="Profile"]'):
            return True
        else:
            return self.__input_login_info()
    
    def is_logged_in(self):
        self.webdriver.get(self.__class__.BASE_URL)
        self.__random_waiting()
        if self.__exists('//a[@aria-label="Profile"]'):
            return True
        else:
            self.webdriver.get(f'{self.__class__.BASE_URL}/i/flow/login')
            self.__random_waiting(10)
            return self.__input_login_info()
    
    def login(self) -> bool:
        self.webdriver.get(self.__class__.BASE_URL)
        self.__random_waiting()
        if os.path.isfile(self.cookies_jar):
            self.prepare_cookies()
            self.__random_waiting()
        if self.is_logged_in():
            print('Login!')
            self.store_cookies()
            return True
        return False

    def __set_trends_location(self, location: str):
        exploreLocations = '//a[@data-testid="exploreLocations"]'
        if self.__locate(exploreLocations) is None:
            self.__locate('//label[@data-testid="currentLocation"]//input').click()
        self.webdriver.get(f'{self.__class__.BASE_URL}/settings/trends/location')
        self.__locate('//input[@data-testid="locationSearchBox"]').input(location)
        ctr = 0
        while self.__locate('(//div[@aria-labelledby="modal-header"]/div/div/div/div[3]//div[@role="button"])[last()]') is None:
            self.__random_waiting()
            print(ctr)
            ctr += 1
            if ctr >= 10:
                self.__locate('//input[@data-testid="locationSearchBox"]').send_keys(Keys.BACK_SPACE)
                self.__locate('//input[@data-testid="locationSearchBox"]').input(location[-1])
        self.__locate('(//div[@aria-labelledby="modal-header"]/div/div/div/div[3]//div[@role="button"])[last()]').click()
        return True

    def __set_trends_personalization(self, personalization: bool):
        checked_status = self.__locate("//input[@aria-describedby='CHECKBOX_2_LABEL']").get_source('checked')
        if personalization == True:
            if checked_status == True:
                return True
        else:
            if checked_status == False or checked_status is None:
                return True
            else:
                self.__locate('//div[@aria-labelledby="CHECKBOX_2_LABEL"]/div').click()
                return self.__set_trends_personalization(personalization)

    def set_trends(self, location: str = None, personalization: bool = False):
        self.webdriver.get(f'{self.__class__.BASE_URL}/settings/trends')
        self.__random_waiting()
        if self.__set_trends_personalization(personalization):
            if self.__set_trends_location(location):
                return

    def crawl_trends(self):
        self.webdriver.get(f'{self.__class__.BASE_URL}/i/trends')
        self.__random_waiting()
        xpath = '//div[@aria-label="Timeline: Trends"]/div/div//div[@data-testid="trend"]'
        if self.__exists(xpath):
            trends = self.loop_locate(xpath)
            return trends

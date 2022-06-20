from datetime import datetime
import random
import time
from selenium.common.exceptions import StaleElementReferenceException

class Elem:

    def __init__(self, elem):
        self.elem = elem
        self.ts = datetime.utcnow().strftime(r'%Y-%m-%d %H:%M:%S.%f')
    
    def click(self):
        self.elem.click()
    
    def get_source(self, attr: str = 'outerHTML'):
        source = None
        try:
            source = self.elem.get_attribute(attr)
        except StaleElementReferenceException as e:
            print(e)
        finally:
            return source
    
    def input(self, val: str):
        for ctr in range(len(val)):
            alph = val[ctr]
            self.elem.send_keys(alph)
            wait = random.randint(0, 15) / 10
            time.sleep(wait)
    
    def send_keys(self, key):
        self.elem.send_keys(key)
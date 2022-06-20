from selenium import webdriver

def get_webdriver(geckodriver: str = None, logpath: str = None, headless: bool = False):
    if geckodriver is not None:
        geckodriver = '../geckodriver'
    if logpath is not None:
        logpath = 'geckodriver.log'
    profile = webdriver.FirefoxProfile()
    profile.set_preference('intl.accept_languages', 'en-US, en')
    options = webdriver.FirefoxOptions()
    options.headless = headless
    driver = webdriver.Firefox(executable_path=geckodriver, log_path=logpath, firefox_profile=profile, options=options)
    driver.set_page_load_timeout(600)
    return driver
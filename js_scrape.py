from selenium import webdriver

options = webdriver.ChromeOptions()

# tell selenium to use the dev channel version of chrome
options.binary_location = '/usr/bin/chrome'

options.add_argument('headless')

# set the window size
options.add_argument('window-size=1200x600')

# initialize the driver
driver = webdriver.Chrome(chrome_options=options)
from .sherdog import sherdog
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary


binary = FirefoxBinary(r'C:\Program Files\Mozilla Firefox\firefox.exe')
ffprofile = webdriver.FirefoxProfile()

driver = webdriver.Firefox(firefox_profile=ffprofile,firefox_binary=binary)
umatrix = r"E:\ff_addons\umatrix-1.3.16-an+fx.xpi"

x = sherdog(driver,umatrix)
x.downloadAllCardsInfo()

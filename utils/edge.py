import logging
import os
from time import sleep

from selenium import webdriver
from selenium.webdriver.edge import service
from selenium.webdriver.edge.options import Options
from logging.handlers import TimedRotatingFileHandler
from selenium.webdriver.remote.remote_connection import LOGGER


LOGGER.setLevel(logging.WARNING)


def get_web_image(url, pic_name):
    # 设置chrome开启的模式，headless就是无界面模式
    # 一定要使用这个模式，不然截不了全页面，只能截到你电脑的高度
    options = Options()
    options.add_argument('headless')
    service.log_path = "NUL"
    driver = webdriver.Edge(options=options,service=service)

    # 控制浏览器写入并转到链接
    driver.get(url)
    sleep(1)
    # 接下来是全屏的关键，用js获取页面的宽高，如果有其他需要用js的部分也可以用这个方法
    width = driver.execute_script("return document.documentElement.scrollWidth")
    height = driver.execute_script("return document.documentElement.scrollHeight")
    print(width, height)
    # 将浏览器的宽高设置成刚刚获取的宽高
    driver.set_window_size(width, height)
    sleep(1)
    # 截图并关掉浏览器
    driver.save_screenshot(pic_name)
    driver.close()
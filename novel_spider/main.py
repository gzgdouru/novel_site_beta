from scrapy.cmdline import execute
import sys, os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

execute(["scrapy", "crawl", "biquge"])

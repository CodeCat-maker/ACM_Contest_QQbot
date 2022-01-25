import requests
import re
import json
import pprint
import os
import time
from lxml import etree
from web_operation.operation import *


# TODO 获取力扣比赛列表
def get_contest():
    pass


# TODO 获取力扣分数
def get_usr_rank(name):
    pass



if __name__ == '__main__':
    pprint.pprint(get_html("https://leetcode-cn.com/contest/"))
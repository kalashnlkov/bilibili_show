"""
上海·BilibiliWorld 2023 购票
vip会员票
仅支持购买单张票，并且为  默认购票人  买票
！！！！成功率低，并且不确保准确！！！
阿b的二刺猿们设计的网页，当某种票卖完后，会被冷却退位，然后把排在它后面的票递补上来，此时则不可确保购票类型的准确性。

v1.1 加入了目标购票类型
"""
import datetime
import time
import pyttsx3
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

engine = pyttsx3.init()

# BW 2023
buy_url = "https://show.bilibili.com/platform/detail.html?id=73710&from=pc_ticketlist"

# test url
# buy_url = "https://show.bilibili.com/platform/detail.html?id=74576&from=pc_ticketlist"
selectable_btn_cln = ["selectable-option"]
# day  = "8月26日"
day  = "7月22日"
tick = "VIP"

print(day)
# 设置购票的日期
days_xpath = f"/html/body/div/div[2]/div[2]/div[2]/div[2]/div[4]/ul[1]/li[2]/div"

# 在这里设置购票的种类
#
ticks_xpath = f"/html/body/div/div[2]/div[2]/div[2]/div[2]/div[4]/ul[2]/li[2]/div"

buy_xpath = f"/html/body/div[1]/div[2]/div[2]/div[2]/div[2]/div[4]/div[2]/div[1]"

if not days_xpath or not ticks_xpath:
    raise Exception("day/tick xpath incorrect", days_xpath, ticks_xpath)

# 加载配置文件
with open('./config.json', 'r') as f:
    config = json.load(f)


# FIXME: can't terminate when CTRL-C. might a subprocess and signal handler will help?
def voice(message):
    engine.setProperty('volume', 1.0)
    while True:
        engine.say(message)
        engine.runAndWait()
        time.sleep(1)

# 设置抢购时间
TargetTime = "2013-10-3 8:00:00.00000000"

WebDriver = webdriver.Firefox()
wait = WebDriverWait(WebDriver, 0.5)
if len(config["bilibili_cookies"]) == 0:
    # 输入目标购买页面
    WebDriver.get(
        buy_url)
    WebDriver.maximize_window()
    time.sleep(1)
    WebDriver.find_element(By.CLASS_NAME, "nav-header-register").click()
    print("请登录")
    while True:
        try:
            WebDriver.find_element(By.CLASS_NAME, "nav-header-register")
        except:
            break
    time.sleep(5)
    config["bilibili_cookies"] = WebDriver.get_cookies()
    with open('./cookie.json', 'w') as f:
        json.dump(config, f, indent=4)
else:
    WebDriver.get(
        buy_url)  # 输入目标购买页面
    for cookie in config["bilibili_cookies"][0]: 
        my_cookie = {
            'domain': cookie['domain'],
            'name': cookie['name'],
            'value': cookie['value'],
            'path': cookie['path'],
        }
        if 'expiry' in cookie:
            cookie['expiry'] = cookie['expiry']
        if 'httpOnly' in cookie:
            cookie['httpOnly'] = cookie['httpOnly']
        if 'sameSite' in cookie:
            cookie['sameSite'] = cookie['sameSite']
        if 'secure' in cookie:
            cookie['secure'] = cookie['secure']

        WebDriver.add_cookie(
            my_cookie
        )
        WebDriver.maximize_window()

while True:
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    print(now + "     " + TargetTime)
    if now >= TargetTime:
        WebDriver.refresh()
        break
# 确定购票日期

def click_target_btn(wd: webdriver.Firefox, par_xpath, target_patt, target_cln=selectable_btn_cln, fuzz=False, click=True):
    eles = wd.find_elements(By.XPATH, par_xpath)
    if fuzz:
        targets = [ ele for ele in eles if target_patt in ele.text]
    else:
        targets = [ ele for ele in eles if target_patt ==  ele.text]

    if len(targets) == 0:
        print("not that one? ", target_patt, [ele.text for ele in targets])
        return False
    print([t.text for t in targets])
    print(targets[0].get_attribute("class"))
    clns = targets[0].get_attribute("class").split(" ")
    print(targets[0].text, clns)
    checker = [x for x in target_cln if x not in clns]
    if len(checker) != 0 or "unable" in clns:
    # if (target_cln not in  clns or "unable" in clns):
        print("%s 's class %s unselectable" % (targets[0].text, clns))
        return False
    if "售罄" in targets[0].text:
        print("%s sold out..." % target_patt)
        return False
    try:
        if click:
            targets[0].click()
            return True
        else:
            return targets[0]
    except Exception as e:
        print(e)
        return False

def buy_tick(wd: webdriver.Firefox):   
    while True:
        wd.refresh()
        time.sleep(1)
        if not click_target_btn(wd, days_xpath, day):
            print("day fail", day)
            continue

        if not click_target_btn(wd, ticks_xpath, tick, fuzz=True):
            print("tick fail!", tick)
            continue

        if not click_target_btn(wd, buy_xpath, "立即购票", ["product-buy", "enable"]):
            print("click buy fail")
            continue

        break

buy_tick(WebDriver)
element = None
while element is None:
    try:
        element = WebDriver.find_element(By.CLASS_NAME, "confirm-paybtn.active")
    except:
        continue
element.click()
print("订单创建完成，请在10分钟内付款")
voice('傻逼B站')
# 语音提醒时间
time.sleep(60)
# while True:
#     try:  # 确认协议按钮iki
#         quereng_button = WebDriver.find_elements(By.XPATH,"/html/body/div/div[2]/div/div[5]/div[1]/div/span[1]").click()
#         # 确认支付按钮
#         quereng_zhifu_button = WebDriver.find_elements(By.XPATH, "/html/body/div/div[2]/div/div[5]/div[2]").click()
#         print("该付款了")
#     except:
#         continue
time.sleep(230722)

import os
import re
import sys
import time
import asyncio
import random
import httpx
import datetime
from log import Log
from other_operation import random_qcjj
from oj_api import atc_api, cf_api, nc_api, lc_api
from mirai.models import NewFriendRequestEvent
from mirai import Startup, Shutdown, MessageEvent
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from mirai_extensions.trigger import HandlerControl, Filter
from mirai import Mirai, WebSocketAdapter, FriendMessage, GroupMessage, At, Plain, MessageChain, Image

sys.stdout = Log.Logger()  # 定义log类
sys.stderr = Log.Logger()
scheduler = AsyncIOScheduler()
API_KEY = 'SWeKQBWfoYiQFuZSJ'

LAST_CF_TIME = 0
LAST_CF_CONTEST_INFO, LAST_CF_CONTEST_BEGIN_TIME, LAST_CF_CONTEST_DURING_TIME = asyncio.run(cf_api.get_contest())

LAST_ATC_TIME = 0
LAST_ATC_CONTEST_INFO = asyncio.run(atc_api.get_contest_lately())

LAST_NC_TIME = 0
LAST_NC_CONTEST_INFO, LAST_NC_CONTEST_BEGIN_TIME = asyncio.run(nc_api.get_contest())

LAST_LC_TIME = 0
LAST_LC_CONTEST_INFO, LAST_LC_CONTEST_BEGIN_TIME = asyncio.run(lc_api.get_contest())

print(LAST_CF_CONTEST_INFO)
print(LAST_CF_CONTEST_BEGIN_TIME)
print(LAST_CF_CONTEST_DURING_TIME)


async def query_now_weather(city: str) -> str:
    """查询天气数据。"""
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f'https://api.seniverse.com/v3/weather/now.json', params={
                'key': API_KEY,
                'location': city,
                'language': 'zh-Hans',
                'unit': 'c',
            })
            time.sleep(0.5)
            resp.raise_for_status()
            data = resp.json()
            return f'当前{data["results"][0]["location"]["name"]}天气为' \
                   f'{data["results"][0]["now"]["text"]}，' \
                   f'气温{data["results"][0]["now"]["temperature"]}℃。'
        except (httpx.NetworkError, httpx.HTTPStatusError, KeyError):
            return f'抱歉，没有找到{city}的天气数据。'


async def query_today_contest():
    global LAST_CF_CONTEST_INFO, LAST_LC_CONTEST_INFO, LAST_ATC_CONTEST_INFO, LAST_NC_CONTEST_INFO, LAST_LC_CONTEST_INFO

    res = ""

    mon = datetime.datetime.now().month
    day = datetime.datetime.now().day

    print(LAST_CF_CONTEST_INFO)
    print(LAST_LC_CONTEST_INFO)
    print(LAST_ATC_CONTEST_INFO[0])
    print(LAST_NC_CONTEST_INFO)
    print(LAST_LC_CONTEST_INFO[0][0])

    # CF
    if time.localtime(LAST_CF_CONTEST_BEGIN_TIME).tm_mon == mon and time.localtime(
            LAST_CF_CONTEST_BEGIN_TIME).tm_mday == day:
        print(1)
        res += (LAST_CF_CONTEST_INFO + '\n\n')

    # ATC
    if LAST_ATC_CONTEST_INFO[1].month == mon and LAST_ATC_CONTEST_INFO[1].day == day:
        print(2)
        res += (LAST_ATC_CONTEST_INFO[0] + '\n\n')

    # NC
    if time.localtime(LAST_NC_CONTEST_BEGIN_TIME).tm_mon == mon and time.localtime(
            LAST_NC_CONTEST_BEGIN_TIME).tm_mday == day:
        print(3)
        res += (LAST_NC_CONTEST_INFO + '\n\n')

    # LC
    if time.localtime(LAST_LC_CONTEST_BEGIN_TIME).tm_mon == mon and time.localtime(LAST_LC_CONTEST_BEGIN_TIME).tm_mday == day:
        print(4)
        res += (LAST_LC_CONTEST_INFO[0][0] + '\n\n')

    print(res)

    return res


if __name__ == '__main__':
    bot = Mirai(
        qq=3409201437,  # 改成你的机器人的 QQ 号
        adapter=WebSocketAdapter(
            verify_key='yirimirai', host='localhost', port=8080
        )
    )
    hdc = HandlerControl(bot)  # 事件接收器


    @bot.on(Startup)
    def start_scheduler(_):
        scheduler.start()  # 启动定时器


    @bot.on(Shutdown)
    def stop_scheduler(_):
        scheduler.shutdown(True)  # 结束定时器


    @bot.on(NewFriendRequestEvent)
    async def allow_request(event: NewFriendRequestEvent):  # 有新用户好友申请就自动通过
        await bot.allow(event)


    @bot.on(MessageEvent)
    async def on_friend_message(event: MessageEvent):
        if str(event.message_chain) == '你好':
            await bot.send(event, 'Hello, World!')


    @bot.on(MessageEvent)
    async def show_list(event: MessageEvent):  # 功能列表展示
        msg = "".join(map(str, event.message_chain[Plain]))
        if msg == ".help":
            if isinstance(event, GroupMessage):
                await bot.send(event, [At(event.sender.id), "\n查询天气 城市 -> 查询城市实时天气"
                                                            "\n查询cf分数 id -> 查询对应id的 cf 分数"
                                                            "\ncf -> 近场 cf 比赛"
                                                            "\natc -> 最新的AtCoder比赛"
                                                            "\n牛客 -> 最新的牛客比赛"
                                                            "\nlc -> 最新的力扣比赛"
                                                            "\ntoday -> 查询今天比赛"
                                                            "\n来只清楚 -> 随机qcjj"
                                                            "\nsetu/涩图 -> 涩图"
                                                            "\nbug联系 -> 1095490883"])
            else:
                await bot.send(event, ["\n查询天气 城市 -> 查询城市实时天气"
                                                            "\n查询cf分数 id -> 查询对应id的 cf 分数"
                                                            "\ncf -> 近场 cf 比赛"
                                                            "\natc -> 最新的AtCoder比赛"
                                                            "\n牛客 -> 最新的牛客比赛"
                                                            "\nlc -> 最新的力扣比赛"
                                                            "\ntoday -> 查询今天比赛"
                                                            "\n来只清楚 -> 随机qcjj"
                                                            "\nsetu/涩图 -> 涩图"
                                                            "\nbug联系 -> 1095490883"])


    @bot.on(MessageEvent)
    async def echo(event: MessageEvent):  # 复读机
        msg = "".join(map(str, event.message_chain[Plain])).strip()
        m = re.match(r'^echo\s*(\w+)\s*$', msg)
        if m and At(bot.qq) in event.message_chain:
            await bot.send(event, msg)


    @bot.on(MessageEvent)
    async def on_group_message(event: MessageEvent):  # 返回
        if At(bot.qq) in event.message_chain and len("".join(map(str, event.message_chain[Plain]))) == 0:
            await bot.send(event, [At(event.sender.id), '你在叫我吗？'])


    @bot.on(MessageEvent)
    async def weather_query(event: MessageEvent):  # 天气查询
        # 从消息链中取出文本
        msg = "".join(map(str, event.message_chain[Plain]))
        # 匹配指令
        m = re.match(r'^查询天气\s*(\w+)\s*$', msg.strip())
        if m:
            print("cha xun")
            # 取出指令中的地名
            city = m.group(1)
            print(city)
            await bot.send(event, '查询中……')
            # 发送天气消息
            await bot.send(event, await query_now_weather(city))


    # CF

    @bot.on(MessageEvent)
    async def query_cf_rank(event: MessageEvent):  # 查询对应人的分数
        msg = "".join(map(str, event.message_chain[Plain]))

        m = re.match(r'^查询CF分数\s*([\w.-]+)\s*$', msg.strip())
        if m is None:
            m = re.match(r'^查询cf分数\s*([\w.-]+)\s*$', msg.strip())
        if m is None:
            m = re.match(r'^查询(.*)的CF分数$', msg.strip())
        if m is None:
            m = re.match(r'^查询(.*)的cf分数$', msg.strip())

        if m:
            name = m.group(1)
            # print(name)

            global LAST_CF_TIME
            if int(time.time()) - LAST_CF_TIME < 5:  # 每次询问要大于5秒
                await bot.send(event, '不要频繁查询，请{}秒后再试'.format(LAST_CF_TIME + 5 - int(time.time())))
                return

            LAST_CF_TIME = int(time.time())
            await bot.send(event, '查询中……')
            statue = await cf_api.get_usr_rating(name)
            if statue != -1:
                await bot.send(event, statue)
            else:
                await bot.send(event, "不存在这个用户或查询出错哦")


    @bot.on(MessageEvent)
    async def query_cf_contest(event: MessageEvent):  # 查询最近比赛
        msg = "".join(map(str, event.message_chain[Plain]))

        m = re.match(r'cf', msg.strip())

        if m is None:
            m = re.match(r'CF', msg.strip())

        if m:
            global LAST_CF_TIME
            global LAST_CF_CONTEST_INFO, LAST_CF_CONTEST_BEGIN_TIME, LAST_CF_CONTEST_DURING_TIME

            print("查询cf比赛")

            if int(time.time()) - LAST_CF_TIME < 5:
                await bot.send(event, LAST_CF_CONTEST_INFO)
                return

            LAST_CF_TIME = int(time.time())
            await bot.send(event, '查询中……')
            # await asyncio.sleep(1)
            LAST_CF_CONTEST_INFO, LAST_CF_CONTEST_BEGIN_TIME, LAST_CF_CONTEST_DURING_TIME = await cf_api.get_contest()
            await bot.send(event, LAST_CF_CONTEST_INFO)


    @scheduler.scheduled_job(CronTrigger(month=time.localtime(LAST_CF_CONTEST_BEGIN_TIME - 10 * 60).tm_mon,
                                         day=time.localtime(LAST_CF_CONTEST_BEGIN_TIME - 10 * 60).tm_mday,
                                         hour=time.localtime(LAST_CF_CONTEST_BEGIN_TIME - 10 * 60).tm_hour,
                                         minute=time.localtime(LAST_CF_CONTEST_BEGIN_TIME - 10 * 60).tm_min))
    async def cf_shang_hao():
        message_chain = MessageChain([
            await Image.from_local('pic/up_cf.jpg')
        ])
        await bot.send_group_message(763537993, message_chain)  # 874149706测试号


    @scheduler.scheduled_job(
        CronTrigger(month=time.localtime(LAST_CF_CONTEST_BEGIN_TIME + LAST_CF_CONTEST_DURING_TIME).tm_mon,
                    day=time.localtime(LAST_CF_CONTEST_BEGIN_TIME + LAST_CF_CONTEST_DURING_TIME).tm_mday,
                    hour=time.localtime(LAST_CF_CONTEST_BEGIN_TIME + LAST_CF_CONTEST_DURING_TIME).tm_hour,
                    minute=time.localtime(LAST_CF_CONTEST_BEGIN_TIME + LAST_CF_CONTEST_DURING_TIME).tm_min))
    async def cf_xia_hao():
        message_chain = MessageChain([
            await Image.from_local('pic/down_cf.jpg')
        ])
        await bot.send_group_message(763537993, message_chain)  # 874149706测试号

        global LAST_CF_CONTEST_INFO, LAST_CF_CONTEST_BEGIN_TIME, LAST_CF_CONTEST_DURING_TIME  # 比完接着更新
        LAST_CF_CONTEST_INFO, LAST_CF_CONTEST_BEGIN_TIME, LAST_CF_CONTEST_DURING_TIME = await cf_api.get_contest()


    # ATC
    @bot.on(MessageEvent)
    async def query_atc_contest(event: MessageEvent):  # 查询最近比赛
        msg = "".join(map(str, event.message_chain[Plain]))

        m = re.match(r'atc', msg.strip())

        if m is None:
            m = re.match(r'ATC', msg.strip())

        if m:
            global LAST_ATC_CONTEST_INFO, LAST_ATC_TIME

            print("查询atc比赛")

            if int(time.time()) - LAST_ATC_TIME < 5:
                await bot.send(event, LAST_ATC_CONTEST_INFO[0])
                return

            LAST_ATC_TIME = int(time.time())
            await bot.send(event, '查询中……')
            # await asyncio.sleep(1)

            LAST_ATC_CONTEST_INFO = await atc_api.get_contest_lately()
            await bot.send(event, LAST_ATC_CONTEST_INFO[0])


    @bot.on(MessageEvent)
    async def query_atc_rank(event: MessageEvent):  # 查询对应人的分数
        msg = "".join(map(str, event.message_chain[Plain]))

        m = re.match(r'^查询ATC分数\s*(\w+)\s*$', msg.strip())
        if m is None:
            m = re.match(r'^查询atc分数\s*(\w+)\s*$', msg.strip())
        if m is None:
            m = re.match(r'^查询(.*)的atc分数$', msg.strip())
        if m is None:
            m = re.match(r'^查询(.*)的ATC分数$', msg.strip())

        if m:
            name = m.group(1)
            # print(name)

            global LAST_ATC_TIME
            if int(time.time()) - LAST_ATC_TIME < 5:  # 每次询问要大于5秒
                await bot.send(event, '不要频繁查询，请{}秒后再试'.format(LAST_ATC_TIME + 5 - int(time.time())))
                return

            LAST_ATC_TIME = int(time.time())
            await bot.send(event, '查询中……')
            statue = await atc_api.get_usr_rank(name)
            if statue != -1:
                await bot.send(event, statue)
            else:
                await bot.send(event, "不存在这个用户或查询出错哦")


    # nowcoder
    @bot.on(MessageEvent)
    async def query_nc_contest(event: MessageEvent):  # 查询最近比赛
        msg = "".join(map(str, event.message_chain[Plain]))

        # m = re.match(r'牛客', msg.strip())

        if msg == "牛客":
            global LAST_NC_TIME
            global LAST_NC_CONTEST_INFO, LAST_NC_CONTEST_BEGIN_TIME

            print("查询牛客比赛")

            if int(time.time()) - LAST_NC_TIME < 5:
                await bot.send(event, LAST_NC_CONTEST_INFO)
                return

            LAST_NC_TIME = int(time.time())
            await bot.send(event, '查询中……')
            # await asyncio.sleep(1)
            LAST_NC_CONTEST_INFO, LAST_NC_CONTEST_BEGIN_TIME = await nc_api.get_contest()
            await bot.send(event, LAST_NC_CONTEST_INFO if LAST_NC_CONTEST_INFO != -1 else "获取比赛时出错，请联系管理员")


    @scheduler.scheduled_job(CronTrigger(month=time.localtime(LAST_NC_CONTEST_BEGIN_TIME - 10 * 60).tm_mon,
                                         day=time.localtime(LAST_NC_CONTEST_BEGIN_TIME - 10 * 60).tm_mday,
                                         hour=time.localtime(LAST_NC_CONTEST_BEGIN_TIME - 10 * 60).tm_hour,
                                         minute=time.localtime(LAST_NC_CONTEST_BEGIN_TIME - 10 * 60).tm_min))
    async def nc_shang_hao():
        message_chain = MessageChain([
            await Image.from_local('pic/up_nc.png')
        ])
        await bot.send_group_message(763537993, message_chain)  # 874149706测试号


    # 力扣
    @bot.on(MessageEvent)
    async def query_lc_contest(event: MessageEvent):  # 查询最近比赛
        msg = "".join(map(str, event.message_chain[Plain]))

        # m = re.match(r'lc', msg.strip())

        if msg == "lc":
            print("查询力扣比赛")

            global LAST_LC_TIME, LAST_LC_CONTEST_INFO

            if int(time.time()) - LAST_LC_TIME < 5:
                await bot.send(event, LAST_LC_CONTEST_INFO[0][0] if LAST_LC_CONTEST_INFO != -1 else "获取比赛时出错，请联系管理员")
                return

            LAST_LC_TIME = int(time.time())
            await bot.send(event, '查询中……')
            # await asyncio.sleep(1)

            await bot.send(event, LAST_LC_CONTEST_INFO[0][0] if LAST_LC_CONTEST_INFO != -1 else "获取比赛时出错，请联系管理员")


    # other
    @bot.on(MessageEvent)
    async def query_today(event: MessageEvent):
        msg = "".join(map(str, event.message_chain[Plain]))

        if msg == 'today':
            res = await query_today_contest()

            if res != '':
                await bot.send(event, "为您查询到今日的比赛有：\n\n" + res.strip())
            else:
                await bot.send(event, "今日无比赛哦~")


    @bot.on(MessageEvent)
    async def qcjj_query(event: MessageEvent):
        # 从消息链中取出文本
        msg = "".join(map(str, event.message_chain[Plain]))
        # 匹配指令
        m = re.match(r'来只清楚', msg.strip())
        if m:
            print("来只清楚")
            img_list = os.listdir('./pic/qcjj/')
            img_local = './pic/qcjj/' + random.choice(img_list)
            print(img_local)
            message_chain = MessageChain([
                await Image.from_local(img_local)
            ])
            await bot.send(event, message_chain)

    # setu
    @bot.on(MessageEvent)
    async def setu_query(event: MessageEvent):
        # 从消息链中取出文本
        msg = "".join(map(str, event.message_chain[Plain]))
        # 匹配指令
        m = re.match(r'setu', msg.strip())
        if m is None:
            m = re.match(r'涩图', msg.strip())
        if m:
            print("setu")
            img_list = os.listdir('./pic/setu/')
            img_local = './pic/setu/' + random.choice(img_list)
            print(img_local)
            message_chain = MessageChain([
                await Image.from_local(img_local)
            ])
            await bot.send(event, message_chain)

    # color_img
    @bot.on(MessageEvent)
    async def color_query(event: MessageEvent):
        # 从消息链中取出文本
        msg = "".join(map(str, event.message_chain[Plain]))
        # 匹配指令
        m = re.match(r'色图', msg.strip())
        if m:
            print("色图")
            message_chain = MessageChain([
                await Image.from_local('./pic/color.jpg')
            ])
            await bot.send(event, message_chain)


    @bot.on(MessageEvent)
    async def ggg_query(event: MessageEvent):
        # 从消息链中取出文本
        msg = "".join(map(str, event.message_chain[Plain]))
        # 匹配指令
        m = re.match(r'管哥哥', msg.strip())
        if m:
            print("setu")
            img_list = os.listdir('./pic/ggg/')
            img_local = './pic/ggg/' + random.choice(img_list)
            print(img_local)
            message_chain = MessageChain([
                await Image.from_local(img_local)
            ])
            await bot.send(event, message_chain)

    # daily
    @scheduler.scheduled_job(CronTrigger(hour=7, minute=30))
    async def update_contest_info():
        now = time.localtime()
        print()
        print(time.strftime("%Y-%m-%d", now))  # 给log换行

        global LAST_CF_CONTEST_INFO, LAST_CF_CONTEST_BEGIN_TIME, LAST_CF_CONTEST_DURING_TIME
        LAST_CF_CONTEST_INFO, LAST_CF_CONTEST_BEGIN_TIME, LAST_CF_CONTEST_DURING_TIME = await cf_api.get_contest()

        global LAST_ATC_CONTEST_INFO
        LAST_ATC_CONTEST_INFO = await atc_api.get_contest_lately()

        global LAST_NC_CONTEST_INFO, LAST_NC_CONTEST_BEGIN_TIME
        LAST_NC_CONTEST_INFO, LAST_NC_CONTEST_BEGIN_TIME = await nc_api.get_contest()

        global LAST_LC_CONTEST_INFO
        LAST_LC_CONTEST_INFO = await lc_api.get_contest()


    @scheduler.scheduled_job(CronTrigger(hour=8, minute=30))
    async def notify_contest_info():
        res = await query_today_contest()

        friends = ['1095490883', '942845546', '2442530380']
        groups = ['687601411', '763537993']

        if res != '':
            # 发送当日信息
            msg = "今日的比赛有：\n\n" + res.strip()
            for friend in friends:
                try:
                    await bot.send_friend_message(friend, msg)  # 发送个人
                except:
                    print("不存在qq号为 {} 的好友".format(friend))

            for group in groups:
                try:
                    await bot.send_group_message(group, msg)  # 发送群组
                except:
                    print("不存在群号为 {} 的群组".format(group))


    # debug
    @Filter(FriendMessage)
    def filter_(event: FriendMessage):  # 定义过滤器，在过滤器中对事件进行过滤和解析
        msg = str(event.message_chain)
        # 如果好友发送的消息格式正确，过滤器返回消息的剩余部分。比如，好友发送“ / command”，过滤器返回'command'。
        # 如果好友发送的消息格式不正确，过滤器隐式地返回None。
        if msg.startswith('/'):
            return msg[1:]


    @hdc.on(filter_)
    async def handler(event: FriendMessage, payload: str):
        global LAST_CF_CONTEST_BEGIN_TIME, LAST_CF_CONTEST_DURING_TIME
        # LAST_CF_CONTEST_BEGIN_TIME = int(time.time())
        # LAST_CF_CONTEST_DURING_TIME = 60
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(LAST_CF_CONTEST_BEGIN_TIME)))
        print(time.strftime("%Y-%m-%d %H:%M:%S",
                            time.localtime(LAST_CF_CONTEST_BEGIN_TIME + LAST_CF_CONTEST_DURING_TIME)))
        await bot.send(event, f'命令 {payload} 执行成功。')


    bot.run()

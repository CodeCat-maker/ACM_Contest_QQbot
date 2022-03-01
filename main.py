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
from oj_api import cf_api, atc_api, lc_api, nc_api, Contest
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

cf = cf_api.CF()

atc = atc_api.ATC()

nc = nc_api.NC()

lc = lc_api.LC()

print(cf.info)
print(atc.info)
print(nc.info)
print(lc.info)


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
    global cf, atc, nc, lc

    res = ""

    mon = datetime.datetime.now().month
    day = datetime.datetime.now().day

    print(cf.info)
    print(lc.info)
    print(atc.info)
    print(nc.info)
    print(lc.info)

    # CF
    if time.localtime(cf.begin_time).tm_mon == mon and time.localtime(
            cf.begin_time).tm_mday == day:
        print(1)
        res += (cf.info + '\n\n')

    # ATC
    if time.localtime(atc.begin_time).tm_mon == mon and time.localtime(
            atc.begin_time).tm_mday == day:
        print(2)
        res += (atc.info + '\n\n')

    # NC
    if time.localtime(nc.begin_time).tm_mon == mon and time.localtime(
            nc.begin_time).tm_mday == day:
        print(3)
        res += (nc.info + '\n\n')

    # LC
    if time.localtime(lc.begin_time).tm_mon == mon and time.localtime(
            lc.begin_time).tm_mday == day:
        print(4)
        res += (lc.info + '\n\n')

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
                await bot.send(event, [At(event.sender.id), "\n查询天气 城市 -> 查询市级城市实时天气"
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
                await bot.send(event, ["查询天气 城市 -> 查询市级城市实时天气"
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
            # await bot.send(event, '查询中……')
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

            global cf
            if int(time.time()) - cf.updated_time < 5:  # 每次询问要大于5秒
                await bot.send(event, '不要频繁查询，请{}秒后再试'.format(cf.updated_time + 5 - int(time.time())))
                return

            # await bot.send(event, '查询中……')
            statue = await cf.get_ranting(name)
            if statue != -1:
                await bot.send(event, statue)
            else:
                await bot.send(event, "不存在这个用户或查询出错哦")


    @bot.on(MessageEvent)
    async def query_cf_contest(event: MessageEvent):  # 查询最近比赛
        msg = "".join(map(str, event.message_chain[Plain]))

        # m = re.match(r'cf', msg.strip())
        #
        # if m is None:
        #     m = re.match(r'CF', msg.strip())

        if msg.strip() == 'CF' or msg.strip() == 'cf':
            global cf

            print("查询cf比赛")

            if int(time.time()) - cf.updated_time < 5:
                await bot.send(event, cf.info)
                return

            # await bot.send(event, '查询中……')
            # await asyncio.sleep(1)
            await cf.update_contest()
            await bot.send(event, cf.info)


    @scheduler.scheduled_job(CronTrigger(month=time.localtime(cf.begin_time - 10 * 60).tm_mon,
                                         day=time.localtime(cf.begin_time - 10 * 60).tm_mday,
                                         hour=time.localtime(cf.begin_time - 10 * 60).tm_hour,
                                         minute=time.localtime(cf.begin_time - 10 * 60).tm_min))
    async def cf_shang_hao():
        message_chain = MessageChain([
            await Image.from_local('pic/up_cf.jpg')
        ])
        await bot.send_group_message(763537993, message_chain)  # 874149706测试号


    @scheduler.scheduled_job(
        CronTrigger(month=time.localtime(cf.begin_time + cf.during_time).tm_mon,
                    day=time.localtime(cf.begin_time + cf.during_time).tm_mday,
                    hour=time.localtime(cf.begin_time + cf.during_time).tm_hour,
                    minute=time.localtime(cf.begin_time + cf.during_time).tm_min))
    async def cf_xia_hao():
        message_chain = MessageChain([
            await Image.from_local('pic/down_cf.jpg')
        ])
        await bot.send_group_message(763537993, message_chain)  # 874149706测试号

        global cf  # 比完接着更新
        await cf.updated_time()


    # ATC
    @bot.on(MessageEvent)
    async def query_atc_contest(event: MessageEvent):  # 查询最近比赛
        msg = "".join(map(str, event.message_chain[Plain]))

        # m = re.match(r'atc', msg.strip())

        # if m is None:
        #     m = re.match(r'ATC', msg.strip())

        if msg.strip() == 'atc' or msg.strip() == 'ATC':
            global atc

            print("查询atc比赛")

            if int(time.time()) - atc.updated_time < 5:
                await bot.send(event, atc.info)
                return

            # await bot.send(event, '查询中……')
            # await asyncio.sleep(1)

            await atc.update_contest()
            await bot.send(event, atc.info)


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

            global atc
            if int(time.time()) - atc.updated_time < 5:  # 每次询问要大于5秒
                await bot.send(event, '不要频繁查询，请{}秒后再试'.format(atc.updated_time + 5 - int(time.time())))
                return

            # await bot.send(event, '查询中……')
            statue = await atc.get_ranting(name)
            if statue != -1:
                await bot.send(event, statue)
            else:
                await bot.send(event, "不存在这个用户或查询出错哦")


    # nowcoder

    @bot.on(MessageEvent)
    async def query_nc_rating(event: MessageEvent):  # 查询牛客rating
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(r'^查询牛客分数\s*([\u4e00-\u9fa5\w.-]+)\s*$', msg.strip())
        if m:
            uname = m.group(1)
            rating = await nc.get_ranting(uname)
            await bot.send(event, rating)


    @bot.on(MessageEvent)
    async def query_nc_contest(event: MessageEvent):  # 查询最近比赛
        msg = "".join(map(str, event.message_chain[Plain]))

        # m = re.match(r'牛客', msg.strip())

        if msg == "牛客":
            global nc

            print("查询牛客比赛")

            if int(time.time()) - nc.updated_time < 5:
                await bot.send(event, nc.info)
                return

            # await bot.send(event, '查询中……')
            # await asyncio.sleep(1)
            await nc.update_contest()
            await bot.send(event, nc.info if nc.info != -1 else "获取比赛时出错，请联系管理员")


    @scheduler.scheduled_job(CronTrigger(month=time.localtime(nc.begin_time - 10 * 60).tm_mon,
                                         day=time.localtime(nc.begin_time - 10 * 60).tm_mday,
                                         hour=time.localtime(nc.begin_time - 10 * 60).tm_hour,
                                         minute=time.localtime(nc.begin_time - 10 * 60).tm_min))
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

            global lc

            if int(time.time()) - lc.updated_time < 5:
                await bot.send(event, lc.info if lc.info != -1 else "获取比赛时出错，请联系管理员")
                return

 
            # await bot.send(event, '查询中……')
            # await asyncio.sleep(1)
            await lc.update_contest()
            await bot.send(event, lc.info if lc.info != -1 else "获取比赛时出错，请联系管理员")


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
        async def update(oj):
            while True:
                await oj.update_contest()
                if oj.info != -1:
                    break


        now = time.localtime()
        print()
        print(time.strftime("%Y-%m-%d", now))  # 给log换行

        global cf
        await update(cf)

        global atc
        await update(atc)

        global nc
        await update(nc)

        global lc
        await update(nc)



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
        global cf
        # cf.begin_time = int(time.time())
        # cf.during_time = 60
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(cf.begin_time)))
        print(time.strftime("%Y-%m-%d %H:%M:%S",
                            time.localtime(cf.begin_time + cf.during_time)))
        await bot.send(event, f'命令 {payload} 执行成功。')


    bot.run()

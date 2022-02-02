import re
import sys
import time
import asyncio
import httpx
from log import Log
from oj_api import atc_api, cf_api, nc_api
from mirai.models import NewFriendRequestEvent
from mirai import Startup, Shutdown
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


    @bot.on(FriendMessage)
    async def on_friend_message(event: FriendMessage):
        if str(event.message_chain) == '你好':
            await bot.send(event, 'Hello, World!')


    @bot.on(GroupMessage)
    async def show_list(event: GroupMessage):  # 功能列表展示
        msg = "".join(map(str, event.message_chain[Plain]))
        if msg == ".help":
            await bot.send(event, [At(event.sender.id), "\n“查询天气 {城市}” 查询城市实时天气"
                                                        "\n“查询CF分数 {id}” 查询对应用户的Codeforces分数"
                                                        "\n“查询cf比赛” 通知最新的Codeforces比赛"
                                                        "\n“查询ATC比赛” 通知最新的AtCoder比赛"
                                                        "\n“查询ATC分数 {id}” 查询对应用户的AtCoder分数"
                                                        "\n“查询牛客比赛” 通知最新的牛客比赛"
                                                        "\n“@上分上分上分 echo {xxx}” 重复xxx"])


    @bot.on(GroupMessage)
    async def echo(event: GroupMessage):  # 复读机
        msg = "".join(map(str, event.message_chain[Plain])).strip()
        m = re.match(r'^echo\s*(\w+)\s*$', msg)
        if m and At(bot.qq) in event.message_chain:
            await bot.send(event, msg)


    @bot.on(GroupMessage)
    async def on_group_message(event: GroupMessage):  # 返回
        if At(bot.qq) in event.message_chain and len("".join(map(str, event.message_chain[Plain]))) == 0:
            await bot.send(event, [At(event.sender.id), '你在叫我吗？'])


    @bot.on(GroupMessage)
    async def weather_query(event: GroupMessage):  # 天气查询
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

    @bot.on(GroupMessage)
    async def query_cf_rank(event: GroupMessage):  # 查询对应人的分数
        msg = "".join(map(str, event.message_chain[Plain]))

        m = re.match(r'^查询CF分数\s*(\w+)\s*$', msg.strip())
        if m is None:
            m = re.match(r'^查询cf分数\s*(\w+)\s*$', msg.strip())
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


    @bot.on(GroupMessage)
    async def query_cf_contest(event: GroupMessage):  # 查询最近比赛
        msg = "".join(map(str, event.message_chain[Plain]))

        m = re.match(r'查询CF比赛', msg.strip())

        if m is None:
            m = re.match(r'查询cf比赛', msg.strip())

        if m:
            global LAST_CF_TIME
            global LAST_CF_CONTEST_INFO, LAST_CF_CONTEST_BEGIN_TIME, LAST_CF_CONTEST_DURING_TIME

            print("查询cf比赛")

            # if int(time.time()) - LAST_CF_TIME < 3600:
            #     await bot.send(event, LAST_CF_CONTEST_INFO)
            #     return

            LAST_CF_TIME = int(time.time())
            await bot.send(event, '查询中……')
            await asyncio.sleep(1)
            # LAST_CF_CONTEST_INFO, LAST_CF_CONTEST_BEGIN_TIME, LAST_CF_CONTEST_DURING_TIME = await cf_api.get_contest()
            await bot.send(event, LAST_CF_CONTEST_INFO)


    @scheduler.scheduled_job(CronTrigger(month=time.localtime(LAST_CF_CONTEST_BEGIN_TIME).tm_mon,
                                         day=time.localtime(LAST_CF_CONTEST_BEGIN_TIME).tm_mday,
                                         hour=time.localtime(LAST_CF_CONTEST_BEGIN_TIME).tm_hour,
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


    @scheduler.scheduled_job(CronTrigger(day=time.localtime(LAST_CF_CONTEST_BEGIN_TIME).tm_mday, hour=10, minute=30))
    async def notify_contest_info():
        # 发送当日信息
        await bot.send_friend_message(1095490883, LAST_CF_CONTEST_INFO)  # lzd
        await bot.send_friend_message(942845546, LAST_CF_CONTEST_INFO)  # wlx
        # await bot.send_friend_message(2442530380, LAST_CF_CONTEST_INFO)  # zsh

        await bot.send_group_message(763537993, LAST_CF_CONTEST_INFO)  # 纳新群
        await bot.send_group_message(687601411, LAST_CF_CONTEST_INFO)  # 训练群


    # ATC
    @bot.on(GroupMessage)
    async def query_atc_contest(event: GroupMessage):  # 查询最近比赛
        msg = "".join(map(str, event.message_chain[Plain]))

        m = re.match(r'查询ATC比赛', msg.strip())

        if m is None:
            m = re.match(r'查询ATC比赛', msg.strip())

        if m:
            global LAST_ATC_CONTEST_INFO, LAST_ATC_TIME

            print("查询atc比赛")

            if int(time.time()) - LAST_ATC_TIME < 3600:
                await bot.send(event, LAST_ATC_CONTEST_INFO)
                return

            LAST_ATC_TIME = int(time.time())
            await bot.send(event, '查询中……')
            await asyncio.sleep(1)

            await bot.send(event, await atc_api.get_contest_lately())


    @bot.on(GroupMessage)
    async def query_atc_rank(event: GroupMessage):  # 查询对应人的分数
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
    @bot.on(GroupMessage)
    async def query_nc_contest(event: GroupMessage):  # 查询最近比赛
        msg = "".join(map(str, event.message_chain[Plain]))

        m = re.match(r'查询牛客比赛', msg.strip())

        if m:
            global LAST_NC_TIME
            global LAST_NC_CONTEST_INFO, LAST_NC_CONTEST_BEGIN_TIME

            print("查询牛客比赛")

            # if int(time.time()) - LAST_CF_TIME < 3600:
            #     await bot.send(event, LAST_CF_CONTEST_INFO)
            #     return

            LAST_NC_TIME = int(time.time())
            await bot.send(event, '查询中……')
            await asyncio.sleep(1)
            # LAST_CF_CONTEST_INFO, LAST_CF_CONTEST_BEGIN_TIME, LAST_CF_CONTEST_DURING_TIME = await cf_api.get_contest()
            await bot.send(event, LAST_NC_CONTEST_INFO)


    @scheduler.scheduled_job(CronTrigger(month=time.localtime(LAST_NC_CONTEST_BEGIN_TIME).tm_mon,
                                         day=time.localtime(LAST_NC_CONTEST_BEGIN_TIME).tm_mday,
                                         hour=time.localtime(LAST_NC_CONTEST_BEGIN_TIME).tm_hour,
                                         minute=time.localtime(LAST_NC_CONTEST_BEGIN_TIME - 10 * 60).tm_min))
    async def nc_shang_hao():
        message_chain = MessageChain([
            await Image.from_local('pic/up_nc.jpg')
        ])
        await bot.send_group_message(763537993, message_chain)  # 874149706测试号


    # daily
    @scheduler.scheduled_job(CronTrigger(hour=10, minute=30))
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

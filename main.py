import re
import time
import asyncio
import httpx
import datetime
import cf_api
from mirai.models import NewFriendRequestEvent
from mirai import Mirai
from mirai_extensions.trigger import HandlerControl, Filter
from mirai import Mirai, WebSocketAdapter, FriendMessage, GroupMessage, At, Plain, MessageChain, Image

API_KEY = 'SWeKQBWfoYiQFuZSJ'
LAST_CF_TIME = 0
LAST_ATC_TIME = 0
LAST_CF_CONTEST_INFO, LAST_CF_CONTEST_BEGIN_TIME, LAST_CF_CONTEST_DURING_TIME = asyncio.run(cf_api.get_contest())
print(LAST_CF_CONTEST_INFO)
print(LAST_CF_CONTEST_BEGIN_TIME)
print(LAST_CF_CONTEST_DURING_TIME)

now = datetime.datetime.now()
begin_time = datetime.datetime.strptime(
    time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(LAST_CF_CONTEST_BEGIN_TIME)), "%Y-%m-%d %H:%M:%S")
end_time = begin_time + datetime.timedelta(seconds=LAST_CF_CONTEST_DURING_TIME)
print(type(now) == type(end_time) == type(begin_time))

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
    hdc = HandlerControl(bot)

    @bot.on(NewFriendRequestEvent)
    async def allow_request(event: NewFriendRequestEvent):
        await bot.allow(event)

    @bot.on(FriendMessage)
    def on_friend_message(event: FriendMessage):
        if str(event.message_chain) == '你好':
            return bot.send(event, 'Hello, World!')


    @bot.on(GroupMessage)
    def show_list(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        if msg == ".help":
            return bot.send(event, [At(event.sender.id), "\n“查询天气 {城市}” 查询城市实时天气"
                                                         "\n“查询CF分数 {id}” 查询对应用户的cf分数"
                                                         "\n“查询cf比赛” 通知最新的CF比赛"
                                                         "\n“@上分上分上分 echo {xxx}” 重复xxx"])


    @bot.on(GroupMessage)
    def echo(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain])).strip()
        m = re.match(r'^echo\s*(\w+)\s*$', msg)
        if m and At(bot.qq) in event.message_chain:
            return bot.send(event, msg)


    @bot.on(GroupMessage)
    def on_group_message(event: GroupMessage):
        if At(bot.qq) in event.message_chain and len("".join(map(str, event.message_chain[Plain]))) == 0:
            return bot.send(event, [At(event.sender.id), '你在叫我吗？'])


    @bot.on(GroupMessage)
    async def weather_query(event: GroupMessage):
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
    async def query_cf_rank(event: GroupMessage):
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
            if int(time.time()) - LAST_CF_TIME < 15:
                await bot.send(event, '不要频繁查询，请{}秒后再试'.format(LAST_CF_TIME + 15 - int(time.time())))
                return


            LAST_CF_TIME = int(time.time())
            await bot.send(event, '查询中……')
            statue = await cf_api.get_usr_rating(name)
            if statue != -1:
                await bot.send(event, statue)
            else:
                await bot.send(event, "不存在这个用户或查询出错哦")


    @bot.on(GroupMessage)
    async def query_cf_contest(event: GroupMessage):
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
            # LAST_CF_CONTEST_INFO, LAST_CF_CONTEST_BEGIN_TIME, LAST_CF_CONTEST_DURING_TIME = await cf_api.get_contest()
            await bot.send(event, LAST_CF_CONTEST_INFO)


    @bot.add_background_task()
    async def shang_hao():
        today_finished = False  # 设置变量标识今天是会否完成任务，防止重复发送
        while True:
            await asyncio.sleep(1)
            now = datetime.datetime.now()
            begin_time = datetime.datetime.strptime(
                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(LAST_CF_CONTEST_BEGIN_TIME)), "%Y-%m-%d %H:%M:%S")

            if now.hour == begin_time.hour and now.minute == (begin_time - datetime.timedelta(minutes=5)).minute and today_finished is False:
            # if now.hour == 1 and 29 and today_finished is False:
                today_finished = True
                message_chain = MessageChain([
                    await Image.from_local('./pic/up.jpg')
                ])
                await bot.send_group_message(874149706, message_chain)  # 874149706测试号

            if now.hour == begin_time.hour and now.minute == (begin_time - datetime.timedelta(minutes=6)).minute:
            # if now.hour == 1 and now.minute == 30:
                today_finished = True


    @bot.add_background_task()
    async def xia_hao():
        today_finished = False  # 设置变量标识今天是会否完成任务，防止重复发送
        while True:
            await asyncio.sleep(1)
            now = datetime.datetime.now()
            begin_time = datetime.datetime.strptime(
                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(LAST_CF_CONTEST_BEGIN_TIME)), "%Y-%m-%d %H:%M:%S")
            end_time = begin_time + datetime.timedelta(seconds=LAST_CF_CONTEST_DURING_TIME)

            print(str(end_time) + " " + str(now) + " " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(LAST_CF_CONTEST_BEGIN_TIME)))

            if now.hour == end_time.hour and now.minute == end_time.minute and today_finished is False:
                message_chain = MessageChain([
                    await Image.from_local('./pic/down.jpg')
                ])
                await bot.send_group_message(874149706, message_chain)  # 874149706 测试号

            if now.hour == end_time.hour and now.minute == (end_time + datetime.timedelta(minutes=1)).minute:
                today_finished = True


    @bot.add_background_task()
    async def auto_update_contest():
        today_finished = False  # 设置变量标识今天是会否完成任务，防止重复发送
        global LAST_CF_CONTEST_INFO, LAST_CF_CONTEST_BEGIN_TIME, LAST_CF_CONTEST_DURING_TIME

        while True:
            await asyncio.sleep(1)
            now = datetime.datetime.now()

            if now.hour == 8 and now.minute == 30 and not today_finished:  # 每天早上 7:30 发送早安
                LAST_CF_CONTEST_INFO, LAST_CF_CONTEST_BEGIN_TIME, LAST_CF_CONTEST_DURING_TIME = asyncio.run(cf_api.get_contest())
                today_finished = True
            if now.hour == 8 and now.minute == 31:
                today_finished = False  # 早上 7:31，重置今天是否完成任务的标识

    # debug
    @Filter(FriendMessage)
    async def filter_(event: FriendMessage):  # 定义过滤器，在过滤器中对事件进行过滤和解析
        msg = str(event.message_chain)
        # 如果好友发送的消息格式正确，过滤器返回消息的剩余部分。比如，好友发送“ / command”，过滤器返回'command'。
        # 如果好友发送的消息格式不正确，过滤器隐式地返回None。
        if msg.startswith('/'):
            return msg[1:]

    @hdc.on(filter_)
    async def handler(event: FriendMessage, payload: str):
        global LAST_CF_CONTEST_BEGIN_TIME, LAST_CF_CONTEST_DURING_TIME
        LAST_CF_CONTEST_BEGIN_TIME = int(time.time())
        LAST_CF_CONTEST_DURING_TIME = 60
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(LAST_CF_CONTEST_BEGIN_TIME)))
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(LAST_CF_CONTEST_BEGIN_TIME + LAST_CF_CONTEST_DURING_TIME)))
        await bot.send(event, f'命令 {payload} 执行成功。')

    bot.run()

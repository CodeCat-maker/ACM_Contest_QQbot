import re
import time

import httpx
import cf_api
import atc_api
from mirai import Mirai, WebSocketAdapter, FriendMessage, GroupMessage, At, Plain

API_KEY = 'SWeKQBWfoYiQFuZSJ'
LAST_CF_TIME = 0
LAST_ATC_TIME = 0

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


    @bot.on(FriendMessage)
    def on_friend_message(event: FriendMessage):
        if str(event.message_chain) == '你好':
            return bot.send(event, 'Hello, World!')


    # TODO list
    @bot.on(GroupMessage)
    def show_list(event: GroupMessage):
        pass


    # TODO echo
    @bot.on(GroupMessage)
    def echo(event: GroupMessage):
        pass


    @bot.on(GroupMessage)
    def on_group_message(event: GroupMessage):
        if At(bot.qq) in event.message_chain:
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

        # TODO 有中文不行，

        m = re.match(r'^查询CF分数\s*(\w+)\s*$', msg.strip())
        if m is None:
            m = re.match(r'^查询cf分数\s*(\w+)\s*$', msg.strip())
        if m is None:
            m = re.match(r'^查询(.*)的CF分数$', msg.strip())
        if m is None:
            m = re.match(r'^查询(.*)的cf分数$', msg.strip())

        if m:
            name = m.group(1)
            print(name)

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


    async def query_cf_contest(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))

        m = re.match(r'查询CF比赛', msg.strip())

        if m is None:
            m = re.match(r'查询cf比赛', msg.strip())

        global LAST_CF_TIME

        if int(time.time()) - LAST_CF_TIME < 3600:
            await bot.send(event, '不要频繁查询，请{}秒后再试'.format(LAST_CF_TIME + 3600 - int(time.time())))
            return

        if m:
            print("查询cf比赛")
            LAST_CF_TIME = int(time.time())
            await bot.send(event, '查询中……')
            await bot.send(event, await cf_api.get_contest())


    bot.run()

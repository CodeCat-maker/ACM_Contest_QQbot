import abc
import asyncio
import time


class Contest(object):
    __metaclass__ = abc.ABCMeta
    info = ""
    during_time = 0
    begin_time = 0
    updated_time = 0

    def __init__(self):
        self.updated_time = time.time()
        self.info, self.begin_time, self.during_time = asyncio.run(self.get_contest())

    async def update_contest(self):
        self.updated_time = time.time()
        self.info, self.begin_time, self.during_time = await self.get_contest()
        # return self.info

    def show_all(self):
        print("info : {}\nduring_time : {}\nbegin_time : {}\n update_time : {}".format(self.info, self.during_time, self.begin_time, self.updated_time))

    @abc.abstractmethod
    async def get_contest(self):
        pass

    @abc.abstractmethod
    async def get_ranting(self, name):
        pass

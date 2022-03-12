import datetime
import os
import time


class Event:
    """
    事件对象
    """

    def __init__(self, kwargs):
        self.event_data = kwargs

    def __turn_to_string__(self):
        self.event_text = "BEGIN:VEVENT\n"
        for item, data in self.event_data.items():
            item = str(item).replace("_", "-")
            if item not in ["ORGANIZER", "DTSTART", "DTEND"]:
                self.event_text += "%s:%s\n" % (item, data)
            else:
                self.event_text += "%s;%s\n" % (item, data)
        self.event_text += "END:VEVENT\n"
        return self.event_text


class Calendar:
    """
    日历对象
    """

    def __init__(self, calendar_name="My Calendar"):
        self.__events__ = {}
        self.__event_id__ = 0
        self.calendar_name = calendar_name

    def add_event(self, **kwargs):
        event = Event(kwargs)
        event_id = self.__event_id__
        self.__events__[self.__event_id__] = event
        self.__event_id__ += 1
        return event_id

    def modify_event(self, event_id, **kwargs):
        for item, data in kwargs.items():
            self.__events__[event_id].event_data[item] = data

    def remove_event(self, event_id):
        self.__events__.pop(event_id)

    def get_ics_text(self):
        self.__calendar_text__ = """BEGIN:VCALENDAR\nPRODID:-//ZHONG_BAI_REN//APPGENIX-SOFTWARE//\nVERSION:2.0
        \nCALSCALE:GREGORIAN\nMETHOD:PUBLISH\nX-WR-CALNAME:%s\nX-WR-TIMEZONE:null\n""" % self.calendar_name
        for key, value in self.__events__.items():
            self.__calendar_text__ += value.__turn_to_string__()
        self.__calendar_text__ += "END:VCALENDAR"
        return self.__calendar_text__

    def save_as_ics_file(self):
        ics_text = self.get_ics_text()
        open("%s.ics" % self.calendar_name, "w", encoding="utf8").write(ics_text)  # 使用utf8编码生成ics文件，否则日历软件打开是乱码

    def open_ics_file(self):
        os.system("%s.ics" % self.calendar_name)


def add_event(cal, SUMMARY, DTSTART, DTEND, DESCRIPTION, LOCATION):
    """
    向Calendar日历对象添加事件的方法
    :param cal: calender日历实例
    :param SUMMARY: 事件名
    :param DTSTART: 事件开始时间
    :param DTEND: 时间结束时间
    :param DESCRIPTION: 备注
    :param LOCATION: 时间地点
    :return:
    """
    time_format = "TZID=Asia/Shanghai:{date.year}{date.month:0>2d}{date.day:0>2d}T{date.hour:0>2d}{date.minute:0>2d}00"
    dt_start = time_format.format(date=DTSTART)
    dt_end = time_format.format(date=DTEND)
    create_time = datetime.datetime.today().strftime("%Y%m%dT%H%M%SZ")
    cal.add_event(
        SUMMARY=SUMMARY,
        DTSTART=dt_start,
        DTEND=dt_end,
        DTSTAMP=create_time,
        UID="{}-11@appgenix-software.com".format(create_time),
        SEQUENCE="0",
        CREATED=create_time,
        DESCRIPTION=DESCRIPTION,
        LAST_MODIFIED=create_time,
        LOCATION=LOCATION,
    )


def make_ics(calendar_name, summary, begin_time, end_time, description, website):
    begin_time = time.localtime(begin_time)
    calendar = Calendar(calendar_name=calendar_name)
    add_event(calendar,
              SUMMARY=summary,
              DTSTART=datetime.datetime(year=begin_time.tm_year, month=begin_time.tm_mon, day=begin_time.tm_mday, hour=begin_time.tm_hour, minute=begin_time.tm_min, second=begin_time.tm_sec),
              DTEND=datetime.datetime(year=2019, month=2, day=19, hour=21, minute=30, second=00),
              DESCRIPTION="测试事件",
              LOCATION="我也不知道在哪儿")
    print(calendar.get_ics_text())
    calendar.save_as_ics_file()


if __name__ == '__main__':
    make_ics()

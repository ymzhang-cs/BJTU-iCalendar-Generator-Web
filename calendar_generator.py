#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from ics import Calendar, Event
from ics.grammar.parse import ContentLine
import pytz
import logging

logger = logging.getLogger(__name__)

# 添加时区 Asia/Shanghai
SHANGHAI_TZ = pytz.timezone("Asia/Shanghai")

# 课程时间段对应的具体时间
TIME_SLOTS = {
    1: "08:00",
    2: "10:10",
    3: "12:10",
    4: "14:10",
    5: "16:20",
    6: "19:00",
    7: "21:00",
}

# 错峰上课时间段
# 思源西楼、逸夫楼第二节课错后20分钟，其余不变
STAGGERED_KEYWORD = ['思源西楼','逸夫教学楼']
STAGGERED_TIME_SLOTS = {
    1: "08:00",
    2: "10:30",
    3: "12:10",
    4: "14:10",
    5: "16:20",
    6: "19:00",
    7: "21:00",
}

# 星期映射 (iCalendar 格式)
WEEKDAY_MAP = {
    1: "MO",
    2: "TU",
    3: "WE",
    4: "TH",
    5: "FR",
    6: "SA",
    7: "SU"
}

class BJTUCalendarGenerator:
    """北京交通大学课表日历生成器"""
    
    def __init__(self):
        pass

    def generate_from_html(self, html_file_path, semester_start=None):
        """从HTML文件生成ICS日历内容"""
        try:
            # 如果没有提供学期开始日期，使用默认值
            if semester_start is None:
                semester_start = self._get_default_semester_start()
            
            # 解析HTML文件
            parser = Parser(html_file_path)
            data = parser.parse()
            
            if not data:
                raise ValueError("未能从HTML文件中解析出课程信息")
            
            # 生成ICS内容
            writer = Writer(data, semester_start)
            cal = writer.generate_ics()
            
            # 转换为字符串
            ics_content = str(cal)
            return ics_content
            
        except Exception as e:
            logger.error(f"生成ICS文件时出错: {str(e)}")
            raise

    def _get_default_semester_start(self):
        """获取默认学期开始日期"""
        # 默认使用当前年份的9月第一个周一
        now = datetime.now()
        year = now.year
        
        # 如果当前月份小于9月，使用上一年的9月
        if now.month < 9:
            year -= 1
        
        # 找到9月第一个周一
        september_first = datetime(year, 9, 1)
        days_ahead = 0 - september_first.weekday()  # 周一是0
        if days_ahead <= 0:
            days_ahead += 7
        
        semester_start = september_first + timedelta(days=days_ahead)
        return semester_start

class Parser:
    """课表HTML解析器"""
    
    def __init__(self, file_path):
        self.file_path = file_path

    def parse(self):
        """
        解析课表 HTML 文件，返回解析后的数据
        数据格式：
        [
            {
                "course_id": "M402004B",
                "class_id": "03",
                "name": "软件工程",
                "time": {
                    "weekday": 1,
                    "lesson": 1,
                },
                "teacher": "魏名元",
                "location": "逸夫教学楼 YF415",
                "weeks": {
                    "type": "continuous",
                    "data": {
                        "start": 1,
                        "end": 16,
                    },
                }
                // OR
                "weeks": {
                    "type": "discontinuous",
                    "data": [2, 4, 6, 8, 10, 12, 14, 16],
                }
                // OR
                "weeks": {
                    "type": "interval",
                    "data": {
                        "start": 1,
                        "interval": 2,
                        "count": 8,
                    },
                }
            }
        ]
        """
        
        # 解析后的数据
        parsed_data = []
        
        with open(self.file_path, "r", encoding="utf-8") as f:
            html = f.read()
        
        # 使用 BeautifulSoup 解析 HTML
        soup = BeautifulSoup(html, "html.parser")
        
        # 选择表格：<table class="table table-bordered">
        table = soup.find("table", class_="table table-bordered")
        
        if not table:
            # 如果没有找到特定class的表格，尝试查找其他表格
            tables = soup.find_all("table")
            if tables:
                table = tables[0]  # 使用第一个表格
            else:
                raise ValueError("未找到课表表格")
        
        # 选择表格中的所有行：<tr>
        rows = table.find_all("tr")
        
        # 遍历每一行 tr
        # 第一行是表头，不需要解析
        for lesson_idx, row in enumerate(rows[1:], start=1):
            # 选择行中的所有单元格：<td>
            cells = row.find_all("td", recursive=False)
            
            # 遍历每一个单元格 td
            # 第一个单元格是时间，不需要解析
            for weekday_idx, cell in enumerate(cells[1:], start=1):
                
                # 遍历每一个div
                for div in cell.find_all("div", recursive=False):
                    try:
                        # 解析课程信息
                        course_info = div.find("span").get_text().strip()
                        course_id, class_id, name = re.match(r"(\w+) \[(\w+)\]\s+(.+)", course_info).groups()
                        
                        # 解析上课周数和老师
                        week_teacher_info = div.find_all("div")[0]
                        weeks_str, teacher_str = week_teacher_info.get_text().strip().split("\n")
                        # 去除老师前面的空格
                        teacher = teacher_str.strip()
                        # 识别周数格式
                        time_type, time_data = week_type_detect(weeks_str)
                        
                        # 解析上课地点
                        # 20250905 修改：发现学校教务系统添加了校区信息，并且分隔使用", " 这里暂时只取第2个和第3个
                        location_spans = div.find_all("span")
                        if len(location_spans) > 1:
                            location = location_spans[1].get_text().strip().split(", ")
                            if len(location) >= 3:
                                location = location[1] + " " + location[2]
                            else:
                                location = location_spans[1].get_text().strip()
                        else:
                            location = "未知地点"
                        
                        # 保存解析后的数据
                        parsed_data.append({
                            "course_id": course_id,
                            "class_id": class_id,
                            "name": name,
                            "time": {"weekday": weekday_idx, "lesson": lesson_idx},
                            "teacher": teacher,
                            "location": location,
                            "weeks": {"type": time_type, "data": time_data}
                        })
                    except Exception as e:
                        logger.warning(f"解析课程信息时出错: {str(e)}")
                        continue

        return parsed_data

def week_type_detect(weeks_str):
    """
    判断周数格式，并返回 time_type 和 time_data
    time_type: "continuous", "discontinuous", "interval"
    time_data:
        - continuous: {"start": int, "end": int}
        - discontinuous: [int, int, ...]
        - interval: {"start": int, "interval": int, "count": int}
    """
    
    if "-" in weeks_str:
        match = re.match(r"第(\d+)-(\d+)周", weeks_str)
        if match:
            start_week, end_week = match.groups()
            time_type = "continuous"
            time_data = {"start": int(start_week), "end": int(end_week)}
        else:
            raise ValueError(f"Unknown week format: {weeks_str}")
    elif ", " in weeks_str:
        match = re.match(r"第(.+)周", weeks_str)
        if match:
            weeks = match.groups()[0].split(", ")
            time_type = "discontinuous"
            time_data = [int(week) for week in weeks]
            # 进一步判断是否为间隔周数
            if len(time_data) > 2:
                interval = time_data[1] - time_data[0]
                if all(time_data[i] - time_data[i-1] == interval for i in range(1, len(time_data))):
                    time_type = "interval"
                    time_data = {"start": time_data[0], "interval": interval, "count": len(time_data)}
        else:
            raise ValueError(f"Unknown week format: {weeks_str}")
    else:
        raise ValueError(f"Unknown week format: {weeks_str}")
    
    return time_type, time_data

class Writer:
    """ICS文件写入器"""
    
    def __init__(self, data, semester_start):
        """
        :param data: 课程数据列表
        :param semester_start: 学期开始日期 (datetime 类型)
        """
        self.data = data
        self.semester_start = semester_start  # 例如 datetime(2025, 3, 3)

    def generate_ics(self):
        """生成 ICS 日历"""
        cal = Calendar()

        for course in self.data:
            course_name = course["name"]
            teacher = course["teacher"]
            location = course["location"]
            weekday = course["time"]["weekday"]
            lesson = course["time"]["lesson"]
            weeks_data = course["weeks"]

            # 计算上课开始时间
            if any(keyword in location for keyword in STAGGERED_KEYWORD):
                start_time = STAGGERED_TIME_SLOTS.get(lesson)
            else:
                start_time = TIME_SLOTS.get(lesson)
            if not start_time:
                continue  # 避免无效时间段

            # 计算课程首次上课日期
            first_week = self.get_first_week(weeks_data)
            first_class_date = self.semester_start + timedelta(days=(first_week - 1) * 7 + (weekday - 1))
            start_dt = datetime.combine(first_class_date, datetime.strptime(start_time, "%H:%M").time())
            
            # 转换为 Asia/Shanghai 时区
            start_dt = SHANGHAI_TZ.localize(start_dt).astimezone(pytz.utc)
            end_dt = start_dt + timedelta(minutes=110 if lesson != 7 else 50)

            event = Event()
            event.name = f"{course_name} - {teacher}"
            event.begin = start_dt
            event.end = end_dt
            event.location = location

            # 生成 RRULE
            rrule = self.get_rrule(weeks_data, weekday)
            if rrule:
                event.extra.append(ContentLine(name="RRULE", value=rrule))  # ✅ 这里使用 ContentLine

            cal.events.add(event)

        return cal

    def get_first_week(self, weeks_data):
        """获取课程的第一次上课周"""
        if weeks_data["type"] == "continuous":
            return weeks_data["data"]["start"]
        elif weeks_data["type"] == "discontinuous":
            return min(weeks_data["data"])
        elif weeks_data["type"] == "interval":
            return weeks_data["data"]["start"]
        return 1  # 默认第 1 周

    def get_rrule(self, weeks_data, weekday):
        """生成 RRULE 规则"""
        week_day = WEEKDAY_MAP[weekday]

        if weeks_data["type"] == "continuous":
            start = weeks_data["data"]["start"]
            end = weeks_data["data"]["end"]
            count = end - start + 1
            return f"FREQ=WEEKLY;BYDAY={week_day};COUNT={count}"

        elif weeks_data["type"] == "discontinuous":
            weeks = weeks_data["data"]
            weeks_str = ",".join(str(w) for w in weeks)
            return f"FREQ=WEEKLY;BYDAY={week_day};BYSETPOS={weeks_str}"

        elif weeks_data["type"] == "interval":
            start = weeks_data["data"]["start"]
            interval = weeks_data["data"]["interval"]
            count = weeks_data["data"]["count"]
            return f"FREQ=WEEKLY;INTERVAL={interval};BYDAY={week_day};COUNT={count}"

        return None

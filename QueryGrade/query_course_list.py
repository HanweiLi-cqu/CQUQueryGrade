from bs4 import BeautifulSoup
import json
import time
import re
import prettytable as pt
from typing import Dict
from requests import Session
from requests.sessions import session
from .login import login
from .database_utils import *
from .query_grade import get_oauth_token,headers
#查询已经选择的课程
def get_selected_list(session: Session)->Dict:
    get_oauth_token(session)
    req=session.get(url="http://my.cqu.edu.cn/api/enrollment/enrollment/registered",headers=headers)
    return json.loads(req.text)

def query_session(username: str, password: str) -> str:
    session_service="http://my.cqu.edu.cn/authserver/authentication/cas"
    course_session = login(username, password, session_service)
    selected_courses=get_selected_list(course_session)
    courses_table = pt.PrettyTable(["课程", "学分","学院","必修/选修", "老师"])
    for items in selected_courses["alreadySelectCourseListVOs"]:
        item=items["selectCourseVOList"][0]
        courses_table.add_row([item["courseName"],item["courseCredit"],item["courseDeptName"],item["courseNature"],item["instructorNames"]])
    print(courses_table)
    

def query_major_course(username: str, password: str):
    session_service="http://my.cqu.edu.cn/authserver/authentication/cas"
    course_session = login(username, password, session_service)
    get_oauth_token(course_session)
    courses_table = pt.PrettyTable(["课程", "学分","学院","必修/选修","是否选满"])
    all_course_list=course_session.get(url="http://my.cqu.edu.cn/api/enrollment/enrollment/course-list",
                         params={
                            "selectionSource": "主修"
                        },
                        headers=headers)
    all_course=json.loads(all_course_list.text)
    for items in all_course["data"][0]["courseVOList"]:
        if(items["courseEnrollSign"]== None):
            courses_table.add_row([items["name"],items["credit"],items["departmentName"],items["courseNature"],"未满"])
        elif(items["courseEnrollSign"]== "已选"):
            courses_table.add_row([items["name"],items["credit"],items["departmentName"],items["courseNature"],"√"])
        else:
            courses_table.add_row([items["name"],items["credit"],items["departmentName"],items["courseNature"],"已满"])
    print(courses_table)



from bs4 import BeautifulSoup
import json
import time
import re
import prettytable as pt
from typing import Dict
from requests import Session
from .login import login
from .database_utils import *

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}

path = "source/Course_2020_07_05.xls"


def current_milli_time():
    return str(int(round(time.time() * 1000)))


def course_page_formdata(course_code: str, session_id: str, form_key: str, csrf_token: str) -> Dict:
    return {
        "courseRangerStr": "全校",
        "selectedLineIndex": "",
        "_checked": "on",
        "searchCourseWrapperContent.courseStatus": "",
        "searchCourseWrapperContent.name": "",
        "searchCourseWrapperContent.codeR": course_code,
        "searchCourseWrapperContent.departmentId": "",
        "searchCourseWrapperContent.degree": "",
        "searchCourseWrapperContent.instNameCodeStr": "",
        "_cmCourseLookUpWrappers[0].checked": "on",
        "umsfz1p_length": "100",
        "pageId": "pageLookUpCourse",
        "viewId": "StartProposalView",
        "formKey": form_key,
        "requestedFormKey": "",
        "sessionId": session_id,
        "flowKey": "",
        "view.applyDirtyCheck": "true",
        "dirtyForm": "false",
        "renderedInDialog": "false",
        "view.singlePageView": "false",
        "view.disableBrowserCache": "true",
        "csrfToken": csrf_token,
        "methodToCall": "searchCourseByFilter",
        "ajaxReturnType": "update-page",
        "ajaxRequest": "true",
        "triggerActionId": "searchCourseCodeInputBetweenBtn",
        "focusId": "searchCourseCodeInputBetweenBtn",
        "csrfToken": csrf_token
    }


def ajax_formdata(formKey: str) -> Dict:
    return {
        "methodToCall": "tableJsonRetrieval",
        "updateComponentId": "LookUpCourseTableList",
        "formKey": formKey,
        "ajaxReturnType": "update-component",
        "ajaxRequest": "true",
        "sEcho": "1",
        "iColumns": "11",
        "sColumns": ",,,,,,,,,,",
        "iDisplayStart": "0",
        "iDisplayLength": "100",
        "mDataProp_0": "function",
        "sSearch_0": "",
        "bRegex_0": "false",
        "bSearchable_0": "true",
        "mDataProp_1": "function",
        "sSearch_1": "",
        "bRegex_1": "false",
        "bSearchable_1": "true",
        "mDataProp_2": "function",
        "sSearch_2": "",
        "bRegex_2": "false",
        "bSearchable_2": "true",
        "mDataProp_3": "function",
        "sSearch_3": "",
        "bRegex_3": "false",
        "bSearchable_3": "true",
        "mDataProp_4": "function",
        "sSearch_4": "",
        "bRegex_4": "false",
        "bSearchable_4": "true",
        "mDataProp_5": "function",
        "sSearch_5": "",
        "bRegex_5": "false",
        "bSearchable_5": "true",
        "mDataProp_6": "function",
        "sSearch_6": "",
        "bRegex_6": "false",
        "bSearchable_6": "true",
        "mDataProp_7": "function",
        "sSearch_7": "",
        "bRegex_7": "false",
        "bSearchable_7": "true",
        "mDataProp_8": "function",
        "sSearch_8": "",
        "bRegex_8": "false",
        "bSearchable_8": "true",
        "mDataProp_9": "function",
        "sSearch_9": "",
        "bRegex_9": "false",
        "bSearchable_9": "true",
        "mDataProp_10": "function",
        "sSearch_10": "",
        "bRegex_10": "false",
        "bSearchable_10": "true",
        "sSearch": "",
        "bRegex": "false",
        "_": current_milli_time(),
    }


def get_course_page_params(session: Session) -> Dict:
    url = "http://my.cqu.edu.cn/cm/portal/course?methodToCall=getSearchCoursePage&viewId=StartProposalView"
    page = session.get(url=url, headers=headers)
    bf = BeautifulSoup(page.text, 'html.parser')
    return {
        "form_key": bf.find("input", {"name": "formKey"})['value'],
        "session_id": bf.find("input", {"name": "sessionId"})['value'],
        "csrf_token": bf.find("input", {"name": "csrfToken"})['value']
    }


def get_course_credit(session: Session, course_id: str, course_page_params: Dict) -> Dict:
    session_id = course_page_params["session_id"]
    form_key = course_page_params["form_key"]
    csrf_token = course_page_params["csrf_token"]
    course_page = session.post(
        url="http://my.cqu.edu.cn/cm/portal/course",
        data=course_page_formdata(course_id, session_id, form_key, csrf_token),
        headers=headers
    )
    soup = BeautifulSoup(course_page.text, 'html.parser')
    tds = soup.find("tbody").find("tr").findAll("td")[2:9]
    info = [td.text.strip() for td in tds]
    column = ['课程名', '课程代码', '开课学院', '层次', '授课老师', '课时', '学分']
    return dict(zip(column, info))
    # course_info = session.get(
    #     url="http://my.cqu.edu.cn/cm/portal/course",
    #     params=ajax_formdata(form_key),
    #     headers=headers
    # ).json()
    # for i in range(2, 9):
    #     key = 'c{}'.format(i)
    #     info_dic[column[i-2]] = course_info['aaData'][0][key]['val']
    # return info_dic

def get_oauth_token(session:Session):
    # 发送这个请求是为了获取后续的code
    response = session.get(
        url="http://my.cqu.edu.cn/authserver/oauth/authorize?client_id=enroll-prod&response_type=code&scope=all&state=&redirect_uri=http://my.cqu.edu.cn/enroll/token-index", allow_redirects=False)
    # 后续的code会隐藏在Location里面
    codeValue = response.headers['Location']
    # 采用正则表达式搜索=开始&结尾的字符串，并通过切片获得code内容
    codeValue = re.search(pattern=r'=.*?&', string=str(codeValue))
    codeValue = codeValue.group()[1:-1]
    # 构造formdata，除了code其它都是不变的
    token_data = {
        'client_id': 'enroll-prod',
        'client_secret': 'app-a-1234',
        'code': str(codeValue),
        'redirect_uri': 'http://my.cqu.edu.cn/enroll/token-index',
        'grant_type': 'authorization_code'
    }
    # 发送post请求获取到token
    access_token = session.post(
        url="http://my.cqu.edu.cn/authserver/oauth/token", data=token_data)
    token_response = json.loads(access_token.content)
    TOKEN = token_response['access_token']
    # 下面是获取个人信息，可以不用这一步，不过这个链接可以用来统一认证
    final = session.get(
        url='http://my.cqu.edu.cn/authserver/simple-user', headers=headers)
    json_text = json.loads(final.text)
    json_item = json_text.items()
    res_dic = {}
    for key, value in json_item:
        if(key == 'krimPermTDTOS'):
            break
        res_dic[key] = value
    # 构造查询寻成绩是个人认证的Authorization
    headers['Authorization'] = "Bearer "+TOKEN

def get_grade(session: Session) -> Dict:
    get_oauth_token(session)
    session.get(
        url="http://my.cqu.edu.cn/resource-api/session/info-detail", headers=headers)
    score = session.get(
        url="http://my.cqu.edu.cn/api/sam/score/student/score", headers=headers)
    return json.loads(score.text)


def query_grade(username: str, password: str, output: bool = True, online: bool = False) -> str:
    grade_service = "http://my.cqu.edu.cn/authserver/authentication/cas"
    grade_session = login(username, password, grade_service)
    if online == True:
        course_service = "http://my.cqu.edu.cn/cm/portal/course"
        course_session = login(username, password, course_service)
        course_page_params = get_course_page_params(course_session)
    else:
        enegine = getEngine()
    grades = get_grade(grade_session)
    course_dic = []  # 课程成绩，学分
    total_credits = 0  # 总学分
    table = pt.PrettyTable(['课程名称', '课程性质', '成绩', '修读性质', '课程代码', '学分'])
    for key, items in grades['data'].items():
        if output:
            print("学期--{}".format(key))
        for item in items:
            if online == True:
                Course_Info = get_course_credit(
                    course_session, item["courseCode"], course_page_params)  # 查询课程学分
            else:
                Course_Info = get_item_by_id(enegine, item["courseCode"])
            table.add_row([item['courseName'], item['courseNature'], item['effectiveScoreShow'],
                           item['studyNature'], item['courseCode'], Course_Info['学分']])
            course_dic.append(
                {"成绩": item['effectiveScoreShow'], "学分": Course_Info['学分']})
            total_credits = total_credits+eval(str(Course_Info['学分']))
        # 打印成绩
        if output:
            print(table)
    five_credits = 0
    four_credits = 0
    avarage_score = 0
    five_level = {"优": 90, "良": 85, "中": 75, "及格": 65, "不及格": 50}
    two_level = {"合格": 85, "不合格": 50}
    for item in course_dic:
        if item['成绩'] in five_level.keys():
            score = five_level[item['成绩']]
        elif item['成绩'] in two_level.keys():
            score = two_level[item['成绩']]
        elif item['成绩'] == None:
            print("没成绩")
            print("优为90,良为85，中为75，及格为65，不及格为50\n合格为85，不合格为50")
            tempscore=int(input("请输入你的分数区间："))
            score = tempscore
        else:
            score = eval(item["成绩"])
        avarage_score += score*eval(str(item["学分"]))
        if score < 60:
            five_credits += 0
            four_credits += 0
        else:
            five_credits += eval(str(item["学分"])) * (1 + (score-60)/10)
            if score > 90:
                score = 90
            four_credits += eval(str(item["学分"])) * (1 + (score-60)/10)
    avarage_score /= total_credits
    five_credits /= total_credits
    four_credits /= total_credits
    credits_table = pt.PrettyTable(["总学分", "平均分", "5分制绩点", "4分制绩点"])
    credits_table.add_row(
        [total_credits, avarage_score, five_credits, four_credits])
    if output:
        print(credits_table)
    if online==False:
        enegine.dispose()
    return table.get_string() + "\n" + credits_table.get_string()

# CQUQueryGrade
重庆大学学生成绩查询（新教务网），也可以参考思路实现认证<br>
注意：统一认证网页输入的学号和密码一旦错三次将会产生验证码认证，该脚本并未实现验证码处理，所以三次以内必须输入正确用户名和密码

## 快速开始
```bash
python -m venv .venv
source .venv/bin/activate  # 环境激活因平台而异
pip install -r requirements.txt
python main.py
```

## 更新
为了更加快速，选择将课程处理成db文件，而不是发生请求获取课程信息。如果需要联网查询子只需要将`QueryGrade\\query_grade.py`的`online`修改成true

## 21.8.30更新
- 将Oauth认证模块单独提取成函数，放在了`QueryGrade\\query_grade.py`里面
- 加入了查询已经选择课程的函数`QueryGrade\\query_course_list.py`，调用方式见main.py。
- 加入了查询本学期的专业课程选课情况`QueryGrade\\query_course_list.py`，调用方式见main.py。

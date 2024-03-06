from QueryGrade.query_grade import query_grade
from QueryGrade.query_course_list import query_session,query_major_course


if __name__ == "__main__":
    username = input("学号(统一认证号): ")
    password = input("密码:")
    while True:
        print("功能：\n\t1-->查询成绩\n\t2-->查询已选择课程\n\t3-->查询本学期选修、必修\n\tq-->退出")
        num=str(input("输入序号："))
        if num=='1':
            query_grade(username, password)
        elif num=='2':
            query_session(username, password)
        elif num=='3':
            query_major_course(username, password)
        elif num=='q':
            break
        else:
            print("请输入有效字符")

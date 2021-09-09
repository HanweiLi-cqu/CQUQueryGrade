from sqlalchemy import create_engine, engine, text
from sqlalchemy.orm import sessionmaker
from typing import Dict


def to_dict(data) -> Dict:
    my_column = ['课程名', '课程代码', '开课学院', '层次', '授课老师', '课时', '学分']
    return dict(zip(my_column, data))


def getEngine() -> engine:
    engine = create_engine('sqlite:///source/course.db',
                           connect_args={'check_same_thread': False})
    return engine


def get_item_by_id(engine: engine, course_id: str) -> Dict:
    session = sessionmaker(engine)()
    sql = """
          select  `课程名称`, `代码`, `部门`,`层次`,`课程负责人`,`总学时`,`学分`
          from  `course`  where 代码=:course_id ;
          """
    res = session.execute(text(
        sql), {"course_id": course_id}).fetchone()

    return to_dict(res)

# enegine=generateDatabase(path)
# get_item_by_id(enegine,'AEME21111')

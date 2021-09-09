import pandas as pd
from sqlalchemy import create_engine


def generate_database(path: str) -> None:
    """Excel数据转储到sqlite中
    """
    df = pd.read_excel(path, header=1)
    try:
        engine = create_engine('sqlite:///source/course.db',
                               connect_args={'check_same_thread': False})
        df.to_sql('course', engine)
    except ValueError:
        print("已经存在了")


generate_database("../source/Course_2020_07_05.xls")

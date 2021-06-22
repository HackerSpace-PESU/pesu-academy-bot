import requests
import pandas as pd
from io import StringIO

df = None
unique_department = set()
unique_campus = set()
unique_course = set()


def readDataFrame():
    global df
    df_link = "https://raw.githubusercontent.com/aditeyabaral/pesu-academy-bot/main/data/faculty.csv"
    response = requests.get(df_link)
    df_content = StringIO(response.content.decode())
    df = pd.read_csv(df_content, sep=',')
    df = df[~df["COURSE"].isna()]


def initialiseFacultyFilters():
    global unique_department
    global unique_campus
    global unique_course

    for row in df.iterrows():
        row = dict(row[1])
        department = row["DEPARTMENT"].lower()
        campus = row["CAMPUS"].lower()
        if not isinstance(row["COURSE"], float):
            course = set([c.lower().strip() for c in row["COURSE"].split(',')])
            unique_course.update(course)
        unique_department.add(department)
        unique_campus.add(campus)


def getFacultyFilterType(queries):
    query_data = list()
    for query in queries:
        query = query.lower()
        if query in unique_campus:
            query_type = "CAMPUS"
        elif query in unique_course:
            query_type = "COURSE"
        elif query in unique_department:
            query_type = "DEPARTMENT"
        else:
            query_type = "NAME"
        query_data.append({query: query_type})
    return query_data


def getFacultyResultsByNameOrCampusOrDepartment(search_query, query_type):
    result = list()
    if query_type in ["NAME", "CAMPUS", "DEPARTMENT"]:
        search_query = search_query.lower()
        for row in df.iterrows():
            row = dict(row[1])
            search_query_field_value = row[query_type].lower()
            if search_query in search_query_field_value:
                result.append(row)
    return result


def getFacultyResultsByCourse(search_course):
    result = list()
    search_course = search_course.lower()
    for row in df.iterrows():
        row = dict(row[1])
        if isinstance(row["COURSE"], float):
            continue
        courses = [c.lower().strip() for c in row["COURSE"].split(',')]
        if search_course in courses:
            result.append(row)
    return result


def getFacultyResultsByTwoFilters(search_query_1, search_query_2, query_type_1, query_type_2):
    result = list()
    if query_type_1 in ["COURSE", "CAMPUS", "DEPARTMENT"] and query_type_2 in ["COURSE", "CAMPUS", "DEPARTMENT"]:
        search_query_1 = search_query_1.lower()
        search_query_2 = search_query_2.lower()
        for row in df.iterrows():
            row = dict(row[1])
            search_query_field_value_1 = row[query_type_1].lower()
            search_query_field_value_2 = row[query_type_2].lower()

            if query_type_1 == "COURSE" or query_type_2 == "COURSE":
                if isinstance(row["COURSE"], float):
                    continue
                courses = [c.lower().strip() for c in row["COURSE"].split(',')]
                if query_type_1 == "COURSE":
                    search_query_field_value_1 = courses
                if query_type_2 == "COURSE":
                    search_query_field_value_2 = courses

            if search_query_1 in search_query_field_value_1 and search_query_2 in search_query_field_value_2:
                result.append(row)

    return result


def getFacultyResultsByThreeFilters(search_query_1, search_query_2, search_query_3, query_type_1, query_type_2, query_type_3):
    result = list()
    if query_type_1 in ["COURSE", "CAMPUS", "DEPARTMENT"] and query_type_2 in ["COURSE", "CAMPUS", "DEPARTMENT"] and query_type_3 in ["COURSE", "CAMPUS", "DEPARTMENT"]:
        search_query_1 = search_query_1.lower()
        search_query_2 = search_query_2.lower()
        search_query_3 = search_query_3.lower()
        for row in df.iterrows():
            row = dict(row[1])
            search_query_field_value_1 = row[query_type_1].lower()
            search_query_field_value_2 = row[query_type_2].lower()
            search_query_field_value_3 = row[query_type_3].lower()

            if query_type_1 == "COURSE" or query_type_2 == "COURSE" or query_type_3 == "COURSE":
                if isinstance(row["COURSE"], float):
                    continue
                courses = [c.lower().strip() for c in row["COURSE"].split(',')]
                if query_type_1 == "COURSE":
                    search_query_field_value_1 = courses
                if query_type_2 == "COURSE":
                    search_query_field_value_2 = courses
                if query_type_3 == "COURSE":
                    search_query_field_value_3 = courses

            if search_query_1 in search_query_field_value_1 and search_query_2 in search_query_field_value_2 and search_query_3 in search_query_field_value_3:
                result.append(row)

    return result


def getFacultyResultsByFilters(query_data):
    result = list()
    for row in df.iterrows():
        flag = True
        row = dict(row[1])
        for filter in query_data:
            query, query_type = list(filter.items())[0]
            query_search_field_value = row[query_type].lower()
            if query_type == 'NAME' and query in query_search_field_value:
                result.append(row)
                return result
            if query_type == "COURSE":
                if isinstance(row["COURSE"], float):
                    continue
                courses = [c.lower().strip() for c in row["COURSE"].split(',')]
                query_search_field_value = courses
            if query not in query_search_field_value:
                flag = False
        if flag:
            result.append(row)
    return result


def getFacultyResults(queries):
    query_data = getFacultyFilterType(queries)
    num_queries = len(query_data)
    if num_queries == 1:
        query, query_type = list(query_data[0].items())[0]
        if query_type == "COURSE":
            result = getFacultyResultsByCourse(query)
        else:
            result = getFacultyResultsByNameOrCampusOrDepartment(
                query, query_type)
    elif num_queries == 2:
        query_1, query_type_1 = list(query_data[0].items())[0]
        query_2, query_type_2 = list(query_data[1].items())[0]
        result = getFacultyResultsByTwoFilters(
            query_1, query_2, query_type_1, query_type_2)
    elif num_queries == 3:
        query_1, query_type_1 = list(query_data[0].items())[0]
        query_2, query_type_2 = list(query_data[1].items())[0]
        query_3, query_type_3 = list(query_data[2].items())[0]
        result = getFacultyResultsByThreeFilters(
            query_1, query_2, query_3, query_type_1, query_type_2, query_type_3)
    else:
        result = getFacultyResultsByFilters(query_data)
    return result

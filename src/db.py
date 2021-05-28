import re
import os
from sqlalchemy import create_engine, MetaData, Table, and_
from sqlalchemy.engine import result
from sqlalchemy.orm import sessionmaker
from dbmodels import Student, Guild
from dotenv import load_dotenv

load_dotenv()
pesudb_engine = create_engine(os.environ["PESU_DATABASE_URL"])
pesudb_connection = pesudb_engine.connect()
pesudb_metadata = MetaData()
pesudb_Session = sessionmaker(bind=pesudb_engine)
pesudb_session = pesudb_Session()

guilddb_engine = create_engine(os.environ["SERVER_CHANNEL_DATABASE_URL"])
guilddb_connection = guilddb_engine.connect()
guilddb_metadata = MetaData()
guilddb_metadata.bind = guilddb_engine
guilddb_Session = sessionmaker(bind=guilddb_engine)
guilddb_session = guilddb_Session()
guilddb_table = Table("guild", guilddb_metadata,
                      autoload=True, autoload_with=guilddb_engine)


def processFilter(filter_type, filter):
    filter_value_map = {
        "DES": "B.DES",
        "RR": "RING ROAD",
        "EC": "ELECTRONIC CITY",
        "PHY": "PHYSICS CYCLE",
        "CHEM": "CHEMISTRY CYCLE"
    }

    if filter_type == "section":
        filter = f"SECTION {filter}"
    if filter_type in ["campus", "cycle"]:
        filter = filter_value_map[filter]
    if filter_type == "branch" and filter == "DES":
        filter = "B.DES"
    if filter_type == "semester":
        filter = f"SEM-{filter}"
    return filter


def getFilterType(filters):
    permitted_filters = {
        "branch": ['CSE', 'ECE', 'EEE', 'ME', 'CV', 'BT', 'BBA', 'BBA-HEM', 'BBA-LLB', 'DES'],
        "section": [chr(i) for i in range(65, 75)],
        "cycle": ["PHY", "CHEM"],
        "semester": ['1', '2', '3', '4', '5', '6', '7', '8'],
        "campus": ["RR", "EC"]
    }

    filter_tags = dict()
    for filter in filters:
        found = False
        for filter_type in permitted_filters:
            if filter in permitted_filters[filter_type]:
                filter = processFilter(filter_type, filter)
                if filter_type not in filter_tags:
                    filter_tags[filter_type] = list()
                filter_tags[filter_type].append(filter)
                found = True
        if not found:
            prn_pattern = re.compile(r"PES(1|2)201\d{6}")
            srn_pattern = re.compile(r"PES(1|2)UG19*")
            if re.match(prn_pattern, filter):
                if "prn" not in filter_tags:
                    filter_tags["prn"] = list()
                filter_tags["prn"].append(filter)

            elif re.match(srn_pattern, filter):
                if "srn" not in filter_tags:
                    filter_tags["srn"] = list()
                filter_tags["srn"].append(filter)

            else:
                if "name" not in filter_tags:
                    filter_tags["name"] = list()
                filter_tags["name"].append(filter)

    return filter_tags


def getQueryType(query):
    permitted_filters = {
        "branch": ['CSE', 'ECE', 'EEE', 'ME', 'CV', 'BT', 'BBA', 'BBA-HEM', 'BBA-LLB', 'DES'],
        "section": [chr(i) for i in range(65, 75)],
        "cycle": ["PHY", "CHEM"],
        "semester": ['1', '2', '3', '4', '5', '6', '7', '8'],
        "campus": ["RR", "EC"]
    }

    if re.match(r'^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$', query):
        return "email"
    elif re.match(r'PES(1|2)201\d{6}', query):
        return "PRN"
    elif re.match(r"PES(1|2)UG19*", query):
        return "SRN"
    else:
        for pf in permitted_filters:
            if query in permitted_filters[pf]:
                return pf
        return "name"


def getQueryResult(filter_tags=None):
    if filter_tags is None:
        result = pesudb_session.query(Student).all()
    else:
        if "name" in filter_tags:
            result = list()
            for name in filter_tags["name"]:
                temp_result = pesudb_session.query(Student).filter(
                    Student.name.ilike(f"%{name}%"))
                result.append(temp_result)
            result = result[0].union(*result[1:])

        elif "srn" in filter_tags:
            result = pesudb_session.query(Student).filter(
                Student.srn.in_(filter_tags["srn"]))

        elif "prn" in filter_tags:
            result = pesudb_session.query(Student).filter(
                Student.prn.in_(filter_tags["prn"]))

        else:

            result = pesudb_session.query(Student)
            if "branch" in filter_tags:
                result = result.filter(
                    Student.branch.in_(filter_tags["branch"]))

            if "section" in filter_tags:
                result = result.filter(
                    Student.section.in_(filter_tags["section"]))

            if "campus" in filter_tags:
                result = result.filter(
                    Student.campus.in_(filter_tags["campus"]))

            if "semester" in filter_tags:
                result = result.filter(
                    Student.semester.in_(filter_tags["semester"]))

            if "department" in filter_tags:
                result = result.filter(
                    Student.department.in_(filter_tags["department"]))

            if "cycle" in filter_tags:
                result = result.filter(Student.cycle.in_(filter_tags["cycle"]))
    listResult, truncated = getListResult(result)
    return listResult, truncated


def getListResult(result):
    records = result.all()
    list_result = list()
    for record in records:
        student = record.__dict__
        tuple_rec = (student["prn"], student["srn"], student["name"],
                     student["semester"], student["section"], student["cycle"],
                     student["department"], student["branch"], student["campus"],
                     student["phone"], student["email"])
        list_result.append(tuple_rec)
    truncated = len(list_result) > 5
    return list_result[:5], truncated


def searchPESUDatabase(filters):
    if len(filters) == 1:
        query = filters[0]
        queryType = getQueryType(query)
        query = processFilter(queryType, query)
        if queryType == "email":
            result = pesudb_session.query(
                Student).filter(Student.email == query)
        elif queryType == "PRN":
            result = pesudb_session.query(Student).filter(Student.prn == query)
        elif queryType == "SRN":
            result = pesudb_session.query(Student).filter(Student.srn == query)
        elif queryType == "branch":
            result = pesudb_session.query(
                Student).filter(Student.branch == query)
        elif queryType == "section":
            result = pesudb_session.query(
                Student).filter(Student.section == query)
        elif queryType == "cycle":
            result = pesudb_session.query(
                Student).filter(Student.cycle == query)
        elif queryType == "semester":
            result = pesudb_session.query(
                Student).filter(Student.semester == query)
        elif queryType == "campus":
            result = pesudb_session.query(
                Student).filter(Student.campus == query)
        else:
            query = query.upper()
            result = pesudb_session.query(Student).filter(
                Student.name.ilike(f"%{query}%"))
        listResult, truncated = getListResult(result)
        return listResult, truncated

    else:
        filters = [i.strip() for i in filters]
        filter_tags = getFilterType(filters)
        listResult, truncated = getQueryResult(filter_tags)
        return listResult, truncated


def addGuild(guild_id, guild_name, channel_id=None, channel_type=None):
    query = guilddb_table.insert().values(guild_id=guild_id, guild_name=guild_name,
                                          channel_id=channel_id, channel_type=channel_type)
    result = guilddb_connection.execute(query)


def removeGuild(guild_id):
    query = guilddb_table.delete().where(guilddb_table.c.guild_id == guild_id)
    result = guilddb_connection.execute(query)


def addChannel(guild_id, guild_name, channel_id, channel_type):
    query = guilddb_table.select().where(and_(guilddb_table.c.guild_id == guild_id, guilddb_table.c.channel_id ==
                                              None, guilddb_table.c.channel_type == None))
    result = guilddb_connection.execute(query).fetchall()
    if result:
        query = guilddb_table.update().where(and_(guilddb_table.c.guild_id == guild_id, guilddb_table.c.channel_id ==
                                                None, guilddb_table.c.channel_type == None)).values(channel_id=channel_id, channel_type=channel_type)
        result = guilddb_connection.execute(query)
    else:
        addGuild(guild_id, guild_name, channel_id, channel_type)


def removeChannel(channel_id):
    query = guilddb_table.delete().where(guilddb_table.c.channel_id == channel_id)
    result = guilddb_connection.execute(query)


def checkServerChannelAndTypeExists(guild_id, channel_id, channel_type):
    query = guilddb_table.select().where(and_(guilddb_table.c.guild_id == guild_id,
                                              guilddb_table.c.channel_id == channel_id, guilddb_table.c.channel_type == channel_type))
    result = guilddb_connection.execute(query).fetchall()
    return bool(result)


def getCompleteDatabase():
    query = guilddb_table.select()
    result = guilddb_connection.execute(query).fetchall()
    return result

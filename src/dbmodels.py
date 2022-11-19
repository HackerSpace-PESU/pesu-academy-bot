from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

'''
class Student(Base):
    __tablename__ = "student"
    _id = Column(Integer, primary_key=True, autoincrement=True)
    srn = Column(String(50))
    prn = Column(String(50))
    name = Column(String(50))
    semester = Column(String(50))
    section = Column(String(50))
    cycle = Column(String(50))
    department = Column(String(50))
    branch = Column(String(50))
    campus = Column(String(50))
    email = Column(String(50))
    phone = Column(String(50))

    def __init__(self, srn, prn, name, semester, section, cycle, department, branch, campus, email, phone):
        self.srn = srn
        self.prn = prn
        self.name = name
        self.semester = semester
        self.section = section
        self.cycle = cycle
        self.department = department
        self.branch = branch
        self.campus = campus
        self.email = email
        self.phone = phone
'''

class Guild(Base):
    __tablename__ = "guild"
    _id = Column(Integer, autoincrement=True, primary_key=True)
    guild_id = Column(String(50), nullable=False)
    guild_name = Column(String(50), nullable=True)
    channel_type = Column(String(10), nullable=True)
    channel_id = Column(String(50), nullable=True)

    def __init__(self, guild_id, guild_name, channel_id, channel_type) -> None:
        self.guild_id = guild_id
        self.guild_name = guild_name
        self.channel_id = channel_id
        self.channel_type = channel_type


class Status(Base):
    __tablename__ = "status"
    variable = Column(String(30), primary_key=True)
    value = Column(String(10), nullable=False)

    def __init__(self, variable, value) -> None:
        self.variable = variable
        self.value = value

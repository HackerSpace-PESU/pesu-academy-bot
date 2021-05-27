import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()
engine = create_engine(os.environ["SERVER_CHANNEL_DATABASE_URL"])
connection = engine.connect()
metadata = MetaData()
Session = sessionmaker(bind=engine)
session = Session()


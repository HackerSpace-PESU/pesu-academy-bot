import os
import dotenv
from flask import Flask, redirect
from flask_sqlalchemy import SQLAlchemy

dotenv.load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ["SERVER_CHANNEL_DATABASE_URL"]
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Guild(db.Model):
    __tablename__ = "guild"
    _id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    guild_id = db.Column(db.String(50), nullable=False)
    guild_name = db.Column(db.String(50), nullable=True)
    channel_type = db.Column(db.String(10), nullable=True)
    channel_id = db.Column(db.String(50), nullable=True)

    def __init__(self, guild_id, guild_name, channel_id, channel_type) -> None:
        self.guild_id = guild_id
        self.guild_name = guild_name
        self.channel_id = channel_id
        self.channel_type = channel_type
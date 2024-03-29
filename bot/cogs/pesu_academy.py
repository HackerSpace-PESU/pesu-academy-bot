import base64
import datetime
import logging
import re
import traceback
from io import BytesIO
from pathlib import Path
from typing import Optional

import discord
import pytz
import requests_html
from bs4 import BeautifulSoup
from discord import app_commands
from discord.ext import commands, tasks

from .db import DatabaseCog

IST = pytz.timezone("Asia/Kolkata")


class PESUAcademyCog(commands.Cog):
    """
    This cog contains all commands and functionalities to interact with PESU Academy
    """

    def __init__(self, client: commands.Bot):
        self.client = client
        self.config = client.config
        self.db = client.db
        self.all_announcements = list()
        self.posted_announcements = list()

        self.update_announcements_loop.start()
        self.reset_announcements_loop.start()

    def cog_unload(self):
        self.update_announcements_loop.cancel()
        self.reset_announcements_loop.cancel()

    def get_announcement_embed(self, date: datetime.date, title: str, text: str):
        """
        Formats the announcement into an embed
        """
        if len(title) > 256:
            embed = discord.Embed(
                title=title[:253] + "...",
                description="..." + title[253:],
                color=discord.Color.blue()
            )
        else:
            embed = discord.Embed(title=title, color=discord.Color.blue())

        embed.description = text if len(text) < 4096 else text[:4093] + "..."

        embed.set_footer(text=date.strftime('%d %B %Y'))
        return embed

    @staticmethod
    def get_know_your_class_and_section(
            username: str,
            session: Optional[requests_html.HTMLSession] = None,
            csrf_token: Optional[str] = None,
    ):
        """
        Gets the student details from Know Your Class and Section
        """

        if not session:
            session = requests_html.HTMLSession()

        if not csrf_token:
            home_url = "https://www.pesuacademy.com/Academy/"
            response = session.get(home_url)
            soup = BeautifulSoup(response.text, "lxml")
            csrf_token = soup.find("meta", attrs={"name": "csrf-token"})["content"]

        try:
            response = session.post(
                "https://www.pesuacademy.com/Academy/getStudentClassInfo",
                headers={
                    "authority": "www.pesuacademy.com",
                    "accept": "*/*",
                    "accept-language": "en-IN,en-US;q=0.9,en-GB;q=0.8,en;q=0.7",
                    "content-type": "application/x-www-form-urlencoded",
                    "origin": "https://www.pesuacademy.com",
                    "referer": "https://www.pesuacademy.com/Academy/",
                    "sec-ch-ua": '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": '"Linux"',
                    "sec-fetch-dest": "empty",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-site": "same-origin",
                    "x-csrf-token": csrf_token,
                    "x-requested-with": "XMLHttpRequest"
                },
                data={
                    "loginId": username
                }
            )
        except Exception:
            logging.error(f"Unable to get profile from Know Your Class and Section: {traceback.format_exc()}")
            return {}

        soup = BeautifulSoup(response.text, "html.parser")
        profile = dict()
        for th, td in zip(soup.find_all("th"), soup.find_all("td")):
            key = th.text.strip()
            key = key.replace(" ", "_").lower()
            value = td.text.strip()
            profile[key] = value

        return profile

    async def get_announcements(self):
        """
        Fetches the available announcements
        """
        username = self.config["pesu"]["username"]
        password = self.config["pesu"]["password"]
        session = requests_html.HTMLSession()
        announcements = list()

        try:
            home_url = "https://www.pesuacademy.com/Academy/"
            response = session.get(home_url)
            soup = BeautifulSoup(response.text, "lxml")
            csrf_token = soup.find("meta", attrs={"name": "csrf-token"})["content"]
        except Exception as e:
            logging.error(f"Unable to fetch csrf token: {traceback.format_exc()}")
            session.close()
            return announcements

        data = {
            "_csrf": csrf_token,
            "j_username": username,
            "j_password": password,
        }

        try:
            auth_url = "https://www.pesuacademy.com/Academy/j_spring_security_check"
            response = session.post(auth_url, data=data)
            soup = BeautifulSoup(response.text, "lxml")
        except Exception as e:
            logging.error(f"Unable to authenticate: {traceback.format_exc()}")
            session.close()
            return announcements

        # if class login-form is present, login failed
        if soup.find("div", attrs={"class": "login-form"}):
            logging.error("Login unsuccessful")
            session.close()
            return announcements

        logging.info("Login successful")
        csrf_token = soup.find("meta", attrs={"name": "csrf-token"})["content"]

        try:
            announcements_url = "https://www.pesuacademy.com/Academy/s/studentProfilePESUAdmin?menuId=667&url=studentProfilePESUAdmin&controllerMode=6411&actionType=5&id=0&selectedData=0&_=1691941665637"
            response = session.get(announcements_url, headers={"x-csrf-token": csrf_token})
            soup = BeautifulSoup(response.text, "lxml")
            announcement_blocks = soup.find_all("div", attrs={"class": "elem-info-wrapper"})
            for announcement_block in announcement_blocks:
                try:
                    title_block = announcement_block.find("h4", attrs={"class": "text-info"})
                    title = title_block.text.strip()
                    date_block = announcement_block.find("span", attrs={"class": "text-muted text-date pull-right"})
                    date = date_block.text.strip()
                    date_object = datetime.datetime.strptime(date, "%d-%B-%Y").date()
                    text_blocks = announcement_block.find("div", attrs={"class": "col-md-12"})
                    images = list()
                    if text_blocks:
                        text_blocks = text_blocks.find_all("p")
                    else:
                        text_blocks = announcement_block.find("div", attrs={"class": "col-md-8"})
                        img_block = announcement_block.find("div", attrs={"class": "col-md-4"})
                        img_data = img_block.find("img").attrs["src"]
                        if img_data:
                            img_data = img_data.split(",")[1]
                            images.append(BytesIO(base64.b64decode(img_data)))
                            
                    text_blocks = list(map(lambda x: x.text.strip(), text_blocks))
                    text = "\n\n".join(text_blocks)
                    text = text.split("Read more")[0]
                    text.replace("\n\n\n\n", "\n\n\n")
                    attachment_links = [link for link in announcement_block.find_all("a") if
                                        link.text.strip().endswith(".pdf")]
                    attachments = list()

                    for attachment_link in attachment_links:
                        attachment_file_id = re.findall(r"\d+", attachment_link.attrs["href"])[0]
                        attachment_filename = Path(attachment_link.text.strip()).name
                        response = session.get(
                            f"https://pesuacademy.com/Academy/s/studentProfilePESUAdmin/downloadAnoncemntdoc/{attachment_file_id}",
                            headers={"x-csrf-token": csrf_token},
                            verify=False
                        )
                        Path("announcements").mkdir(parents=True, exist_ok=True)
                        with open(f"announcements/{attachment_filename}", "wb") as f:
                            f.write(response.content)
                        attachments.append(attachment_filename)
                    announcements.append({
                        "date": date_object,
                        "title": title,
                        "text": text,
                        "attachments": attachments,
                        "images": images
                    })

                except Exception as e:
                    logging.error(f"Unable to parse announcement: {traceback.format_exc()}")
                    continue

            session.close()
            return announcements

        except Exception as e:
            logging.error(f"Unable to fetch announcements: {traceback.format_exc()}")
            session.close()
            return announcements

    @app_commands.command(name="know_your_class_and_section", description="Get your class and section")
    @app_commands.describe(username="The PRN, SRN, Mobile Number or Email ID of the student")
    async def know_your_class_and_section(self, interaction: discord.Interaction, username: str):
        """
        Gets the student details from Know Your Class and Section
        """
        logging.info(f"Getting profile from Know Your Class and Section for {username}")
        profile = self.get_know_your_class_and_section(username=username)
        if not profile:
            embed = discord.Embed(
                title="Unable to get profile",
                description="Unable to get profile from Know Your Class and Section. "
                            "Please check the username and try again",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(
                title="Profile from Know Your Class and Section",
                color=discord.Color.green(),
            )
            for key, value in profile.items():
                if key in ["prn", "srn"]:
                    key = key.upper()
                else:
                    key = key.title()
                embed.add_field(name=key, value=value, inline=False)
            await interaction.response.send_message(embed=embed)

    @tasks.loop(minutes=5)
    async def update_announcements_loop(self):
        """
        Updates the available announcements every 5 minutes and posts any new announcements
        """
        await self.client.wait_until_ready()
        logging.info("Updating announcements")
        updated_announcements = await self.get_announcements()
        if updated_announcements:
            updated_announcements.sort(key=lambda x: x["date"], reverse=True)
            self.all_announcements = updated_announcements
            logging.info("Announcements updated")

            current_date = datetime.datetime.now(IST).date()
            for announcement in self.all_announcements:
                # TODO: Enable this while not testing
                check_announcement = announcement.copy()
                check_announcement.pop("images")
                if check_announcement not in self.posted_announcements and announcement["date"] == current_date:
                    channel_ids = self.db.get_channels_with_mode("announcements")
                    embed = self.get_announcement_embed(
                        date=announcement["date"],
                        title=announcement["title"],
                        text=announcement["text"]
                    )
                    # TODO: Wrap the below code into a function since pesu_academy, reddit and instagram reuse it
                    for channel_id in channel_ids:
                        channel = self.client.get_channel(int(channel_id))
                        if channel is None:
                            logging.warning(f"Unable to find channel with id {channel_id}")
                            continue
                        # TODO: Enable this while not testing
                        # await channel.send("@everyone", embed=embed)
                        file = None
                        if announcement["images"]:
                            buffer = announcement["images"][0]
                            buffer.seek(0)
                            file = discord.File(buffer, filename="image.png")
                        try:
                            await channel.send(file=file, embed=embed)
                        except discord.errors.Forbidden:
                            logging.error(f"Unable to send announcement to {channel.id} in '{channel.guild.name}'")
                            continue
                        if announcement["attachments"]:
                            for attachment in announcement["attachments"]:
                                files = []
                                with open(f"announcements/{attachment}", "rb") as f:
                                    files.append(discord.File(f))
                                await channel.send(files=files)
                    self.posted_announcements.append(check_announcement)
        else:
            logging.error("Unable to update announcements")

    @tasks.loop(hours=1)
    async def reset_announcements_loop(self):
        """
        Resets the posted announcements list at 12:00 AM IST
        """
        await self.client.wait_until_ready()
        current_time = datetime.datetime.now(IST)
        if current_time.hour == 0:
            logging.info("Resetting announcements")
            self.posted_announcements = list()
            logging.info("Announcements reset")

    @app_commands.command(name="sgpa",description="Calculates the SGPA of the student")
    @app_commands.describe(sub1_grade="Enter your grade for subject 1", sub1_credits="Enter the credits for subject 1", sub2_grade="Enter your grade for subject 2", sub2_credits="Enter the credits for subject 2", sub3_grade="Enter your grade for subject 3", sub3_credits="Enter the credits for subject 3", sub4_grade="Enter your grade for subject 4", sub4_credits="Enter the credits for subject 4", sub5_grade="Enter your grade for subject 5", sub5_credits="Enter the credits for subject 5", sub6_grade="Enter your grade for subject 6", sub6_credits="Enter the credits for subject 6", sub7_grade="Enter your grade for subject 7", sub7_credits="Enter the credits for subject 7", sub8_grade="Enter your grade for subject 8", sub8_credits="Enter the credits for subject 8", sub9_grade="Enter your grade for subject 9", sub9_credits="Enter the credits for subject 9", sub10_grade="Enter your grade for subject 10", sub10_credits="Enter the credits for subject 10")
    async def sgpa(self, interaction: discord.Interaction, sub1_grade: str, sub1_credits: app_commands.Range[int, 1, 6], sub2_grade: str=None, sub2_credits: app_commands.Range[int, 1, 6]=0, sub3_grade: str=None, sub3_credits: app_commands.Range[int, 1, 6]=0, sub4_grade: str=None, sub4_credits: app_commands.Range[int, 1, 6]=0, sub5_grade: str=None, sub5_credits: app_commands.Range[int, 1, 6]=0, sub6_grade: str=None, sub6_credits: app_commands.Range[int, 1, 6]=0, sub7_grade: str=None,sub7_credits: app_commands.Range[int, 1, 6]=0, sub8_grade: str=None, sub8_credits: app_commands.Range[int, 1, 6]=0, sub9_grade: str=None, sub9_credits: app_commands.Range[int, 1, 6]=0, sub10_grade: str=None, sub10_credits: app_commands.Range[int, 1, 6]=0):
        """
        Calculates the sgpa of the student
        """
        await interaction.response.defer(ephemeral=True)
        grade_copy = {"S": 10, "A": 9, "B": 8, "C": 7, "D": 6, "E": 5, "F": 0}
        sgpa_sum, total_credits_taken = 0, 0
        try:
            for i in range(1,11):
                grade = eval(f"sub{i}_grade")
                credits = eval(f"sub{i}_credits")
                if grade and credits:
                    sgpa_sum += grade_copy[grade] * credits
                    total_credits_taken += credits
        except KeyError:
            await interaction.followup.send("Invalid Grade")
            return
        await interaction.followup.send("Your SGPA is "+"`{:.2f}`".format(round(sgpa_sum/total_credits_taken,2)))

    @app_commands.command(name="cgpa",description="Calculates the CGPA of the student")
    @app_commands.describe(sem1_gpa="Enter your SGPA for semester 1", sem1_credits="Enter the credits for semester 1", sem2_gpa="Enter your SGPA for semester 2", sem2_credits="Enter the credits for semester 2", sem3_gpa="Enter your SGPA for semester 3", sem3_credits="Enter the credits for semester 3", sem4_gpa="Enter your SGPA for semester 4", sem4_credits="Enter the credits for semester 4", sem5_gpa="Enter your SGPA for semester 5", sem5_credits="Enter the credits for semester 5", sem6_gpa="Enter your SGPA for semester 6", sem6_credits="Enter the credits for semester 6", sem7_gpa="Enter your SGPA for semester 7", sem7_credits="Enter the credits for semester 7", sem8_gpa="Enter your SGPA for semester 8", sem8_credits="Enter the credits for semester 8")
    async def cgpa(self, interaction: discord.Interaction, sem1_gpa: app_commands.Range[float, 0, 10], sem1_credits: app_commands.Range[int, 1, 30], sem2_gpa: app_commands.Range[float, 0, 10]=None, sem2_credits: app_commands.Range[int, 1, 30]=0, sem3_gpa: app_commands.Range[float, 0, 10]=None, sem3_credits: app_commands.Range[int, 1, 30]=0, sem4_gpa: app_commands.Range[float, 0, 10]=None, sem4_credits: app_commands.Range[int, 1, 30]=0, sem5_gpa: app_commands.Range[float, 0, 10]=None, sem5_credits: app_commands.Range[int, 1, 30]=0, sem6_gpa: app_commands.Range[float, 0, 10]=None, sem6_credits: app_commands.Range[int, 1, 30]=0, sem7_gpa: app_commands.Range[float, 0, 10]=None, sem7_credits: app_commands.Range[int, 1, 30]=0, sem8_gpa: app_commands.Range[float, 0, 10]=None, sem8_credits: app_commands.Range[int, 1, 30]=0):
        """
        Calculates the cgpa of the student
        """
        await interaction.response.defer(ephemeral=True)
        cgpa_sum, total_credits_taken = 0, 0
        for i in range(1,9):
            gpa = eval(f"sem{i}_gpa")
            credits = eval(f"sem{i}_credits")
            if gpa and credits:
                cgpa_sum += gpa * credits
                total_credits_taken += credits
        await interaction.followup.send("Your CGPA is "+"`{:.2f}`".format(round(cgpa_sum/total_credits_taken,2)))


async def setup(client: commands.Bot):
    """
    Adds the cog to the bot
    """
    await client.add_cog(PESUAcademyCog(client))
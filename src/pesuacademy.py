import time
import asyncio
import datetime
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


async def searchPESUAcademy(driver, query):
    query = query.upper()

    driver.get("https://www.pesuacademy.com/Academy/")
    class_section_button = driver.find_element_by_xpath(
        r'//*[@id="knowClsSection"]')
    class_section_button.click()

    entry_box = driver.find_element_by_xpath(
        r'//*[@id="knowClsSectionModalLoginId"]')
    await asyncio.sleep(0.4)

    entry_box.send_keys(query)

    search_button = driver.find_element_by_xpath(
        r'//*[@id="knowClsSectionModalSearch"]')
    search_button.click()
    await asyncio.sleep(0.4)

    try:
        _ = driver.find_element_by_xpath(
            r'//*[@id="knowClsSectionModalTableDate"]/tr/td[3]').text
    except:
        return None
    else:
        result = list()
        table = driver.find_element(By.ID, 'knowClsSectionModalTableDate')
        rows = table.find_elements(By.TAG_NAME, "tr")
        for row in rows:
            col = row.find_elements(By.TAG_NAME, "td")
            col = [t.text for t in col]
            result.append(col)
    return result
'''

async def getPESUHallTicket(chrome, username, password):
    chrome.get("https://pesuacademy.com/Academy")
    time.sleep(2)

    username_box = chrome.find_element_by_xpath(r'//*[@id="j_scriptusername"]')
    password_box = chrome.find_element_by_xpath(r'//*[@name="j_password"]')

    username_box.send_keys(username)
    time.sleep(0.3)
    password_box.send_keys(password)
    time.sleep(0.3)

    sign_in_button = chrome.find_element_by_xpath(
        r'//*[@id="postloginform#/Academy/j_spring_security_check"]')
    sign_in_button.click()
    time.sleep(1)

    menu_options = chrome.find_elements_by_xpath(r'//*[@class="menu-name"]')
    menu_options[12].click()
    time.sleep(0.3)

    download_button = chrome.find_element_by_xpath(
        r'//*[@class="btn btn-default btn-sm"]')
    download_button.click()
    time.sleep(3)
'''

async def getPESUAnnouncements(chrome, username, password):
    chrome.get("https://pesuacademy.com/Academy")

    try:
        username_box = WebDriverWait(chrome, 10).until(
            EC.presence_of_element_located((By.ID, "j_scriptusername")))
        password_box = WebDriverWait(chrome, 10).until(
            EC.presence_of_element_located((By.NAME, "j_password")))
        login_button = WebDriverWait(chrome, 10).until(EC.presence_of_element_located(
            (By.ID, "postloginform#/Academy/j_spring_security_check")))
    except:
        return list()

    username_box.send_keys(username)
    time.sleep(0.3)
    password_box.send_keys(password)
    time.sleep(0.3)
    login_button.click()

    try:
        menu_options = WebDriverWait(chrome, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "menu-name")))
    except:
        return list()

    for option in menu_options:
        if option.text == "Announcements":
            chrome.execute_script("arguments[0].click();", option)
            break

    try:
        announcement_boxes = WebDriverWait(chrome, 15).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "elem-info-wrapper")))
    except:
        return list()

    data = list()
    for a_box in announcement_boxes:
        header_box = a_box.find_element_by_xpath(r'.//*[@class="text-info"]')
        header = header_box.text

        date_box = a_box.find_element_by_xpath(
            r'.//*[@class="text-muted text-date pull-right"]')
        date = datetime.datetime.strptime(date_box.text, "%d-%B-%Y").date()

        bodies = a_box.find_elements_by_xpath(r'.//*[@class="col-md-12"]')
        all_attachments = list()
        if not bodies:
            bodies = a_box.find_elements_by_xpath(r'.//*[@class="col-md-8"]')
        for b in bodies:
            paragraphs = b.find_elements_by_tag_name("p")
            attachments = b.find_elements_by_xpath(
                r'.//*[@class="pesu-ico-download"]')
            attachment_names = b.find_elements_by_tag_name("a")
            if paragraphs:
                content = '\n'.join([p.text for p in paragraphs])
            if attachments:
                attachment_names = [
                    a_name.text for a_name in attachment_names if a_name.text != "Read more"]
                all_attachments.extend(attachment_names)
                for a in attachments:
                    a.click()
                    time.sleep(1)

        img_base64 = None
        img_box = a_box.find_elements_by_xpath(
            r'.//*[@class="img-responsive"]')
        if img_box:
            img_base64 = img_box[0].get_attribute("src")

        temp = {
            "date": date,
            "header": header,
            "body": content,
            "img": img_base64,
            "attachments": all_attachments
        }

        data.append(temp)

    return data

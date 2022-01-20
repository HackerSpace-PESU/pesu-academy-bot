import datetime
from docx.api import Document
import re

def loadPESUCalendar():
    document = Document('data/calendar.docx')
    table = document.tables[0]

    calendar_data = dict()
    weeks = list()
    for i, row in enumerate(table.rows):
        text = list(cell.text for cell in row.cells)
        if not text[0]:
            weeks.append(text)

    first_date_month = weeks[0][1]
    first_date = weeks[0][2]
    last_date_month = weeks[-1][1]
    last_date = weeks[-1][-4]


    temp_date = datetime.datetime.strptime(f"{first_date.zfill(2)} {first_date_month} 2022", r"%d %b %Y").date()
    last_date_obj = datetime.datetime.strptime(f"{last_date.zfill(2)} {last_date_month} 2022", r"%d %b %Y").date()
    while temp_date <= last_date_obj:
        calendar_data[temp_date] = list()
        temp_date = temp_date + datetime.timedelta(days=1)


    for week in weeks:
        month = week[1]
        events = week[-1]
        days = list(set(week[2:9]))

        if '/' in month:
            month = month.split('/')
        
        for day in days:
            if '\n' in day:
                day_num = int(day.split('\n')[0])
                day_events = day.split('\n')[1:]
                if isinstance(month, list):
                    if day_num <= 5:
                        event_month = month[1]
                    else:
                        event_month = month[0]
                else:
                    event_month = month
                day_num = str(day_num)
                key = datetime.datetime.strptime(f"{day_num.zfill(2)} {event_month} 2022", r"%d %b %Y").date()
                for de in day_events:
                    calendar_data[key].append(de)


        for event in events.split('\n'):
            event = event.strip()
            event = re.sub(r' +', ' ', event)
            if event:
                m = re.match(r'\d+', event)
                if m:
                    day_num = [int(m.group())]
                    if chr(8211) in event:
                        event = event.split(chr(8211))[1].strip()
                    else:
                        event = event.split(chr(45))[1].strip()
                    event = ('H', event)
                else:
                    day_num = list(map(lambda x: int(x.split('\n')[0].strip()), days))
                
                for day in day_num:
                    if isinstance(month, list):
                        if day <= 5:
                            event_month = month[1]
                        else:
                            event_month = month[0]
                    else:
                        event_month = month
                    day = str(day)
                    key = datetime.datetime.strptime(f"{day.zfill(2)} {event_month} 2022", r"%d %b %Y").date()
                    if isinstance(event, tuple) and event[0] == 'H' and 'H' in calendar_data[key]:
                        calendar_data[key].remove('H')
                    calendar_data[key].append(event)

    return calendar_data
            

calendar_data = loadPESUCalendar()           
for d in calendar_data:
    print(d, calendar_data[d])


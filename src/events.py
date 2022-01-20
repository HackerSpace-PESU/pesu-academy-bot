import re
import datetime
from docx.api import Document

calendar_data = None

def loadPESUCalendar():
    global calendar_data
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


def getSeriesCalendarDayResults(num_results, time_period):
    num_days = time_period * num_results
    start_date = datetime.datetime.now().date()
    end_date = start_date + datetime.timedelta(days=num_days)
    result = list()
    current_date = start_date
    while current_date <= end_date and current_date in calendar_data:
        if calendar_data[current_date]:
            events = calendar_data[current_date]
            temp_result = list()
            for event in events:
                if isinstance(event, tuple):
                    temp_result.append(f"{event[0]}: {event[1]}")
                else:
                    temp_result.append(event)
            # temp_result = ", ".join(temp_result)
            result.append((current_date, temp_result))
        current_date = current_date + datetime.timedelta(days=1)
    return result


def getCalendarResultFromQuery(query):
    result = list()
    for day in calendar_data:
        events = calendar_data[day]
        temp_result = list()
        for event in events:
            if isinstance(event, tuple):
                if query in event[0]:
                    temp_result.append(f"{event[0]}: {event[1]}")
            else:
                if query in event:
                    temp_result.append(event)
        if temp_result:
            result.append((day, temp_result))
            
    return result



def getCalendarResults(query_type, num_results):
    query_codes = ["LWD", "EWD", "H", "PTM", "ASD", "CCM", "FASD", "FAM", "ISA"]
    if query_type.upper() in query_codes:
        return getCalendarResultFromQuery(query_type.upper())
    if query_type == "day":
        return getSeriesCalendarDayResults(num_results, 1)
    if query_type == "week":
        return getSeriesCalendarDayResults(num_results, 7)
    elif query_type == "month":
        return getSeriesCalendarDayResults(num_results, 30)
    elif query_type == "sem" or query_type == "semester":
        return "file"
    else:
        try:
            date = datetime.datetime.strptime(query_type, r"%d-%m-%Y").date()
            if date in calendar_data:
                events = calendar_data[date]
                result = list()
                temp_result = list()
                for event in events:
                    if isinstance(event, tuple):
                        temp_result.append(f"{event[0]}: {event[1]}")
                    else:
                        temp_result.append(event)
                result.append((date, temp_result))
                return result
            else:
                return list()
        except:
            return None
    


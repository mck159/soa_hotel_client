from datetime import timedelta, datetime

__author__ = 'maciek'

def datesFromRanges(dateRanges):
    dates = []
    for datesRange in dateRanges:
        dateFrom = datetime.strptime(datesRange['from'], '%Y-%m-%d').date()
        dateTo = datetime.strptime(datesRange['to'], '%Y-%m-%d').date()
        days = (dateTo - dateFrom).days + 1
        for day in range(days):
            date = (dateFrom + timedelta(days = day))
            dates.append(date.strftime('%Y-%m-%d'))
    return dates



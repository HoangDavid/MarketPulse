from datetime import datetime, timedelta


def convert_time_filter(time_filter: str):
    start_date = None
    end_date = datetime.now()
    interval = "1d"
    
    if time_filter == "year":
        start_year = (end_date - timedelta(days=365)).year
        start_date = datetime(start_year, 1, 1)   
    elif time_filter == "month":
        d = (end_date - timedelta(days=30))
        start_date = datetime(d.year, d.month, 1)
    elif time_filter == "week":
        start_date = end_date - timedelta(days=7)
    elif time_filter == "day":
        #  TODO: add for live streaming
        interval = "1h"

    return  start_date, end_date, interval

    


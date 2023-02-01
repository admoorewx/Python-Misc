import os
from datetime import datetime
import requests
import csv

start_date = datetime(2019,8,29)
end_date = datetime(2019,8,30)
save_directory = "/home/andrew/Research/surface_obs"
outfile = f'asos_{datetime.strftime(start_date,"%Y%M%d")}_{datetime.strftime(end_date,"%Y%M%d")}.csv'
URL = f'https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?data=tmpf&data=dwpf&data=drct&data=sknt&data=mslp&data=vsby&data=gust&data=skyc1&data=skyc2&data=skyc3&data=wxcodes&year1={start_date.year}&month1={start_date.month}&day1={start_date.day}&year2={end_date.year}&month2={end_date.month}&day2={end_date.day}&tz=Etc%2FUTC&format=onlycomma&latlon=yes&elev=no&missing=M&trace=T&direct=yes&report_type=3&report_type=2'
with requests.Session() as s:
    download = s.get(URL)
    decoded_content = download.content.decode('utf-8')
    with open(os.path.join(save_directory,outfile), 'w', newline="\n") as csvfile:
        csvwriter = csv.writer(csvfile,delimiter=',')
        for line in decoded_content.split("\n"):
            csvwriter.writerow(line.split(","))
    csvfile.close()
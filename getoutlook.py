import csv, os
import requests
import zipfile
import datetime


# Laptop
# DataDirectory = 'C:\\Users\\admoo\\Desktop\\Projects\\FalseAlarm\\csv\\'
# outdir = 'C:\\Users\\admoo\\Desktop\\Projects\\FalseAlarm\\outlooks\\'
# WARfilename = 'ConWarnings_2015_2018.csv'

# home PC
DataDirectory = 'H:\\Research\\FalseAlarm\\csv\\'
outdir = 'H:\\Research\\FalseAlarm\\outlooks\\shapefiles\\'
indir = 'H:\\Research\\FalseAlarm\\outlooks\\'
WARfilename = 'ConWarnings_2015_2018.csv'

def correctDate(datestring):
    date = datetime.datetime.strptime(datestring, "%Y%m%d%H%M")
    if date.hour < 12:
        date = date - datetime.timedelta(days=1)
    new_date = datetime.datetime.strftime(date, "%Y%m%d")
    return new_date

def getDates(DataDirectory,filename):
    print("Processing file: " + DataDirectory + filename+"\n")
    output = []
    os.chdir(DataDirectory)
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            date = correctDate(row[2])
            if date in output:
                pass
            else:
                output.append(date)
    csv_file.close()
    return output


def getOutlook(date,indir):
    year = date[0:4]
    url = "https://www.spc.noaa.gov/products/outlook/archive/"+year+"/day1otlk_"+date+"_1300-shp.zip"
    savename = "day1otlk_"+date+"_1300-shp.zip"
    r = requests.get(url)
    with open(indir+savename,'wb') as f:
        f.write(r.content)
    print("Retrieved file "+savename)
    return savename


def unzip(zfile,indir,outdir):
    inpath = indir+zfile[0:-8]
    outpath = outdir
    #os.mkdir(inpath)
    with zipfile.ZipFile(indir+zfile,'r') as zip_ref:
        zip_ref.extractall(outpath)
    print("Unzipped file "+zfile+"\n")


output = getDates(DataDirectory,WARfilename)
for date in output:
   filename = getOutlook(date,indir)
   unzip(filename,indir,outdir)
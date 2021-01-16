import csv, os
import requests
import zipfile


# Laptop
DataDirectory = 'C:\\Users\\admoo\\Desktop\\Projects\\FalseAlarm\\csv\\'
outdir = 'C:\\Users\\admoo\\Desktop\\Projects\\FalseAlarm\\outlooks\\'
WARfilename = 'ConWarnings_2015_2018.csv'

def getDates(DataDirectory,filename):
    print("Processing file: " + DataDirectory + filename+"\n")
    output = []
    os.chdir(DataDirectory)
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            if row[2][0:-4] in output:
                pass
            else:
                output.append(row[2][0:-4])
    csv_file.close()
    return output


def getOutlook(date,outdir):
    year = date[0:4]
    url = "https://www.spc.noaa.gov/products/outlook/archive/"+year+"/day1otlk_"+date+"_1300-shp.zip"
    savename = "day1otlk_"+date+"_1300-shp.zip"
    r = requests.get(url)
    with open(outdir+savename,'wb') as f:
        f.write(r.content)
    print("Retrieved file "+savename)
    return savename


def unzip(zfile,datadir):
    path = datadir+zfile[0:-8]
    os.mkdir(path)
    with zipfile.ZipFile(datadir+zfile,'r') as zip_ref:
        zip_ref.extractall(path)
    print("Unzipped file "+zfile+"\n")


# output = getDates(DataDirectory,WARfilename)
# for date in output[0:2]:
#     filename = getOutlook(date,outdir)
#     unzip(filename,outdir)
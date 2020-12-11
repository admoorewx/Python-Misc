import fiona
import csv

# Read in a shapefile and export a CSV file with the data.

shpfile = 'H:\\Research\\FalseAlarm\\wwa_2018_2020\\wwa_2018_2020.shp'
outdir = 'H:\\Research\\FalseAlarm\\' # directory where you want output images to be saved to
filename = 'ConWarn_2018_2020.csv'

shape = fiona.open(shpfile)

outfile = outdir + filename + ".csv"
with open(outfile, mode='w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')

    for feat in shape:
        #print(feat['geometry'])
        WFO = feat['properties']['WFO']
        ISSUED = feat['properties']['ISSUED']
        EXPIRED = feat['properties']['EXPIRED']
        Phenom = feat['properties']['PHENOM']
        COORD = feat['geometry']['coordinates'][0]

        if Phenom == "TO" or Phenom == "SV":
            data = [WFO, Phenom, ISSUED, EXPIRED, COORD]
            writer.writerow(data)

    csvfile.close()

print("success")
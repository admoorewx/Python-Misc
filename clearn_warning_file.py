import os
import csv

DataDirectory = 'H:\\Research\\FalseAlarm\\' # Path to where your metar data is stored
outdir = 'H:\\Research\\FalseAlarm\\' # directory where you want output images to be saved to
filename = 'ConWarnings_2015_2020.csv'
filename2 = 'ConWarn_2018_2020.csv'
LSRfilename = '1950-2018_actual_tornadoes.csv'

def dataReadIn(DataDirectory,filename):
    print("Processing file: " + DataDirectory + filename+"\n")
    output = []
    os.chdir(DataDirectory)
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            if int(row[2][0:4]) <= 2018:
                output.append(row)
    csv_file.close()
    return output


def outputsToCSV(data1,data2,outdir,filename):
    # For multiple data array output - they're likely a better way to do this, but 'eh'.
    outfile = outdir + filename + ".csv"
    with open(outfile, mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        for line in data1:
            writer.writerow(line)
        for line2 in data2:
            writer.writerow(line2)
        csvfile.close()
    print("File Writing Complete.")


def outputToCSV(data,outdir,filename):
    # For single data array output
    outfile = outdir + filename + ".csv"
    with open(outfile, mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        for line in data:
            writer.writerow(line)
        csvfile.close()
    print("File Writing Complete.")



def filterLSRs(DataDirectory,filename,year1,year2):
    print("Processing file: " + DataDirectory + filename + "\n")
    output = []
    os.chdir(DataDirectory)
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            try: # This avoids the header line
                if int(row[1]) >= year1 and int(row[1]) <= year2:
                    output.append(row)
            except:
                continue
    csv_file.close()
    return output


output = dataReadIn(DataDirectory,filename)
#output2 = dataReadIn(DataDirectory,filename2)
#outputsToCSV(output,outdir,"ConWarnings_2015_2020")

#output = filterLSRs(DataDirectory,LSRfilename,2015,2018)
outputToCSV(output, outdir, "2015_2018_ConWarn")
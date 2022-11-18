from csv import writer
from csv import reader
# import csv
import os

outputFile = '/import/data/esxtop/output_1.csv'

def calculateAvgs(inputFile):
    # Open the input_file in read mode and output_file in write mode
    count_vals_c0 = 0
    sum_vals_c0 = 0
    count_vals_c1 = 0
    sum_vals_c1 = 0
    count_vals_c2 = 0
    sum_vals_c2 = 0
    with open(inputFile, 'r') as read_obj, \
            open(outputFile, 'w', newline='') as write_obj:
        # Create a csv.reader object from the input file object
        csv_reader = reader(read_obj)
        print('##### '+inputFile+' has been read')
        # csv_reader = reader(read_obj)
        # Create a csv.writer object from the output file object
        csv_writer = writer(write_obj)
        print('##### '+outputFile+' has been opened for writing')
        # Read each row of the input csv file as list
        firstLine = True
        C0_columns = []
        C1_columns = []
        C2_columns = []
        for row in csv_reader:
            if firstLine:
                firstLine = False
                j = 0
                flag = 0
                while flag!=-1:
                    item = row[j]
                    if ('C0' in item):
                        C0_columns.append(j)
                    elif ('C1' in item):
                        C1_columns.append(j)
                    elif ('C2' in item):
                        C2_columns.append(j)
                    j = j+1
                    if(j >= len(row)):
                        flag = -1
                row.append('\\esxi5.\PCPU Power State(%C0 AVG)')
                row.append('\\esxi5.\PCPU Power State(%C1 AVG)')
                row.append('\\esxi5.\PCPU Power State(%C2 AVG)')
            else:
                # print('Reading another row')
                k = 0
                flag = 0
                while flag!=-1:
                    if k in C0_columns:
                        sum_vals_c0 = sum_vals_c0 + float(row[k])
                        count_vals_c0 = count_vals_c0 + 1
                    elif k in C1_columns:
                        sum_vals_c1 = sum_vals_c1 + float(row[k])
                        count_vals_c1 = count_vals_c1 + 1
                    elif k in C2_columns:
                        sum_vals_c2 = sum_vals_c2 + float(row[k])
                        count_vals_c2 = count_vals_c2 + 1
                    k = k+1
                    if(k >= len(row)):
                        flag = -1
                avg_c0 = sum_vals_c0 / count_vals_c0
                avg_c1 = sum_vals_c1 / count_vals_c1
                avg_c2 = sum_vals_c2 / count_vals_c2
                row.append(avg_c0)
                row.append(avg_c1)
                row.append(avg_c2)
            # Add the updated row / list to the output file
            csv_writer.writerow(row)
        print('Finished writing...')

for fname in os.listdir('/import/data/esxtop'):
    fullPath = os.path.join('/import/data/esxtop',fname)
    newPath = os.path.join('/import/data/archive',fname)
    if os.path.isfile(fullPath) and fname[0] != "." :
        calculateAvgs(fullPath)

os.rename(fullPath, newPath)

import random
import csv
import os


class CSVFileUploadService:
    def load_csv(self, csv_file):
        filename = "temp_file_{}.csv".format(random.randint(1000000, 9999999))
                
        with open(filename, "wb") as f:
            if csv_file.multiple_chunks():
                for chunk in csv_file.chunks():
                    f.write(chunk)
            else:
                f.write(csv_file.read())
                    
        with open(filename, "r") as f:
            datareader = csv.reader(f)
                        
            line_index = 0
                        
            for row in datareader:
                if line_index == 0:
                    header = row
                    print(header)
                else:
                    # TODO: insert data
                    pass
                                
                line_index += 1
        
        os.remove(filename)                    
        return ("{} lines are read. \nheader: {}".format(line_index, header))
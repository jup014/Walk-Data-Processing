import random
import csv
import os

from data.models import RawSteps

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
                    
            objects = []    
            for row in datareader:
                if line_index == 0:
                    header = row
                else:
                    # TODO: insert data
                    objects.append(RawSteps(local_datetime=row[2], user_id=row[0], steps=row[1], local_date=row[3], local_time=row[4]))
                                
                line_index += 1
            RawSteps.objects.bulk_create(objects)
                    
        os.remove(filename)                    
        return ("{} lines are read. \nheader: {}".format(line_index, header))
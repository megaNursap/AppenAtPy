import csv


class SourceDataReader:
    def __init__(self, file_path):
        self.file_path = file_path

    def read(self):
        reader = csv.DictReader(open(self.file_path, "r"))

        data = []
        for element in reader:
            data.append(element)

        return data

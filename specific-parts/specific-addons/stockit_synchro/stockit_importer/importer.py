import csv
import base64
import datetime
import tempfile


class StockitImporter(object):
    """
    Utilities to import stockit files and read them
    """

    def __init__(self, ftp=None):
        self.ftp = ftp
        self.csv_reader = None
        self.data = None

    def ftp_get(self, path, ftp=None):
        ftp = ftp or self.ftp
        if not ftp:
            raise Exception('Error', 'No FTP connection')
        pass

    def _to_list(self):
        """ Returns a list with data
        """
        res = []
        for row in self.csv_reader:
            res.append(row)
        return res

    def csv_to_dict(self, header):
        """ Returns a dict with data
        """
        self.csv_reader = csv.reader(self.data, dialect='stockit')
        csv_list = self._to_list()
        res = [dict(zip(header, row)) for row in csv_list]
        return res

    def cast_rows(self, rows, conversion_rules):
        for row in rows:
            for rule in conversion_rules:
                if conversion_rules[rule] == datetime.datetime:
                    date_string = row[rule].split(' ')[0]
                    row[rule] = datetime.datetime.strptime(date_string,
                                                           '%Y-%M-%d')
                else:
                    row[rule] = conversion_rules[rule](row[rule])
        return rows

    def read_from_base64(self, data):
        decoded_data = base64.b64decode(data)
        csv_file = tempfile.NamedTemporaryFile()
        csv_file.write(decoded_data)
        # We ensure that cursor is at begining of file
        csv_file.seek(0)
        self.data = csv_file

    def read_from_file(self, filename):
        csv_file = open(filename, 'r')
        self.data = csv_file

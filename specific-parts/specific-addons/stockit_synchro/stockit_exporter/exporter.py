import StringIO
import os
from stockit_synchro.unicode_csv.writer import UnicodeWriter


class StockitExporter(object):
    """
    Utilities to write stockit files and export them
    """

    def __init__(self, filename=None):
        self.filename = filename

    def get_csv_data(self, rows):
        file_data = StringIO.StringIO()
        writer = UnicodeWriter(file_data, dialect='stockit')
        writer.writerows(rows)
        file_value = file_data.getvalue()
        file_data.close()
        return file_value

    def _write_file(self, data):
        file = open(self.filename, 'w')
        file.write(data)
        file.close()
        # stockit needs to drop the file so we have to put the write permission on the group
        os.chmod(self.filename, 0664)

    def export_file(self, csv_data):
        if not self.filename:
            raise Exception('Error', 'Please specify a filename!')
        if csv_data:
            self._write_file(csv_data)

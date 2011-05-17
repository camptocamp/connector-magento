from stockit_synchro.file_writer.writer import UnicodeWriter


class StockitExporter(object):
    """
    Utilities to write stockit files and export them
    """

    def __init__(self, filename):
        self.filename = filename

    def _write_file(self, data):
        file = open(self.filename, 'w')
        writer = UnicodeWriter(file, delimiter='|')
        writer.writerows(data)
        file.close()

    def export_file(self, data):
        self._write_file(data)

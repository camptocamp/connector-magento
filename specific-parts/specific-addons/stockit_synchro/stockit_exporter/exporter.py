from stockit_synchro.file_writer.writer import UnicodeWriter


class StockitExporter(object):
    """
    Utilities to write stockit files and export them
    """

    def __init__(self, filename, ftp=None):
        self.filename = filename
        self.ftp = ftp

    def _write_file(self, data):
        file = open(self.filename, 'w')
        writer = UnicodeWriter(file, dialect='stockit')
        writer.writerows(data)
        file.close()

    def _ftp_put(self):
        pass

    def export_file(self, data):
        self._write_file(data)
        if self.ftp:
            self._ftp_put()

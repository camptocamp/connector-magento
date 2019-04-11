import csv


class StockitCsvDialect(csv.Dialect):
    delimiter = '|'
    quotechar = '"'
    escapechar = None
    doublequote = True
    lineterminator = "\r\n"
    quoting = csv.QUOTE_MINIMAL
    skipinitialspace = False

csv.register_dialect("stockit", StockitCsvDialect())

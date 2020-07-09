# Gergely Nagy <greg@gnome.hu>
#
import base
from revelation import data, entry

import time
import csv
from cStringIO import StringIO


class CSV(base.DataHandler):
    "Data handler for CSV files"

    name        = "Comma Separated Values (CSV)"
    importer    = False
    exporter    = True
    encryption  = False

    def __init__(self):
        base.DataHandler.__init__(self)

    def export_data(self, entrystore, password = None):
        "Exports data to a CSV file"

        # fetch and sort entries
        entries = []
        iter = entrystore.iter_nth_child(None, 0)

        while iter is not None:
            e = entrystore.get_entry(iter)

            if type(e) != entry.FolderEntry:
                entries.append(e)

            iter = entrystore.iter_traverse_next(iter)

        entries.sort(lambda x,y: cmp(x.name.lower(), y.name.lower()))


        stringwriter = StringIO()
        csvwriter = csv.writer(stringwriter, dialect="excel")

        keys = set()
        for e in entries:
            for f in e.fields:
                keys.add(f.name)

        # 'Email', 'Hostname', 'Password', 'URL', 'Username'
        keys = sorted(keys)

        csvwriter.writerow(['Name', 'Type', 'Description', 'Updated'] + keys)

        for e in entries:

            values = []
            for key in keys:
                value = ''
                for field in e.fields:
                    if key == field.name:
                        value = field.value
                values.append(value)

            updated = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(e.updated))
            csvwriter.writerow([e.name, e.typename, e.description, updated] + values)


        return stringwriter.getvalue()


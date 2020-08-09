# Gergely Nagy <greg@gnome.hu>
#
from . import base
from revelation import data, entry

import time
import csv
from io import StringIO


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


class Bitwarden(base.DataHandler):
    "Data handler for Bitwarden Web Vault (CSV file)"

    name		= "Bitwarden Web Vault (CSV)"
    importer	= False
    exporter	= True
    encryption	= False

    bitwarden_csv_header_keys = [
        'folder',
        'favorite',
        'type',
        'name',
        'notes',
        'fields',
        'login_uri',
        'login_username',
        'login_password',
        'login_totp',
    ]

    # revelation type -> Bitwarden type
    type_mapping = {
        'Creditcard': 'note',  # Bitwarden type 'card' exists but seems unmanaged.
        'Crypto Key': 'login',
        'Database': 'login',
        'Door lock': 'note',
        'Email': 'login',
        'FTP': 'login',
        'Generic': 'login',
        'Phone': 'note',
        'Remote Desktop': 'login',
        'Shell': 'login',
        'VNC': 'login',
        'Website': 'login',
    }

    # revelation field -> Bitwarden field
    field_mapping = {
        'Name': 'name',
        'Type': 'type',
        'Description': 'notes',
        'Updated': 'notes',
        'CCV number': 'notes',
        'Card number': 'notes',
        'Card type': 'notes',
        'Certificate': 'notes',
        'Code': 'notes',
        'Database': 'notes',
        'Domain': 'notes',
        'Email': 'notes',
        'Expiry date': 'notes',
        'Hostname': 'login_uri',
        'Key File': 'notes',
        'Location': 'notes',
        'PIN': 'notes',
        'Password': 'login_password',
        'Phone number': 'notes',
        'Port number': 'notes',
        'URL': 'login_uri',
        'Username': 'login_username',
    }

    date_format = "%Y-%m-%d %H:%M:%S"

    def __init__(self):
        base.DataHandler.__init__(self)

    def export_data(self, entrystore, password = None):
        "Exports data to a Bitwarden CSV file"

        # fetch and sort entries
        entries = []
        iter = entrystore.iter_nth_child(None, 0)

        stringwriter = StringIO()
        csvwriter = csv.writer(stringwriter, dialect="excel")
        csvwriter.writerow(self.bitwarden_csv_header_keys)

        while iter is not None:
            e = entrystore.get_entry(iter)

            if type(e) != entry.FolderEntry:
                # Find the directory path of this item.
                path = ''
                parent = entrystore.iter_parent(iter)
                while parent:
                    path = entrystore.get_entry(parent).name + '/' + path
                    parent = entrystore.iter_parent(parent)

                values = []
                for key in self.bitwarden_csv_header_keys:
                    # Special fields
                    if key == 'folder':
                        values.append(path)
                        continue
                    if key == 'favorite':
                        values.append('')
                        continue
                    if key == 'name':
                        values.append(e.name)
                        continue
                    if key == 'type':
                        values.append(self.type_mapping[e.typename])
                        continue

                    value = ''

                    # Add export time as a note by default.
                    # Add e.description as a note.
                    # Add revelation updated time as a note.
                    if key == 'notes':
                        now = time.strftime(self.date_format, time.localtime())
                        updated = time.strftime(self.date_format, time.localtime(e.updated))
                        value += "Exported from Revelation on %s\n" % now
                        value += "Last Revelation Update: %s\n" % updated
                        if e.description:
                            value += "Description: %s\n" % e.description
                        if e.notes != '':
                            value += "Revelation Notes: %s\n" % e.notes

                    for field in e.fields:
                        if key == self.field_mapping[field.name]:
                            if self.field_mapping[field.name] == 'notes' and field.value:
                                value += '%s: %s\n' % (field.name, field.value)
                            else:
                                value += field.value
                    values.append(value)

                csvwriter.writerow(values)

            iter = entrystore.iter_traverse_next(iter)

        return stringwriter.getvalue()

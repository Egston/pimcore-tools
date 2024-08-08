#!/usr/bin/env python3

import pymysql
import json
import sys
import getpass
import argparse
from odf.opendocument import OpenDocumentSpreadsheet
from odf.table import Table, TableColumn, TableRow, TableCell
from odf.text import P


def fetch_data_from_db(host, user, password, database):
    db_config = {
        'host': host,
        'user': user,
        'password': password,
        'database': database
    }

    query = "SELECT data FROM settings_store WHERE scope LIKE 'pimcore_select_options'"

    try:
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        all_rows = []

        for row in results:
            json_data = row[0]
            data = json.loads(json_data)

            id_val = data.get("id", "")
            group_val = data.get("group", "")
            use_traits_val = data.get("useTraits", "")
            implements_interfaces_val = data.get("implementsInterfaces", "")
            select_options = data.get("selectOptions", [])

            for option in select_options:
                all_rows.append({
                    "id": id_val,
                    "group": group_val,
                    "useTraits": use_traits_val,
                    "implementsInterfaces": implements_interfaces_val,
                    "value": option.get("value", ""),
                    "label": option.get("label", ""),
                    "name": option.get("name", "")
                })

        return all_rows

    except pymysql.MySQLError as err:
        print(f"Error: {err}")
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()


parser = argparse.ArgumentParser(description="Export Pimcore Select Options from MySQL DB to ODS files")
parser.add_argument('--host', required=True, help='MySQL server host')
parser.add_argument('-u', '--user', default='pimcore', help='MySQL user name')
parser.add_argument('-p', '--password', nargs='?', const=True, required=True, help='MySQL password. If no password is provided, it will be requested interactively.')
parser.add_argument('--database', default='pimcore', help='MySQL database name')
parser.add_argument('-o', '--output', required=True, help='Output ODS file name')

args = parser.parse_args()

if args.password is True:
    password = getpass.getpass(prompt='Enter MySQL password: ')
else:
    password = args.password

data = fetch_data_from_db(args.host, args.user, password, args.database)

doc = OpenDocumentSpreadsheet()

table = Table(name="Select Options")

table.addElement(TableColumn())
table.addElement(TableColumn())
table.addElement(TableColumn())

header_row = TableRow()
for header in data[0].keys():
    cell = TableCell()
    cell.addElement(P(text=header))
    header_row.addElement(cell)
table.addElement(header_row)

for input_row in data:
    output_row = TableRow()
    # dynamically output all in option dict
    for key, value in input_row.items():
        cell = TableCell()
        cell.addElement(P(text=value))
        output_row.addElement(cell)
    table.addElement(output_row)

doc.spreadsheet.addElement(table)

doc.save(args.output)

print(f"Data exported to {args.output}")

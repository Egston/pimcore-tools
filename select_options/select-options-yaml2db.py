#!/usr/bin/env python3

# This script reads YAML files containing select options definitions and outputs SQL statements
# to insert them into a MySQL database.
# This is usefull when chaning configuration location from symfony-config to settings-store.

import yaml
import json
import sys
import pymysql


def process_file(file_name):
    try:
        with open(file_name, 'r') as file:
            data = yaml.safe_load(file)

        definitions = data['pimcore']['objects']['select_options']['definitions']

        for key, value in definitions.items():
            select_options = value['selectOptions']
            select_options_json = json.dumps({"selectOptions": select_options})
            
            # Ensure correct escaping of JSON for SQL
            select_options_json_escaped = pymysql.converters.escape_string(select_options_json)
            
            insert_statement = f"INSERT INTO settings_store (id, scope, data, type) VALUES ('{key}', 'pimcore_select_options', '{select_options_json_escaped}', 'string');"
            print(insert_statement)
    
    except Exception as e:
        print(f"Error processing file {file_name}: {e}")


def main():
    if len(sys.argv) < 2:
        print("Usage: select-options-yaml2db.py <filename1.yaml> <filename2.yaml> ...")
        sys.exit(1)

    for file_name in sys.argv[1:]:
        process_file(file_name)


if __name__ == "__main__":
    main()

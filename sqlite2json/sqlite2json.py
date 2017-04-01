import sqlite3
import json
import sys
import os


def tables(connection):
    query = "SELECT name FROM sqlite_master WHERE type='table'"
    return [r[0] for r in connection.execute(query, ())]


def table_content(connection, table):
    connection.row_factory = sqlite3.Row  # http://stackoverflow.com/questions/7831371/
    return [{key: value for (key, value) in zip(r.keys(), r)}
            for r in connection.execute("SELECT * FROM %s" % table, ())]


def content(connection):
    return {table: table_content(connection, table) for table in tables(connection)}


def save_json(connection, dest_file):
    with open(dest_file, 'w', encoding='utf8') as f:
        json.dump(content(connection), f)


def save_schema(connection, dest_file):
    with open(dest_file, 'w', encoding='utf8') as f:
        for r in connection.execute("SELECT sql FROM sqlite_master WHERE type='table'"):
            f.write(r[0])
            f.write('\n\n')


def main(db_file):
    (directory, file_name) = os.path.split(db_file)
    base_file = os.path.splitext(file_name)[0]
    with sqlite3.connect(db_file) as db:
        save_json(db, os.path.join(directory, base_file + ".json"))
        save_schema(db, os.path.join(directory, base_file + "_schema.json"))


if __name__ == '__main__':
    main(sys.argv[1])

import sqlite2json

import unittest
import sqlite3


def ordered(obj):  # http://stackoverflow.com/questions/25851183/
    if isinstance(obj, dict):
        return sorted((k, ordered(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(ordered(x) for x in obj)
    else:
        return obj


class TestSqlite2Json(unittest.TestCase):
    def setUp(self):
        self.data = {
            'numbers': [
                {'name': 'one', 'value': 1},
                {'name': 'two', 'value': 2}
            ],
            'countries': [
                {'name': 'France', 'capital': 'Paris'},
                {'name': 'Germany', 'capital': 'Berlin'}
            ]
        }
        self.db = sqlite3.connect(':memory:')
        self.db.execute('CREATE TABLE numbers (name TEXT, value INT)')
        for r in self.data['numbers']:
            self.db.execute('INSERT INTO numbers VALUES (?, ?)', (r['name'], r['value']))
        self.db.execute('CREATE TABLE countries (name TEXT, capital TEXT)')
        for r in self.data['countries']:
            self.db.execute('INSERT INTO countries VALUES (?, ?)', (r['name'], r['capital']))
        self.db.commit()

    def test_return_table_names(self):
        tables = sqlite2json.tables(connection=self.db)
        self.assertEqual(['countries', 'numbers'], sorted(tables))

    def test_return_table_content(self):
        content = sqlite2json.table_content(connection=self.db, table='numbers')
        self.assertEqual(ordered(self.data['numbers']), ordered(content))

    def test_return_all_tables_content(self):
        js = sqlite2json.content(connection=self.db)
        self.assertEqual(ordered(self.data), ordered(js))


import sqlite2json

import unittest
import sqlite3
import io


def ordered(obj):  # http://stackoverflow.com/questions/25851183/
    if isinstance(obj, dict):
        return sorted((k, ordered(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(ordered(x) for x in obj)
    else:
        return obj


test_data = {
    'numbers': [
        {'name': 'one', 'value': 1},
        {'name': 'two', 'value': 2}
    ],
    'countries': [
        {'name': 'France', 'capital': 'Paris'},
        {'name': 'Germany', 'capital': 'Berlin'}
    ]
}


class TestToJson(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(':memory:')
        self.db.execute('CREATE TABLE numbers (name TEXT, value INT)')
        for r in test_data['numbers']:
            self.db.execute('INSERT INTO numbers VALUES (?, ?)', (r['name'], r['value']))
        self.db.execute('CREATE TABLE countries (name TEXT, capital TEXT)')
        for r in test_data['countries']:
            self.db.execute('INSERT INTO countries VALUES (?, ?)', (r['name'], r['capital']))
        self.db.commit()

    def test_return_table_names(self):
        tables = sqlite2json.tables(connection=self.db)
        self.assertEqual(['countries', 'numbers'], sorted(tables))

    def test_return_table_content(self):
        content = sqlite2json.table_content(connection=self.db, table='numbers')
        self.assertEqual(ordered(test_data['numbers']), ordered(content))

    def test_return_all_tables_content(self):
        js = sqlite2json.content(connection=self.db)
        self.assertEqual(ordered(test_data), ordered(js))


class TestFromJson(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")

    def test_tables_created(self):
        schema = """
        CREATE TABLE numbers (name TEXT, value INT);
        CREATE TABLE countries (name TEXT, capital TEXT);
        """
        sqlite2json.load_schema(connection=self.db, schema_fp=io.StringIO(schema))
        self.assertEqual(['countries', 'numbers'], sorted(sqlite2json.tables(connection=self.db)))

    def test_object_imported(self):
        self.db.execute("CREATE TABLE numbers (name TEXT, value INT);")
        self.db.execute("CREATE TABLE countries (name TEXT, capital TEXT);")
        inserted = sqlite2json.load_content_obj(connection=self.db, data=test_data)
        self.assertEqual(4, inserted)
        numbers = self.db.execute('SELECT * FROM numbers ORDER BY value')
        self.assertEqual([('one', 1), ('two', 2)], list(numbers))

#!/usr/bin/python
# coding: utf-8
import pg8000

# sql statements
CREATE_TABLE_SQL = """CREATE TABLE favicon (id              SERIAL PRIMARY KEY,
                                            url             VARCHAR(4096) UNIQUE NOT NULL,
                                            favicon_url     VARCHAR(4096) NULL,
                                            create_date     TIMESTAMP,
                                            updated         BOOLEAN,
                                            update_date     TIMESTAMP
                                            );
                                            """
DELETE_TABLE_SQL = "DROP TABLE IF EXISTS favicon;"


# class to wrap icon database
class IconDB():

    def __init__(self, host, port, database, user, password):
        self._host = host
        self._port = port
        self._database = database
        self._user = user
        self._password = password

        self._conn = pg8000.connect(user=user,
                                    password=password,
                                    host=host,
                                    port=port,
                                    database=database)

    def _execute(self, sqltext, commit=True):
        print(sqltext)
        with self._conn.cursor() as cursor:
            cursor.execute(sqltext)
            if commit:
                self._conn.commit()
            return cursor.rowcount

    def _query(self, sqltext, all_rows=False):
        print(sqltext)
        with self._conn.cursor() as cursor:
            cursor.execute(sqltext)
            print(cursor.rowcount)
            return cursor.fetchone() if not all_rows else cursor.fetchall()

    def create_table(self):
        self._execute(CREATE_TABLE_SQL)
        # need to create index on url as well

    def delete_table(self):
        self._execute(DELETE_TABLE_SQL)

    def create_row(self, target_url, favicon_url=None):
        if favicon_url:
            sqltext = f"""INSERT INTO favicon (url, favicon_url, create_date, updated, update_date)
                           VALUES ('{target_url}', '{favicon_url}', NOW(), TRUE, NOW());"""
        else:
            sqltext = f"""INSERT INTO favicon (url, create_date, updated)
                           VALUES ('{target_url}', NOW(), FALSE);"""
        self._execute(sqltext)

    def read_row(self, target_url):
        sqltext = f"SELECT * from favicon where url = '{target_url}'"
        return self._query(sqltext)

    def read_all_rows(self):
        sqltext = f"SELECT * from favicon"
        return self._query(sqltext, True)

    def update_favicon_url_row(self, target_url, favicon_url):
        sqltext = f"""UPDATE favicon SET favicon_url = '{favicon_url}', updated = TRUE, update_date = NOW()
                            WHERE url = '{target_url}'"""
        self._execute(sqltext)


if __name__ == "__main__":

    host = 'crayon-postgres.coghvekvxrjf.us-east-1.rds.amazonaws.com'
    # host = 'localhost'
    port = 5432
    database = 'favicon'
    user = 'crayon'
    password = 'Crayonpw99'

    icondb = IconDB(host, port, database, user, password)

    # icondb.create_table()

    # icondb.delete_table()

    print(icondb.read_row('aaa'))

    # icondb.create_row('ddd', 'eee')
    # icondb.create_row('fff', 'xxx')
    icondb.create_row('ggg')

    print(icondb.read_all_rows())


# CREATE TABLE favicon (
#   id              SERIAL PRIMARY KEY,
#   url             VARCHAR(4096) NOT NULL,
#   favicon_url     VARCHAR(4096) NULL,
#   create_date     TIMESTAMP,
#   updated         BOOLEAN,
#   update_date     TIMESTAMP
# );
# select column_name, data_type, character_maximum_length
# from INFORMATION_SCHEMA.COLUMNS where table_name = 'favicon';

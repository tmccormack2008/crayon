#!/usr/bin/python
# coding: utf-8
from datetime import datetime

import pg8000

# sql statements
CREATE_TABLE_SQL = """CREATE TABLE IF NOT EXISTS favicon
                                            (id              SERIAL PRIMARY KEY,
                                            url             VARCHAR(4096) UNIQUE NOT NULL,
                                            favicon_url     VARCHAR(4096) NULL,
                                            create_date     TIMESTAMP,
                                            updated         BOOLEAN,
                                            update_date     TIMESTAMP,
                                            update_comment  VARCHAR(4096) NULL
                                            );
                                            """
TABLE_INDEX_SQL = 'CREATE UNIQUE INDEX IF NOT EXISTS favicon_url_index ON favicon (url);'
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
        with self._conn.cursor() as cursor:
            try:
                cursor.execute(sqltext)
                if commit:
                    self._conn.commit()
            except Exception as error:
                print(f'Error executing sql {sqltext}')
                print(error)

            return cursor.rowcount

    def _query(self, sqltext, all_rows=False):
        with self._conn.cursor() as cursor:
            try:
                cursor.execute(sqltext)
            except Exception as error:
                print(f'Error executing sql {sqltext}')
                print(error)

            # return data rows
            return cursor.fetchone() if not all_rows else cursor.fetchall()

    def create_table(self):
        self._execute(CREATE_TABLE_SQL)
        self._execute(TABLE_INDEX_SQL)

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

    def create_error_row(self, target_url, update_comment):
        sqltext = f"""INSERT INTO favicon (url, create_date, updated, update_comment)
                       VALUES ('{target_url}', NOW(), FALSE, '{update_comment}');"""
        self._execute(sqltext)

    def read_row(self, target_url):
        sqltext = f"SELECT * from favicon where url = '{target_url}'"
        return self._query(sqltext)

    def read_unloaded_urls(self, max_rows=100):
        sqltext = f"SELECT url FROM favicon where favicon_url IS NULL and updated = FALSE limit {max_rows};"
        responses = self._query(sqltext, True)
        return [resp[0] for resp in responses]

    def update_favicon_url_row(self, target_url, favicon_url):
        sqltext = f"""UPDATE favicon SET favicon_url = '{favicon_url}', updated = TRUE, update_date = NOW()
                            WHERE url = '{target_url}'"""
        self._execute(sqltext)

    def update_error_row(self, target_url, update_comment):
        sqltext = f"""UPDATE favicon SET updated = TRUE, update_date = NOW(), update_comment = '{update_comment}'
                            WHERE url = '{target_url}'"""
        self._execute(sqltext)

    def seed_icondb_from_list(self, url_list):

        create_date = datetime.now()
        updated = False

        url_sql = ''
        for url in url_list:
            if url_sql:
                url_sql += f",('{url}', '{create_date}', {updated})"
            else:
                url_sql = f"('{url}', '{create_date}', {updated})"

        sqltext = f'INSERT INTO favicon (url, create_date, updated) VALUES {url_sql};'
        self._execute(sqltext)

        return len(url_list)

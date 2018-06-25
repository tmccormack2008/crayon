#!/usr/bin/python
# coding: utf-8
import requests
from requests.exceptions import ConnectionError, ReadTimeout, RequestException
from urllib import parse
from datetime import datetime
from pprint import pprint

from icondb import IconDB
from extract_utils import split_files

FAVICON_TEXT = 'favicon.ico'


def getIconDBParams():

    # setup function so we can pull from SSM later
    params = {'host': 'crayon-postgres.coghvekvxrjf.us-east-1.rds.amazonaws.com',
              'port': 5432,
              'database': 'favicon',
              'user': 'crayon',
              'password': 'Crayonpw99',
              }

    return params


def getIconDBConn(params):
    return IconDB(params['host'], params['port'], params['database'], params['user'], params['password'])


def getFaviconUrlFromRow(row):
    return row[2]


class FavIconDBUtils():

    def __init__(self):

        # use single connection for duration of processing
        self._icondb = getIconDBConn(getIconDBParams())

        # persist session to handles cookies JIC
        self._session = requests.Session()

        # create table if it does not exist
        self._icondb.create_table()

    def check_url(self, favicon_url):
        # head since we are just checking for existence
        status_code = 0
        try:
            resp = self._session.head(favicon_url, timeout=10, allow_redirects=True)
        except ReadTimeout:
            status_code = 408
        else:
            status_code = resp.status_code
            if resp.status_code == requests.codes.ok:
                return(resp)

        # try a get since some websites don't handle 'HEAD'
        print(f'HTTP HEAD returned {status_code} for {favicon_url}, trying GET')
        try:
            resp = self._session.get(favicon_url, timeout=10)
        except RequestException:
            raise
        except Exception:
            raise
        else:
            return(resp)

    def generate_favicon_url(self, temp_url):
        # build favicon url from parsed target_url
        base_url = '{0}://{1}'.format(temp_url.scheme, temp_url.netloc if temp_url.netloc else temp_url.path)
        return base_url, parse.urljoin(base_url, FAVICON_TEXT)

    def getFaviconUrl(self, target_url, force_refresh=False):

        if not target_url:
            msg = f'Missing target url'
            return 400, None, msg

        temp_url = parse.urlsplit(target_url, scheme='http')

        # if we don't have either a netloc or a path component, bail
        if not temp_url.netloc and not temp_url.path:
            msg = f'Invalid target url {target_url}'
            return 400, None, msg

        # forcing a refresh, just overwrite the current data
        # if not, check the database and if an icon reference exists, use it and bail
        # otherwise try to read it again
        if force_refresh:
            update_row = True
        else:
            update_row = False
            row = self._icondb.read_row(target_url)
            if row:
                favicon_url = getFaviconUrlFromRow(row)
                if favicon_url:
                    return requests.codes.ok, favicon_url, ''
                else:
                    update_row = True

        # build favicon url from parsed target_url
        base_url, favicon_url = self.generate_favicon_url(temp_url)

        # check for existence of favicon
        return_status = ()
        try:
            # try head, if it doesn't work try get just in case
            resp = self.check_url(favicon_url)
        except ConnectionError:
            msg = f'Unable to reach website {base_url}'
            self.writeIconDBErrorRow(target_url, msg, update_row)
            return_status = (404, None, msg)
        except ReadTimeout:
            msg = f'Timeout trying to reach website {base_url}'
            self.writeIconDBErrorRow(target_url, msg, update_row)
            return_status = (408, None, msg)
        except RequestException as error:
            print(error)
            msg = f'Requests error reaching {base_url} - {error}'
            self.writeIconDBErrorRow(target_url, msg, update_row)
            return_status = (404, None, msg)
        except Exception as error:
            print(error)
            msg = f'Urllib error reaching {base_url} - {error}'
            self.writeIconDBErrorRow(target_url, msg, update_row)
            return_status = (404, None, msg)

        else:
            if resp.status_code == requests.codes.ok:
                self.writeIconDBRow(target_url, favicon_url, update_row)
                return_status = (resp.status_code, favicon_url, '')
            else:
                msg = f'Error {resp.status_code} reading favicon from {favicon_url}'
                self.writeIconDBErrorRow(target_url, msg, update_row)
                return_status = (resp.status_code, None, msg)

        return return_status

    def bulkLoadInconDB(self, input_path, row_count):

        file_list = split_files(input_path, row_count)
        if not file_list:
            print(f'Invalid input file {input_path}')
            return

        load_path = file_list[0][0]
        if not load_path:
            print(f'Invalid file list {file_list}')
            return

        with open(load_path) as load_file:
            row_count = 0

            while True:
                line = load_file.readline().strip()
                if not line:
                    print(f'Loaded {row_count} rows from {input_path}')
                    return row_count

                rank, url = line.split(',')
                self.getFaviconUrl(url)
        return

    def seedIconDBFromList(self, url_list):
        start_time = datetime.now()
        row_count = self._icondb.seed_icondb_from_list(url_list)
        duration = datetime.now() - start_time
        print(f'Inserted {row_count} rows in {duration}')
        return row_count

    def seedIconDBFromFile(self, load_path, rows=1000):

        total_rows = 0
        url_list = []

        with open(load_path) as load_file:
            row_count = 0

            while True:
                line = load_file.readline().strip()
                if not line:
                    total_rows += self.seedIconDBFromList(url_list)
                    print(f'Loaded {total_rows} rows from {load_path}')
                    break

                rank, url = line.split(',')
                url_list.append(url)

                row_count += 1
                if row_count >= rows:
                    total_rows += self.seedIconDBFromList(url_list)
                    row_count = 0
                    url_list = []
        return total_rows

    def loadSeededRows(self, rows=10, force_refresh=False):
        url_list = self._icondb.read_unloaded_urls(rows)

        bad_results = []
        rows_processed = 0
        row_count = 0
        for url in url_list:
            status, favicon_url, msg = self.getFaviconUrl(url, force_refresh)
            rows_processed += 1
            if status == requests.codes.ok:
                row_count += 1
            else:
                bad_results.append((status, msg))
            if rows_processed % 100 == 0:
                print(f'...{rows_processed} rows processed...')
        return rows_processed, row_count, bad_results

    def writeIconDBRow(self, target_url, favicon_url, update_row=True):
        if update_row:
            self._icondb.update_favicon_url_row(target_url, favicon_url)
        else:
            self._icondb.create_row(target_url, favicon_url)

    def writeIconDBErrorRow(self, target_url, update_comment, update_row=True):
        if update_row:
            self._icondb.update_error_row(target_url, update_comment)
        else:
            self._icondb.create_error_row(target_url, update_comment)


if __name__ == "__main__":

    # host = 'crayon-postgres.coghvekvxrjf.us-east-1.rds.amazonaws.com'
    # # host = 'localhost'
    # port = 5432
    # database = 'favicon'
    # user = 'crayon'
    # password = 'Crayonpw99'

    # icondb = IconDB(host, port, database, user, password)

    # icondb.create_table()

    # icondb.delete_table()

    # start_time = datetime.now()
    favicondb = FavIconDBUtils()

    # print(favicondb.getFaviconUrl('wikipedia.org'))
    print(favicondb.getFaviconUrl('usps.com', True))
    # print(favicondb.getFaviconUrl('thesaurus.com'))
    # print(favicondb.getFaviconUrl('homedepot.com'))
    print(favicondb.getFaviconUrl('latticesemi.com', True))
    print(favicondb.getFaviconUrl('thepiratebay.pet', True))
    print(favicondb.getFaviconUrl('https://www.usps.com', True))
    print(favicondb.getFaviconUrl('amazon.it', True))

    # input_path = 'd:/crayon/data/top-1m.csv'
    # row_count = 200000

    # favicondb.bulkLoadInconDB(input_path, row_count)
    # load_path = 'd:/crayon/data/top-1m001.csv'
    # total_rows = favicondb.seedIconDBFromFile(load_path, 3000)

    # total_rows, bad_results = favicondb.loadSeededRows(100)
    # if bad_results:
    #     pprint(bad_results)

    # duration = datetime.now() - start_time
    # print(f'Seeded {total_rows} rows in {duration}')

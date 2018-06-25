#!/usr/bin/python
# coding: utf-8
from datetime import datetime
from pprint import pprint

from favicon_utils import FavIconDBUtils

if __name__ == "__main__":

    start_time = datetime.now()
    favicondb = FavIconDBUtils()

    total_rows, loaded_rows, bad_results = favicondb.loadSeededRows(10000)

    duration = datetime.now() - start_time

    print('Errors:')
    if bad_results:
        pprint(bad_results)

    print(f'Processed {total_rows} rows')
    print(f'Loaded {loaded_rows} rows in {duration}')
    print(f'Found errors with {len(bad_results)} urls')

#!/usr/bin/python
# coding: utf-8
from datetime import datetime

from favicon_utils import FavIconDBUtils

if __name__ == "__main__":

    start_time = datetime.now()
    favicondb = FavIconDBUtils()

    load_path = 'd:/crayon/data/top-1m001.csv'
    total_rows = favicondb.seedIconDBFromFile(load_path, 3000)

    duration = datetime.now() - start_time
    print(f'Seeded {total_rows} rows in {duration}')

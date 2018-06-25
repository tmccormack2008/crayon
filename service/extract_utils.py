#!/usr/bin/python
# coding: utf-8
import os


def split_files(input_path, rows):

    filecount = 0
    output_base, output_ext = os.path.splitext(input_path)

    results = []

    row_count = 0
    with open(input_path) as input_file:

        # loop through file and write out sliced chunks of files
        while True:

            # generate output file name
            filecount += 1
            output_path = f'{output_base}{filecount:03d}{output_ext}'

            # write output file of 'rows' size
            row_count = write_output_file(input_file, rows, output_path)

            # broke on exact boundaries, decrement filecount
            if not row_count:
                break

            print(f'wrote {row_count} rows rows to {output_path}')
            results.append((output_path, row_count))

            if row_count < rows:
                break

    return results


def write_output_file(input_file, rows, output_path):

    # break out when no addtional lines
    line = input_file.readline()
    if not line:
        return

    row_count = 0
    with open(output_path, 'w') as output_file:

        # copy up to rows lines into output file
        while True:

            # write out line and increment count
            output_file.write(line)
            row_count += 1

            # break out of loop
            if row_count >= rows:
                break

            # break out when no addtional lines
            line = input_file.readline()
            if not line:
                return row_count

    return row_count


if __name__ == "__main__":

    input_path = 'd:/crayon/data/top-1m.csv'
    row_count = 200000
    print(split_files(input_path, row_count))

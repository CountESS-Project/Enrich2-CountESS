import os
import sys
from itertools import product

cwd = os.path.dirname(__file__)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: <input file> <output directory>"
              "\n\nNames should not contain spaces")
        sys.exit(0)

    input_file = sys.argv[1]
    out_dir = sys.argv[2]

    with open(input_file, 'rt') as fp:
        lines = [line.split(',') for line in fp if line.strip() != '']
    
    if len(lines) != 2:
        print("Input file should be two lines that are comma delimited")
        sys.exit(0)
    
    file_prefixes, hdf5_store_groups = lines
    for prefix, store_group in product(file_prefixes, hdf5_store_groups):
        file_name = "{}_{}.tsv".format(prefix.strip(), store_group.strip())
        file_path = os.path.join(cwd, out_dir, file_name)
        open(file_path, 'wt').close()


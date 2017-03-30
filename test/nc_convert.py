import os
import sys
import glob


def get_dir_contents(directory, file_type):
	for path in glob.glob('{0}/*.{1}'.format(directory, file_type)):
		yield path


def create_file_path(fname):
    path = os.path.join(os.path.dirname(__file__), fname)
    return path


def convert_coding_file_to_non_coding_file(file_name):
    full_path = create_file_path(file_name)
    new_path = full_path.replace('c_', 'n_')
    output_ = open(new_path, 'w')
    input_ = open(full_path, 'r')
    for line in input_:
        xs = line.strip().split(';')
        if len(xs) >= 2:
            left, right = xs
            if "stats" in full_path:
                new_left = left.strip()
            else:
                ids = [x.strip().split(' ')[0] for x in left.split(', ')]
                ids = [x.replace('c.', 'n.') for x in ids]
                new_left = ', '.join(ids)
            output_.write("{};{}\n".format(new_left, right))
    output_.close()
    input_.close()


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Usage: python nc_convert.py <path_to_directory>")
        sys.exit(0)
    path_to_dir = sys.argv[1]
    for file_name in get_dir_contents(path_to_dir, file_type='tsv'):
        print(file_name)
        convert_coding_file_to_non_coding_file(file_name)
import sys
import os
import re
from os import path

import numpy as np
from algorithm.parameters import params


def read_dataset_input_output_from_txt_with_inval_outval_as_str_list(datasets_sub_folder, dataset_type):
    dataset_type = dataset_type.upper().strip()
    datasets_sub_folder = datasets_sub_folder.strip()
    if dataset_type not in ("TRAIN", "TEST"):
        raise ValueError(f'Error for dataset type ({dataset_type}) not being in (TRAIN, TEST).')
    path_of_actual_dataset = path.join("..", "datasets", datasets_sub_folder, params['DATASET_'+dataset_type])
    with open(path_of_actual_dataset, 'r') as data_file_txt:
        d = {}
        all_lines = data_file_txt.readlines()
        if len(all_lines) != 2:
            raise ValueError(f'File {path_of_actual_dataset} contains {len(all_lines)}, it must contain exactly 2 lines.')
        for i in range(2):
            s = all_lines[i].strip()
            s = re.sub(r'\s+', ' ', s.replace('\t', ' ').replace('\n', ' ').replace('\r', ' ').strip()).strip()
            s = s.replace('invals', 'inval')
            s = s.replace('outvals', 'outval')
            s = s.replace('inval = ', 'inval=')
            s = s.replace('inval =', 'inval=')
            s = s.replace('inval= ', 'inval=')
            s = s.replace('outval = ', 'outval=')
            s = s.replace('outval =', 'outval=')
            s = s.replace('outval= ', 'outval=')
            s = s[s.index('=')+2:-1].strip()
            s = s.replace('] , [', '], [')
            s = s.replace('] ,[', '], [')
            s = s.replace('], [', '],[')
            s = s.replace('],[', ']<SPLITSEPARATOR>[')
            l = s.split('<SPLITSEPARATOR>')
            if i == 0:
                d['in'] = l
            if i == 1:
                d['out'] = l
        if len(d['in']) != len(d['out']):
            raise ValueError(f'Length of input ({len(d["in"])}) and length of output ({len(d["out"])}) do not match.')
        if dataset_type == 'TRAIN':
            d['in'] = d['in'][:params['NUM_TRAIN_EXAMPLES']]
            d['out'] = d['out'][:params['NUM_TRAIN_EXAMPLES']]
    return d


def get_Xy_train_test_separate(train_filename, test_filename, skip_header=0):
    """
    Read in training and testing data files, and split each into X
    (all columns up to last) and y (last column). The data files should
    contain one row per training example.
    
    :param train_filename: The file name of the training dataset.
    :param test_filename: The file name of the testing dataset.
    :param skip_header: The number of header lines to skip.
    :return: Parsed numpy arrays of training and testing input (x) and
    output (y) data.
    """

    if params['DATASET_DELIMITER']:
        # Dataset delimiter has been explicitly specified.
        delimiter = params['DATASET_DELIMITER']

    else:
        # Try to auto-detect the field separator (i.e. delimiter).
        f = open(train_filename)
        for line in f:
            if line.startswith("#") or len(line) < 2:
                # Skip excessively short lines or commented out lines.
                continue

            else:
                # Set the delimiter.
                if "\t" in line:
                    delimiter = "\t"
                    break
                elif "," in line:
                    delimiter = ","
                    break
                elif ";" in line:
                    delimiter = ";"
                    break
                elif ":" in line:
                    delimiter = ":"
                    break
                else:
                    print(
                        "Warning (in utilities.fitness.get_data.get_Xy_train_test_separate)\n"
                        "Warning: Dataset delimiter not found. "
                        "Defaulting to whitespace delimiter.")
                    delimiter = " "
                    break
        f.close()

    # Read in all training data.
    train_Xy = np.genfromtxt(train_filename, skip_header=skip_header,
                             delimiter=delimiter)

    try:
        # Separate out input (X) and output (y) data.
        train_X = train_Xy[:, :-1] # all columns but last
        train_y = train_Xy[:, -1]  # last column

    except IndexError:
        s = "utilities.fitness.get_data.get_Xy_train_test_separate\n" \
            "Error: specified delimiter '%s' incorrectly parses training " \
            "data." % delimiter
        raise Exception(s)

    if test_filename:
        # Read in all testing data.
        test_Xy = np.genfromtxt(test_filename, skip_header=skip_header,
                                delimiter=delimiter)

        # Separate out input (X) and output (y) data.
        test_X = test_Xy[:, :-1] # all columns but last
        test_y = test_Xy[:, -1]  # last column

    else:
        test_X, test_y = None, None

    return train_X, train_y, test_X, test_y


def get_data(train, test):
    """
    Return the training and test data for the current experiment.
    
    :param train: The desired training dataset.
    :param test: The desired testing dataset.
    :return: The parsed data contained in the dataset files.
    """

    # Get the path to the training dataset.
    train_set = path.join("..", "datasets", train)

    if test:
        # Get the path to the testing dataset.
        test_set = path.join("..", "datasets", test)

    else:
        # There is no testing dataset used.
        test_set = None

    # Read in the training and testing datasets from the specified files.
    training_in, training_out, test_in, \
    test_out = get_Xy_train_test_separate(train_set, test_set, skip_header=1)

    return training_in, training_out, test_in, test_out

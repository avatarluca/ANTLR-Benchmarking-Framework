import csv
import json
import os.path
import logging
import shutil
from datetime import datetime

from config import DIFF_TOL, DECIMALS, USE_SNAPSHOT, PARSER_GRAMMAR_PATH, \
    TEMP_PARSER_GRAMMAR_PATH


logger = logging.getLogger('Parsing Performance Measurement')
results = []
metadata = {}


def load_snapshot(path, name):
    """
        Loads the results and metadata for a given name.

        Args:
            path (str): The path to the snapshot.
            name (str): The name of the snapshot.
    """

    current_path = os.path.abspath(os.curdir)
    path = os.path.join(current_path, path, name)

    if not os.path.exists(path):
        raise FileNotFoundError(f'Snapshot with name "{name}" doesn\'t exist.')

    csvfile_path = os.path.join(path, 'measurements.csv')
    metadata_path = os.path.join(path, 'metadata.json')

    with open(csvfile_path, newline='') as csvfile:
        snapshot_reader = csv.reader(csvfile)
        for row in snapshot_reader:
            results.append(row)

    with open(metadata_path, newline='') as jsonfile:
        global metadata
        metadata = json.load(jsonfile)

def recreate_snapshot(path, name):
    """
        Recreates the snapshot.
        This is done by saving the new antlr grammar, overriding the file with the old antlr grammar building, measure and finally rewrite new grammar.

        Args:
            path (str): The path to the snapshot.
            name (str): The name of the snapshot.
    """

    current_path = os.path.abspath(os.curdir)
    path = os.path.join(current_path, path, name)
    old_grammar_path = os.path.join(path,'Grammar.g4')
    new_grammar_path = PARSER_GRAMMAR_PATH
    temp_grammar_path = TEMP_PARSER_GRAMMAR_PATH

    os.makedirs(os.path.dirname(temp_grammar_path), exist_ok=True)
    shutil.copyfile(new_grammar_path, temp_grammar_path)
    shutil.copyfile(old_grammar_path, new_grammar_path)

def close_recreate_snapshot(new_results):
    """
        Resolves the snapshot by copying the temp back to origin.

        Args:
            new_results (list): The results of the snapshot.
    """

    new_grammar_path = PARSER_GRAMMAR_PATH
    temp_grammar_path = TEMP_PARSER_GRAMMAR_PATH

    shutil.copyfile(temp_grammar_path, new_grammar_path)

    # Because of backup reasons, the temp file gets not deleted. If this is not necessary uncomment the following line.
    # os.remove(temp_grammar_path)

    global results
    results = new_results

def save_snapshot(path, header, data, metadata, name=""):
    """
        Saves the results and metadata of a snapshot.
        The snapshot gets saved as "snapshot-[CURRENT_TIMESTAMP]".
        This can be changed by setting the name arg

        Args:
            path (str): The path to the snapshot.
            header (list): The header (column names) of the snapshot.
            data (list): The results of the snapshot.
            metadata (dict): The metadata of the snapshot.
            name (str): The name of the snapshot.
    """

    current_path = os.path.abspath(os.curdir)
    if not name: name = "snapshot-" + datetime.now().strftime("%y%m%d_%H%M%S")
    path = os.path.join(current_path, path, name)

    csvfile_path = os.path.join(path,'measurements.csv')
    metadata_path = os.path.join(path,'metadata.json')
    grammar_path = os.path.join(path,'Grammar.g4')

    if not os.path.exists(path):
        os.makedirs(path)

    with open(csvfile_path, mode='w', newline='') as csvfile:
        snapshot_writer = csv.writer(csvfile)
        snapshot_writer.writerow(header)
        snapshot_writer.writerows(data)

    with open(metadata_path, mode='w', newline='') as jsonfile:
        json.dump(metadata, jsonfile)

    shutil.copyfile(PARSER_GRAMMAR_PATH, grammar_path)

    print(f"📥 Measurement saved as {name}")

def get_result(method_name, class_name):
    """
        Searches a subarray of the results with a given methodname (first row of the snapshot).

        Args:
            method_name (str): The name of the method to search for.
            class_name (str): The name of the class to search for (used because their can be same methods in different classes).
        Error:
            ValueError: If the method is not found.
    """

    result = next((tupel for tupel in results if (tupel[0] == method_name and tupel[5] == class_name)), None)

    if result is None:
        raise ValueError("Method name with the given class name not available")

    return result

def method_exists(method_name, class_name):
    """
        Check if the method exists in snapshot.

        Args:
            method_name (str): The name of the method to search for.
            class_name (str): The name of the class to search for (used because their can be same methods in different classes).
        Return:
            True, if the method exists.
    """

    method_exists = False

    try:
        get_result(method_name, class_name)
        method_exists = True
    except ValueError:
        logger.info(f"Method name {method_name} with class name {class_name} does not exist in snapshot {USE_SNAPSHOT}")

    return method_exists

def get_all_methods_that_not_exist(current_results):
    """
        Get all methods that do not exist in current results but exists in snapshot.

        Args:
            current_results (list): The results of the snapshot.
        Returns:
            A list of all methods that do not exist in current results but exist in snapshot.
    """

    methods = []

    for result in results:
        exist = False
        for current_result in current_results:
            if current_result[0] == result[0] and current_result[5] == result[5]: exist = True

        if not exist: methods.append([result[5], result[0]])

    return methods

def benchmark(current_results):
    """
        Benchmarking all tests, by comparing which tests exist in both lists (current and snapshots) and summing up their measurements.
        This is simply done by looping the current results list and sum up those parts which exists in snapshot.

        Returns:
            The benchmark (tuple of avg current and snapshot and a list of the summed up methods) of all tests.
    """

    benchmarked_methods = []
    sum_avg_benchmark_current = 0
    sum_avg_benchmark_snapshot = 0

    for result in current_results:
        if method_exists(result[0], result[5]):
            sum_avg_benchmark_current += result[1]

            snap_result = get_result(result[0], result[5])
            sum_avg_benchmark_snapshot += float(snap_result[1])

            benchmarked_methods.append([result[5], result[0]])

    return sum_avg_benchmark_current, sum_avg_benchmark_snapshot, benchmarked_methods

"""
Queries
"""
def check_difference(method_name, new_value, class_name):
    """
        Calculates the difference between current value of snapshot and new value.

        Args:
            method_name (str): The name of the method to search for.
            new_value (float): The new value.
            class_name (str): The name of the class to search for (used because their can be same methods in different classes).
    """

    value = 0
    try:
        value = float(get_result(method_name, class_name)[1])
    except ValueError:
        logger.info(f"ℹ️ Method name {method_name} in snapshot not available. Difference is set to 0.")

    diff = new_value - value

    return 0 if (abs(diff) < DIFF_TOL and value > 1) else round(diff, DECIMALS)

def check_percent(method_name, new_value, class_name):
    """
        Calculates the percent difference between current value of snapshot and new value.

        Args:
            method_name (str): The name of the method to search for.
            new_value (float): The new value.
            class_name (str): The name of the class to search for (used because their can be same methods in different classes).
    """

    value = 0
    try:
        value = float(get_result(method_name, class_name)[1])
    except ValueError:
        logger.info(f"ℹ️ Method name {method_name} and class name {class_name} in snapshot not available. Percent is set to 100.")

    return round(100 / value * new_value, DECIMALS) if value != 0 else 100

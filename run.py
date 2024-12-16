import logging
import timeit
import unittest
from io import StringIO
import subprocess

from snapshot_handler import check_difference, check_percent, \
    load_snapshot, save_snapshot, method_exists, get_all_methods_that_not_exist, benchmark, recreate_snapshot, \
    close_recreate_snapshot
from config import NUMBER_OF_RUNS_PER_TEST, TEST_CASES, USE_SNAPSHOT, BUILD_PARSER, \
    PARSER_BUILD_SCRIPT_PATH, SNAPSHOTS_FOLDER_NAME, \
    MAKE_SNAPSHOT, SNAPSHOT_NAME, RESULT_HEADER, PARSING_TIME_ANALYSIS, OUTLIER_DETECTION, RUN_TESTS_MULTIPLE_TIMES, \
    RECREATE_SNAPSHOT, LOGGING_FILE_NAME, LOGGER_NAME, NUMBER_OF_BENCHMARKS

from print import print_progress_bar, print_results, print_title, \
    print_recreate_title, print_metadata_results


logger = logging.getLogger(LOGGER_NAME)
results = []
metadata_collection = []
total_time = 0


def measure():
    """
        Runs the main measurement process.
        When small values (< tolerance) is activated, they will run for just once to test if the unit test is still successfully.

        Returns:
            A tuple of amount of tests, which were executed, sum of all test results, 2 lists of methodnames which not exist in snapshot vice versa and a list of failed tests.
    """

    amount_of_tests = 0
    not_available_tests_in_snapshot = []
    failed_tests = []

    for test_case in TEST_CASES:
        test_class = test_case[0]
        class_name = fullname(test_class())
        test_methods = [method for method in dir(test_class) if method.startswith("test_")]

        for method_name in test_methods:
            print(f"\n> {class_name}::{method_name}:")

            exists_in_snapshot = method_exists(method_name, class_name)

            if not exists_in_snapshot:
                not_available_tests_in_snapshot.append([class_name, method_name])

            avg, res = run_test_case(test_class, method_name)

            total_parsing_time = 0

            if PARSING_TIME_ANALYSIS and RUN_TESTS_MULTIPLE_TIMES: # TODO: Add total parsing time also for RUN_TESTS_MULTIPLE_TIMES = False. For now its 0 if RUN_TESTS_MULTIPLE_TIMES = False.
                global total_time
                total_parsing_time = total_time
                
                """
                You can also set total parsing time directly to the parsetree antlr transformation function.

                Example:
                from use_antlr_to_transform_from_grammar_to_ir import parsing_time
                total_parsing_time = parsing_time
                """
                

            if not res: failed_tests.append([class_name, method_name])

            diff = check_difference(method_name, avg, class_name)
            percent = check_percent(method_name, avg, class_name)
            results.append([method_name, avg, diff, res, percent, class_name, total_parsing_time])

            amount_of_tests += 1

    not_available_tests_in_current = get_all_methods_that_not_exist(results)

    sum_avg = 0
    sum_total_parsing_time = 0
    for result in results:
        sum_avg += result[1]
        sum_total_parsing_time += result[6]

    # remove header elements if they exist in list
    remove_element_from_list([RESULT_HEADER[5], RESULT_HEADER[1]], not_available_tests_in_current)
    remove_element_from_list([RESULT_HEADER[5], RESULT_HEADER[1]], not_available_tests_in_snapshot)

    return amount_of_tests, sum_avg, not_available_tests_in_snapshot, not_available_tests_in_current, failed_tests, sum_total_parsing_time

def remove_element_from_list(remove_element, lst):
    for element in lst:
        if len(element) != len(remove_element): continue

        for j in range(len(remove_element)):
            if remove_element[j] == element[j]: lst.remove(element)

def run_test_case(test_class, method_name, it=NUMBER_OF_RUNS_PER_TEST):
    """
        Runs a single unit test.

        Args:
            test_class (str): The test class.
            method_name (str): The method name.
            it (int): The number of iterations, which the test gets executed.
        Returns:
            A tuple of the average time from all iterations and if the test was successfully.
    """
    if not RUN_TESTS_MULTIPLE_TIMES: it = 1

    measurements = []
    for i in range(it):
        res = False
        try:
            global total_time

            suite = unittest.TestSuite()

            if suite is None:
                raise ValueError("Test-Suite not loaded")

            output = StringIO()

            suite.addTest(test_class(method_name))
            runner = unittest.TextTestRunner(stream=output, verbosity=0)

            if runner is None:
                raise ValueError("Test-Runner not created")

            start_total_time = timeit.default_timer()

            temp_res = runner.run(suite)

            end_total_time = timeit.default_timer()
            total_time = (end_total_time - start_total_time) * 1000
            
            res = temp_res.wasSuccessful()
        except Exception as e:
            logger.error(f"Error in executing {method_name}: {e}")
            continue

        if RUN_TESTS_MULTIPLE_TIMES:
            from measure_performance import last_performance_measure_in_ms
            measurements.append(last_performance_measure_in_ms)
        else:
            from measure_performance import last_performance_measure_in_ms_list
            measurements = last_performance_measure_in_ms_list
        print_progress_bar(i + 1, it)

    time_avg = detect_outliers_and_calculate_avg(measurements, detection=OUTLIER_DETECTION)
    print_progress_bar(it, it)

    return time_avg, res

def detect_outliers_and_calculate_avg(measurements, detection="high-low"):
    """
        Detects outliers and calculates average time without outliers.

        Args:
            measurements (list): A list of measurements.
            detection (str): The type of detection.
        Returns:
            The average time without outliers.
    """

    def calc_avg(lst): return sum(lst) / len(lst)

    if detection == "high-low": # handles outliers by removing highest and lowest point
        if len(measurements) > 2:
            measurements.remove(max(measurements))
            measurements.remove(min(measurements))
    if detection == "iqr":
        Q1 = calulate_quartil(measurements, 0.25)
        Q3 = calulate_quartil(measurements, 0.75)

        IQR = Q3 - Q1
        bottom_border = Q1 - 1.5 * IQR
        top_border = Q3 + 1.5 * IQR

        measurements = [x for x in measurements if x >= bottom_border and x <= top_border]

    return calc_avg(measurements)

def calulate_quartil(data, quartil):
    """
        Calculates a quartil of the given data.

        Args:
            data (list): A list of measurements.
            quartil (float): The quartil.
        Returns:
            The quartil of the data.

    """

    data.sort()
    index = (len(data) - 1) * quartil
    if index.is_integer():
        return data[int(index)]
    else:
        lower_index = int(index)
        upper_index = lower_index + 1
        return (data[lower_index] + data[upper_index]) / 2

def fullname(o):
    """
        Gets the full name of an object.

        Args:
            o (object): The object to get the full name of.
        Returns:
            The full name of an object.
    """

    klass = o.__class__
    module = klass.__module__
    if module == 'builtins':
        return klass.__qualname__ # avoid outputs like 'builtins.str'
    return module + '.' + klass.__qualname__

def run(recreate=False, suffix=""):
    """
        The main loop for the benchmarking framework.

        Args:
            recreate (bool): If True, then the results will not be shown.
            suffix (string): The suffix to append to the filename (specially used when there are multiple benchmarks).
    """

    amount_of_tests, sum_avg, not_available_tests_in_snapshot, not_available_tests_in_current, failed_tests, sum_total_parsing_time = measure()
    sum_avg_benchmark_current, sum_avg_benchmark_snapshot, benchmarked_methods = benchmark(results)

    list_of_tested_methods = [result[0] for result in results]

    metadata = {
        "sum_avg": sum_avg,
        "sum_total_parsing_time": sum_total_parsing_time,
        "failed_tests": failed_tests,
        "amount_of_tests": amount_of_tests,
        "list_of_tested_methods": list_of_tested_methods,
        "RUN_TESTS_MULTIPLE_TIMES": RUN_TESTS_MULTIPLE_TIMES,
        "NUMBER_OF_RUNS_PER_TEST": NUMBER_OF_RUNS_PER_TEST,
    }

    metadata_collection.append([metadata, sum_avg_benchmark_snapshot])

    if MAKE_SNAPSHOT and not recreate: save_snapshot(SNAPSHOTS_FOLDER_NAME, RESULT_HEADER, results, metadata, name=SNAPSHOT_NAME + suffix)
    if not recreate: print_results(amount_of_tests, results, failed_tests, sum_avg, sum_avg_benchmark_current, sum_avg_benchmark_snapshot, benchmarked_methods, not_available_tests_in_snapshot, not_available_tests_in_current, sum_total_parsing_time)

if __name__ == '__main__':
    logging.basicConfig(filename=SNAPSHOTS_FOLDER_NAME + "/" + LOGGING_FILE_NAME,
                        filemode='a', # append logs
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.INFO)

    if RECREATE_SNAPSHOT:
        print_recreate_title()

        recreate_snapshot(SNAPSHOTS_FOLDER_NAME, USE_SNAPSHOT)
        subprocess.call(['sh', PARSER_BUILD_SCRIPT_PATH])

        run(True)

        close_recreate_snapshot(results)
        results = []
        metadata_collection = []
    else:
        # not necessary if RECREATE_SNAPSHOT = true, because results are already set in the correct spots
        load_snapshot(SNAPSHOTS_FOLDER_NAME, USE_SNAPSHOT)

    print_title()
    if BUILD_PARSER: subprocess.call(['sh', PARSER_BUILD_SCRIPT_PATH])

    for i in range(NUMBER_OF_BENCHMARKS):
        suffix = "" if i == 0 else str(i)

        print(f'\n💡 New measure and benchmark run: {i + 1}')

        run(suffix = suffix)

        results = []

    if NUMBER_OF_BENCHMARKS > 1:
        sum_avg_benchmark = []

        for i, benchmark in enumerate(metadata_collection):
            sum_avg_benchmark.append(benchmark[0]['sum_avg'])

        print_metadata_results(metadata_collection,
                               detect_outliers_and_calculate_avg(sum_avg_benchmark, detection=OUTLIER_DETECTION),
                               metadata_collection[0][1])

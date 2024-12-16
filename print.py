import logging
import sys

from tabulate import tabulate

from config import RESULT_HEADER, USE_SNAPSHOT, BUILD_PARSER, DECIMALS, \
    RUN_TESTS_MULTIPLE_TIMES, PARSING_TIME_ANALYSIS, LOGGER_NAME, RECREATE_SNAPSHOT


logger = logging.getLogger(LOGGER_NAME)


def print_recreate_title():
    """
        Prints the recreation title of the benchmark.
        This also contains some information of the current config.
    """
    print(f"\n\n{'♻️ Recreate measurement with old grammar from snapshot':^100}")
    print('=' * 100)

    logger.info(f"\n\n{'♻️ Recreate measurement with old grammar from snapshot':^100}")

def print_title():
    """
        Prints the title of the benchmark.
        This also contains some information of the current config.
    """
    print(f"\n\n{'🛫 Start measurement':^100}")
    print('=' * 100)
    print(f'📤 {"Use recreated snapshot" if RECREATE_SNAPSHOT else "Load snapshot " + USE_SNAPSHOT }"{" and build parser of current grammar" if BUILD_PARSER else ""} ...')

    logger.info(f"\n{'Create measurement':^100}")
    logger.info(f'📤 Load snapshot "{USE_SNAPSHOT}"{" and build parser of current grammar" if BUILD_PARSER else ""} ...')

def print_progress_bar(iteration, total, length=40):
    """
        Prints a progress bar.

        Args:
            iteration: current iteration
            total: total iterations
            length: length of progress bar
    """

    percent = (iteration / total) * 100
    filled_length = int(length * iteration // total)
    bar = '█' * filled_length + '-' * (length - filled_length)
    sys.stdout.write(f'\r|{bar}| {percent:.2f}% Complete')
    sys.stdout.flush()

def print_metadata_results(metadata_collection, sum_avg_over_all_benchmarks, sum_avg_over_snapshot):
    """
        Prints the result over all benchmarks.

        Args:
              metadata_collection (list): list of benchmark results
              sum_avg_over_all_benchmarks (float): average over all measured benchmarks.
              sum_avg_over_snapshot (float): average benchmark results of snapshot
    """
    print(f"\n\n{'🚀 Analysis: Results over all benchmarks':^100}")
    print('=' * 100)
    print(f'ℹ️ Benchmarked {len(metadata_collection)} times\n')
    logger.info(f'🚀 Benchmarking Analysis: Results over all benchmarks\n')
    logger.info(f'ℹ️ Benchmarked {len(metadata_collection)} times')

    for i, benchmark in enumerate(metadata_collection):
        print(f'🧮 Benchmark {i + 1}\nCurrent measure: {benchmark[0]["sum_avg"]}\nOld measure: {benchmark[1]}\n')
        logger.info(f'🧮 Benchmark {i}\nCurrent measure: {benchmark[0]["sum_avg"]}\nℹ️ Old measure: {benchmark[1]}\n')

    print(f"🧮 Average sum of benchmark current measurement: {round(sum_avg_over_all_benchmarks, DECIMALS)} ms")
    print(f"🧮 Average sum of benchmark snapshot measurement: {round(sum_avg_over_snapshot, DECIMALS)} ms")
    print(f"🚩 Improvement: {format_cell(sum_avg_over_all_benchmarks - sum_avg_over_snapshot, 0)} ms ({format_cell((100 / sum_avg_over_snapshot * sum_avg_over_all_benchmarks - 100) if sum_avg_over_snapshot else 0, 0)} %)")

    logger.info(f"🧮 Average sum of benchmark current measurement: {round(sum_avg_over_all_benchmarks, DECIMALS)} ms")
    logger.info(f"🧮 Average sum of benchmark snapshot measurement: {round(sum_avg_over_snapshot, DECIMALS)} ms")
    logger.info(f"🚩 Improvement: {format_cell(sum_avg_over_all_benchmarks - sum_avg_over_snapshot, 0)} ms ({format_cell((100 / sum_avg_over_snapshot * sum_avg_over_all_benchmarks - 100) if sum_avg_over_snapshot else 0, 0)} %)")
    print('=' * 100)

def print_results(amount_of_tests, results, failed_tests, sum_avg, sum_avg_benchmark_current, sum_avg_benchmark_snapshot, benchmarked_methods, not_available_tests_in_snapshot, not_available_tests_in_current, sum_total_parsing_time):
    """
        Prints the result to output stream.
        The result contains:
        - Table of measurements
        - Test success message
        - Sum of the average measurements of all test methods
        - Benchmarking (sum of the same methods from both versions)
        - Amount of test message

        Args:
            amount_of_tests (int): number of tests
            results (list): list of test results
            failed_tests (list): list of failed tests
            sum_avg (float): sum of all test results
            sum_avg_benchmark_current (float): sum of benchmark current test results
            sum_avg_benchmark_snapshot (float): sum of benchmark snapshot test results
            benchmarked_methods (list): list of benchmark methods
            not_available_tests_in_snapshot (list): list of test results
            not_available_tests_in_current (list): list of benchmark test results
            sum_total_parsing_time (float): sum of total parsing time
    """
    print(f"\n\n{'⚖️ Results of current measurement':^100}")
    print('=' * 100)

    formatted_data = [[item1, item2, format_cell(value1, 0), item3, format_cell(value2, 100) + "%", item4, item5] for item1, item2, value1, item3, value2, item4, item5 in results]

    measure_table = tabulate(formatted_data, headers=RESULT_HEADER, tablefmt='fancy_grid')
    print("\n", measure_table)
    logger.info(measure_table)

    if PARSING_TIME_ANALYSIS and RUN_TESTS_MULTIPLE_TIMES:
        print(f"ℹ️ Sum of total parsing time (ANTLR & Visitor): {round(sum_total_parsing_time, DECIMALS)} ms")
        print(f"ℹ️ Sum of ANTLR parsing: {round(sum_avg, DECIMALS)} ms ({round(100 / sum_total_parsing_time * sum_avg, DECIMALS)} %)")

        logger.info(f"ℹ️ Sum of total parsing time (ANTLR & Visitor): {round(sum_total_parsing_time, DECIMALS)} ms")
        logger.info(f"ℹ️ Sum of ANTLR parsing: {round(sum_avg, DECIMALS)} ms ({round(100 / sum_total_parsing_time * sum_avg, DECIMALS)} %)")
    else:
        print(f"ℹ️ Sum of ANTLR parsing: {round(sum_avg, DECIMALS)} ms")
        logger.info(f"ℹ️ Sum of ANTLR parsing: {round(sum_avg, DECIMALS)} ms")

    print(f"ℹ️ Parsed and tested a total of {amount_of_tests}")
    logger.info(f"ℹ️ Parsed and tested a total of {amount_of_tests}")

    if all(result[3] for result in results):
        print("✅ All tests were successful")
        logger.info(f"✅ All tests were successful")
    else:
        print(f"❌ Some tests failed: {failed_tests}")
        logger.info(f"❌ Some tests failed: {failed_tests}")

    print(f"\n{'Benchmarking':^50}")
    print('-' * 50)
    print(f"🧮 Average sum of benchmark current measurement: {round(sum_avg_benchmark_current, DECIMALS)} ms")
    print(f"🧮 Average sum of benchmark snapshot measurement: {round(sum_avg_benchmark_snapshot, DECIMALS)} ms")
    print(f"🚩 Improvement: {format_cell(sum_avg_benchmark_current - sum_avg_benchmark_snapshot, 0)} ms ({format_cell((100 / sum_avg_benchmark_snapshot * sum_avg_benchmark_current - 100) if sum_avg_benchmark_snapshot else 0, 0)} %)")
    print(f"\nℹ️ Benchmarked methods ({len(benchmarked_methods)}): {benchmarked_methods}")

    logger.info(f"\n{'Benchmarking':^50}")
    logger.info('-' * 50)
    logger.info(f"🧮 Average sum of benchmark current measurement: {round(sum_avg_benchmark_current, DECIMALS)} ms")
    logger.info(f"🧮 Average sum of benchmark snapshot measurement: {round(sum_avg_benchmark_snapshot, DECIMALS)} ms")
    logger.info(f"🚩 Improvement: {format_cell(sum_avg_benchmark_current - sum_avg_benchmark_snapshot, 0)} ms ({format_cell((100 / sum_avg_benchmark_snapshot * sum_avg_benchmark_current - 100) if sum_avg_benchmark_snapshot else 0, 0)} %)")
    logger.info(f"\nℹ️ Benchmarked methods ({len(benchmarked_methods)}): {benchmarked_methods}")

    if not_available_tests_in_snapshot or not_available_tests_in_current:
        print(f"\nSnapshot and current measurement aren't synchronized.")
        print(f"Methods in snapshot but not in current measurement: {not_available_tests_in_current}")
        print(f"Methods in current measurement but not in snapshot: {not_available_tests_in_snapshot}")

        logger.info(f"\nSnapshot and current measurement aren't synchronized.")
        logger.info(f"Methods in snapshot but not in current measurement: {not_available_tests_in_current}")
        logger.info(f"Methods in current measurement but not in snapshot: {not_available_tests_in_snapshot}")
    print('-' * 50)
    print('=' * 100)

def format_cell(value, threshold):
    """
        Formats the given value red if it's higher than threshold else green

        Args:
            value (int): The value to format
            threshold (int): The threshold to use for formatting
        Returns:
            str: The formatted value
    """

    if value <= threshold:
        return f"\033[92m{value}\033[0m"
    else:
        return f"+\033[91m{value}\033[0m"

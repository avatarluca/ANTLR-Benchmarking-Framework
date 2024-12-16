from example_tests.example_test import GrammarTransformTest


"""
Snapshot Settings
"""
# If a snapshot should be created
MAKE_SNAPSHOT = False

# The folder name, where the snapshots get saved
SNAPSHOTS_FOLDER_NAME = "measurement_snapshots"

# The new snapshot name (when MAKE_SNAPSHOT is true). Default value is an empty string: Snapshot gets saved as "snapshot-[CURRENT_TIMESTAMP]".
SNAPSHOT_NAME = ""

# The (old) snapshot which gets compared with the new measurement
USE_SNAPSHOT = "init"

# If true, then the old loaded snapshot will be recreated by the old grammar file, so both measurements have similar conditions. This takes twice as long as normal.
RECREATE_SNAPSHOT = False


"""
Outlier Settings
"""
# The mode, how the outliers get detected and removed / handled. Default: "high-low".
OUTLIER_DETECTION = "iqr" # "iqr", "high-low"


"""
Test Settings
"""
# If the difference value (old time - new time) is in this tolerance, the value is set to 0
DIFF_TOL = 0 # ms

# How much a test gets reran.
NUMBER_OF_RUNS_PER_TEST = 50

# The unittest classes with the test methods
TEST_CASES = [
    [GrammarTransformTest, "example_test"]
] # Array of [TESTCLASS, STRING_METHOD_NAME]

# Run tests NUMBER_OF_RUNS_PER_TEST times.
RUN_TESTS_MULTIPLE_TIMES = True


"""
Output Table Settings
"""
# Filter for the console table. Rows with avg parsing time < IGNORE_TOLERANCE will not be shown.
IGNORE_TOLERANCE = 1 # ms

# The table headers (also for csv files in snapshots)
RESULT_HEADER = ["Test Name", "Avg. Parsing Time [ms]", "Difference to origin [ms]", "Success", "Percentage", "Test Class", "Total parsing time [ms]"]


"""
General Settings
"""
# If the parser should be rebuilt before the measurement gets started.
BUILD_PARSER = False

# The rebuild script (only important if BUILD_PARSER = True).
PARSER_BUILD_SCRIPT_PATH = "example_grammar/build.sh"

# The grammar file
PARSER_GRAMMAR_PATH = "example_grammar/Grammar.g4"

# The temp grammar file (which gets created when the parser gets rebuild with old grammar)
TEMP_PARSER_GRAMMAR_PATH = "example_grammar/TestGrammar.txt"

# If the total time (ANTLR parsing & visitors) should get measured too.
PARSING_TIME_ANALYSIS = True

# The amount of decimal places the values should get rounded.
DECIMALS = 2


""" 
Logging Settings
"""
# Name of the logger.
LOGGER_NAME = 'Parsing Performance Measurement'

# File name for the logs.
LOGGING_FILE_NAME = "measure_log"


"""
Benchmarking Settings
"""
# Amount of benchmarking repetitions. Make multiple benchmarking for a more precise condition.
# Mainly used when MAKE_SNAPSHOT = False, because else it would generate NUMBER_OF_BENCHMARKS snapshots.
NUMBER_OF_BENCHMARKS = 1


"""
ATN Analysis Settings
"""
# Directory of the .dot files.
ATN_ANALYSIS_INPUT_DIRECTORY = "example_grammar"

# Directory where the atn images should be saved.
ATN_ANALYSIS_OUTPUT_DIRECTORY = "atn"

import gc
import timeit


last_performance_measure_in_ms = 0
last_performance_measure_in_ms_list = []


def measure_performance_in_ms(callback):
    """
        Measure performance of callback function.

        Args:
            callback (function): callback function.
        Returns:
            Tuple of callback return and measured time in ms.
    """

    from config import RUN_TESTS_MULTIPLE_TIMES, NUMBER_OF_RUNS_PER_TEST

    if RUN_TESTS_MULTIPLE_TIMES:
        gcold = gc.isenabled()
        gc.disable()

        t0 = timeit.default_timer()
        parse_out = callback()
        t1 = timeit.default_timer()

        if gcold: gc.enable()

        global last_performance_measure_in_ms
        last_performance_measure_in_ms = (t1 - t0) * 1000
    else:
        global last_performance_measure_in_ms_list
        last_performance_measure_in_ms_list = timeit.repeat(callback, setup='pass', repeat=NUMBER_OF_RUNS_PER_TEST, number=1)
        last_performance_measure_in_ms_list = [t * 1000 for t in last_performance_measure_in_ms_list]
        parse_out = callback()

    return parse_out

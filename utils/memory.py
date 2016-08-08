"""
This module defines functions for extracting memory measurements from a
G4Hive job stored in a JobResult object.
"""

def get_max_mem(job):
    """Calculate peak memory consumption in GB of a job"""
    return job.times_mems['mems'].max()*1e-6

def get_mem_data(job):
    """
    Extracts memory sampling data points of a job.

    Returns: (times, mems), where times and mems are numpy arrays
    of the memory measurements (in GB) and the relative time (in seconds)
    since the start of the job.
    """
    mems = job.times_mems['mems']*1e-6
    raw_times = job.times_mems['times']*1e-9
    times = raw_times - raw_times[0]
    return times, mems

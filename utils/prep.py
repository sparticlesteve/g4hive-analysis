"""
This module contains code for parsing out measurements from the input
log files and preparing the results in a convenient form for analysis.
Users probably only need the parse_job_results function for this.

I use numpy's genfromtxt to do most of the parsing:
http://docs.scipy.org/doc/numpy-1.10.0/reference/generated/numpy.genfromtxt.html
"""

from __future__ import print_function
import os
import numpy as np

class JobResult:
    """A structure to hold all the measurements associated with one job"""
    def __init__(self, nThread, nProc, nEvent):
        self.nThread, self.nProc, self.nEvent = nThread, nProc, nEvent

def peek_file(filename):
    """Dump a few lines of a file for testing"""
    print('%s:' % filename)
    with open(filename) as f:
        for line in f.readlines()[0:3]:
            print('    %s' % line.strip())

def parse_job_info(file_name):
    """
    Parses out basic job info from the file-name.
    Returns (nThread, nProc, nEvent)
    """
    config_str = file_name.split('.')[1]
    nThread, nProc, nEvent = config_str.split('_')
    return int(nThread), int(nProc), int(nEvent)

def parse_mem_file(mem_file):
    """
    Use numpy to parse the memory monitoring log file.
    Returns a structured 2D array of monitoring data.
    """
    return np.genfromtxt(mem_file, delimiter=',', dtype='i8,i4',
                         names=['times', 'mems'])

def parse_time_file(time_file):
    """Extract job start and end time from a time log file"""
    with open(time_file) as f:
        lines = f.readlines()
    start_time, end_time = int(lines[0]), int(lines[-1])
    return start_time, end_time

def parse_timeline(timeline):
    """Parse alg timing results for one job with numpy"""
    results = np.genfromtxt(timeline, skip_header=2, skip_footer=1,
                            dtype='i8,i8,U15,i4,i4,i4',
                            names=['starts', 'ends', 'algs',
                                   'tids', 'slots', 'events'])
    results.sort(order='starts')
    return results

def parse_job_results(results_dir):
    """
    Parse and prepare all measurements in a log directory.

    This function will identify the memory and timeline logs from naming
    conventions, parse out the measurements, and organize them into JobResult
    objects.

    Arguments:
      results_dir is a path to a directory of log files.

    Returns:
      A list of JobResult objects sorted by nThread.
    """
    all_files = os.listdir(results_dir)
    mem_files = [f for f in all_files if f.startswith('mem.')]
    time_files = [f for f in all_files if f.startswith('timeline.')]

    # Print out some basic information
    print('Using results directory:', results_dir)
    print(len(all_files), 'total files')
    print(len(mem_files), 'memory log files')
    print(len(time_files), 'timeline log files')
    assert(len(mem_files) == len(time_files))

    job_results = []
    for mem_file, time_file in zip(mem_files, time_files):
        mem_file = os.path.join(results_dir, mem_file)
        time_file = os.path.join(results_dir, time_file)
        nThread, nProc, nEvent = parse_job_info(mem_file)
        # I'm assuming both are sorted the same, but verify it here
        assert((nThread, nProc, nEvent) == parse_job_info(time_file))
        j = JobResult(nThread, nProc, nEvent)
        j.times_mems = parse_mem_file(mem_file)
        # Currently, I'm dumping the start/end times into the timeline file
        j.start_time, j.end_time = parse_time_file(time_file)
        j.timeline_results = parse_timeline(time_file)
        job_results.append(j)

    # Sort results by nThread
    job_results.sort(key=lambda j: j.nThread)
    return job_results


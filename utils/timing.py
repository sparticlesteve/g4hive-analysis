"""
This module defines functions for extracting useful timing info from a
G4Hive job stored in a JobResult object.
"""

from __future__ import print_function
import numpy as np

def get_job_time(job):
    """Length of full job in seconds"""
    return (job.end_time - job.start_time)*1e-9

def get_evloop_start_time(job):
    """Raw timestamp (in nanoseconds) of the start of the event loop"""
    return job.timeline_results['starts'].min()

def get_evloop_end_time(job):
    """Raw timestamp (in nanoseconds) of the end of the event loop"""
    return job.timeline_results['ends'].max()

def get_evloop_time(job):
    """Duration of the event loop in seconds"""
    return (get_evloop_end_time(job) - get_evloop_start_time(job))*1e-9

def get_avg_thread_time(job):
    """Get the thread-averaged event loop time in seconds"""
    tids = job.timeline_results['tids']
    unique_tids = np.unique(tids)
    start = get_evloop_start_time(job)
    ends = job.timeline_results['ends']
    time = 0
    for tid in unique_tids:
        thread_ends = ends[tids == tid]
        # Within a thread, results are chronological, so take the last
        thread_end = thread_ends[-1]
        time += (thread_end - start)*1e-9
    return time / job.nThread

def get_initialization_time(job):
    """Duration of job initialization in seconds"""
    events_start = get_evloop_start_time(job)
    return (events_start - job.start_time)*1e-9

def get_finalization_time(job):
    """Duration of job finalization in seconds"""
    events_end = get_evloop_end_time(job)
    return (job.end_time - events_end)*1e-9

def print_timing_summary(job_results):
    """Dump a table of basic job timing results"""
    print('Threads Events Job-time Init-time Loop-time Final-time')
    for j in job_results:
        print('{0:7d} {1:6d} {2:8.1f} {3:9.1f} {4:9.1f} {5:10.1f}'
                .format(j.nThread, j.nEvent, get_job_time(j),
                        get_initialization_time(j),
                        get_evloop_time(j),
                        get_finalization_time(j)))

def get_throughput(job):
    """
    Calculate event throughput (events/s) for a job,
    ignoring initialization and finalization.
    """
    return job.nEvent / get_evloop_time(job)

def get_avg_throughput(job):
    """
    Calculates thread-averaged event throughput (events/s) for a job.
    Differs from get_throughput method above by ignoring idle time of threads
    at the end of the event loop, resulting in a more stable measurement.
    """
    return job.nEvent / get_avg_thread_time(job)

def calc_alg_timings(job):
    """
    Transform the timeline results to be more useful.
    - Normalize start times to the beginning of event loop.
    - Calculate durations of each alg's execute
    - Store results converted to seconds as job.alg_starts, job.alg_durations
    """
    loop_start = get_evloop_start_time(job)
    raw_starts = job.timeline_results['starts']
    raw_ends = job.timeline_results['ends']
    job.alg_durations = (raw_ends - raw_starts)*1e-9
    job.alg_starts = (raw_starts - loop_start)*1e-9
    assert(job.alg_durations.min() >= 0)
    assert(job.alg_starts.min() >= 0)

def get_timeline_alg_idxs(job, alg):
    """Get the index array for one alg in the timeline"""
    return job.timeline_results['algs'] == alg

def get_timeline_thread_idxs(job, tid):
    """Get the index array for one thread ID in the timeline"""
    return job.timeline_results['tids'] == tid

def all_timeline_thread_idxs(job):
    """Get timeline results split by thread.
    Returns a list of timeline index arrays; one per thread"""
    tids = job.timeline_results['tids']
    unique_tids = np.unique(tids)
    return [get_timeline_thread_indices(job, tid) for tid in unique_tids]

def get_alg_duration_map(job):
    """Returns dict of alg name to a list of execuion durations"""
    algs = job.timeline_results['algs']
    unique_algs = np.unique(algs)
    duration_map = {}
    for alg in unique_algs:
        indices = algs == alg
        duration_map[alg] = job.alg_durations[indices]
    return duration_map

#!/usr/bin/env python3

from __future__ import print_function

import argparse
import os

from utils import prep

def parse_args():
    """Parse command line arguments"""
    formatter = argparse.ArgumentDefaultsHelpFormatter
    parser = argparse.ArgumentParser('parseResults.py', formatter_class=formatter)
    add_arg = parser.add_argument
    add_arg('results_dir', help='Directory of G4Hive log files')
    add_arg('output_file', help='Output pickle file')
    add_arg('-v', '--verbose', action='store_true',
            help='Verbose printing of progress')
    return parser.parse_args()

def main():
    args = parse_args()

    # Parse the inputs
    job_results = prep.parse_job_results(args.results_dir, verbose=args.verbose)

    # Serialize the results
    print('Serializing results to ', args.output_file)
    prep.save_job_results(job_results, args.output_file)

    print('Success')

if __name__ == '__main__':
    main()

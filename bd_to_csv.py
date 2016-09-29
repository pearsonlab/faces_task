### Processes behavioral data files (json files) that have been converted
### from initial saved format from task to the standard template for AWS
### (i.e. they must ALREADY be in standard format).
### Behavioral data files should be saved together in a directory 
### "behavioral data" and output csv files will be saved to new directory
### "csv_files" separately by task, with a single meta data file per
### participant which includes the summary information about the trial.


import numpy as np
import pandas as pd
import os

import json
import argparse
import sys
import csv

def open_json_file(file):
    with open(file) as behavioral_file:    
        behavioral = json.load(behavioral_file)

    return behavioral

def make_csv(behavioral_data, file):
    # behavioral data
    data_df = pd.DataFrame(behavioral_data['data'])

    csv_file_pre = file.strip(".json")
    csv_file = csv_file_pre.strip('behavioral_data')
    
    if not os.path.exists('csv_files/'):
        os.makedirs('csv_files')
    
    pd.DataFrame.to_csv(data_df, path_or_buf = "csv_files" + csv_file + ".csv")

    participant = file[-9:-5]

    meta_file = 'csv_files/meta_'+participant+'.csv'

    # Creates new meta file if one hasn't been created (starts it with keys)
    if not os.path.isfile(meta_file):
        with open(meta_file, 'a+') as f:
            writer = csv.writer(f)
            writer.writerow(behavioral_data['meta'].keys())

    # Writes meta data for this task to meta file
    with open(meta_file, 'a') as fd:
        writer = csv.writer(fd)
        writer.writerow(behavioral_data['meta'].values())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Take .json files and covert to .csv")
    parser.add_argument(nargs='+', dest='files',
                        help="Files to process"
                        )

    args = parser.parse_args()
    
    for file in args.files:
        behavioral_data = open_json_file(file)
        make_csv(behavioral_data, file)
import torch
import numpy as np
import pandas as pd
import argparse
import os
import sys
import time
from stageII_predict import predict_stageII
from preprocess import *
import contextlib

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", '--input_directory_path', type=str) # directory -> subdirectory(PUBMED} -> abstract from pubmed, and paper html from PMC. e.g. ../input_data/
    parser.add_argument("-d", '--is_direct', type=str)  # tfb -> direct, tfr -> indirect, both -> direct & indirect
    parser.add_argument("-check", '--need_check_format', type=int) # default 1, 1 -> check input title contains keyword, 0 -> not check
    parser.add_argument("-o", '--out_file_name', type=str)
    opt = parser.parse_args()
    start = time.time()
    predict_stageII(opt.is_direct, opt.out_file_name, opt.input_directory_path)
    print('Successfully completed ! Total take time :', time.time()-start)

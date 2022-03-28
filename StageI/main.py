import torch
import numpy as np
import pandas as pd
import argparse
from bert_predict import *
import contextlib

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", '--input_directory_path', type=str) # directory -> subdirectory(PUBMED} -> abstract from pubmed, and paper html from PMC. e.g. ../input_data/
    parser.add_argument("-d", '--is_direct', type=str)  # tfb -> direct, tfr -> indirect, both -> direct & indirect
    parser.add_argument("-check", '--need_check_format', type=int) # default True, True -> check input title contains keyword, False -> not check
    parser.add_argument("-o", '--out_file_name', type=str)
    opt = parser.parse_args()
    start = time.time()
    files = preprocess_input_files(opt.input_directory_path)
    print('StageI preprocess take time:', time.time()-start)
    start = time.time()
    #predict(files, opt.is_direct, opt.need_check_format)
    predict_stageI(files, opt.out_file_name, opt.is_direct, opt.need_check_format)
    stageI_cost = time.time()
    print('StageI take time :',time.time()-start)
    print('Successfully completed !')

# encoding='utf-8'
import torch
import numpy as np
import pandas as pd
import argparse
import contextlib
import sys
from torch.utils.data import DataLoader, TensorDataset
from sklearn.metrics import roc_curve, roc_auc_score
from Models import BertClassifier
from utils import set_seeds, load_checkpoint, create_mini_batch
from utils import bioBERT_evaluate, softmax
import time
import os
import requests
import random
from bs4 import BeautifulSoup
import re


## preprocess_input_files to file name list
def preprocess_input_files(dir_path):
    file_list = []
    if dir_path[-1] == '/':
        pass
    else:
        dir_path = dir_path+'/'
    for sub_dir in os.listdir(dir_path):
        for fname in os.listdir(dir_path+sub_dir):
            if '.txt' in fname:
                file_list.append(dir_path+sub_dir+'/'+fname)
                break
            elif 'html' in fname:
                file_list.append(dir_path+sub_dir+'/'+fname)
                break
            else:
                pass
    return file_list

## check if paper title contain 'yeast' or 'Saccharomyces cerevisiae'
def check_ilegal(fname):
    if 'html' in fname:
        pmid, title, content = parsehtml_abstract(fname)
    else:
        with open(fname) as f:
            rows = f.readlines()
            empty_lines = []
            tmp, start, end = 0, 0, 0
            for idx, row in enumerate(rows):
                if '1.' == row[:2]:
                    tmp = idx
                    break
            for idx, row in enumerate(rows):
                if row=='\n':
                    empty_lines.append(idx)
            for index, idx in enumerate(empty_lines):
                if idx>tmp:
                    idy = index
                    break
            start = empty_lines[idy]
            end = empty_lines[idy+1]
            #print(tmp, start, end)
            content = rows[start:end]
            title = ''
            title = title.join(content).replace('\n', '')
            #print(title)
    if 'yeast' in title.lower() or 'yeast'.upper() in title.upper() or 'saccharomyces cerevisiae' in title.lower() or 'Saccharomyces cerevisiae'.upper() in title.upper():
        return True
    else:
        return False
   
## preprocess txt file to get abstract
def preprocess_abstract(fname):
    with open(fname) as f:
        rows = f.readlines()
#        print(rows)
        empty_lines = []
        tmp, tmp2, start, end = 0, 0, 0, 0
        for idx, row in enumerate(rows):
            if row=='\n':
                empty_lines.append(idx)
        for idx, row in enumerate(rows):
            if 'DOI:' in row:
                tmp = idx
                break
        for idx, row in enumerate(rows):
            if 'Copyright' in row:
                tmp2 = idx

        for idx,row in enumerate(rows):
            if 'PMID' in row:
                pmid = row.split(' ')[1]
        idy = 0
        for index, idx in enumerate(empty_lines):
            if tmp2!=0 and tmp2<tmp:
                if idx<tmp:
                    idy = index
                    end = idx
                start = empty_lines[idy-2]
            else:
                if idx<tmp:
                    idy = index
                    end = idx
                start = empty_lines[idy-1]
         
        #print(tmp, start, end)
        abstract = rows[start:end]
        #print(abstract)
        connect = ''
        connect = connect.join(abstract).replace('\n', '')
        #print(connect)
    return pmid, connect


## load data from file name list
def load_data(file_list, need_check_format=1):
    print('\nThere are %d rows data'%len(file_list))
    print('Load data and preprocessing ...')
    if need_check_format:
        print('check if paper title contain yeast or Saccharomyces cerevisiae')

    cols = ['pmid', 'abstract', 'label']
    rows = []
    for fname in file_list:
        if need_check_format:
            if check_ilegal(fname):
                if '.html' in fname:
                    pmid, title, abstract = parsehtml_abstract(fname)
                    label = 1
                    rows.append({'pmid': pmid,'abstract':abstract, 'label':label})
                else:
                    pmid, abstract = preprocess_abstract(fname)
                    label = 1
                    rows.append({'pmid': pmid,'abstract':abstract, 'label':label})
            else:
                print('title in paper %s is not contain yeast/saccharomyces cerevisiae...'%fname)
        else:
            if '.html' in fname:
                pmid, title, abstract = parsehtml_abstract(fname)
                label = 1
                rows.append({'pmid': pmid,'abstract':abstract, 'label':label})
            else:
                #pmid = fname.split('-')[1].replace('.txt','')
                pmid, abstract = preprocess_abstract(fname)
                label = 1
                rows.append({'pmid': pmid,'abstract':abstract, 'label':label})

    df = pd.DataFrame(rows, columns=cols)
    #print(df)
    return df

## parse download html file (only Abstract)
def parsehtml_abstract(html_file):
    html_content = ''
    section = ['MATERIALS AND METHODS','Supplementary Material',
                   'Acknowledgments','Abbreviations used:','Footnotes','REFERENCES']
    section1 = ['Abstract']
    ipfirst=[]
    iplast=[]
    ipfirstlast=[]
    ipcaption=[]
    with open(html_file, 'r') as f:
        rows = f.readlines()
        for row in rows:
            html_content = html_content+row
    soup = BeautifulSoup(html_content,'html.parser')
    content = ''
    ip = soup.select('.tsec.sec')
    ip_caption = soup.select('div.caption p')

    reg = re.compile('{"type[^}]*}*')

    for j in ip:
        temp = j.find('h2')
        if temp != None:
            #print(temp.text)
            temp2 = j.select('p')
            for i in temp2:
                if i not in ip_caption and temp.text in section1:
                    c = i.text.replace('\xe2\x80\x8b','').replace('\u200b','').replace('\n','').strip()
                    content = content+' '+c
                f = reg.findall(content)
                content = reg.sub('',content)
                content = content.strip()
    pmid = soup.find("meta", {"name":"citation_pmid"})['content']
    title = soup.find("meta", {"name":"DC.Title"})['content']
    return pmid, title, content


## predict the classification result
def predict(file_list, output_fname, is_direct, need_check_format):
    
    SEED = 78
    set_seeds(SEED)

    NUM_LABELS = 2
    BATCH_SIZE = 128
    MAX_SEQ_LENGTH = 512

    fname = '../StageI/'+output_fname.split('.txt')[0]+'_'+is_direct+'.txt'
    MODEL_NUMS = 5
    bert_models = [BertClassifier.from_pretrained("dmis-lab/biobert-base-cased-v1.1", 
                                                  num_labels=NUM_LABELS, output_hidden_states=True) 
                                                  for _ in range(5)]

    if is_direct=='tfb':
        DIRECT_OR_INDIRECT = 'direct'
    elif is_direct=='tfr':
        DIRECT_OR_INDIRECT = 'indirect'
    else:
        print('Illegal input!')
        sys.exit(0)

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    models_dir = '../Models/'+DIRECT_OR_INDIRECT +'/'
    print('-'*15)
    ## load data from file name list
    _df = load_data(file_list, need_check_format)
    df = _df[['abstract', 'label']]

    all_probs = np.zeros((df.shape[0], 5))
    # model 1~5
    start = time.time()
    print('Load %s model to predict...'%DIRECT_OR_INDIRECT)
    for i in range(5):
        bert_model = load_checkpoint(models_dir+'model_'+str(i+1)+'.pt', bert_models[i], device)
        bert_model = bert_model.to(device)
        data_loader = DataLoader(df.values, batch_size=BATCH_SIZE, 
                                 shuffle=False, collate_fn=create_mini_batch)
        loss, logits, labels = bioBERT_evaluate(bert_model, data_loader, device)
        acc = sum(np.argmax(logits, axis=1) == labels) / len(labels)
        probs = np.array([softmax(logit) for logit in logits])[:, 1]
        all_probs[:, i] = probs
    print('StageI load model and predict take time :', time.time()-start)
    ## calculate average result in 5 models
    avg_probs = sum(all_probs[:,i] for i in range(5))/5
    #print(avg_probs)
    predicted = []
    f1 = open(fname, 'w')
    f1.write('PMID\tEvidence\tAbstract\n')
    for probs in avg_probs:
        if probs>0.5:
            predict_label = is_direct.upper()
        else:
            predict_label = 'non-'+is_direct.upper()
        predicted.append(predict_label)
    for idx, row in _df.iterrows():
        f1.write(row['pmid']+'\t'+str(predicted[idx])+'\t'+row['abstract']+'\n')
    f1.close()

# predict stageI
def predict_stageI(file_list, output_fname, is_direct, need_check_format):
    if is_direct == 'tfb':
        predict(file_list, output_fname, is_direct, need_check_format)
    elif is_direct == 'tfr':
        predict(file_list, output_fname, is_direct, need_check_format)
    elif is_direct == 'both':
        predict(file_list, output_fname, 'tfb', need_check_format)
        predict(file_list, output_fname, 'tfr', need_check_format)
    else:
        print('no specified input arguments')

import torch
import numpy as np
import pandas as pd
import argparse
import contextlib
import time
import sys
from torch.utils.data import DataLoader, TensorDataset
from sklearn.metrics import roc_curve, roc_auc_score
from Models import BertClassifier
from utils import set_seeds, load_checkpoint, create_mini_batch
from utils import bioBERT_evaluate, softmax
from preprocess import *
from download import *

## close the message SettingWithCopyWarning
pd.options.mode.chained_assignment = None

## preprocess_stageI_preprocess_result
def preprocess_stageI_result(fname):
    tfb_data, tfr_data = [], []
    with open(fname) as f:
        rows = f.readlines()
        for idx, row in enumerate(rows[1:]):
            flag = row.split('\t')[0].split('@')[3].strip()
            if flag == 'TFB':
                tfb_data.append(row.strip())
            elif flag == 'TFR':
                tfr_data.append(row.strip())
            else:
                continue

    return tfb_data, tfr_data

## load data from data list
def load_data(data_list):
    origin_abstracts = []
    with open('./data/ori_preprocess', 'r') as f:
        rows = f.readlines()
        for idx, row in enumerate(rows):
            line = row.split('\t')
            abstract = line[1].strip()
            origin_abstracts.append(abstract)

    col_name = ['PMID', 'TF', 'Gene', 'Class', 'Abstract', 'Origin_Abstract', 'Label']
    data = []
    for idx, row in enumerate(data_list):
        ref = row.split('\t')[0]
        pmid = ref.split('@')[0]
        tf_orf = ref.split('@')[1]
        gene_orf = ref.split('@')[2]
        _class = ref.split('@')[3]
        abstract = row.split('\t')[1]
        label = int(row.split('\t')[2].strip())
        origin_abstract = origin_abstracts[idx]

        data.append({'PMID':pmid, 'TF':tf_orf, 'Gene':gene_orf, 'Class':_class, 'Abstract':abstract, 'Origin_Abstract': origin_abstract, 'Label':label})
    df = pd.DataFrame(data, columns = col_name)
    return df

# predict_data
def _predict(fname, isDirect, dir_path):

    if not os.path.exists('../StageI/result_'+isDirect+'.txt'):
        print('You need to predict StageI first !!')
        sys.exit(0)

    _article = get_article('../StageI/result_'+isDirect+'.txt', dir_path)
    new_article = mark_article(_article)
    start = time.time()
    stageII_preprocess(new_article)
    replace_sep('./data/preprocess_done.csv')
    print('StageII preprocess take time:', time.time()-start)
    ## load data from file name list
    tfb_data, tfr_data = preprocess_stageI_result('./data/preprocess_done.tsv')

    evidence_code = ''
    if isDirect == 'tfb':
        data = tfb_data
        evidence_code = 'binding'
    elif isDirect == 'tfr':
        data = tfr_data
        evidence_code = 'regulatory'
    else:
        pass

    SEED = 30
    set_seeds(SEED)

    NUM_LABELS = 2
    BATCH_SIZE = 128
    MAX_SEQ_LENGTH = 512

    MODEL_NUMS = 1

    _df = load_data(data)
    df = _df[['Abstract', 'Label']]

    #weight = [1] * len(df)
    df['sample_weight'] = 1
    
    if len(df) != 0:
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        start = time.time()
        # load model
        if isDirect == 'tfb':
            print('Load direct model to predict...')
            models_dir = '../Models/'
            bert_models = [BertClassifier.from_pretrained("dmis-lab/biobert-base-cased-v1.1",
                                                  num_labels=NUM_LABELS, output_hidden_states=True)]
            bert_model = load_checkpoint(models_dir+'direct/best_model.pt', bert_models[0], device)

        if isDirect == 'tfr':
            print('Load indirect model to predict...')
            models_dir = '../Models/'
            bert_models = [BertClassifier.from_pretrained("dmis-lab/biobert-base-cased-v1.1",
                                                  num_labels=NUM_LABELS, output_hidden_states=True)]
            bert_model = load_checkpoint(models_dir+'indirect/best_model.pt', bert_models[0], device)

        print('StageII load model take time :', time.time()-start)        
        bert_model = bert_model.to(device)
        data_loader = DataLoader(df.values, batch_size=BATCH_SIZE, 
                                 shuffle=False, collate_fn=create_mini_batch)
        loss, logits, labels = bioBERT_evaluate(bert_model, data_loader, device)
        acc = sum(np.argmax(logits, axis=1) == labels) / len(labels)
        probs = np.array([softmax(logit) for logit in logits])[:, 1]

        TFs, Genes, TFtoalias, orftogenealias, orftoTF, genealiastoorf, TFtoorf = load_gene_tf_alias('./data/Tf.csv', './data/all_alias_ver3.csv')
        pair_dict = {}
        for idx, row in _df.iterrows():
            pair = row['TF'] + '@' + row['Gene'] + '@' + row['PMID']
            if pair not in pair_dict:
                pair_dict[pair] = []
                pair_dict[pair].append(str(probs[idx]) + '@' + row['Origin_Abstract'])
            else:
                pair_dict[pair].append(str(probs[idx]) + '@' + row['Origin_Abstract'])

        f1 = open(fname, 'w')
        f1.write('TF_ORF\tTF_Alias\tGene_ORF\tGene_Alias\tPMID\tEvidence\tSentence_Description\n')
        for pair, probs_sentences in pair_dict.items():
            tf_orf = pair.split('@')[0]
            gene_orf = pair.split('@')[1]
            Tf_aliases = list(dict.fromkeys(orftoTF[tf_orf]))
            Gene_aliases = list(dict.fromkeys(orftogenealias[gene_orf]))
            for i in Tf_aliases:
                if tf_orf in i:
                    Tf_aliases.remove(i)
            for i in Gene_aliases:
                if i.startswith('Y'):
                    Gene_aliases.remove(i)
            Tf_alias = ''
            Gene_alias = ''
            Tf_alias = '/'.join(Tf_aliases)
            Gene_alias = '/'.join(Gene_aliases)

            pmid = pair.split('@')[-1]
            count_pos = 0
            pos_sentences = []
            for i in probs_sentences:
                prob = float(i.split('@')[0])
                if prob > 0.5:
                    count_pos += 1
                    pos_sentences.append(i.split('@')[-1])
            if count_pos * 2 >=  len(probs_sentences):
                f1.write(tf_orf+'\t'+Tf_alias+'\t'+gene_orf+'\t'+Gene_alias+'\t'+pmid+'\t'+evidence_code+'\t'+'<sep>'.join(pos_sentences) + '\n')
        f1.close()

    else:
        f1 = open(fname, 'w')
        f1.wirte('TF_ORF\tTF_Alias\tGene_ORF\tGene_Alias\tPMID\tEvidence\tSentence_Description\n')
        f1.close()

## predict the classification result
def predict_stageII(isDirect, fname, dir_path):
    
    print('-'*15)
    print('StageII predicting...')

    start = time.time()
    if isDirect == 'tfb': 
        _predict(fname.split('.txt')[0]+'_tfb.txt', isDirect, dir_path)
        print('StageII predict take time:', time.time()-start)
    elif isDirect == 'tfr' :
        _predict(fname.split('.txt')[0]+'_tfr.txt', isDirect, dir_path)
        print('StageII predict take time:', time.time()-start)
    elif isDirect == 'both':
        _predict(fname.split('.txt')[0]+'_tfb.txt', 'tfb', dir_path)
        _predict(fname.split('.txt')[0]+'_tfr.txt', 'tfr', dir_path)
    else:
        pass
    if os.path.exists('./data/preprocess_done.csv'):
        os.remove('./data/preprocess_done.csv')
    if os.path.exists('./data/preprocess_done.tsv'):
        os.remove('./data/preprocess_done.tsv')
    if os.path.exists('./data/ori_preprocess'):
        os.remove('./data/ori_preprocess')

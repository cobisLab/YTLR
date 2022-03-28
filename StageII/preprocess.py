import codecs
import nltk
import spacy
import os
import time
from download import *

# deal the punctuation with input sentences, return words list
def processword(word):
    targetList = []
    if len(word) == 0:
        return []
    if word[-1] == '.':
        word = word[:-1]
    if len(word) == 0:
        return []
    if word[-1] == ',':
        word = word[:-1]
    if len(word) == 0:
        return []
    if word[-1] == ';':
        word = word[:-1]
    if len(word) == 0:
        return []
    if word[-1] == ':':
        word = word[:-1]
    if len(word) == 0:
        return []
    if word[-1] == ')' and '(' not in word:
        word = word[:-1]
    if len(word) == 0:
        return []
    if word[0] == '(' and ')' not in word:
        word = word[1:]
    if len(word) == 0:
        return []
    if word[0] == '(' and word[-1] == ')':
        word = word[1:-1]
    if len(word) == 0:
        return []
    if '/' in word:
        temps = word.split('/')
        targetList += temps
        for temp in temps[1:]:
            targetList.append(temps[0][0:-1] + temp)
    elif '-' in word:
        targetList += word.split('-')
    else:
        targetList.append(word)
    return targetList

# phrase of input sententence exists tf-gene evidence
def findEvidenceList(tf_record, gene_record, genealiastoorf, tftoorf, sents):
    split_data = list()
    for tfinfo in tf_record:
        tf = tfinfo.split('#')[0]
        tfidx = int(tfinfo.split('#')[1])
        tfwordidx = int(tfinfo.split('#')[2])
        tforf = tftoorf[tf.upper()]
        #print('tf', tf, 'tfidx', tfidx, 'tfwordidx', tfwordidx, 'tforf', tforf)
        for geneinfo in gene_record:
            gene = geneinfo.split('#')[0]
            geneidx = int(geneinfo.split('#')[1])
            genewordidx = int(geneinfo.split('#')[2])
            geneorf = genealiastoorf[gene.upper()]
            #print('gene', gene, 'geneidx', geneidx, 'genewordidx', genewordidx, 'geneorf', geneorf)
            if tforf == geneorf:
                continue
            if tfwordidx == genewordidx and tfidx == geneidx:
                continue
            if abs(tfidx-geneidx) < 2:
                start = min(tfidx, geneidx)
                end = max(tfidx, geneidx)
                if tfidx < geneidx:
                    realtfwordidx = tfwordidx
                    realgenewordidx = len(sents[int(tfidx)].split(' ')) + int(genewordidx)
                if geneidx < tfidx:
                    realgenewordidx = genewordidx
                    realtfwordidx = len(sents[int(geneidx)].split(' ')) + int(tfwordidx)
                if geneidx == tfidx:
                    realgenewordidx = genewordidx
                    realtfwordidx = tfwordidx
                split_data.append(tforf+'@'+geneorf+'@'+str(start)+'#'+str(end)+'@'+str(realtfwordidx)+'#'+str(realgenewordidx)+'@'+tf+'@'+gene)
    return split_data

# final data preprocess output
def finalsent(tfwordidx, genewordidx, sent, orftoTF, orftogenealias, tfs, genes):
    final_sent = ''
    final_sent_2 = ''
    for idx, word in enumerate(sent.strip().split(' ')):
#         print(idx)
#         print(tfwordidx)
        punc = ''
        if len(word) == 0:
            continue
        if word[-1] == '.':
            punc = '.'
        if word[-1] == ',':
            punc = ','
        if word[-1] == ';':
            punc = ';'
        if word[-1] == ':':
            punc = ':'
        if int(idx) == int(tfwordidx):
            if punc != '':
                final_sent += '<tf>' + punc + ' '
            else:
                final_sent += '<tf> '
        elif int(idx) == int(genewordidx):
            if punc != '':
                final_sent += '<gene>' + punc + ' '
            else:
                final_sent += '<gene> '
        else:
            final_sent += word + ' '
#     print('final_sent: '+final_sent)
    for word in final_sent.split(' '):
        check_tf = False
        check_gene = False
        punc = ''
        if len(word) == 0:
            continue
        if word[-1] == '.':
            punc = '.'
        if word[-1] == ',':
            punc = ','
        if word[-1] == ';':
            punc = ';'
        if word[-1] == ':':
            punc = ':'
        targetList = processword(word)
#                 print('word: '+word)
                            
        for tf in tfs:
            for target in targetList:
                if tf.upper() == target.upper():
                    if punc != '':
                        final_sent_2 += '<tf>' + punc + ' '
                    else:
                        final_sent_2 += '<tf> '
                    check_tf = True
        if check_tf == False:
            for gene in genes:
                for target in targetList:
                    if gene.upper() == target.upper():
                        if punc != '':
                            final_sent_2 += '<gene>' + punc + ' '
                        else:
                            final_sent_2 += '<gene> '
                        check_gene = True
        if check_tf == False and check_gene == False:
            final_sent_2 += word + ' '
#         print(sent)
    
    return final_sent_2

# output of processing
def writeSentdir(pmid, split_data, sents, orftoTF, orftogenealias, outFname, isDirect):
    f = open(outFname, 'a')
    ori_f = open('./data/ori_preprocess','a')
    if isDirect:
        label = "TFB"
    else:
        label = "TFR"
    check = set()
    for data in split_data:
        sent = ''
        data = data.split('@')
        tf_orf = data[0]
        tfs = orftoTF[tf_orf.upper()]
        gene_orf = data[1]
        genes = orftogenealias[gene_orf.upper()]
        idx = data[2].split('#')
        wordidx = data[3].split('#')
        tfwordidx = wordidx[0]
        genewordidx = wordidx[1]
        tf = data[4]
        gene = data[5]

        for length in range((int(idx[1])+1)-int(idx[0])):
            sent += sents[int(idx[0])+length] + ' '
#         print(sent)

        final_sent = finalsent(tfwordidx, genewordidx, sent, orftoTF, orftogenealias, tfs, genes)
        if '<tf>' not in final_sent or '<gene>' not in final_sent:
            continue
        if tf_orf+'@'+gene_orf+'@'+label+'@'+sent.strip() not in check:
            check.add(tf_orf+'@'+gene_orf+'@'+label+'@'+sent.strip())
            f.write(pmid+'@'+tf_orf+'@'+gene_orf+'@'+label+'\t'+final_sent.strip()+'\n')
            ori_f.write(pmid+'@'+tf_orf+'@'+tf+'@'+gene_orf+'@'+gene+'@'+label+'\t'+sent.strip()+'\n')
    f.close()            
    ori_f.close()            
# load_gene_tf_alias
def load_gene_tf_alias(fname1, fname2):
    TFs = set()
    Genes = set()
    TFtoalias = dict()
    orftogenealias = dict()
    orftoTF = dict()
    genealiastoorf = dict()
    TFtoorf = dict()
    with open(fname1,'r')as f:
        rows = f.readlines()
        for row in rows:
            tf_alias = []
            row = row.rstrip('\n')
            if row[-1].upper() == 'P':
                row = row[:-1]
            with open(fname2,'r')as f1:
                lines = f1.readlines()
                for line in lines:
                    orf = line.split('\t')[0].split('#')[0].upper()
                    if row.upper() == line.split('\t')[0].split('#')[1].upper():
    #                     print(line)
                        for i in line.split('\t')[0].split('#'):
                            TFs.add(i.upper())
                            TFs.add(i.upper()+'P')
                            TFtoorf[i.upper()]=orf
                            TFtoorf[i.upper()+'P']=orf
                            tf_alias.append(i.upper())
                            tf_alias.append(i.upper()+'P')
                        for i in line.split('\t')[1].split('@')[:-1]:
                            TFs.add(i.upper())
                            TFs.add(i.upper()+'P')
                            TFtoorf[i.upper()]=orf
                            TFtoorf[i.upper()+'P']=orf
                            tf_alias.append(i.upper())
                            tf_alias.append(i.upper()+'P')
                        orftoTF[line.split('\t')[0].split('#')[0].upper()] = tf_alias
            TFtoalias[row.upper()]=tf_alias
        
    with open(fname2,'r')as f:
        lines = f.readlines()
        for line in lines:
            orf = line.split('\t')[0].split('#')[0]
            orf_alias = []
            for i in line.split('\t')[0].split('#'):
                Genes.add(i.upper())
                genealiastoorf[i.upper()] = orf.upper()
                orf_alias.append(i.upper())
            for i in line.split('\t')[1].split('@')[:-1]:
                Genes.add(i.upper())
                genealiastoorf[i.upper()] = orf.upper()
                orf_alias.append(i.upper())
            orftogenealias[orf.upper()]=orf_alias
            
    return TFs, Genes, TFtoalias, orftogenealias, orftoTF, genealiastoorf, TFtoorf

# mark sentence of article
def mark_article(articles):
    print('marking article...')
    nlp = spacy.load("en_core_web_trf")
    ['al', 'i.e', 'e.g', 'etc', 'Fig.', 'fig.']
    new_article = dict()
    for idx, (article, data) in enumerate(articles.items()):
        pmid = data[0]
        label = data[1]
        tokens = nlp(article)
        tempString = ''
        for sent in tokens.sents:
            tempString += sent.text.strip()+'@'
        tempString += '\n'
        new_article[tempString] = (pmid,label)
    return new_article

# get_article_dict.
def get_article(fname, dir_path):
    _article = dict()
    has_finish = set()
    with open(fname,'r')as f:
        rows = f.readlines()
        for row in rows[1:]:
            row = row.rstrip('\n').split('\t')
            pmid = row[0].strip()
            label = row[1].strip()
            if 'non-' in label:
                continue
            for sub_dir in sorted(os.listdir(dir_path)):
                for f in sorted(os.listdir(dir_path+sub_dir)):
                    if '.html' in f and dir_path+sub_dir+'/'+f not in has_finish:
                        pmid2, content = parsehtml(dir_path+sub_dir+'/'+f)
                        has_finish.add(dir_path+sub_dir+'/'+f)
                        if content != '':
                            article = content.strip()
                        else: 
                            article = row[1].strip()
                        _article[article] = (pmid2, label)
                        break
                    else:
                        article = row[1].strip()
                        _article[article] = (pmid, label)
                        break
    return _article

# get positive pmids. reutrn dircet/indirect
def get_pos_pmid_dict(fname):
    pmiddirpos = dict()
    pmidindirpos = dict()
    with open(fname,'r')as f:
        rows = f.readlines()
        for row in rows:
            row = row.rstrip('\n')
            pmid = row.split('@')[0]
            for pairs in row.split('@')[1:-1]:
                pair = pairs.split('#')
                tf = pair[0]
                if tf[-1].upper() == 'P':
                    tf = tf[:-1]
                tf = TFtoorf[tf.upper()]
                gene = pair[1]
                dir_indir = isdir[(pmid+tf+gene).upper()]
                if dir_indir == 'Direct':
                    if pmid in pmiddirpos:
                        exist = pmiddirpos[pmid]
                        exist.append((tf+gene).upper())
                        pmiddirpos[pmid] = exist
                    if pmid not in pmiddirpos:
                        init = []
                        init.append((tf+gene).upper())
                        pmiddirpos[pmid] = init
                if dir_indir == 'Indirect':
                    if pmid in pmidindirpos:
                        exist = pmidindirpos[pmid]
                        exist.append((tf+gene).upper())
                        pmidindirpos[pmid] = exist
                    if pmid not in pmidindirpos:
                        init = []
                        init.append((tf+gene).upper())
                        pmidindirpos[pmid] = init
                        
    return pmiddirpos, pmidindirpos

# remove original segment, and add new factor
def replace_sep(fname):
    with open(fname, 'r') as f:
        data = f.readlines()
    f = open('./data/preprocess_done.tsv', 'w')
    f.write('References(PubMed)\tabstract\tlabel\n')
    for idx, row in enumerate(data):
        if row == 'References(PubMed)\tabstract\tlabel\n':
            continue
        ref = row.split('\t')[0]
        abstract = row.split('\t')[1].strip().replace('<SEP>', ' ')
        label = 0
        abstract = '<tf><gene>[SEP]' + abstract
        f.write(ref+'\t'+abstract+'\t'+str(label)+'\n')
    f.close()

#sentence with tf or gene
def stageII_preprocess(data_dict):
    outFname = './data/preprocess_done.csv'
    TFs, Genes, TFtoalias, orftogenealias, orftoTF, genealiastoorf, TFtoorf = load_gene_tf_alias('./data/Tf.csv', './data/all_alias_ver3.csv')    
    for article_idx, (article, data) in enumerate(data_dict.items()):
        print('preprocess '+str(article_idx+1)+' / '+str(len(data_dict)))
        pmid = data[0]
        label = data[1]
        
        if label == "TFB":
            flag = True # direct
        elif label == "TFR":
            flag = False # indirect
        else:
            continue
        sents = article.split('@')
        tf_record = list()
        gene_record = list()
        for idx, sent in enumerate(sents):
            for idxword, word in enumerate(sent.split(' ')):
                targetList = processword(word)
                for tf in TFs:
                    for target in targetList:
                        if tf.upper() == target.upper():
                            if tf+'#'+str(idx) not in tf_record:
                                tf_record.append(tf+'#'+str(idx)+'#'+str(idxword))
                for gene in Genes:
                    for target in targetList:
                        if gene.upper() == target.upper():
                            if gene+'#'+str(idx) not in gene_record:
                                gene_record.append(gene+'#'+str(idx)+'#'+str(idxword))
        split_data = findEvidenceList(tf_record, gene_record, genealiastoorf, TFtoorf, sents)
        writeSentdir(pmid, split_data, sents, orftoTF, orftogenealias, outFname, flag)
        
#_article = get_article('../StageI/result.txt')
#new_article = mark_article(_article)
#_preprocess(new_article)

import sys
import torch
import inspect
import numpy as np
from transformers import AutoTokenizer
from torch.utils.data import DataLoader, TensorDataset, SequentialSampler
from torch.nn.utils.rnn import pad_sequence

def softmax(x):
    return np.exp(x) / np.sum(np.exp(x), axis=0)

def chunk_idx_ranges(length, n):
    seq = np.arange(length)
    np.random.shuffle(seq)
    avg = length / float(n)
    sub_seqs = []
    last = 0.0

    while last < len(seq):
        sub_seqs.append(seq[int(last):int(last + avg)])
        last += avg

    return sub_seqs

def create_mini_batch(data_batch):
    max_seq_length=512
    connected = False
    while not connected:
        try:
            tokenizer = AutoTokenizer.from_pretrained("dmis-lab/biobert-base-cased-v1.1")
            connected = True
        except Exception:
            connected = False

    seqs, labels = [], []
    for abstract, label in data_batch:
        token_ids = tokenizer.encode(abstract, truncation=True, max_length=max_seq_length)[:-1]
        token_ids = token_ids[:max_seq_length] if len(token_ids) > max_seq_length else token_ids
        seqs.append(torch.tensor(token_ids))
        labels.append(label)
    
    seqs = pad_sequence(seqs, padding_value=tokenizer.pad_token_id, batch_first=True)
    labels = torch.tensor(labels)
    
    masks = torch.zeros(seqs.size(), dtype=torch.long)
    masks = masks.masked_fill(seqs!=0, 1)
    
    return seqs, labels, masks


def create_cv_dataloaders(df, cv=5, batch_size=8):
    idx_sub_seqs = chunk_idx_ranges(df.shape[0], cv)
    dataloaders = []
    
    for i in range(cv):
        data_loader = DataLoader(df.loc[idx_sub_seqs[i]].values, batch_size=batch_size, 
                                shuffle=True, collate_fn=create_mini_batch)
        dataloaders.append(data_loader)
    
    return dataloaders

def save_checkpoint(save_path, model):
    if save_path == None:
        return
    torch.save(model.state_dict(), save_path)
    print(f'Model saved to ==> {save_path}')


def load_checkpoint(load_path, model, device):    
    if load_path==None:
        return
    state_dict = torch.load(load_path, map_location=device)
    #print(f'\nModel loaded from <== {load_path}')
    
    model.load_state_dict(state_dict)
    return model


def save_metrics(save_path, train_info):
    if save_path == None:
        return
    torch.save(train_info, save_path)
    print(f'\nMetrics saved to ==> {save_path}')


def load_metrics(load_path):
    device='cpu'
    if load_path==None:
        return
    state_dict = torch.load(load_path, map_location=device)
    print(f'\nMetrics loaded from <== {load_path}')
    
    return state_dict


def load_models(init_models, dir_path, device):
    models = []
    for i in range(len(init_models)):
        models.append(load_checkpoint(dir_path+'model_'+str(i+1)+'.pt', init_models[i], device))
    return models


def set_seeds(seed):
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def raiseNotDefined():
    filename = inspect.stack()[1][1]
    line = inspect.stack()[1][2]
    method = inspect.stack()[1][3]

    print("*** Method not implemented: %s at line %s of %s" % (method, line, filename))
    sys.exit(1)


def bioBERT_evaluate(model, data_loader, device):
    eval_loss = 0.0
    total_labels, total_logits = None, None

    model.eval()
    with torch.no_grad():
        for data in data_loader:
            seqs, labels, masks = [t.to(device) for t in data]

            # forward pass
            outputs = model(input_ids=seqs, attention_mask=masks, labels=labels)
            loss, logits = outputs[0], outputs[1]

            if total_labels is None:
                total_labels = labels
            else:
                total_labels = torch.cat([total_labels, labels], dim=0)

            if total_logits is None:
                total_logits = logits
            else:
                total_logits = torch.cat([total_logits, logits], dim=0)

            # 紀錄當前 batch loss
            eval_loss += loss.item()

    loss = eval_loss / len(data_loader)
    total_logits = total_logits.detach().cpu().numpy()
    total_labels = total_labels.detach().cpu().numpy()

    return loss, total_logits, total_labels


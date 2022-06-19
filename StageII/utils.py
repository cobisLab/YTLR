import sys
import torch
import inspect
import numpy as np
from transformers import AutoTokenizer
from torch.utils.data import DataLoader, TensorDataset, SequentialSampler
from torch.nn.utils.rnn import pad_sequence
from torch.optim import Optimizer
from torch.optim.lr_scheduler import LambdaLR
from tqdm import tqdm
import math

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

    seqs, labels, segments, sample_weights = [], [], [], []
    for abstract, label, sample_weight in data_batch:
        token_ids = tokenizer.encode(abstract, truncation=True, max_length=max_seq_length)[:-1]
        token_ids = token_ids[:max_seq_length] if len(token_ids) > max_seq_length else token_ids
        seqs.append(torch.tensor(token_ids))
        labels.append(label)
        sample_weights.append(sample_weight)
   
    seqs = pad_sequence(seqs, padding_value=tokenizer.pad_token_id, batch_first=True)
    labels = torch.tensor(labels)

    for seq in seqs:
        segment_id = 9
        for idx, ids in enumerate(seq):
            if ids == 102:
                segment_id = idx+1

        segment = [0]*segment_id + [1]*(len(seq)-segment_id)
        segments.append(segment)

    segments = torch.tensor(segments)
    sample_weights = torch.tensor(sample_weights)
    
    masks = torch.zeros(seqs.size(), dtype=torch.long)
    masks = masks.masked_fill(seqs!=0, 1)

    return seqs, labels, masks, segments, sample_weights

def save_cv_dataloaders(df, isDirect, cv=5, batch_size=8):
    idx_sub_seqs = chunk_idx_ranges(df.shape[0], cv)


    for i in range(cv):
        seqs, labels, masks, segments, sample_weights = create_mini_batch(df.loc[idx_sub_seqs[i]].values)
        dataset = TensorDataset(seqs, labels, masks, segments, sample_weights)
        torch.save(dataset, './data/'+isDirect+'/trainset_'+str(i)+'_'+str(batch_size)+'.pt')

def create_cv_dataloaders(df, isDirect, cv=5, batch_size=8):
    idx_sub_seqs = chunk_idx_ranges(df.shape[0], cv)
    dataloaders = []

    for i in range(cv):
        dataset = torch.load('./data/'+isDirect+'/trainset_'+str(i)+'_'+str(batch_size)+'.pt')
        #dataset = torch.load('./data/'+isDirect+'/john/trainset_'+str(i)+'_2_'+str(batch_size)+'.pt')
        #print('load dataloader from ./data/'+isDirect+'/john/trainset_'+str(i)+'_2_'+str(batch_size)+'.pt')
        print('load dataloader from ./data/'+isDirect+'/trainset_'+str(i)+'_'+str(batch_size)+'.pt')
#         data_loader = DataLoader(df.loc[idx_sub_seqs[i]].values, batch_size=batch_size,
#                                 shuffle=True, collate_fn=create_mini_batch)
        data_loader = DataLoader(dataset, batch_size=batch_size,
                                shuffle=True)

#         print(data_loader)
        dataloaders.append(data_loader)

    return dataloaders

'''
def create_cv_dataloaders(df, cv=5, batch_size=8):
    idx_sub_seqs = chunk_idx_ranges(df.shape[0], cv)
    dataloaders = []
    
    for i in range(cv):
        data_loader = DataLoader(df.loc[idx_sub_seqs[i]].values, batch_size=batch_size, 
                                shuffle=True, collate_fn=create_mini_batch)
        dataloaders.append(data_loader)
    
    return dataloaders
'''

def create_ensemble_cv_dataloaders(probs, labels, cv=5, batch_size=512):
    assert (probs.shape[0] == labels.shape[0])
    idx_sub_seqs = chunk_idx_ranges(probs.shape[0], cv)
    dataloaders = []
    for i in range(cv):
        probs_tensor = torch.tensor(probs[idx_sub_seqs[i]])
        labels_tensor = torch.tensor(labels[idx_sub_seqs[i]])
        cv_data = TensorDataset(probs_tensor, labels_tensor)
        sampler = torch.utils.data.SequentialSampler(cv_data)
        loader = DataLoader(cv_data, batch_size=batch_size, sampler=sampler)
        dataloaders.append(loader)

    return dataloaders


def create_ensemble_val_dataloader(probs, labels, batch_size=512):
    probs_tensor = torch.tensor(probs)
    labels_tensor = torch.tensor(labels)
    dataset = TensorDataset(probs_tensor, labels_tensor)
    sampler = SequentialSampler(dataset)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False, sampler=sampler)

    return dataloader

def save_checkpoint(save_path, model):
    if save_path == None:
        return
    torch.save(model.state_dict(), save_path)
    print(f'Model saved to ==> {save_path}')


def load_checkpoint(load_path, model, device):    
    if load_path==None:
        return
    state_dict = torch.load(load_path, map_location=device)
    print(f'\nModel loaded from <== {load_path}')
    
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
    #for i in range(len(init_models)):
    for i in range(5):
        for j in range(5):
            models.append(load_checkpoint(dir_path+'model_'+str(i+1)+'_cv_'+str(j+1)+'.pt', init_models[5*i+j], device))
        #models.append(load_checkpoint(dir_path+'model_3_cv_'+str(i+1)+'.pt', init_models[5+i], device))
        #models.append(load_checkpoint(dir_path+'model_5_cv_'+str(i+1)+'.pt', init_models[10+i], device))
    #models.append(load_checkpoint(dir_path+'model_2.pt', init_models[15], device))
    #models.append(load_checkpoint(dir_path+'model_4.pt', init_models[16], device))
    return models

def load_fine_tune_models(init_models, dir_path, model_name, device):
    models = []
    for i in range(len(init_models)):
        #models.append(load_checkpoint(dir_path+'model_'+str(model_name)+'.pt', init_models[i], device))
        models.append(load_checkpoint('model/indirect/model_1_cv_2_2022-02-10_15:48:05.811244.pt', init_models[i], device)) # direct transfer
    return models

def get_cosine_schedule_with_warmup(optimizer: Optimizer, num_warmup_steps: int, num_training_steps: int, num_target_steps: int, num_final_steps: int, num_cycles: float = 0.5, last_epoch: int = -1, last_lr: float = 1e-10):
    def lr_lambda(current_step):
        if current_step < num_warmup_steps:
            return float(current_step) / float(max(1, num_warmup_steps))
        progress = float(current_step - num_warmup_steps) / float(max(1, num_training_steps - num_warmup_steps))
        target_progress = float(num_target_steps - num_warmup_steps) / float(max(1, num_training_steps - num_warmup_steps))
        target = 0.5 * (1.0 + math.cos(math.pi * float(num_cycles) * 2.0 * target_progress))
#         final_progress = float(num_final_steps - num_warmup_steps) / float(max(1, num_training_steps - num_warmup_steps))
#         final = 0.5 * (1.0 + math.cos(math.pi * float(num_cycles) * 2.0 * final_progress))
#         print(target)
        if 0.5 * (1.0 + math.cos(math.pi * float(num_cycles) * 2.0 * progress)) < target:
            return last_lr
        else:
#             print(0.5 * (1.0 + math.cos(math.pi * float(num_cycles) * 2.0 * progress)))
#             print(max(0.0, 0.5 * (1.0 + math.cos(math.pi * float(num_cycles) * 2.0 * progress))))
            return max(0.0, 0.5 * (1.0 + math.cos(math.pi * float(num_cycles) * 2.0 * progress)))


    return LambdaLR(optimizer, lr_lambda, last_epoch)


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
            seqs, labels, masks, segments, sample_weight = [t.to(device) for t in data]

            # forward pass
            outputs = model(input_ids=seqs, attention_mask=masks, token_type_ids = segments, labels=labels, custom_weight = sample_weight)
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


def ensemble_evaluate(model, data_loader, device):
    eval_loss = 0.0
    total_labels, total_logits = None, None

    model.eval()
    with torch.no_grad():
        for data in data_loader:
            probs, labels = [t.to(device) for t in data]

            # forward pass
            logits = model(probs.float())
            loss_fct = torch.nn.CrossEntropyLoss()
            loss = loss_fct(logits, labels)

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

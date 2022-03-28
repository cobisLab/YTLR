import utils
import torch
import numpy as np
import time
from tqdm import tqdm 

from Models import BertClassifier, EnsembleNN
from utils import save_checkpoint, save_metrics, load_checkpoint
from transformers import get_cosine_schedule_with_warmup


# you shouldn't use this class straightly to instance a Trainer
# There are still 'BertTrainer' and 'Ensemble' classes below, both are  
# subclasses of Trainer, and also the classes you should actually use.
class Trainer:
    def __init__(self, name, train_loaders, val_loader, 
                 device, cv, model_num, lr, epochs, metrics_dir, models_dir):
        self._cv = cv
        self._lr = lr
        self._name = name
        self._train_loaders = train_loaders
        self._val_loader = val_loader
        self._epochs = epochs
        self._device = device
        self._model_num = model_num
        self._metrics_dir = metrics_dir
        self._models_dir = models_dir

    def _init_models(self):
        utils.raiseNotDefined()


    def _init_model(self):
        utils.raiseNotDefined()


    def train(self, model, data_loaders, optimizer, scheduler):
        utils.raiseNotDefined()

    def evaluate_batch(self, model, data_batch):
        utils.raiseNotDefined()

    def evaluate(self, model, data_loaders, is_val=True):
        utils.raiseNotDefined()


    def run_epochs(self, model, train_loaders_in_cv, val_loader_in_cv, cv_num):
        lowest_val_loss = np.inf
        epochs_record = {'epoch_'+str(i):{} for i in range(self._epochs)}
        model = model.to(self._device)
        optimizer = torch.optim.Adam(model.parameters(), lr=self._lr)
        total_steps = sum(len(loader) for loader in train_loaders_in_cv) * self._epochs
        #print('total_steps:',total_steps)
        scheduler = get_cosine_schedule_with_warmup(optimizer, 
                                                    num_warmup_steps=total_steps//10, 
                                                    num_training_steps=total_steps, 
                                                    num_cycles=0.5)
        _dir = self._models_dir.split('/')[1] 
        #scheduler = torch.optim.lr_scheduler.ExponentialLR(optimizer, 0.98)
        for epoch in range(self._epochs):
            print("Epoch:" + str(epoch))
            st_time = time.time()
            # train
            # _ = self.train(model, train_loaders_in_cv, optimizer, scheduler)
            train_loss, train_logits, train_labels = self.train(model, train_loaders_in_cv, optimizer, scheduler)
            
            # evaluation
            #train_loss, train_logits, train_labels = self.evaluate(model, train_loaders_in_cv, is_val=False)
            train_acc = sum(np.argmax(train_logits, axis=-1) == train_labels) / len(train_labels)
            epochs_record['epoch_'+ str(epoch)].update({'train_acc': train_acc})
            epochs_record['epoch_'+ str(epoch)].update({'train_loss': train_loss})
            epochs_record['epoch_'+ str(epoch)].update({'train_logits': train_logits})
            epochs_record['epoch_'+ str(epoch)].update({'train_labels': train_labels})

            val_loss, val_logits, val_labels = self.evaluate(model, val_loader_in_cv)
            val_acc = sum(np.argmax(val_logits, axis=1) == val_labels) / len(val_labels)
            epochs_record['epoch_'+ str(epoch)].update({'val_acc': val_acc})
            epochs_record['epoch_'+ str(epoch)].update({'val_loss': val_loss})
            epochs_record['epoch_'+ str(epoch)].update({'val_logits': val_logits})
            epochs_record['epoch_'+ str(epoch)].update({'val_labels': val_labels})

            # if self._epochs <= 10 or ((epoch+1)%10==0 and (epoch)!=0):
            print('CV: %d/%d, Epoch: %d/%d, train_loss: %.4f, train_acc: %.4f, val_loss: %.4f, val_acc: %.4f ==> cost time: %s' 
                    %(cv_num, self._cv, epoch+1, self._epochs, train_loss, train_acc, val_loss, val_acc, time.time()-st_time))
            
            # check whether the best model and save it
            if val_loss < lowest_val_loss:
                lowest_val_loss = val_loss
                save_path = self._models_dir+'model_'+str(self._model_num)+'_cv_' + str(cv_num) +'.pt'
                #save_path = self._models_dir+'model_'+'cv_' + str(cv_num) +'.pt'
                save_checkpoint(save_path, model)
                
        return epochs_record


    def fit_cv(self):
        records = {'cv_'+ str(i): {} for i in range(self._cv)}
        records.update({'lr': self._lr})
        
        #for cv_num in range(1):
        for cv_num in range(self._cv):
            val_loader = self._train_loaders[cv_num]
            train_loaders = [self._train_loaders[i] for i in range(self._cv) 
                             if self._train_loaders[i] != val_loader]
            
            epochs_record = self.run_epochs(self._cv_models[cv_num], train_loaders, val_loader, cv_num+1)
            records['cv_'+ str(cv_num)].update(epochs_record)
            print('cv_'+ str(cv_num))

        # save 5-fold metrics
        save_path = self._metrics_dir+'model_'+ str(self._model_num) +'_cv_metrics.pt'
        save_metrics(save_path, records)
        print()

        return records


    def choose_cv_model(self, init_model):
        val_loss_s = np.zeros(self._cv)
        records = {'cv_'+str(i):{} for i in range(self._cv)}
        _dir = self._models_dir.split('/')[1]
        #for cv_num in range(1):
        for cv_num in range(self._cv):
            #model = load_checkpoint(self._models_dir+'model_'+'cv_'+ str(cv_num+1) +'.pt',
            #                        init_model, self._device)
            model = load_checkpoint(self._models_dir+'model_'+str(self._model_num)+'_cv_'+ str(cv_num+1) +'.pt', 
                                    init_model, self._device)
            model = model.to(self._device)
            val_loss, val_logits, val_labels = self.evaluate(model, self._val_loader)
            val_acc = sum(np.argmax(val_logits, axis=1) == val_labels) / len(val_labels)
            records['cv_'+ str(cv_num)].update({'val_acc': val_acc})
            records['cv_'+ str(cv_num)].update({'val_loss': val_loss})
            records['cv_'+ str(cv_num)].update({'val_logits': val_logits})
            records['cv_'+ str(cv_num)].update({'val_labels': val_labels})
            val_loss_s[cv_num] = val_loss
            print(f'CV_{cv_num+1} val loss: {val_loss}')

        best_cv_model = np.argmin(val_loss_s)
        model = load_checkpoint(self._models_dir+'model_'+str(self._model_num)+'_cv_'+ str(best_cv_model+1) +'.pt', model, self._device)
        
        save_path = self._models_dir+'model_'+ str(self._model_num) +'.pt'
        save_checkpoint(save_path, model)

        save_path = self._metrics_dir+'val_metrics_'+ str(self._model_num) +'.pt'
        save_metrics(save_path, records)

        return records

    def run(self):
        cv_metrics = self.fit_cv()
        val_metrics = self.choose_cv_model(self._init_model())


        return cv_metrics, val_metrics

class BertTrainer(Trainer):
    def __init__(self, num_labels, **kwargs):
        super(BertTrainer, self).__init__(**kwargs)
        self._num_labels = num_labels
        self._cv_models = self._init_models()

    def _init_models(self):
        return [BertClassifier.from_pretrained("dmis-lab/biobert-base-cased-v1.1", 
                num_labels=self._num_labels, 
                output_hidden_states=True) for _ in range(self._cv)]

    def _init_model(self):
        return BertClassifier.from_pretrained("dmis-lab/biobert-base-cased-v1.1", 
                                              num_labels=self._num_labels, 
                                              output_hidden_states=True)
    def evaluate_batch(self, model, seqs, labels, masks):
        batch_loss = 0.0
        step_count = 0
        total_labels, total_logits = None, None

        model.eval()
        with torch.no_grad():
            #for data in data_batch:
                #seqs, labels, masks = [t.to(self._device) for t in data]

                # forward pass
            outputs = model(input_ids=seqs, attention_mask=masks, labels=labels)
            loss, logits = outputs[0], outputs[1]

            #if total_labels is None:
            total_labels = labels
            #else:
            #    total_labels = torch.cat([total_labels, labels], dim=0)

            #if total_logits is None:
            total_logits = logits
            #else:
            #    total_logits = torch.cat([total_logits, logits], dim=0)

            batch_loss += loss.item()
            #step_count += 1

        #batch_loss = batch_loss / step_count

        total_logits = total_logits.detach().cpu().numpy()
        total_labels = total_labels.detach().cpu().numpy()

        return batch_loss, total_logits, total_labels

    def train(self, model, data_loaders, optimizer, scheduler):
        eval_batch_loss = 0.0
        step_count = 0
        total_labels, total_logits = None, None
        
        model.train()

        for _, train_loader in tqdm(enumerate(data_loaders), total=len(data_loaders)):
        #for train_loader in data_loaders:
            for _, data in tqdm(enumerate(train_loader), total=len(train_loader), leave = False):
            #for data in train_loader:
                seqs, labels, masks = [t.to(self._device) for t in data]

                # 將參數梯度歸零
                optimizer.zero_grad()
                # forward pass
                outputs = model(input_ids=seqs, attention_mask=masks, labels=labels)
                loss = outputs[0]
                #loss, logits = outputs[0], outputs[1]
                loss.backward()
                optimizer.step()
                scheduler.step()

                batch_loss, batch_logits, batch_labels = self.evaluate_batch(model, seqs, labels, masks)

                eval_batch_loss += batch_loss

                if total_logits is None:
                    total_logits = batch_logits
                else:
                    total_logits = np.concatenate((total_logits, batch_logits), axis=0)
                    #total_logits= torch.cat([total_logits, batch_logits], dim=0)

                if total_labels is None:
                    total_labels = batch_labels
                else:
                    total_labels = np.concatenate((total_labels, batch_labels), axis=0)
                    #total_labels = torch.cat([total_labels, batch_labels], dim=0)

                step_count+=1
                model.train()
                # backward
                # loss.backward()
                # optimizer.step()
                # scheduler.step()

        eval_batch_loss = eval_batch_loss/step_count
        #total_logits = total_logits.detach().cpu().numpy()
        #total_labels = total_labels.detach().cpu().numpy()

        return eval_batch_loss, total_logits, total_labels


    def evaluate(self, model, data_loaders, is_val=True):
        eval_loss = 0.0
        step_count = 0
        total_labels, total_logits = None, None

        if is_val:
            data_loaders = [data_loaders]

        model.eval()
        with torch.no_grad():
            for loader in data_loaders:
                for data in loader:
                    seqs, labels, masks = [t.to(self._device) for t in data]

                    # forward pass
                    outputs = model(input_ids=seqs, attention_mask=masks, labels=labels)
                    loss, logits = outputs[0], outputs[1]
                    # print(loss)
                    if total_labels is None:
                        total_labels = labels
                    else:
                        total_labels = torch.cat([total_labels, labels], dim=0)

                    if total_logits is None:
                        total_logits = logits
                    else:
                        total_logits = torch.cat([total_logits, logits], dim=0)

                    # 紀錄當前 batch loss
                    # print(step_count,loss.item())
                    eval_loss += loss.item()
                    step_count += 1

        eval_loss = eval_loss / step_count

        total_logits = total_logits.detach().cpu().numpy()
        total_labels = total_labels.detach().cpu().numpy()

        return eval_loss, total_logits, total_labels



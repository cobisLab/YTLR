import torch
from transformers.modeling_outputs import SequenceClassifierOutput
from transformers.models.bert.modeling_bert import BertPreTrainedModel, BertModel

def weighted_loss(y, y_hat, w):
    loss_fct = torch.nn.CrossEntropyLoss(reduction='none')
    return (loss_fct(y, y_hat)*w).mean()

class BertClassifier(BertPreTrainedModel):
    def __init__(self, config):
        super(BertClassifier, self).__init__(config)
        self.num_labels = config.num_labels
        self.bert = BertModel(config)
        #self.dropout = torch.nn.Dropout(config.hidden_dropout_prob)
        self.dropout = torch.nn.Dropout(0.5)
        self.classifier = torch.nn.Linear(config.hidden_size, self.num_labels)
        self.init_weights()

    def forward(self, input_ids=None, attention_mask=None, token_type_ids=None, position_ids=None, 
                head_mask=None, inputs_embeds=None, labels=None, output_attentions=None, 
                output_hidden_states=None, return_dict=None, custom_weight=None):
        
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        sample_weight = custom_weight if custom_weight is not None else torch.full(labels.shape, 1) 

        outputs = self.bert(
            input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
            position_ids=position_ids,
            head_mask=head_mask,
            inputs_embeds=inputs_embeds,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict
        )

        pooled_output = outputs[1]

        pooled_output = self.dropout(pooled_output)
        logits = self.classifier(pooled_output)

        loss = None
        if labels is not None:
            #loss_fct = torch.nn.CrossEntropyLoss()
            #loss = loss_fct(logits.view(-1, self.num_labels), labels.view(-1))
            loss = weighted_loss(logits.view(-1, self.num_labels), labels.view(-1), sample_weight)
        if not return_dict:
            output = (logits,) + outputs[2:]
            return ((loss,) + output) if loss is not None else output

        return SequenceClassifierOutput(
            loss=loss,
            logits=logits,
            hidden_states=outputs.hidden_states,
            attentions=outputs.attentions,
        )


class EnsembleNN(torch.nn.Module):
    def __init__(self, layers, in_shape, hidden, out_shape, dropout_rate, device):
        super(EnsembleNN, self).__init__()
        self._device = device
        
        self.in_layer = torch.nn.Linear(in_shape, hidden)
        #self.in_layer = torch.nn.Linear(in_shape, 256)
        torch.nn.init.xavier_uniform_(self.in_layer.weight)
        
        self.hidden_layers2 = [torch.nn.Linear(hidden, hidden) for _ in range(layers)]
        for layer in self.hidden_layers2:
            torch.nn.init.xavier_uniform_(layer.weight)

        self.out_layer = torch.nn.Linear(hidden, out_shape)
        torch.nn.init.xavier_uniform_(self.out_layer.weight)

        self.dropout = torch.nn.Dropout(dropout_rate)
        self.activation = torch.nn.PReLU()

        self.bn1 = torch.nn.BatchNorm1d(num_features=in_shape)

    def forward(self, x):
        #logits = self.dropout(x)
        logits = self.bn1(x)

        logits = self.in_layer(logits)
        logits = self.activation(logits)
        
        for hidden_layer in self.hidden_layers2:
            hidden_layer = hidden_layer.to(self._device)
            logits = self.dropout(logits)
            logits = hidden_layer(logits)
            logits = self.activation(logits)        
        
        logits = self.dropout(logits)
        logits = self.out_layer(logits)
        logits = self.activation(logits)

        return logits

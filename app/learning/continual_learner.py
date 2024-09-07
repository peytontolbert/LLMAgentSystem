import torch
import torch.nn as nn
import torch.optim as optim
from typing import List, Dict, Any
import random
import torch.nn.functional as F
class EWC(nn.Module):
    def __init__(self, model: nn.Module, dataset: List[Dict[str, Any]]):
        super().__init__()
        self.model = model
        self.dataset = dataset
        self.params = {n: p for n, p in self.model.named_parameters() if p.requires_grad}
        self._means = {}
        self._precision_matrices = self._diag_fisher()

    def _diag_fisher(self):
        precision_matrices = {}
        for n, p in self.params.items():
            precision_matrices[n] = p.clone().detach().fill_(0)

        self.model.eval()
        for input_data in self.dataset:
            self.model.zero_grad()
            output = self.model(input_data['input'])
            loss = F.nll_loss(F.log_softmax(output, dim=1), input_data['target'])
            loss.backward()

            for n, p in self.model.named_parameters():
                precision_matrices[n].data += p.grad.data ** 2 / len(self.dataset)

        precision_matrices = {n: p for n, p in precision_matrices.items()}
        return precision_matrices

    def penalty(self, model: nn.Module):
        loss = 0
        for n, p in model.named_parameters():
            _loss = self._precision_matrices[n] * (p - self._means[n]) ** 2
            loss += _loss.sum()
        return loss

    def update(self, model: nn.Module):
        self.model = model
        self._means = {n: p.clone().detach() for n, p in self.model.named_parameters() if p.requires_grad}

class ContinualLearner:
    def __init__(self, model: nn.Module, ewc_lambda: float = 0.4):
        self.model = model
        self.ewc = None
        self.ewc_lambda = ewc_lambda
        self.optimizer = optim.Adam(self.model.parameters())

    def learn(self, new_data: List[Dict[str, Any]]):
        if self.ewc is None:
            self.ewc = EWC(self.model, new_data)
        else:
            self.ewc.update(self.model)

        for epoch in range(10):  # Adjust the number of epochs as needed
            random.shuffle(new_data)
            for data in new_data:
                self.optimizer.zero_grad()
                output = self.model(data['input'])
                loss = F.nll_loss(F.log_softmax(output, dim=1), data['target'])
                ewc_loss = self.ewc_lambda * self.ewc.penalty(self.model)
                total_loss = loss + ewc_loss
                total_loss.backward()
                self.optimizer.step()

    def predict(self, input_data: Any):
        with torch.no_grad():
            return self.model(input_data)
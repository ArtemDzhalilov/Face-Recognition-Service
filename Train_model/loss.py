from torch.nn import CrossEntropyLoss
from torch import Tensor
import torch.nn.functional as F
from typing import Callable, Optional


class MultiCrossEntropyLoss(CrossEntropyLoss):
    def forward(self, input1: Tensor, input2: Tensor, input3: Tensor, input4: Tensor, target: Tensor) -> Tensor:
        return 0.125 * F.cross_entropy(input4, target, weight=self.weight,
                                       ignore_index=self.ignore_index, reduction=self.reduction,
                                       label_smoothing=self.label_smoothing) + 0.25 * F.cross_entropy(input4, target,
                                                                                                      weight=self.weight,
                                                                                                      ignore_index=self.ignore_index,
                                                                                                      reduction=self.reduction,
                                                                                                      label_smoothing=self.label_smoothing) + 0.5 * F.cross_entropy(
            input2, target, weight=self.weight,
            ignore_index=self.ignore_index, reduction=self.reduction,
            label_smoothing=self.label_smoothing) + 1 * F.cross_entropy(input1, target, weight=self.weight,
                                                                        ignore_index=self.ignore_index,
                                                                        reduction=self.reduction,
                                                                        label_smoothing=self.label_smoothing)

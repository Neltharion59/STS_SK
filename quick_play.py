from dataset_utils import load_dataset
from final_split import stratified_split

from tree_loader import load_enhanced_tree

import matplotlib.pyplot as plt
import numpy as np


dataset = load_dataset("sick_sk.txt")

scores = [float(score) for (_,_,score) in dataset]

plt.violinplot(scores)
plt.show()
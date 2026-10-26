# Runnable script to download and install  Wordnet, OMW Wordnets and Slovak WordNet to device

import nltk
import os
from shutil import copyfile

# Download WordNet library
nltk.download('wordnet')
# Download OMW WordNets
nltk.download('omw-1.4')

# Create entry for Slovak ('slk')
resource_path = r".\resources\slk_wordnet"
slk_path = os.path.join(nltk.data.find("corpora"), "omw", "slk")

# Create folder for Slovak WordNet (including parent directories)
try:
    os.makedirs(slk_path, exist_ok=True)
except FileExistsError:
    pass

# Copy Slovak WordNet files (from this repository) to where they need to be
copy_files = os.listdir(resource_path)
for file in copy_files:
    copyfile(os.path.join(resource_path, file), os.path.join(slk_path, file))

from sklearn.model_selection import train_test_split
from json import loads, dumps

def load_dataset(dataset):     
    data = []
    with open(dataset,"r",encoding = "utf-8-sig") as file:
        for line in file:
            line = line.strip().split("\t")
            data.append((line[1],line[2],float(line[0])))
    return data

def count_names(row):
    count = 0

    sentence1 = row[0].split()[1:]
    sentence2 = row[1].split()[1:]

    for word in sentence1:
        if word[0].isupper():
            count += 1

    for word in sentence2:
        if word[0].isupper():
            count += 1

    return count
    
def count_words(row):
    return len(row[0].split()) + len(row[1].split())

def get_score_bucket(row):
    score = row[2]

    if score < 1:
        return 1

    elif score < 2:
        return 2

    elif score < 3:
        return 3

    elif score < 4:
        return 4

    return 5

def get_name_bucket(row):
    names = count_names(row)

    if names == 0:
        return 0

    elif names == 1:
        return 1

    return 2

def get_length_bucket(row):
    words = count_words(row)

    if words < 15:
        return "short"

    elif words < 25:
        return "medium"

    return "long"

def stratified_split(dataset):

    try:
        with open('split/train_final.txt','r',encoding='utf-8-sig') as f:
            train_data = loads(f.read())
        with open('split/test_final.txt','r',encoding='utf-8-sig') as f:
            test_data = loads(f.read())
    except FileNotFoundError:
        labels = []

        for row in dataset:

            label = (
                str(get_score_bucket(row))
                + "_"
                + get_length_bucket(row)
                + "_"
                + str(get_name_bucket(row))
            )

            labels.append(label)

        train_data, test_data = train_test_split(
            dataset,
            test_size=len(dataset) - 1000,
            stratify=labels
        )

        with open('split/train_final.txt','w+',encoding='utf-8-sig') as f:
            f.write(dumps(train_data))
        with open('split/test_final.txt','w+',encoding='utf-8-sig') as f:
            f.write(dumps(test_data))

    return train_data, test_data


dataset = load_dataset('sick_sk.txt')
stratified_split(dataset)
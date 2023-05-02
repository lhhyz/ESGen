# ESGen: Commit Message Generation Based on Edit Sequence of Code Change

This is the dataset for ESGen. The dataset is saved in the ```/data``` folder.

## Quick start
If you want to train your own dataset, start with the step1, otherwise skip the step2.

### Step1: get pre-trained model

```wget https://storage.googleapis.com/bert_models/2018_10_18/uncased_L-12_H-768_A-12.zip 
unzip uncased_L-12_H-768_A-12.zip```

### Step2: data preprocess
> + please place the diff, seq and commit message files under data folder with the following names:<br>
>-train_story.txt <br>
>-train_summ.txt <br>
-train_ast.txt <br>
-eval_story.txt <br>
-eval_summ.txt <br>
-eval_seq.txt <br>
-test_story.txt <br>
-test_summ.txt <br>
-test_seq.txt <br>
> each story and summary must be in a single line (see sample text given.)
>
> + Run the preprocess.py <br>
Command: ```python preprocess.py```<br>
This will creates three tfrecord files under the datawash folder.

### Step3: train the model
> run the main.py <br>
Command: ```python main.py``` <br>
Configurations for the model can be changes from config.py file

### Step4: generate commit message and test your trained model
> + Firstly, generate commit message for the test set <br>
> run the generation.py <br>
> Command: ```python generation.py```
> + Then, evaluate the generation commit message<br>
> run the Metrics.sh <br>
> Command: ```./Metrics.sh Reference Prediction ScoreSaveFile```


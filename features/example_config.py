import datetime
import os 
import pandas as pd

inputfile= '../data/burnc-small.csv'
#inputfile= '../data/burnc-new.csv'
date = datetime.date.today().strftime("%Y-%m-%d")

config = {
    'input_file': inputfile
}

df = pd.read_csv(inputfile)
#df.to_csv(inputfile,sep = ',', encoding='utf-8', index=False, line_terminator='\r\n')


sent_id = -1
prev_parse_tree = ''
for index, row in df.iterrows():
    if row['parse_tree'] != prev_parse_tree:
        sent_id = sent_id + 1
        prev_parse_tree = row['parse_tree']
        df.loc[index,'sent_id'] = sent_id
        #row['sentence_id'] = sent_id
    else:
        df.loc[index,'sent_id'] = sent_id


df.to_csv('../data/burnc-new.csv',sep = ',', encoding='utf-8', index=False, line_terminator='\r\n')
'''
This scripts add Features based on word relations.
Features described in this paper https://arxiv.org/pdf/1904.04764.pdf

SpeechLab @ CU Fall 2020
'''
from example_config import config
import pandas as pd
from nltk.tree import Tree
from nltk.tree import ParentedTree
import string

#Helper Functtions

def height_pos(parenttree, HEIGHT):
    '''
    Returns the array of the height of the POS tags of the leaves in the tree
    '''
    Height_POS = []
    n_leaves = len(parenttree.leaves())
    leavepos = set(parenttree.leaf_treeposition(n) for n in range(n_leaves))
    Height_POS = []
    for pos in parenttree.treepositions():
        if pos in leavepos:
            Height_POS.append((parenttree[pos], HEIGHT - (len(pos)-1)))
    return Height_POS

def traverse(t, HEIGHT, result = []):
    '''
    Traveses each subtree in the parent Tree. 
    Returns tuple(subtree.label, phrase, relative_height)
    '''
    try:
        t.label()
    except AttributeError:
        return
    else:

        if t.height() == 2:   #child nodes
            rel_len_to_root = HEIGHT - len(t.parent().treeposition())
            result.append((t.parent().label(), " ".join(t.parent().leaves()), rel_len_to_root))
            return

        for child in t:
            traverse(child, HEIGHT, result)
    return result 


def func_HBCW(list_of_const, sent_list):
    '''
    Returns an array of tuples for each word in the sentence and the HBCW
    HBCW Highest-level phrase beginning with the current word if it has else NONE
    '''
    HBCW = []
    for i in range(len(sent_list)):
        wd = sent_list[i]
        const_with_wd = [const for const in list_of_const if (const[1].split(" ")[0] == wd and const[0] != "S")]
        if const_with_wd:
            tag = max(const_with_wd, key=lambda x: len(x[1].split(" ")))[0]
            HBCW.append((wd,tag))
        else:
            HBCW.append((wd,'NONE'))
    return HBCW


def func_HEPW(list_of_const, sent_list):
    '''
    Returns an array of tuples for each word in the sentence and the HBCW
    HEPW Highest-level phrase ending with the previous word if it has else NONE
    '''
    HEPW = []
    for i in range(len(sent_list)):
        wd = sent_list[i-1]
        curr_wd = sent_list[i]
        const_with_wd = [const for const in list_of_const if (const[1].split(" ")[-1] == wd and const[0] != "S")]
        if const_with_wd:
            tag = max(const_with_wd, key=lambda x: len(x[1].split(" ")))[0]
            HEPW.append((curr_wd,tag))
        else:
            HEPW.append((curr_wd,'NONE')) 
    return HEPW

def func_LCA(list_of_const, sent_list, HEIGHT):
    '''
    Return a list of tuples of the Lowest Commeon Ancestor LCA for the current and previous word or S if none
    '''
    LCA = []
    for i in range(len(sent_list)):
        wd_pair = sent_list[i-1] +' ' + sent_list[i]
        const_with_wd_pairs = [const for const in list_of_const if wd_pair in const[1]]
        if const_with_wd_pairs:
            LCA_tuple = min(const_with_wd_pairs, key=lambda x: len(x[1].split(" ")))
            tag = LCA_tuple[0]
            Height_LCA = LCA_tuple[2]
            LCA.append((sent_list[i], tag, Height_LCA))
        else:
            LCA.append((sent_list[i],'S', HEIGHT-1))
    return LCA

def syn_Distance(parenttree, sent_list, LCA , HEIGHT):
    '''
    DCP stands for distance between the current word POS and the previous word POS; 𝐷𝑐𝑝 = 𝐷𝑐𝑙 + 𝐷𝑝𝑙
    𝐷𝑐𝑙 : refers to the distance between LCA and current POS
    𝐷pl : refer to the distance between LCA and the preceeding POS
    '''
    Height_POS = height_pos(parenttree, HEIGHT)
    DIST = []
    for index, item in enumerate(sent_list):
        Hl = LCA[index][2]
        Hc = Height_POS[index][1]
        Hp = Height_POS[index-1][1]
        D_cl = Hl - Hc
        D_pl = Hl - Hp
        D_cp = D_cl + D_pl
        DIST.append((sent_list[index-1], item,  LCA[index][1], D_cp))
    return DIST


def extract_sentFeats(parse_tree):
    feature_set = []
    parenttree = ParentedTree.fromstring(parse_tree)
    sent_list = parenttree.leaves()
    HEIGHT = parenttree.height()-2
    res = traverse(parenttree, HEIGHT, result = [])
    list_of_const = set([const for const in res if len(const[1].split(' ')) > 1])
    HEPW = func_HEPW(list_of_const, sent_list)
    HBCW = func_HBCW(list_of_const, sent_list)
    LCA = func_LCA(list_of_const, sent_list, HEIGHT)
    DIST = syn_Distance(parenttree, sent_list, LCA, HEIGHT)
    HEPW = [tup[1] for tup in HEPW]
    HBCW = [tup[1] for tup in HBCW]
    LCA = [tup[1] for tup in LCA]
    DIST = [tup[3] for tup in DIST]
    for ind in range(len(sent_list)):
        # print(sent_list[ind],HEPW[ind], HBCW[ind], LCA[ind], DIST[ind])
        #Skip punctuation and posessives
        if sent_list[ind] in list(string.punctuation)+["'s", "n't"]:
            ind = ind + 1
        else:
            feature_set.append([sent_list[ind], HEPW[ind], HBCW[ind], LCA[ind], DIST[ind]])
    return feature_set

def main():

    #inputfile = config['input_file']
    inputfile = "../data/burnc-new.csv"
    print(inputfile)
    df1 = pd.read_csv(inputfile, engine='python')
    df = df1.head(120)
    #print(df.head())

    prev_row_sentid = -1
    for index, row in df.iterrows():
        if row['sentence_id'] != prev_row_sentid:
           # print(row['sentence_id'], row['word'])
            prev_row_sentid = row['sentence_id']
            word_features = extract_sentFeats(row['parse_tree'])
            index_feats = word_features[0]
            print(row['sentence_id'], row['word'], index_feats)
            df.loc[index,'HEPW'] = index_feats[1]
            df.loc[index,'HBCW'] = index_feats[2]
            df.loc[index,'LCA'] = index_feats[3]
            df.loc[index,'DIST'] = index_feats[4]
        else:
            index_feats =  word_features[row['word_number_in_sentence']-1]
            print(row['sentence_id'], row['word'], index_feats)
            df.loc[index,'HEPW'] = index_feats[1]
            df.loc[index,'HBCW'] = index_feats[2]
            df.loc[index,'LCA'] = index_feats[3]
            df.loc[index,'DIST'] = index_feats[4]

    #print(df.head())

    #df.to_csv("BNC_aug24.csv",sep = ',', encoding='utf-8', index=False, line_terminator='\r\n')

    df = df[['sentence_id','word','word_pos_tag', 'parse_tree', 'HEPW', 'HBCW', 'LCA', 'DIST']]
    df.to_csv("Burnc_sample.csv",sep = ',', encoding='utf-8', index=False, line_terminator='\r\n')


if __name__ == '__main__':
    main()
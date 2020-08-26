from nltk.tree import Tree
from nltk.draw.tree import TreeView
t = Tree.fromstring("(ROOT (S (NP (NNP William) (NNP Weld)) (VP (VBZ says) (SBAR (S (NP (PRP he)) (VP (VBZ wants) (S (VP (TO to) (VP (VB break) (NP (NP (DT the) (NN stranglehold)) (SBAR (S (NP (DT the) (JJ Democratic) (NN party)) (VP (VBZ has) (VP (PP (IN on) (NP (NNP Massachusetts) (NNS politics))))))))))))))) (. .)))")
TreeView(t)._cframe.print_to_file('sent3.ps')

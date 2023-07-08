import pandas as pd
import numpy as np
import sys
import networkx as nx

anchors_new_file = sys.argv[1]
vorchor = sys.argv[2]

with open(anchors_new_file) as f:
    anchors1=f.readlines()
    df_anchors=pd.DataFrame(anchors1)
    df_anchors=df_anchors[0].str.split("\t",expand=True)
    df_anchors=df_anchors.fillna('###\n')
    df_anchors=df_anchors.drop([0])
    df_abchors1='-'.join([str(i) for i in df_anchors[0]])
    df_abchors1=df_abchors1.split('-###\n-')
    df_abchors1=pd.DataFrame(df_abchors1)
    df_abchors1=df_abchors1.replace('###\n-','',regex=True)
    df_anchors2='-'.join([str(i) for i in df_anchors[1]])
    df_anchors2=df_anchors2.split('-###\n-')
    df_anchors2=pd.DataFrame(df_anchors2)
    df_anchors3 = '-'.join([str(i) for i in df_anchors[2]])
    df_anchors3 = df_anchors3.split('-###\n-')
    df_anchors3 = pd.DataFrame(df_anchors3)
    df_anchors3 = df_anchors3[0].str.replace('\n','')
    df=df_abchors1.merge(df_anchors2,how='inner',left_index=True, right_index=True)
    df=df.merge(df_anchors3,how='inner', left_index=True,right_index=True)

def merge_sets(set_list):
    for i in range(len(set_list)):
        # 添加判定条件
        # 如果集合元素的前三个字母不同，则跳过后续处理
        if any(set_list[i][0][:3] != set_list[j][0][:3] for j in range(i+1, len(set_list))):
            continue

        for j in range(i+1, len(set_list)):
            set1 = set(set_list[i])
            set2 = set(set_list[j])

            # 判断是否存在子集关系，如果是，则合并集合
            if set1.issubset(set2) or set2.issubset(set1):
                set_list[i] = list(set1.union(set2))
                set_list[j] = list(set2.union(set1))
            else:
                intersection = set1 & set2
                union = set1 | set2
                overlap = len(intersection) / len(union)

                # 判断重叠率是否大于0.5，如果是，则合并集合
                if overlap > 0.5:
                    set_list[i] = list(union)
                    set_list[j] = list(union)

    return [s for s in set_list if s]


set_list_a = []
set_list_b = []
score_average_list = []
for index, row in df.iterrows():
    a = row['0_x'].split('-')
    b = row['0_y'].split('-')
    s = np.mean([float(num) for num in row[0].split('-')])
    set_list_a.append(a)
    set_list_b.append(b)
    score_average_list.append(s)

set_list_a1 = merge_sets(set_list_a)
set_list_b1 = merge_sets(set_list_b)

series1 = pd.Series(set_list_a1, name='block1')
series2 = pd.Series(set_list_b1, name='block2')
series3 = pd.Series(score_average_list, name='score')
df_block1 = pd.concat([series1,series2,series3],axis=1)
#df_block1.to_csv(str(vorchor)+'final_anchor_new_block4.csv',sep='\t',index=None)



simple_block1 = []
simple_block2 = []
block_imap = pd.DataFrame()

for index, row in block.iterrows():
    block1 = str(sorted(eval(row['block1']))[0]) + ":" + str(sorted(eval(row['block1']))[-1])
    block2 = str(sorted(eval(row['block2']))[0]) + ":" + str(sorted(eval(row['block2']))[-1])
    simple_block1.append(block1)
    simple_block2.append(block2)
    block_imap = block_imap.append({
        'block': block1,
        'details': sorted(eval(row['block1'])),
        'length': len(eval(row['block1']))
    }, ignore_index=True)
    block_imap = block_imap.append({
        'block': block2,
        'details': sorted(eval(row['block2'])),
        'length': len(eval(row['block2']))
    }, ignore_index=True)

# 给新的 DataFrame 添加列名
block_simple = pd.DataFrame({'simple_block1': simple_block1, 'simple_block2': simple_block2})
block_imap.columns = ['block', 'details', 'length']

block_imap_uniq = block_imap.loc[block_imap.groupby('block')['length'].idxmax()]
#block_imap_uniq

imap_dic = dict(zip(block_imap_uniq['block'],block_imap_uniq['details']))
#imap_dic

G =nx.Graph()
for index, row in block_simple.iterrows():
    Block1=row["simple_block1"]
    Block2=row["simple_block2"]
    #sorce =row["score"]
    G.add_edge(Block1,Block2)


output_set = set()
with open("path_output.txt", "w") as f:
    for node in G.nodes():
        visited = set()
        visited.add(node)
        path = [node]
        current_node = node
        while True:
            neighbors = list(G.neighbors(current_node))
            if not neighbors:
                break
            next_node = None
            max_length = -1  # 用于记录当前已访问节点路径的最大长度
            for neighbor in neighbors:
                if neighbor not in visited and neighbor[:3] != current_node[:3] and len(neighbor) > max_length:
                    next_node = neighbor
                    max_length = len(imap_dic[neighbor])
            if next_node is None:
                break
            visited.add(next_node)
            path.append(next_node)
            current_node = next_node
        path_set = frozenset(path)
        if path_set not in output_set:
            f.write(str(path) + '\t' + str(len(path)) + "\n")
            output_set.add(path_set)



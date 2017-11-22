#coding=utf8
#基于BGP异常事件与网络服务异常事件关联场景的FP-growth算法改进


import json
from datetime import datetime
from fp_growth_modified import find_frequent_itemsets as modified_fpg
from fp_growth import find_frequent_itemsets as orginal_fpg
# from generate_rule import generateRules

def load_data():
    with open('examples/db.json') as f:
        data = json.loads(f.read())
        transactions = [data[tid] for tid in data]
        # for tid in data:
        #     for item in data[tid]:
        #         if 'www' not in item:
        #             transactions.append(data[tid])
        #             break
        # print len(transactions)
        mix_transactions = []
        bgp_transactions = []
        for tr in transactions:
            bgp = []
            web = []
            for item in tr:
                if 'www' in item:
                    web.append(item)
                else:
                    bgp.append(item)
            for e in web:
                mix_transactions.append(bgp + [e])
            bgp_transactions.append(bgp)

        # return new_transactions
        # return transactions
        return mix_transactions, bgp_transactions

def load_bgp_data():
    with open('examples/db.json') as f:
        data = json.loads(f.read())
        transactions = []
        for tid in data:
            tr = []
            for item in data[tid]:
                if 'www' not in item:
                    tr.append(item)
            if len(tr) > 0:
                transactions.append(tr)
        print len(transactions)
        return transactions

def fpg(mix_transactions, ant_transactions , minsupp):   
    mix_result = []
    for itemset, support in modified_fpg(mix_transactions, minsupp, True):
        mix_result.append((itemset,support))

    ant_result = []
    for itemset, support in modified_fpg(ant_transactions, minsupp, True):
        ant_result.append((itemset,support))

    # result = sorted(result, key=lambda i: i[0])
    # for itemset, support in result:
    #     print str(itemset) + ' ' + str(support)

    return mix_result, ant_result

def gen_rules(mix_fp, ant_fp, mincof):
    supp_dict = {}
    for fp in mix_fp:
        supp_dict[frozenset(fp[0])] = fp[1]

    for fp in ant_fp:
        supp_dict[frozenset(fp[0])] = fp[1]

    for fp in mix_fp:
        for item in fp[0]:
            if 'www' in item:
                consequent = item
                break
        antecedent = frozenset(fp[0]) - frozenset([item])
        if supp_dict[frozenset(fp[0])] / supp_dict[antecedent] > mincof:
            print str(list(antecedent)), '===>', consequent


def main():
    db, ant_db = load_data()
    starttime = datetime.now()
    print 'begin fpg %s' % starttime.isoformat()
    mix_fp, ant_fp = fpg(db, ant_db, 20)
    endtime = datetime.now()
    print 'done fpg %s' % endtime.isoformat()
    print endtime - starttime
    rules = gen_rules(mix_fp, ant_fp, 0.8)

# def analysis_test(transactions, minsupp):   
#     result = []
#     for itemset, support in orginal_fp(transactions, minsupp, True):
#         print itemset, support
#         result.append((itemset,support))

#     result = sorted(result, key=lambda i: i[0])
#     for itemset, support in result:
#         print str(itemset) + ' ' + str(support) 

# def test():
#     db = load_bgp_data()
#     starttime = datetime.now()
#     print 'begin analysis %s' % starttime.isoformat()
#     analysis_test(db, 20)
#     endtime = datetime.now()
#     print 'done analysis %s' % endtime.isoformat()
#     print endtime - starttime

if __name__ == '__main__':
    main()
    # test()
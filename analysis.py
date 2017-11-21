#coding=utf8
#基于BGP异常事件与网络服务异常事件关联场景的FP-growth算法改进


import json
from datetime import datetime
from fp_growth_modified import find_frequent_itemsets
from fp_growth import find_frequent_itemsets as orginal_fp
from generate_rule import generateRules

def load_data():
    with open('examples/db.json') as f:
        data = json.loads(f.read())
        transactions = []
        for tid in data:
            for item in data[tid]:
                if 'www' not in item:
                    transactions.append(data[tid])
                    break
        print len(transactions)
        # new_transactions = []
        # for tr in transactions:
        #     bgp = []
        #     web = []
        #     for item in tr:
        #         if 'www' in item:
        #             web.append(item)
        #         else:
        #             bgp.append(item)
        #     for e in web:
        #         new_transactions.append(bgp + [e])
        # print len(new_transactions)
        # exit()
        # return new_transactions
        return transactions

def load_bgp_data():
    with open('examples/db.json') as f:
        data = json.loads(f.read())
        transactions = []
        for tid in data:
            tr = []
            for item in data[tid]:
                if 'www' not in item:
                    tr.append(data[tid])
            if len(tr) > 0:
                transactions.append(tr)
        print len(transactions)
        return transactions

def analysis(transactions, minsupp):   
    result = []
    for itemset, support in find_frequent_itemsets(transactions, minsupp, True):
        print itemset, support
        result.append((itemset,support))

    result = sorted(result, key=lambda i: i[0])
    for itemset, support in result:
        print str(itemset) + ' ' + str(support)

def analysis_test(transactions, minsupp):   
    result = []
    for itemset, support in orginal_fp(transactions, minsupp, True):
        print itemset, support
        result.append((itemset,support))

    result = sorted(result, key=lambda i: i[0])
    for itemset, support in result:
        print str(itemset) + ' ' + str(support)    

def main():
    db = load_data()

    print 'begin analysis %s' % datetime.now().isoformat()
    analysis(db, 20)   
    print 'done analysis %s' % datetime.now().isoformat()

def test():
    db = load_bgp_data()
    print 'begin analysis %s' % datetime.now().isoformat()
    analysis_test(db, 20)   
    print 'done analysis %s' % datetime.now().isoformat()
if __name__ == '__main__':
    # main()
    test()
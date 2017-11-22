#coding=utf8
#
import json
import pandas as pd
from datetime import datetime
from fp_growth_modified import find_frequent_itemsets as modified_fpg
from fp_growth import find_frequent_itemsets as orginal_fpg
from mlxtend.frequent_patterns import association_rules

def load_data():
    with open('examples/db.json') as f:
        data = json.loads(f.read())
        transactions = [data[tid] for tid in data]
        return transactions

def fpg(transactions, minsupp): 
    cons_transactions = []
    ante_transactions = []
    for tr in transactions:
        bgp = []
        web = []
        for item in tr:
            if 'www' in item:
                web.append(item)
            else:
                bgp.append(item)

        if len(bgp) > 0:
            for e in web:
                cons_transactions.append(bgp + [e])
            ante_transactions.append(bgp)

    cons_result = []
    for itemset, support in modified_fpg(cons_transactions, minsupp, True):
        cons_result.append((itemset,support))

    ante_result = []
    for itemset, support in orginal_fpg(ante_transactions, minsupp, True):
        ante_result.append((itemset,support))

    # result = sorted(result, key=lambda i: i[0])
    # for itemset, support in result:
    #     print str(itemset) + ' ' + str(support)

    return cons_result, ante_result

def gen_rules(cons_fp, ante_fp, mincof):
    supp_dict = {}
    for fp in cons_fp:
        supp_dict[frozenset(fp[0])] = fp[1]

    for fp in ante_fp:
        supp_dict[frozenset(fp[0])] = fp[1]

    # supp_file = open('supp.json', 'w')
    # supp_file.write(json.dumps([{'itemset': list(iset), 'supp': supp_dict[iset]} for iset in supp_dict]))
    # supp_file.close()
    rules = []
    for fp in cons_fp:
        for item in fp[0]:
            if 'www' in item:
                consequent = item
                break
        antecedent = frozenset(fp[0]) - frozenset([item])
        conf = float(supp_dict[frozenset(fp[0])]) / float(supp_dict[antecedent])
        if conf >= mincof:            
            rules.append([str(list(antecedent)), consequent, supp_dict[frozenset(fp[0])], conf]) 
    rules.sort(key=lambda r: r[2], reverse=True)
    for r in rules:
        print r[0], '===>', r[1], (r[2], r[3])


def main(minsupp=8, minconf=0.8):
    db = load_data()

    starttime = datetime.now()
    print 'begin fpg %s' % starttime.isoformat()

    cons_fp, ante_fp = fpg(db, minsupp)

    endtime = datetime.now()
    print 'done fpg %s' % endtime.isoformat()
    print endtime - starttime

    rules = gen_rules(cons_fp, ante_fp, minconf)
    
    endtime = datetime.now()
    print 'done generate rules %s' % endtime.isoformat()
    print endtime - starttime

def analysis_test(minsupp, minconf):
    transactions = load_data()
    starttime = datetime.now()
    print 'begin fpg %s' % starttime.isoformat()
    fp = []
    for itemset, support in orginal_fpg(transactions, minsupp, True):
        fp.append((itemset,support))

    fp = sorted(fp, key=lambda i: i[0])
    association_rules(pd.DataFrame(fp, columns=['itemsets', 'support']), metric="confidence", min_threshold=minconf)
    endtime = datetime.now()
    print 'done fpg %s' % endtime.isoformat()
    print endtime - starttime


def pyfim_test(minsupp=-8, minconf=80, prun=False):
    from fim import fpgrowth
    transactions = load_data()
    appear = {}
    for tr in transactions:
        for item in tr:
            if 'www' in item:
                appear[item] = 'cons'
            else:
                appear[item] = 'ante'
    
    starttime = datetime.now()
    print 'begin pyfim fpg %s' % starttime.isoformat()
    rules = fpgrowth(transactions, target='r', supp=minsupp, conf=minconf, appear=(appear if prun else {}), report='sc')
    endtime = datetime.now()
    print 'done pyfim fpg %s' % endtime.isoformat()
    print endtime - starttime

    rules.sort(key=lambda r: r[2], reverse=True)
    for r in rules:
        print r[1], '===>', r[0], (r[2], r[3])

def supp_test():
    f = open('supp.json', 'r')
    supp_data = json.loads(f.read())
    supp_dict = {}
    for d in supp_data:
        supp_dict[frozenset(d['itemset'])] = d['supp']

    ante = frozenset((u'24138', u'4538'))
    cons = frozenset([u'www.mama.cn'])
    rule = ante | cons
    print supp_dict[rule], supp_dict[ante], float(supp_dict[rule])/float(supp_dict[ante])

def db_test():
    with open('examples/db.json') as f:
        data = json.loads(f.read())
        itemset = [u'4538', u'4809', u'4812']
        count = 0
        time_series = sorted(data.keys())
        for tid in time_series:
            tr = data[tid]
            flag = True
            for item in itemset:
                if item not in tr:
                    flag = False
                    break
            if flag:
                print tid
                count += 1
        print count

def fpg_comparison():
    db = load_data()
    minsupp = len(db) * 0.01
    minconf = 0.8
    print 'orignal fpg start'
    analysis_test(minsupp, minconf)

    print '\nmodified fpg start'
    main(minsupp, minconf)



if __name__ == '__main__':
    # main()
    # test()
    pyfim_test(1, prun=False)
    # supp_test()
    # db_test()
    # fpg_comparison()
#coding=utf8
import json
import pandas as pd
from datetime import datetime
from fp_growth_modified import find_frequent_itemsets as modified_fpg
from fp_growth import find_frequent_itemsets as orginal_fpg
from mlxtend.frequent_patterns import association_rules

def load_data(test_data=None):
    if test_data:
        with open('examples/' + test_data) as f:
            data = {}
            l = f.readline()
            while l:
                d = l[:-1].split(' ') #删除换行符后分割
                if data.get(d[0]) is None:
                    data[d[0]] = []
                data[d[0]].append(d[1])
                l = f.readline()
            transactions = [data[tid] for tid in data]
            return transactions

    else:
        with open('examples/db.json') as f:
            data = json.loads(f.read())
            transactions = [data[tid] for tid in data]
            return transactions

def pcfpg(transactions, minsupp, getPos): 
    cons_transactions = []
    ante_transactions = []
    for tr in transactions:
        ante = []
        cons = []
        for item in tr:
            if getPos(item) == 'cons':
                cons.append(item)
            else:
                ante.append(item)

        if len(ante) > 0:
            for e in cons:
                cons_transactions.append(ante + [e])
            ante_transactions.append(ante)
 
    cons_result = []
    for itemset, support in modified_fpg(cons_transactions, minsupp, getPos, True):
        cons_result.append((itemset,support))
    # print cons_result
    ante_result = []
    for itemset, support in orginal_fpg(ante_transactions, minsupp, True):
        ante_result.append((itemset,support))

    # result = sorted(result, key=lambda i: i[0])
    # for itemset, support in result:
    #     print str(itemset) + ' ' + str(support)

    return cons_result, ante_result

def gen_rules(cons_fp, ante_fp, mincof, getPos):
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
            if getPos(item) == 'cons':
                consequent = item
                break
        antecedent = frozenset(fp[0]) - frozenset([item])
        conf = float(supp_dict[frozenset(fp[0])]) / float(supp_dict[antecedent])
        if conf >= mincof:            
            rules.append([list(antecedent), consequent, supp_dict[frozenset(fp[0])], conf]) 
    # rules.sort(key=lambda r: r[2], reverse=True)

    rules.sort(key=lambda r: len(r[0]), reverse=True)
    v_rules = []
    for r in rules:
        flag = False
        # for vr in v_rules:
        #     if r[1] == vr[1] and set(vr[0]) > set(r[0]):
        #         flag = True
        #         break

        if flag:
            continue
        v_rules.append(r)
    rules = v_rules
    rules.sort(key=lambda r: r[3], reverse=True)
    for r in rules:
        print r[0], '===>', r[1], (r[2], r[3])
    print 'rules', len(rules)
    return rules


def main(minsupp=8, minconf=0.8):
    db = load_data()

    starttime = datetime.now()
    print 'begin fpg %s' % starttime.isoformat()

    cons_fp, ante_fp = pcfpg(db, minsupp, lambda item: 'cons' if 'www' in item else 'ante')

    endtime = datetime.now()
    print 'done fpg %s' % endtime.isoformat()
    print endtime - starttime

    rules = gen_rules(cons_fp, ante_fp, minconf, lambda item: 'cons' if 'www' in item else 'ante')
    
    endtime = datetime.now()
    print 'done generate rules %s' % endtime.isoformat()
    print endtime - starttime

def pcfpg_test():
    db = load_data('D20T4I4.txt')
    minsupp = 30
    minconf = .8
    starttime = datetime.now()
    print 'begin pcfpg %s' % starttime.isoformat()

    cons_fp, ante_fp = pcfpg(db, minsupp, lambda item: 'cons' if int(item) > 300 else 'ante')

    endtime = datetime.now()
    print 'done pcfpg %s' % endtime.isoformat()
    print endtime - starttime
    print 'cons_fp:', len(cons_fp), 'ante_fp', len(ante_fp)

    rules = gen_rules(cons_fp, ante_fp, minconf, lambda item: 'cons' if int(item) > 300 else 'ante')
    
    endtime = datetime.now()
    print 'done generate rules %s' % endtime.isoformat()
    print endtime - starttime
    return rules


def analysis_test(minsupp=-8, minconf=0.8, dataset=None):
    transactions = load_data(dataset)
    starttime = datetime.now()
    print 'begin fpg %s' % starttime.isoformat()
    fp = []
    for itemset, support in orginal_fpg(transactions, minsupp, True):
        fp.append((itemset, float(support)))

    fp = sorted(fp, key=lambda i: i[0])

    print 'fp:', len(fp), datetime.now().isoformat()
    rules = association_rules(pd.DataFrame(fp, columns=['itemsets', 'support']), metric="confidence", min_threshold=0.8)


    def getPos(item):
        return 'cons' if int(item) > 300 else 'ante'

    v_rules = []
    for i in range(len(rules['antecedants'])):
        flag = False
        if len(rules['consequents'][i]) > 1:
            continue
        for ante in rules['antecedants'][i]:
            if getPos(ante) != 'ante':
                flag = True
                break
        if flag:
            continue

        for cons in rules['consequents'][i]:
            if getPos(cons) != 'cons':
                flag = True
                break
        if flag:
            continue       

        v_rules.append([rules['antecedants'][i], rules['consequents'][i], rules['support'][i], rules['confidence'][i]])
        # v_rules.append([rules['antecedants'][i],  '===>', rules['consequents'][i]])
        print rules['antecedants'][i], rules['consequents'][i], rules['support'][i], rules['confidence'][i]
 

    print 'rules',len(v_rules)
    endtime = datetime.now()
    print 'done fpg %s' % endtime.isoformat()
    # print 'rules', len(rules)
    print endtime - starttime
    return v_rules

def test():
    # r_pcfpg = pcfpg_test()
    # r_origin = analysis_test(minsupp=10,dataset='D20T4I4.txt')
    r_pcfpg = analysis_test(minsupp=10,dataset='D20T4I4.txt')
    r_origin = pcfpg_test()
    for r in r_pcfpg:
        flag = False
        for o in r_origin:
            if frozenset(r[0]) == frozenset(o[0]) and frozenset(r[1]) == frozenset(o[1]):
                flag = True
                break
        if flag:
            continue
        print r


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
    # pyfim_test(1, prun=False)
    # supp_test()
    # db_test()
    # fpg_comparison()
    pcfpg_test()
    # analysis_test(minsupp=30,dataset='D20T4I4.txt')
    # analysis_test(minsupp=15)
    # test()
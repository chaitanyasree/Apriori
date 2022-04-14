from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from itertools import combinations


app = Flask(__name__)
app = Flask(__name__, template_folder='./templates')

app.config["UPLOAD_FOLDER"] = "static/"

from itertools import chain, combinations
import sys

def find_frequent_itemsets(item_set, transactions_list, min_sup):
    candidate_set = set()
    candidate_list = list(item_set)
    
    for item in candidate_list:
        count = 0
        for transaction in transactions_list:
            if item.issubset(transaction):
                count += 1       
        
        if(count >= min_sup): 
            candidate_set.add(item)

    return candidate_set

def  has_infrequent_subset(filtered_items,transactions_list,min_sup):
    frequent_items = set()
    for fitem in filtered_items:
        frequent_items.add(fitem)

    size = 2

    while (len(filtered_items) != 0):    

        candidate_items = set([i.union(j) for i in filtered_items for j in filtered_items if len(i.union(j)) == size])
        
        new_candidate_set = set()
        for candidate in candidate_items:
            subSets = set([frozenset(list(x)) for x in list(chain.from_iterable(combinations(candidate, r) for r in range(size-1, size)))])
            areAllItemsFreq =  all(item in frequent_items for item in subSets)

            if areAllItemsFreq is True:
                new_candidate_set.add(candidate)
                    

        filtered_items = find_frequent_itemsets(new_candidate_set,transactions_list, min_sup)
        
        for candidate in filtered_items:
            subSets = set([frozenset(list(x)) for x in list(chain.from_iterable(combinations(candidate, r) for r in range(size-1, size)))])
            frequent_items.add(candidate)
            frequent_items = frequent_items - subSets
        
        size += 1

    return frequent_items



    

def apriori_gen(file, min_sup):
    items = set()
    transactions_list = []

    for line in file.readlines():
        transaction = line.split(", ")
        key = transaction.pop(0)
        items = items.union(transaction)
        transaction = set([int(x) for x in transaction])
        transaction.add(key+'key')
        transactions_list.append(frozenset(transaction))

    itemSet = set(frozenset([int(item)]) for item in items)

    
    filtered_items = find_frequent_itemsets(itemSet, transactions_list, min_sup)    
    
    
    frequent_items = has_infrequent_subset(filtered_items,transactions_list, min_sup)
    
    returnItem = [set(x) for x in frequent_items]
    return returnItem 


@app.route('/')
def upload_file():
    return render_template('index.html')
	
@app.route('/display', methods = ['GET', 'POST'])
def algorithm():
  if request.method == 'POST':
    f = request.files['file']      
    filename = secure_filename(f.filename)
    f.save(app.config['UPLOAD_FOLDER'] + filename)
    f = open(app.config['UPLOAD_FOLDER']+filename,'r')    
    min_sup = int(request.form["min_sup"])       
    
    output = apriori_gen(f, min_sup)
    return render_template('index1.html',result=output,total_items = len(output))
  return render_template('index.html')

if __name__ == '__main__':
    app.run(debug = True)
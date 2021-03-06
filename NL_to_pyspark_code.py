# -*- coding: utf-8 -*-
"""
Created on Sun Nov 10 01:25:38 2019

@author: User
"""
from nltk.corpus import wordnet 
import pandas as pd
from itertools import product
from fuzzywuzzy import fuzz
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize 
import pycountry
import nltk
import re
from dateutil.parser import parse
from dateparser.search import search_dates


##input inquiry 
example_sent = "What’s the lowest pick in round 1?"

example_sent=example_sent.lower()
## configuring dictionary for the dataframes available with their attributes 
DF_att={"employee":["salary","employee names","department","employee id","manager"],"customer":["customer id","orders","order_id","author","customer names","year","book"],"players":["player name","round","position","nationality","team","pick","school"]}
##configuring mapping Dictionaries and dataframes
mapping_DF = pd.DataFrame(columns=['Select', 'AGG', 'Where',"operator"])
mapping_Dic={"Select":[],"AGG":[],"Where":[],"operator":[],"op_values":[],"between":[]}

## identifying the select statment and removing its input words from the sentence 

SELECT_Dict={}

#extracting select pointers and removing them from sentence
select_list=["calculate","i have","extract","select","look for","what is","give","show","choose","return","look","bring","search","what","what's","what is","find","get","who","want"]
for i in select_list:
    if i in example_sent:
        example_sent = re.sub(i, '', example_sent)
        select_statment = True
        SELECT_Dict[i]="select"

Select_sent=example_sent
##tokenizing the inquiry 
word_tokens = word_tokenize(example_sent) 


# solving ID issue by concating ID to the previous word so as to have best match with our attribute 
for f in range(len(word_tokens)):
    if "ID" == word_tokens[f] or "id" == word_tokens[f] :
        x=word_tokens[f-1] +word_tokens[f]
        example_sent = re.sub(word_tokens[f-1] +" " + word_tokens[f], x, example_sent)
        
word_tokens = word_tokenize(example_sent) 
    
word_tokens_select = word_tokenize(example_sent) 
list_attributes_matched=[]
where_exist=False
#splitting the sentenance into 2 sentences select and where clauses if exist and retokenize them  
Where_list=["have","has","having","during","which","for","from","with","between","lower than","greater than","more than","less than","before","after","at","where","in","When"]

for i in range(len(word_tokens)):
    if word_tokens[i] in Where_list:
        if i == 0:
            m=word_tokens[i] + " "
            splitted_text=example_sent.split(m)
            Select_sent=splitted_text[1]
            word_tokens_select = word_tokenize(splitted_text[1])  

        else:
             m=" " + word_tokens[i] + " "
             splitted_text=example_sent.split(m)
             Select_sent=splitted_text[0]
             Where_sent=splitted_text[1]
             word_tokens_where = word_tokenize(splitted_text[1]) 
             where_exist=True
             word_tokens_select = word_tokenize(splitted_text[0])  
        break

  #check for country names
for country in pycountry.countries:
    if country.name in example_sent:
        print(country.name)
        
stop_words = set(stopwords.words('english')) 
stop_words.discard("in") 
stop_words.discard("before") 
stop_words.discard("after") 
stop_words.discard("is") 
stop_words.discard("from") 
stop_words.discard("where") 
stop_words.discard("which") 
stop_words.discard("whome")
stop_words.discard("above") 
stop_words.discard("'over'") 
stop_words.discard("'at'") 
stop_words.discard("'what'") 
stop_words.add("please")
stop_words.discard("more")
stop_words.discard("below") 
stop_words.discard("between") 
stop_words.add("what is ") 
stop_words.add(",") 
stop_words.add("done")
stop_words.add("?")



 

########## filtering select Clause after removing stop words

  
filtered_sentence_select = [] 

for w in word_tokens_select: 
    if w not in stop_words: 
        filtered_sentence_select.append(w) 
  
print(word_tokens_select) 
print(filtered_sentence_select) 

Df_name=[]

########## tokenizing and filtering Where Clause 
if where_exist:

    filtered_sentence_where = [] 

    for w in word_tokens_where: 
       if w not in stop_words: 
          filtered_sentence_where.append(w) 
  
    print(word_tokens_where) 
    print(filtered_sentence_where)    
    ww= filtered_sentence_where
###matching words with attributes dictionaries for Where statment 
    splitted_attribute_where=[]
    for n in DF_att:
        for i in DF_att[n]:
            Where_attribute_exist=False
            l=" " + i + " "
            Where_sent_with_spaces=" " + Where_sent +" "
            if l in Where_sent_with_spaces:            
                mapping_Dic["Where"].append(i)
                Where_attribute_exist=True
                splitted_attribute_where=i.split(" ")
                for e in splitted_attribute_where:
                    if e in filtered_sentence_where:
                        filtered_sentence_where.remove(e)
        if Where_attribute_exist ==True:
             continue
    
  
    words_matching_dic_where={}
    
    att_Dict_where={}
    for n in DF_att: ## iterating on tables names 
    #print(n)
    #print(DF_att[n])
       for word1, word2 in product(filtered_sentence_where, DF_att[n]):
           Ratio = fuzz.ratio(word1.lower(),word2.lower())
           Partial_Ratio = fuzz.partial_ratio(word1.lower(),word2.lower())
           Token_Sort_Ratio = fuzz.token_sort_ratio(word1,word2)
           Token_Set_Ratio = fuzz.token_set_ratio(word1,word2)
           if Ratio >= 65:
               print(  word1 +" matches with attribute  "+ word2+" with ratio " + str(Ratio) + " in the where clause ")
               list_attributes_matched.append(word2)
               ID_list=[" ID ","_ID"]
               ID_conflict=False
               for d in ID_list: 
                   if d in word2 and d not in word1:
                      ID_conflict=True
                   elif d in word1 and d in word2:
                       mapping_Dic["Where"].append(word2)
                      # Df_name.append(n)
                       
               if ID_conflict==True:
                   continue
               if word1 in words_matching_dic_where:
                     if Ratio > words_matching_dic_where[word1][1]:
                         words_matching_dic_where[word1]=[word2,Ratio]
               elif word2 in att_Dict_where :
                    if Ratio > att_Dict_where[word2][1]:
                        word1_old=att_Dict_where[word2][0]
                        att_Dict_where[word2]=[word1,Ratio]
                        del words_matching_dic_where[word1_old]
                        words_matching_dic_where[word1]=[word2,Ratio]
                        

               else:
                     att_Dict_where[word2]=[word1,Ratio]
                     words_matching_dic_where[word1]=[word2,Ratio]


                  
       for k in  words_matching_dic_where:
            mapping_Dic["Where"].append(words_matching_dic_where[k][0])
                #Df_name.append(n)
           
            
    
            


               
              
#matching  attributes synonyms for Where
    sims_=[]
    for n in DF_att: ## iterating on tables names 
     for word1, word2 in product(filtered_sentence_where, DF_att[n]):
        syns1 = wordnet.synsets(word1)
        syns2 = wordnet.synsets(word2)
        for sense1, sense2 in product(syns1, syns2):
           d= wordnet.wup_similarity(sense1, sense2)
           sims_.append((d, word1, word2))
           if d != None:
               if d > 0.91:
                   print(d,word1,word2)              
                   mapping_Dic["Where"].append(word2)
                   words_matching_dic_where[word1]=[word2,d]
                  # Df_name.append(n)
#remove duplicate from where attributes 

    mapping_Dic["Where"] = list(dict.fromkeys(mapping_Dic["Where"]))
    
    

##checking words in a stop_words set or not 
#if  "after" in stop_words:
 #    print("yes")
#else :
 #   print("NO")
 
 


        
##find verbs tags not important now
#tag = nltk.pos_tag(['Google'])  # check on tagging 
#Verbs_list=[]
#sentence = nltk.sent_tokenize(example_sent)
#for sent in sentence:
#    tagger=nltk.pos_tag(nltk.word_tokenize(sent))
    
#for f in range(len(word_tokens_select)):
#    if tagger[f][1] =="VB" or tagger[f][1] =="VBP":
 #       print(tagger[f])
  #      if tagger[f][0] in filtered_sentence_select:
   #         Verbs_list.append(tagger[f][0])
    #        filtered_sentence_select.remove(tagger[f][0])


###matching words with attributes dictionaries for select statment 
words_matching_dic_select={}
select_All=[" all data ","all info","all information"]
selectall=False
for n in DF_att:## iterating on tables names 
    for j in select_All:
       if  j in Select_sent:
         mapping_Dic["Select"].append("*")
         selectall=True
    if selectall ==True:
        break
    
     
    for i in DF_att[n]: 
        select_attribute_exist=False 
        l= i 
        if l in Select_sent:
            mapping_Dic["Select"].append(i)
            select_attribute_exist=True
            splitted_attribute=i.split(" ")
            for e in splitted_attribute:
                if e in filtered_sentence_select:
                     filtered_sentence_select.remove(e)
                
        if select_attribute_exist ==True:
              continue
    
    att_Dict_select={} 
    
       
    #print(n)
    #print(DF_att[n])
    for word1, word2 in product(filtered_sentence_select, DF_att[n]):
        Ratio = fuzz.ratio(word1.lower(),word2.lower())
        Partial_Ratio = fuzz.partial_ratio(word1.lower(),word2.lower())
        Token_Sort_Ratio = fuzz.token_sort_ratio(word1,word2)
        Token_Set_Ratio = fuzz.token_set_ratio(word1,word2)
        if Ratio > 65:
            
              print(  word1 +" matches with attribute  "+ word2+" with ratio " + str(Ratio) + " in the select clause")
              list_attributes_matched.append(word2)
              ID_list=["id"]
              ID_conflict=False 
              for d in ID_list:
                  if d in word2 and d not in word1:
                       ID_conflict=True
                  
                  #elif d in word1 and d in word2:
                      # mapping_Dic["Select"].append(word2)
                     #  print("hi" + word2)
              if ID_conflict==True:
                   continue
              if word1 in words_matching_dic_select:
                  if Ratio > words_matching_dic_select[word1][1]:
                     word2_old=words_matching_dic_select[word1][0]
                     del att_Dict_select[word2_old] 
                     att_Dict_select[word2]=[word1,Ratio]
                     words_matching_dic_select[word1]=[word2,Ratio]
              elif word2 in att_Dict_select:
                  if Ratio > att_Dict_select[word2][1]:  
                      word1_old=att_Dict_select[word2][0]
                      del words_matching_dic_select[word1_old]
                      words_matching_dic_select[word1]=[word2,Ratio] 
                      att_Dict_select[word2]=[word1,Ratio]
              else:
                  att_Dict_select[word2]=[word1,Ratio] 
                  words_matching_dic_select[word1]=[word2,Ratio]
                     
    for k in  words_matching_dic_select:
        mapping_Dic["Select"].append(words_matching_dic_select[k][0])
        if k in filtered_sentence_select:
              filtered_sentence_select.remove(k)
       
        

#matching  attributes synonyms for select
    sims=[]         
    for word1, word2 in product(filtered_sentence_select, DF_att[n]):
        syns1 = wordnet.synsets(word1)
        syns2 = wordnet.synsets(word2)
        for sense1, sense2 in product(syns1, syns2):
           d= wordnet.wup_similarity(sense1, sense2)
           sims.append((d, word1, word2))
           if d != None:
               if d > 0.91:
                  print(d,word1,word2)
                  mapping_Dic["Select"].append(word2)
                #  Df_name.append(n)
                  if word1 in filtered_sentence_select:
                     filtered_sentence_select.remove(word1)

                      
                  
                       
#remove duplicate from Select attributes 

mapping_Dic["Select"] = list(dict.fromkeys(mapping_Dic["Select"]))
#print(list_attributes_matched) 

list_attributes_matched = list(dict.fromkeys(list_attributes_matched))

## removing matched attributes from filtered where sentence 
if where_exist:
    for h in filtered_sentence_where:    
            if h in words_matching_dic_where:
               filtered_sentence_where.remove(h)
               
##removing attributes from filtered select sentence
for h in filtered_sentence_select:    
            if h in words_matching_dic_select:
                filtered_sentence_select.remove(h)
        
agg_Dict={"min":"min"," max ":"max","minimumm":"min","maximum":"max","total number":"count","number":"count","total":"sum","count":"count","least":"min","highest":"max","sum":"sum","mean":"Avg","average":"avg","lowest":"min","avg":"avg"}
for i in agg_Dict:
    if i in example_sent:
         splitted_AGG=i.split(" ")
         filtered_sentence_wh=filtered_sentence_where
         if filtered_sentence_select!=[] or filtered_sentence_where!=[]:
             mapping_Dic["AGG"].append(agg_Dict[i])
         for e in splitted_AGG:
             if e in filtered_sentence_select:
                  filtered_sentence_select.remove(e)
             if e in filtered_sentence_where:
                   filtered_sentence_where.remove(e)
                   
            

         

        
operator_Dic={"with names":"=","named":"=","before":"<","after":">","since":">","greater than":">","less than" : "<","more than": ">","lower than":"<","equal":"=","equals":"=","=":"="," is in ":"=","is":"="," in ":"=","are":"=","during":"="}
previous_word=""
for i in operator_Dic:
    if i in previous_word:
        continue
    if i in example_sent:      
        count_op=example_sent.count(i)
        for c in range(count_op):
            mapping_Dic["operator"].append(operator_Dic[i])   
            splitted_operator=i.split(" ")
        for e in splitted_operator:
               if where_exist:
                  if e in filtered_sentence_where:
                     filtered_sentence_where.remove(e) 
               elif e in filtered_sentence_select:
                   filtered_sentence_select.remove(e)
        previous_word=i

Ranges_Dic=["between" , "from"]
for i in Ranges_Dic:
    if i in example_sent:
        if i == "between":
            if "and" in Where_sent:
                mapping_Dic["between"]=filtered_sentence_where
        elif i == "from":
            if "to" in Where_sent:
                mapping_Dic["between"]=filtered_sentence_where     
        
        
                   
                      
if where_exist:

     mapping_Dic["op_values"]=filtered_sentence_where
else:
    mapping_Dic["op_values"]=filtered_sentence_select

print(mapping_Dic["Where"])

  
      
if mapping_Dic["operator"]==[]:
   if mapping_Dic["Where"]!=[]:
     if mapping_Dic["op_values"] != []:
        mapping_Dic["operator"]=["="]
        
if mapping_Dic["Select"]==[]:
   if mapping_Dic["Where"]!=[]:
     if mapping_Dic["op_values"] != []:
       if mapping_Dic["operator"]!=[]:    
           mapping_Dic["Select"]=mapping_Dic["Where"]   
           
if mapping_Dic["Select"]!=[]:
   if mapping_Dic["Where"]!=[]:
     if mapping_Dic["op_values"] == []:
       if mapping_Dic["operator"]==[]:
           if mapping_Dic["between"]==[]:
                mapping_Dic["Select"].append(mapping_Dic["Where"][0])
                mapping_Dic["Where"]=[]
           
if mapping_Dic["Select"]!=[]:
   if mapping_Dic["Where"]==[]:
       if mapping_Dic["operator"]==[]:
               mapping_Dic["op_values"] = []
# searching for years in my sentence 
#if mapping_Dic["between"]!=[]:           
   # if search_dates(mapping_Dic["between"][0]):
    #      mapping_Dic["Where"]=["year"]

## checking on numbers
def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)


if mapping_Dic["op_values"]!=[]:
   # if len(mapping_Dic["op_values"])!=len(mapping_Dic["Where"]):
        for x in mapping_Dic["op_values"]:
              if search_dates(x): 
                  if hasNumbers(x):
                      y = int(x)
                      if y > 1950 and y < 2020:
                          mapping_Dic["Where"]=["year"]
                   #mapping_Dic["Where"].append("year")
                      
                   
if mapping_Dic["between"]!=[]:
        for x in mapping_Dic["between"]:
              if search_dates(x):  
                  if hasNumbers(x):
                      y = int(x)
                      if y > 1950 and y <2020:
                          mapping_Dic["Where"]=["year"]
                          
                      
                
if mapping_Dic["Where"]==[]:
    if mapping_Dic["op_values"] != []:
        if mapping_Dic["operator"] != []:
            mapping_Dic["Where"]=mapping_Dic["Select"]    
            
   ##merging the strings found in op_values if the where fields are less than op_value fields (example operating values have names)         
if len(mapping_Dic["op_values"])>len(mapping_Dic["Where"]):
    if  "and" not in Where_sent:
        #m=len(mapping_Dic["op_values"])-len(mapping_Dic["Where"]) 
        mapping_Dic["op_values"]=[' '.join(mapping_Dic["op_values"])]
        
        
for r in mapping_Dic["Select"]:
    for n in DF_att:
        if r in DF_att[n]:
            Df_name.append(n)
            
for r in mapping_Dic["Where"]:
    for n in DF_att:
        if r in DF_att[n]:
            Df_name.append(n)            
    
    
    
    
Df_name=list(dict.fromkeys(Df_name))   
if len(Df_name) > 1:
    print ("error: attributes are from different tables" )

print(mapping_Dic)

## generating the query
if mapping_Dic["Select"] != [] and len(Df_name) == 1:
    if mapping_Dic["AGG"] != []:
        output_query= Df_name[0] + ".selectExpr('"  + mapping_Dic["AGG"][0] +"("+ mapping_Dic["Select"][0] + ")')"
    else:
        output_query= Df_name[0] + ".select('"  + mapping_Dic["Select"][0]
        for c in range(len(mapping_Dic["Select"])):
            if c !=0:
                output_query= output_query + "','"  + mapping_Dic["Select"][c] 
        output_query=output_query+"')"
    if mapping_Dic["between"]!=[]:
         output_query=output_query + ".where('" + mapping_Dic["Where"][0]+"').between("+ mapping_Dic["between"][0]+","+ mapping_Dic["between"][1] +")"
    if mapping_Dic["Where"]!=[] and mapping_Dic["between"]==[]:
         output_query=output_query + ".where('" + mapping_Dic["Where"][0]+"'"+ mapping_Dic["operator"][0] +"'"+mapping_Dic["op_values"][0]+"')"
        
    

print("output info are:")
 
print(mapping_Dic)
print(output_query)

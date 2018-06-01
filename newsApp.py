import requests
import sys
import os
import json
from watson_developer_cloud import DiscoveryV1
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, json, jsonify




app = Flask(__name__)

username = "55661b79-fa4c-4657-901a-d8ccefca3e89"
    #os.environ.get('USERNAME', None)
password = "mqOz5JbOZaGQ"
    #os.environ.get('PASSWORD', None)
environment_id ="d3755050-a1c6-4cdb-a480-3bc1df719e7d"
    #os.environ.get('ENVIRONMENT_ID', None)
collection_id = "c8117070-40cb-44b1-bb6c-29fac8f620d6"
    #os.environ.get('COLLECTION_ID', None)
endpoint = "https://gateway.watsonplatform.net/discovery/api/v1/environments/"+environment_id+"/collections/"+collection_id+"/query?version=2017-11-07&"


def discovery(keyword):

    global resultados_query
    discovery = DiscoveryV1(
        version="2018-03-05",
        username="55661b79-fa4c-4657-901a-d8ccefca3e89",
        password="mqOz5JbOZaGQ",
        url = 'https://gateway.watsonplatform.net/discovery/api'
    )

    my_query = discovery.query(environment_id='d3755050-a1c6-4cdb-a480-3bc1df719e7d', collection_id='c8117070-40cb-44b1-bb6c-29fac8f620d6', query=keyword)#, filter='enrichedTitle.entities.type:Person', aggregation='nested(enrichedTitle.entities)')
                               #, return_fields='{return_fields}')
    #result=json.dumps(my_query, indent=2)
    resultados_query=my_query['results']

    docs=[]
    for article in resultados_query:
        docs.append(article['extracted_metadata']['filename'])

    return(docs)

def discovery_entities(text):

    entities=[]
    textos=[]
    count=0


    for entitie in resultados_query:
        entities.append(entitie['enriched_text']['entities'][count])
        count+1
        for enti in entities:
            if enti['count']>3:
                if enti['text'] in textos | enti['text'] in text:
                    continue
                else:
                    textos.append(enti['text'])

    return(textos)


@app.route('/')
def error():
    
    return "Please specify a search term in your URL"

@app.route('/newHeadlines', methods=['POST'])
def newHeadlines():
    combo = request.json['combo']
    comboWords=combo.replace("\"","").split('|')

    combos=[]
    headlines={}
    
    
    try:
        get_url = endpoint+"query=title:("+combo+")|enrichedTitle.entities.text:("+combo+")&count=50&return=title,url"
        results2 = requests.get(url=get_url, auth=(username, password))
        response = results2.json()

    
        for article in response['results']:
            combos[:]=[]
            for word in comboWords:
                if word.upper() in article['title'].upper():
                    combos.append(word)
            comboStr = ''.join(sorted(combos))
            comboLen = len(combos)
            if comboLen not in headlines:
                headlines[comboLen]={}
            if comboStr not in headlines[comboLen]:
                headlines[comboLen][comboStr]={}
            headlines[comboLen][comboStr][article['title']]=article['url']

            
    except Exception as e:
        print(e)
    output = { 'headlines': headlines }  
    return jsonify(output)

@app.route('/click', methods=['GET', 'POST'])
def click():

    nodes=request.json['nodes']
    links=request.json['links']
    bigWords=request.json['bigWords']
    index=request.json['current']
    #wordList=request.json['wordList']
    
    x = nodes[index]['x']
    y = nodes[index]['y']
    text = nodes[index]['text']

    length = len(nodes)
    words={}
    headlines={}
    combo=""
    comboWords=[]
    combos=[]
    for node in nodes:
        words[node['text']] = node['index']
        if node['expand'] == 1:
            comboWords.append(node['text'])
    for word in comboWords:
        combo+="\""+word+"\"|"
    combo=combo[:-1]

    try:
    #    get_url = endpoint+"query=title:("+combo+")|enrichedTitle.entities.text:("+combo+")&count=50&return=title,url"
    #    results = requests.get(url=get_url, auth=(username, password))
    #    response = results.json()

    
        for article in resultados_query['results']:
            combos[:]=[]
            for word in comboWords:
                if word.upper() in article['title'].upper():
                    combos.append(word)
            comboStr = ''.join(sorted(combos))
            comboLen = len(combos)
            if comboLen not in headlines:
                headlines[comboLen]={}
            if comboStr not in headlines[comboLen]:
                headlines[comboLen][comboStr]={}
            headlines[comboLen][comboStr][article['title']]=article['url']

    except Exception as e:
        print(e)
    
    output = { 'results': { 'nodes': [], 'links': [], 'headlines': headlines, 'combo': combo } }

    try:
        #get_url = endpoint+"query=title:\""+text+"\"&aggregation=nested(enrichedTitle.entities).filter(enrichedTitle.entities.type:Person).term(enrichedTitle.entities.text,count:100)&count=0"
        #results = requests.get(url=get_url, auth=(username, password))
        #response=results.json()
        
        #add to bigWords
        wordList = discovery_entities(text)
        output['results']['links'].append({'source':index,'target':text})
        for entity in wordList:

            output['results']['nodes'].append({'x': x, 'y': y, 'text': entity, 'size': 1.5, 'color': 'white', 'expand': 0})
            output['results']['links'].append({'source':length,'target':index})
            length+=1
            #count1+=1

                    
    except Exception as e:
        print(e) 
                
    return jsonify(output)

@app.route('/favicon.ico')
def favicon():
   return ""


@app.route('/<keyword>')
def news_page(keyword):
    index=0
    nodes=[]
    links=[]
    headlines={}
    headlines[1]={}
    headlines[1][keyword]={}
    
    bigWords={}
    
    #try:
     #   get_url = endpoint+"query=title:("+keyword+")|enrichedTitle.entities.text:("+keyword+")&count=50&return=title,url"
      #  results = requests.get(url=get_url, auth=(username, password))
       # response = results.json()
    
        #for article in response['results']:
         #   headlines[1][keyword][article['title']]=article['url']
            

    #except Exception as e:
     #   print(e)
 
    try:
        #get_url = endpoint+"query=title:\""+keyword+"\"&aggregation=nested(enrichedTitle.entities).filter(enrichedTitle.entities.type:Person).term(enrichedTitle.entities.text,count:100)&count=0"
        #results = requests.get(url=get_url, auth=(username, password))
        #response=results.json()

        #add to bigWords
        wordList = discovery(keyword)
        #for kword in response['aggregations'][0]['aggregations'][0]['aggregations'][0]['results']:
         #   wordList.append(kword['key'])
        #bigWords[keyword]={'wordList':wordList,'expand':1}
        count=0
        nodes.insert(0, {'x': 300, 'y': 200, 'text': keyword, 'size': 3, 'fixed': 1, 'color': '#0066FF', 'expand': 1})
        for word in wordList: #bigWords[keyword]['wordList']:
            if count > 10:
                break
            if word == keyword:
                continue
            else:
                nodes.append({'x': 300, 'y': 200, 'text': word, 'size': 1.5, 'color': 'white', 'expand': 0})
                links.append({'source':count + 1,'target':0})
                count+=1

    except Exception as e:
        print(e)
 

                   
    return render_template('cloud.html', nodes=json.dumps(nodes), links=json.dumps(links), bigWords=json.dumps(bigWords), headlines=json.dumps(headlines))

port = os.getenv('VCAP_APP_PORT', '8000')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(port), debug=True)


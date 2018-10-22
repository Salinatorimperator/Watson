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


    textos=[]
    for article in resultados_query:
        if text in article['extracted_metadata']['filename']:
            for entity in article['enriched_text']['entities']:
                    if entity['count']>3:
                        if entity['text'] in textos:
                            continue
                        else:
                            if entity['text']+".pdf" not in text:
                                textos.append(entity['text'])

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
    #bigWords=request.json['bigWords']
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
        print(wordList)
        #output['results']['links'].append({'source':index,'target':text})

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






















 for kword in response['aggregations'][0]['aggregations'][0]['aggregations'][0]['results']:
        wordList.append(kword['key'])
        bigWords[text]={'wordList':wordList,'expand':1}
        output['results']['bigWords']=bigWords
        count1=0
        count2=0

        for newWord in wordList:         #bigWords[text]['wordList']:
            if newWord in words:
                    output['results']['links'].append({'source':index,'target':words[newWord]})
                    continue
            if count2 < 5:
                for bigWord in bigWords:
                    if bigWords[bigWord]['expand']==0:
                        continue
                    if bigWord == text:
                        continue
                    if newWord in bigWords[bigWord]['wordList']:
                        if newWord not in words:
                            output['results']['nodes'].append({'x': x, 'y': y, 'text': newWord, 'size': 1.5, 'color': 'white', 'expand': 0})
                            words[newWord]=length
                            length+=1
                            count2+=1
                        output['results']['links'].append({'source':words[newWord],'target':words[bigWord]})
                        output['results']['links'].append({'source':words[newWord],'target':index})
            if newWord not in words and count1 < 5:
                output['results']['nodes'].append({'x': x, 'y': y, 'text': newWord, 'size': 1.5, 'color': 'white', 'expand': 0})
                output['results']['links'].append({'source':length,'target':index})
                length+=1
                count1+=1





function grabHeadlines(d) {

  console.log(combo)
  var delWord = d.text
  console.log(delWord)
  if (combo.indexOf(delWord) == 1) {
  	combo = combo.replace('"'+delWord+'"|','')
  }
  else {
  	combo = combo.replace('|"'+delWord+'"','')
  }
  console.log(combo)
$.ajax
  ({
      type: "POST",
      url: "{{ url_for('newHeadlines') }}",
      contentType: 'application/json',
      dataType: 'json',
      data: JSON.stringify({'combo': combo}),
      success: function(data) {
	  	headlines = data.headlines;
  	  	loadHeadlines();
  		}
  });

}



function loadHeadlines() {
    $(".titles").empty();
    for (var fcount=fixedCount; fcount>0; fcount--) {
        console.log(fcount)
        if (fcount in headlines) {
            for (var c in headlines[fcount]) {
                for (var h in headlines[fcount][c]) {
                    $(".titles").append('<a href="'+headlines[fcount][c][h] +'" target="_blank">'+ h + '<hr>')
                }
            }
         }
    }
}




df2 = pd.read_csv("air_reserve.csv")
df2 = pd.read_csv("store_id_relation.csv")
merged = df1.merge(df2, on="hpg_store_id", how="outer").fillna("-")
merged.to_csv("merged2.csv", index=False)


#esto para eliminar columnsa
df1.drop(columns=['hpg_store_id'])

#esto para eliminar filas cuando cumplen la condicion, en este caso que air_store_id = -
df1 = df1.drop(df1[df1.air_store_id == '-'].index)

#esto para crear un nuevo csv solo con esas variables, aunque si quitas la primera columna, te crea una columna con ids automatico
df1=df1[["air_store_id","visit_datetime","reserve_datetime","reserve_visitors"]]

#esto para unir un csv al final, al air_reserve uno el df1, que en este caso era el anterior
with open('air_reserve.csv', 'a') as f:
             df1.to_csv(f, header=False)


#en la 43 de layout, despues detodo
{% block body %}{% endblock %}




#del cloud.html despues de div class graph y antes de script

<div class=headlines>

    <div style="display:none" id="view-change-button" class="button" onclick="PayloadPanel.togglePanel(event, this)">
    <img class="option full" src="../img/Chat Button.png">
    <img class="option not-full" src="../img/Code Button.png">
    </div>
  <div id="contentParent" class="responsive-columns-wrapper">

    <div id="chat-column-holder" class="responsive-column content-column">
      <div class="chat-column">
        <div id="scrollingChat"></div>
        <label for="textInput" class="inputOutline">
          <input id="textInput" class="input responsive-column"
                 placeholder="Type something" type="text"
                 onkeydown="ConversationPanel.inputKeyDown(event, this)">
        </label>
      </div>
    </div>
    <div style="display:none"  id="payload-column" class="fixed-column content-column">
      <div id="payload-initial-message">
        Type something to see the output
      </div>
      <div id="payload-request" class="payload"></div>
      <div id="payload-response" class="payload"></div>
    </div>
  </div>

</div>


#cloud.html al principio

{% extends "layout.html" %}
{% block body %}

#al final
{% endblock %}




# $('id').keyup(function(){
    funcion()
 }

#$(document).ready# $('id').keyup(function(){
    funcion()
 }

#$(document).ready




   <script>
    $(document).ready(function(){
      $('.buscador').on(function(){
         var val1 = $("#id_query").val();
         $.ajax({
          url: "/search",
          type: "get",
          data: {val1: val1},
          success: function(response) {
             $(".graph").html('<p>hola</p>');
          },
         });
      });
    });
   </script>



keyword=request.form['query']




<input type="button" onclick="window.location.href='/search'>
<button type="submit" form='buscador_1' value="Submit"></button>




#al final del render template : headlines=json.dumps(headlines)

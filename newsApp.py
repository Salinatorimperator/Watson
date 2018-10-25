import requests
import sys
import os
import json
from watson_developer_cloud import DiscoveryV1, ConversationV1
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, json, jsonify
import flask_sijax
import webbrowser



path = os.path.join('.', os.path.dirname(__file__), 'static/js/sijax/')

creds_assist=json.load(open("credenciales", "r"))


app = Flask(__name__)
app.config['SIJAX_STATIC_PATH'] = path
app.config['SIJAX_JSON_URI'] = '/static/js/sijax/json2.js'
flask_sijax.Sijax(app)

discovery_v1 = DiscoveryV1(
    version="2018-08-01",
    username="55661b79-fa4c-4657-901a-d8ccefca3e89",
    password="mqOz5JbOZaGQ",
    url = 'https://gateway.watsonplatform.net/discovery/api'
)



wall_e = ConversationV1(
    version="2017-05-26",
    url=creds_assist['conversation']['url'],
    username=creds_assist['conversation']['username'],
    password=creds_assist['conversation']['password']

)

def discovery_docs(keyword):

    global resultados_query


    my_query = discovery_v1.query(environment_id='868d81c4-735d-40f3-94ad-10cd4f304b43', collection_id='f876ed4e-5f13-4bfb-bf63-c105910d0e17', query=keyword)#, filter='enrichedTitle.entities.type:Person', aggregation='nested(enrichedTitle.entities)')

    resultados_query=my_query['results']

    docs=[]
    for article in resultados_query:
        docs.append(article['extracted_metadata']['filename'])

    return(docs)

def discovery_assistant(keyword):


    my_query_assist = discovery_v1.query(environment_id='868d81c4-735d-40f3-94ad-10cd4f304b43', collection_id='f876ed4e-5f13-4bfb-bf63-c105910d0e17', query=keyword)#, filter='enrichedTitle.entities.type:Person', aggregation='nested(enrichedTitle.entities)')

    result_query=my_query_assist['results']

    #print(json.dumps(result_query,indent=2))
    response=[]
    for article in resultados_query:
        response.append(article['extracted_metadata']['filename'])

    return(response)



def discovery_entities(text):


    textos=[]
    for article in resultados_query:
        if text in article['extracted_metadata']['filename']:
            for entity in article['enriched_text']['entities']:
                if entity['count']>2:
                    if entity['text'] in textos:
                        continue
                    else:
                        if entity['text']+".pdf" not in text:
                            textos.append(entity['text'])

    return(textos)

#cambiar al metodo de keyword
#@app.route('/')
#def error():

    #return "Please specify a search term in your URL"


@app.route('/api/message', methods=['POST'])
def get_message():

    user_input = json.loads(request.data.decode("utf-8"))
    if "input" in user_input:
        user_text = user_input['input']
    else:
        user_text = {"text" : ""}
    if "context" in user_input:
        user_context = user_input['context']
    else:
        user_context = {}

    wall_e_response = wall_e.message(creds_assist['conversation']['workspace_id'],input=user_text, context=user_context)


    if "discovery" in wall_e_response['context']:
        texto_discovery=wall_e_response['input']['text']

        query_assistant = discovery_v1.query(environment_id='868d81c4-735d-40f3-94ad-10cd4f304b43', collection_id='f876ed4e-5f13-4bfb-bf63-c105910d0e17', natural_language_query=texto_discovery, passages='true', passages_count=1, deduplicate='false', highlight='true')#, filter='enrichedTitle.entities.type:Person', aggregation='nested(enrichedTitle.entities)')

        for passage in query_assistant['passages']:

            wall_e_response['output']['text']=passage['passage_text']
            del wall_e_response['context']['discovery']
            print(wall_e_response)
            return json.dumps(wall_e_response)
    # print(wall_e_response)
    return json.dumps(wall_e_response)





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

        #add to bigWords
        wordList = discovery_entities(text)
        #print(text)
        #output['results']['links'].append({'source':index,'target':text})

        for entity in wordList:

            output['results']['nodes'].append({'x': x, 'y': y, 'text': entity, 'size': 1.5, 'color': 'white', 'expand': 0})
            output['results']['links'].append({'source':length,'target':index})
            length+=1


    except Exception as e:
        print(e)
    webbrowser.open_new_tab('https://www.comillas.edu/es/noticias-catedra-industria-conectada/17218-francisco-j-riberas-director-general-de-gestamp-en-el-ciclo-desayunos-cic')
    return jsonify(output)

@app.route('/favicon.ico')
def favicon():
   return ""




@app.route('/', methods=['GET','POST'])
def home():


    #if request.method == 'POST':
        #keyword=request.form['query']
        #print(keyword)
    #return render_template('layout.html'nodes=json.dumps(nodes), links=json.dumps(links), bigWords=json.dumps(bigWords), headlines=json.dumps(headlines))

#@app.route('/search', methods=['GET','POST'])
#def news_page():

    #keyword = Flask.request.args.get('val1')
    keyword=''
    wordList=""
    nodes=[]
    links=[]
    headlines={}
    headlines[1]={}
    headlines[1][keyword]={}
    #print(request.method)

    if request.method == 'POST':
        keyword=request.form['query']
        #keyword = Flask.request.args.get('val1')
        index=0
        #print(keyword)


        bigWords={}

        try:


            #add to bigWords

            wordList = discovery_docs(keyword)
            #print(wordList)
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


        #print(json.dumps(nodes))
        return render_template('layout.html', nodes=json.dumps(nodes), links=json.dumps(links), bigWords=json.dumps(wordList))
        #return Flask.jsonify({"graph":wordList})


    #wordList = discovery_docs(keyword)
    #return render_template('layout.html')
    return render_template('layout.html', nodes=json.dumps(nodes), links=json.dumps(links), bigWords=json.dumps(wordList))

port = os.getenv('VCAP_APP_PORT', '8000')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(port), debug=True)


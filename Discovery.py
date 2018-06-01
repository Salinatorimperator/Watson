import os
import json
from watson_developer_cloud import DiscoveryV1

discovery = DiscoveryV1(
    version="2018-03-05",
    username="55661b79-fa4c-4657-901a-d8ccefca3e89",
    password="mqOz5JbOZaGQ",
    url = 'https://gateway.watsonplatform.net/discovery/api'
)

my_query = discovery.query(environment_id='d3755050-a1c6-4cdb-a480-3bc1df719e7d', collection_id='c8117070-40cb-44b1-bb6c-29fac8f620d6', query='grupo antolin')#, filter='enrichedTitle.entities.type:Person', aggregation='nested(enrichedTitle.entities)')
                           #, return_fields='{return_fields}')
result=json.dumps(my_query, indent=2)
results=my_query['results']



entities=[]
docs=[]
for article in results:
   docs.append(article['extracted_metadata']['filename'])

textos=[]
count=0
for entitie in results:
    entities.append(entitie['enriched_text']['entities'][count])
    count+1
    for enti in entities:
        if enti['count']>3:
            if enti['text'] in textos | enti['text'] in keyword:
                continue
            else:
                textos.append(enti['text'])
print(textos)



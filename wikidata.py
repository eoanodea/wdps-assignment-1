import json

import trident
KBPATH='assets/wikidata-20200203-truthy-uri-tridentdb'

from elasticsearch import Elasticsearch

def return_amount_po_entity(entity):
    db = trident.Db(KBPATH)
    id_of_test = db.lookup_id(entity)
    object_from_subject = db.o_aggr_froms(id_of_test)
    object_from_subject_text = [db.lookup_str(i) for i in object_from_subject]
    return (len(object_from_subject_text))

def elastic_search(query, n=20):
    e = Elasticsearch()
    p = { "query" : { "query_string" : { "query" : query }}}
    response = e.search(index="wikidata_en", body=json.dumps(p), size=n)
    id_labels = {}
    if response:
        for hit in response['hits']['hits']:
            source = hit['_source']
            if ('schema_name' in source):
                label = source['schema_name']
            elif ('schema_description' in source):
                label = source['schema_description']
            else:
                continue
            id = hit['_id']
            id_labels.setdefault(id, set()).add(label)
    return id_labels

    def get_p_overlap(entities):

    #define list which holds predicates for each entity
    p_list = []
    #get all predicates
    for entity in entities:
        entitie_pos = db.po(db.lookup_id(entity))
        predicates = ([po[0] for po in entitie_pos])
        p_list.append(predicates)
    overlap = (set.intersection(*map(set, p_list)))

    return (overlap)


def ne_based_model(candidate, random_overlap):

    #get po's from candidate
    id_of_test = db.lookup_id(candidate)
    contents_of_subject = db.po(id_of_test)
    #check whether predicates of the overlap of five persons is in candidate predicates
    predicates_of_candidate = [po[0] for po in contents_of_subject]
    if random_overlap.issubset(set(predicates_of_candidate)):
        print('CHECK')
    else:
        print('NO')


def base_model(candidate):

    id_of_test = db.lookup_id(candidate)
    contents_of_subject = db.po(id_of_test)

    return (len(contents_of_subject))


def get_random_entities(predicate,label):

    query="""PREFIX wde: <http://www.wikidata.org/entity/> \
        PREFIX wdp: <http://www.wikidata.org/prop/direct/> \
        PREFIX wdpn: <http://www.wikidata.org/prop/direct-normalized/> \
        select ?s where { ?s wdp:""" + predicate + """ wde:""" + label + """ . } 
        OFFSET 210 #random number variable
        LIMIT 10
    """

    #get query of n random entities
    persons = db.sparql(query)
    #results = db.sparql(query)
    json_results = json.loads(persons)
    variables = json_results["head"]["vars"]

    entity_list = []
    results = json_results["results"]
    for b in results["bindings"]:
        for var in variables:
            entity_list.append("<"+ b[var]["value"] + ">")
    return entity_list

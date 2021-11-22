import gzip
import re

import nltk
# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')
# nltk.download('maxent_ne_chunker')
# nltk.download('words')

from bs4 import BeautifulSoup

from test_elasticsearch_server import search

import trident
KBPATH='assets/wikidata-20200203-truthy-uri-tridentdb'


# import flair
# from flair.data import Sentence
# from flair.models import SequenceTagger


KEYNAME = "WARC-TREC-ID"

# The goal of this function process the webpage and returns a list of labels -> entity ID


def find_labels(payload):
    if payload == '':
        return


    # The variable payload contains the source code of a webpage and some additional meta-data.
    # We firt retrieve the ID of the webpage, which is indicated in a line that starts with KEYNAME.
    # The ID is contained in the variable 'key'
    key = None
    for line in payload.splitlines():
        if line.startswith(KEYNAME):
            key = line.split(': ')[1]
            break

    # Problem 1: The webpage is typically encoded in HTML format.
    # We should get rid of the HTML tags and retrieve the text. How can we do it?
    def clean(data):
    
        soup = BeautifulSoup(data, 'html.parser')
        clean = ""

        # Loop through every p tag within the payload  
        for paragraph in soup.find_all('p'):
            # Remove any left over HTML tags
            stripped = re.sub('<[^>]*>', '', str(paragraph))
            
            # Number of \n tags in the stripped string
            nLength = len(stripped.split('\n'))
            
            # The length of the string
            strLength = len(stripped)

            # If the string has a length of more then 100
            # and contains less than 3 \n tags, 
            # add it to the final result
            if strLength > 100 and nLength < 3:
                clean += stripped + '\n'

        return clean.replace('\n', '')   
    # The resulting string
    # print(clean)

    # Problem 2: Let's assume that we found a way to retrieve the text from a webpage. How can we recognize the
    # entities in the text?

    def get_entities_nltk(cleaned):   

        if(cleaned != ""):
            
            # Loop through tokenised version of the data
            for sent in nltk.sent_tokenize(cleaned):
                # Apply POS tagging to sentenice and loop through
                for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sent))):
                    # Maybwe we can do something here?
                    if hasattr(chunk, 'label'):
                        return (chunk.label(), ' '.join(c[0] for c in chunk))

    cleaned = clean(payload)

    chunks = get_entities_nltk(cleaned)
    
    


    
    # Problem 3: We now have to disambiguate the entities in the text. For instance, let's assugme that we identified
    # the entity "Michael Jordan". Which entity in Wikidata is the one that is referred to in the text?
    
    
    if chunks is not None:
        
        QUERY = chunks[1]
        items = search(QUERY).items()
        
        # something something sparql

        for entity, labels in items:
            
            if key and (chunks[1] in payload):
                label = next(iter(labels))
                category = chunks[0]

                wdp = "P31" # Instance of

                db = trident.Db(KBPATH)    

                # p = predicate, s = subject, o = object
                # subject_id = db.lookup_id(entity) 
                # pos = db.po(subject_id) # db.po(s: int) -> List[(p: int, o: int)]|None ==> thus ID = s: int | ID = subject (entity)

                # i think i got it

                # I'm trying to figure out how this works, i'm assuming here that db.po = db.predicate_object()
                # thus the result (a, b) = array of (predicate_id, object_id)
                # and because the first argument is id, it means that s = entiity
                # so now we can https://canvas.vu.nl/courses/55617/pages/extra-documentation-on-first-assignment 
              
              
              
                # print(lookup_str())

                # now we somehow need to figure out what the predicate_id is of category (chunks[0])
                # for predicate_id, object_id in pos:
                    # print(predicate_id)
                    # print(db.lookup_str(predicate_id))
                    # print(db.search_id("person"))
                    #the IDs are so weird - sometimes they are 1, or 5 and other times 3099744467
                    # i think the lower numbers are more like 'base' types?
                    # I'd assume that "PERSON" has a lower ID than a full name
                    # print(db.exists(subject_id, predicate_id, object_id))
                #     if db.exists(subject_id, predicate_id, object_id):
                # category = "https://www.wikidata.org/wiki/Q215627"
              
                query = """
                    PREFIX wdp: <http://www.wikidata.org/prop/direct/> 
                    PREFIX wdpn: <http://www.wikidata.org/prop/direct-normalized/>
                    select ?s where { ?s wdp:%s %s . } LIMIT 10
                """ % (wdp, entity)

                # print(query)

                # results = db.sparql(query)

                # print(results)


                # print(db.outdegree()) # Killed, oh there goes your elasticsearch connection
                # nice to know that trident can kill an elasticsearch connection c:
                
               

        

                # predicates_objects = db.po(subject_id)
                # for predicate_id, object_id in predicates_objects:
                #     print(object_id)
                #     print(db.lookup_str(object_id)) # doesn't look like objects to me (or i just don't know what an object is)
                    # maybe i dont know what an object is 😅
                    # i thoughts objects were things like (person, organization, etc.)
                    # however, the ID 3260604856 tells me there are possibly millions of objects, so I'm not really sure anymore hahah
                    # I think my brain is fried

                    
# %s = subject, wdp = wiki data predicate, wde = wiki data entity,  wdpn = wiki data predicate normalized (because p = predicate and the url says normalized)?? (that's probably the .)
                # select subject where { subject, predicate(instance_of), object(person?) }
                # where subject is a person
                # ASK { ?s rdf:type category } 
                # oooohh shit
            
                # category labels: FACILITY, GPE, GSP, LOCATION, ORGANIZATION, PERSON
                # do we need to find these WDE's on our own?
                # Maybe we can generate them somehow
                # PERSON = https://www.wikidata.org/wiki/Q215627
                # GPE = https://www.wikidata.org/wiki/Q561912
                # or do we need to query it?
                # print("i think here: ", category)

                # hmmmm look at this:https://query.wikidata.org/#PREFIX%20wde%3A%20%3Chttp%3A%2F%2Fwww.wikidata.org%2Fentity%2F%3E%20%0APREFIX%20wdp%3A%20%3Chttp%3A%2F%2Fwww.wikidata.org%2Fprop%2Fdirect%2F%3E%20%0APREFIX%20wdpn%3A%20%3Chttp%3A%2F%2Fwww.wikidata.org%2Fprop%2Fdirect-normalized%2F%3E%0Aselect%20%3Fs%20where%20%7B%20%3Fs%20wdp%3AP31%20wde%3AQ10373242%20.%20%7D%20LIMIT%2010
                # instance of (WDT P31) death (WD Q4)
                # results: wd:Q431888, wd:Q523883
                # does that mean we have to: instanceof (Person), and check if the elasticsearch result is in the trident result?
                # would be weird, considering that there are probably billions of persons in there
                # yeah it seems a bit strange
                # SELECT elasticsearch_result WHERE { wdp: person } ??? would that work
                # Possibly, I'm trying to look online but I can't find much on it
                # isn't there some cheat sheet on canvas?

                # there is one way to do it, but it requires using their API which maybe is a bit much

                # https://www.wikidata.org/w/api.php?action=wbsearchentities&search=Person&language=en
                                                                                    #^^ key word
                # Maybe it can be returned from NLTK along with the name of the entity
                # https://canvas.vu.nl/courses/55617/pages/extra-documentation-on-first-assignment

                # db.lookup_relstr(id: int) -> str|None

                # ... wait a second:
                # term = "<http://www.wikidata.org/entity/Q145>"
                # term_id = db.lookup_id(term)
                # print(db.po(term_id))
                # Apparently the regex wasn't really needed


                # results = db.sparql(query)
                
                yield key, label, entity 

        # "For instance, if you know that the webpage refers to persons
        # then you can query the knowledge base to filter out all the entities that are not persons..."
    

        
    

    # To tackle this problem, you have access to two tools that can be useful. The first is a SPARQL engine (Trident)
    # with a local copy of Wikidata. The file "test_sparql.py" shows how you can execute SPARQL queries to retrieve
    # valuable knowledge. Please be aware that a SPARQL engine is not the best tool in case you want to lookup for
    # some strings. For this task, you can use elasticsearch, which is also installed in the docker image.
    # The file start_elasticsearch_server.sh will start the elasticsearch server while the file
    # test_elasticsearch_server.py shows how you can query the engine.

    # A simple implementation would be to first query elasticsearch to retrieve all the entities with a label
    # that is similar to the text found in the web page. Then, you can access the SPARQL engine to retrieve valuable
    # knowledge that can help you to disambiguate the entity. For instance, if you know that the webpage refers to persons
    # then you can query the knowledge base to filter out all the entities that are not persons...

    # Obviously, more sophisticated implementations that the one suggested above are more than welcome :-)

    # For now, we are cheating. We are going to returthe labels that we stored in sample-labels-cheat.txt
    # Instead of doing that, you should process the text to identify the entities. Your implementation should return
    # the discovered disambiguated entities with the same format so that I can check the performance of your program.
    # cheats = dict((line.split('\t', 2) for line in open(
    #     'data/sample-labels-cheat.txt').read().splitlines()))
    # for label, wikidata_id in cheats.items():
    #     if key and (label in payload):
    #         yield key, label, wikidata_id


def split_records(stream):
    payload = ''
    for line in stream:
        if line.strip() == "WARC/1.0":
            yield payload
            payload = ''
        else:
            payload += line
    yield payload


if __name__ == '__main__':
    import sys
    try:
        _, INPUT = sys.argv
    except Exception as e:
        print('Usage: python starter-code.py INPUT')
        sys.exit(0)

    with gzip.open(INPUT, 'rt', errors='ignore') as fo:
        for record in split_records(fo):
            for key, label, wikidata_id in find_labels(record):
                # print(key + '\t' + label + '\t' + wikidata_id)
                pass

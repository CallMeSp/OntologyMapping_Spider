
def getOwlBase():
    with open('baseOwl.owl','r') as f:
        return f.read()

WholerightTag='</rdf:RDF>'


def genIndividualOwl(value,classtype,properties:dict):
    leftTag='<owl:NamedIndividual rdf:about="http://www.semanticweb.org/callmesp/ontologies/2018/4/DrugTry#'+value+'">'
    typeTag='<rdf:type rdf:resource="http://www.semanticweb.org/callmesp/ontologies/2018/4/untitled-ontology-9#%s"/>'%classtype
    result=leftTag+'\n'+typeTag+'\n'
    for propertyDict in properties.items():
        key,value=propertyDict
        result+='<DrugTry:%s rdf:resource="http://www.semanticweb.org/callmesp/ontologies/2018/4/DrugTry#%s"/>\n'%(key,value)
    rightTag=' </owl:NamedIndividual>\n'
    result+=rightTag
    return result




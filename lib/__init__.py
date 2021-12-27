from json import load, dump
from .analysis import Analyze
from .script import CoursePrerequisites

def doTerm(term):
    with open("Catalogs/Raws/"+term+".html") as f:
        CoursePrerequisites(f, term)
        try:
            Analyze(term)
        except Analyze.CycleError as err:
            e = {}
            with open('Catalogs/Errors/' + term + '.json', 'r') as fp:
                e = load(fp)
            
            e["cycle"] = str(err.problems)
            with open('Catalogs/Errors/' + term + '.json', 'w') as fp:
                dump(e, fp)



def doTerms(terms):
    print("doing", terms)
    for term in terms:
        doTerm(term)

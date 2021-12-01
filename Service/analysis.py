from sympy import *
from sympy.logic.boolalg import BooleanFunction

import json
import re

def Analyze(term: str):
    def parse_course_name(full_name):
        return "".join(full_name.split(" - ")[0].split(" "))

    with open("Catalogs/Originals/" + term + ".json", "r") as f:
        courses = json.loads(f.read())
        

    fullnames_dict = {} # full course name -> course name
    courses_dict = {} # course name -> course symbol
    prereq_strings_dict = {} # course name -> prereq string
    prereqs_dict = {} # course name -> prerequisite expression or none


    for (course_name, prerequisites) in courses.items():
        name = parse_course_name(course_name)
        fullnames_dict[course_name] = name
        courses_dict[name] = Symbol(name)
        prereq_strings_dict[name] = prerequisites


    for (name, prerequisites_string) in prereq_strings_dict.items():
        if not prerequisites_string:
            continue
        else:
            try:
                prereqs_dict[name] = eval(prerequisites_string, courses_dict)
            except NameError:
                # there are some required classes that are not in the symbols dictionary yet (were not in the catalog)
                # TODO: these should be marked in some way
                
                # find all course names
                for new_course_name in re.findall("\w+", prerequisites_string):
                    # create a symbol for the course if doesnt exist
                    if new_course_name not in courses_dict:
                        courses_dict[new_course_name] = Symbol(new_course_name)
            prereqs_dict[name] = eval(prerequisites_string, courses_dict)


    # returns set of of (course >> prerequisites) for all needed prerequisites for a given course 
    # "set of prerequisite expressions of all courses a given course depends on in any way"
    def get_all_prereqs(prerequisites, course=None, ret=set()):
        if not prerequisites:
            return ret
        
        if course:
            ret.add(course >> prerequisites)
        
        # get sub-prerequisites for every course in the prerequisites
        for sub_course_symbol in prerequisites.atoms():
            if isinstance(sub_course_symbol, Symbol) and sub_course_symbol.name in prereqs_dict:
                get_all_prereqs(prereqs_dict[sub_course_symbol.name], sub_course_symbol, ret)
        return ret


    # checks if a given expression is satisfiable with given assumptions
    # givens should be a set of SymPy boolean expressions
    def satisfiable_with_givens(expr, givens):
        return satisfiable(And(expr, *givens));


    # checks if an arbitrary prerequisite expression (eg. "course & course & course") implies another
    # true if a >> b
    def prereq_implies_prereq(a, b):
        # a does not imply b if it is possible to have a=true b=false
        # check if (a&!b) is satisfiable
        # if it is satisfiable, implies is false. if it is not satisfiable, implies is true.
        res = satisfiable_with_givens(a&~b, get_all_prereqs(a) | get_all_prereqs(b))
        
        return not bool(res)


    def a_is_redundant(func, a, b):
        if func is Or:
            return prereq_implies_prereq(a, b)
        elif func is And:
            return prereq_implies_prereq(b, a)


    # returns A simplified prerequisite expression
    def simplify_prereqs(course_prerequisites, verbose=True):
        if not isinstance(course_prerequisites, BooleanFunction):
            return course_prerequisites;

        parts = course_prerequisites.args

        # simplify all components of this prereq string before simplifying the whole thing
        parts = [simplify_prereqs(component, verbose) for component in parts]
        if verbose:
            print("analysing:", course_prerequisites.args, [(p, type(p)) for p in parts])
        
        
        for i in range(len(parts)):
            A = parts[i]
            B = course_prerequisites.func(*parts[0:i], *parts[i+1:len(parts)])
            if verbose:
                print(course_prerequisites.func, A, ",", B)
            
            # check if A is needed for this prerequisite
            p = a_is_redundant(course_prerequisites.func, A, B)
            
            # if A is redundant
            if p: 
                if verbose:
                    print(strike("("+str(A)+")"), sep="", end=" ")
                # remove A from the prereq string by making it the identity for this operation
                parts[i] = course_prerequisites.func.identity
        return course_prerequisites.func(*parts)


    # use our methods to analyze all courses that have prerequisites, then save the simplified prerequisites
    changes = {}
    new_prereqs_dict = {}

    for (full_name, name) in fullnames_dict.items():
        if name in prereqs_dict:
            prereqs = prereqs_dict[name]
            new_prereqs = simplify_prereqs(prereqs, False)
            new_prereqs_dict[full_name] = new_prereqs
            if not prereqs.equals(new_prereqs):
                changes[full_name] = {"old": str(prereqs), "new": str(new_prereqs)}
            
        else:
            new_prereqs_dict[full_name] = ""

    # save outputs
    with open('Catalogs/Updates/' + term + '.json', 'w') as fp:
        json.dump({n: str(p) for (n, p) in new_prereqs_dict.items()}, fp)

    with open('Catalogs/Changes/' + term + '.json', 'w') as fp:
        json.dump(changes, fp)
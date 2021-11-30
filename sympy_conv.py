#!/usr/bin/env python
# coding: utf-8

# We would like to use SymPy methods to analyze course prerequisites. For this, every course will be defined as a variable (Symbol) and the prerequisite strings will be converted into SymPy expressions.

# In[1]:


from sympy import *
from sympy.logic.boolalg import BooleanFunction

import json
import re
import time

chrono1 = time.perf_counter()

def parse_course_name(full_name):
    return "".join(full_name.split(" - ")[0].split(" "))

with open("CoursePrerequisites.json", "r") as f:
    courses = json.loads(f.read())
    
# https://stackoverflow.com/a/25244576
def strike(text):
    result = ''
    for c in text:
        result = result + c + '\u0336'
    return result


# In[2]:


fullnames_dict = {} # full course name -> course name
courses_dict = {} # course name -> course symbol
prereq_strings_dict = {} # course name -> prereq string

for (course_name, prerequisites) in courses.items():
    name = parse_course_name(course_name)
    fullnames_dict[course_name] = name
    courses_dict[name] = Symbol(name)
    prereq_strings_dict[name] = prerequisites


# In[3]:


# prereqs_dict: course name -> prerequisite expression or none
prereqs_dict = {}
# "CS515" -> 𝐴𝐶𝐶201∨𝑀𝐺𝑀𝑇202

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


# In[4]:


# check results
prereqs_dict["ACC301"]


# In[5]:


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


# In[6]:


# test recursion with a 2 level deep example
get_all_prereqs(prereqs_dict["CS515"], courses_dict["CS515"])


# In[7]:


# checks if a given expression is satisfiable with given assumptions
# givens should be a set of SymPy boolean expressions
def satisfiable_with_givens(expr, givens):
    return satisfiable(And(expr, *givens));


# In[8]:


# checks if an arbitrary prerequisite expression (eg. "course & course & course") implies another
# true if a >> b
def prereq_implies_prereq(a, b):
    # a does not imply b if it is possible to have a=true b=false
    # check if (a&!b) is satisfiable
    # if it is satisfiable, implies is false. if it is not satisfiable, implies is true.
    res = satisfiable_with_givens(a&~b, get_all_prereqs(a) | get_all_prereqs(b))
    
    return not bool(res)


# In[9]:


def a_is_redundant(func, a, b):
    if func is Or:
        return prereq_implies_prereq(a, b)
    elif func is And:
        return prereq_implies_prereq(b, a)


# In[10]:


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


# In[11]:


def check(course):
    print("checking", course+":\ncurrent prereq is:")
    print(prereqs_dict[course])
    print("processed prereq is:")
    print("\n"+str(simplify_prereqs(prereqs_dict[course])))
    print("\n")

check("POLS302")
check("POLS409")
check("POLS410")


# In[12]:


# use our methods to analyze all courses that have prerequisites, then save the simplified prerequisites
changes = {}
new_prereqs_dict = {}
c = 0
chrono2 = time.perf_counter()

for (full_name, name) in fullnames_dict.items():
    if name in prereqs_dict:
        prereqs = prereqs_dict[name]
        new_prereqs = simplify_prereqs(prereqs, False)
        new_prereqs_dict[full_name] = new_prereqs
        if not prereqs.equals(new_prereqs):
            changes[full_name] = {"old": str(prereqs), "new": str(new_prereqs)}
        c+=1
        
    else:
        new_prereqs_dict[full_name] = ""

end = time.perf_counter()
chrono1 = end - chrono1
chrono2 = end - chrono2
print("Analysis complete,", c, "prerequisite expressions in", chrono2, "seconds.")
print("Average of", chrono2/c, "seconds per expression.")
print("Totals:")
print("\tcourses:", len(new_prereqs_dict))
print("\tchanges:", len(changes))
print("\ttime:", chrono1, "seconds")


# save outputs
with open('updatedValues.json', 'w') as fp:
    json.dump({n: str(p) for (n, p) in new_prereqs_dict.items()}, fp)

with open('changelist.json', 'w') as fp:
    json.dump(changes, fp)


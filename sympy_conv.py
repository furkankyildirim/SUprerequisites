from sympy import *
import json
import re

def parse_course_name(full_name):
    return "".join(full_name.split(" - ")[0].split(" "))


# returns set of of (course >> prerequisites) for all needed prerequisites for a given 
# "set of prerequisite expressions of all courses a given course depends on in any way"
def get_all_prereqs(prerequisites, course=None, ret=set()):
    if not prerequisites:
        return ret
    
    if course:
        ret.add(course >> prerequisites)
    
    # get sub-prerequisites for every course in the prerequisites
    for sub_course_symbol in prerequisites.atoms():
        if sub_course_symbol.name in prereqs_dict:
            get_all_prereqs(prereqs_dict[sub_course_symbol.name], sub_course_symbol, ret)
    return ret


# checks if a given expression is satisfiable with given assumptions
# givens should be a set of SymPy boolean expressions
def satisfiable_with_givens(expr, givens):
    return satisfiable(And(expr, *givens));


# checks if an arbitrary prerequisite expression (eg. "course & course & course")
def prereq_implies_prereq(a, b):
    # lhs does not imply b if it is possible to have a=true b=false
    # check if (a&!b) is satisfiable
    # if it is satisfiable, implies is false. if it is not satisfiable, implies is true.
    res = satisfiable_with_givens(a&~b, get_all_prereqs(a) | get_all_prereqs(b))
    return not bool(res)

if __name__ == "__main__":

    with open("CoursePrerequisites.json", "r") as f:
        courses = json.loads(f.read())

        courses_dict = {} # course name -> course symbol
        prereq_strings_dict = {} # course name -> prereq string

        for (course_name, prerequisites) in courses.items():
            name = parse_course_name(course_name)
            courses_dict[name] = Symbol(name)
            prereq_strings_dict[name] = prerequisites


        # prereqs_dict: course name -> prerequisite expression or none
        prereqs_dict = {}

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
    print(get_all_prereqs(prereqs_dict["ACC406"], courses_dict["ACC406"]))
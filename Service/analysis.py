from sympy import *
from sympy.logic.boolalg import BooleanFunction

import json
import re

class Analyze():
    
    class ProblemCoursesError(Exception):
        """Exception for when some courses that are being analyzed are problematic"""

        def __init__(self, problems: dict):
            self.problems = problems
    
    class CycleError(ProblemCoursesError):
        """Exception for when there is a cycle in the input"""
        pass

    class AmbiguousError(ProblemCoursesError):
        """Exception for when there are ambiguous prerequisites in the given input"""
        pass
    

    
    def __init__(self, term, **kwargs):
        with open("Catalogs/Originals/" + term + ".json", "r") as f:
            courses = json.loads(f.read())

            self.fullnames_dict = {}  # full course name -> course name
            self.courses_dict = {}  # course name -> course symbol
            self.prereq_strings_dict = {}  # course name -> prereq string
            self.prereqs_dict = {}  # course name -> prerequisite expression or none

            for (course_name, prerequisites) in courses.items():
                name = Analyze.parse_course_name(course_name)
                self.fullnames_dict[course_name] = name
                self.courses_dict[name] = Symbol(name)
                self.prereq_strings_dict[name] = prerequisites
            
            self.ambiguous = {name: prereq_text for name, prereq_text in self.prereq_strings_dict.items() if Analyze.is_ambiguous(prereq_text)}
            if kwargs.get("raise_ambiguous", False):
                if len(self.ambiguous):
                    raise Analyze.AmbiguousError(self.ambiguous)

            for (name, prerequisites_string) in self.prereq_strings_dict.items():
                if not prerequisites_string:
                    continue
                else:
                    try:
                        self.prereqs_dict[name] = eval(
                            prerequisites_string, self.courses_dict)
                    except NameError:
                        # there are some required classes that are not in the symbols dictionary yet (were not in the catalog)
                        # TODO: these should be marked in some way

                        # find all course names
                        for new_course_name in re.findall("\w+", prerequisites_string):
                            # create a symbol for the course if doesnt exist
                            if new_course_name not in self.courses_dict:
                                self.courses_dict[new_course_name] = Symbol(
                                    new_course_name)
                    self.prereqs_dict[name] = eval(
                        prerequisites_string, self.courses_dict)

            # check if there are any cycles
            cyclics = {name: prereqs for (name, prereqs) in self.prereqs_dict.items()
                       if self.is_cyclic(prereqs, self.courses_dict[name], set())}
            if len(cyclics):
                raise Analyze.CycleError(cyclics)

            # use our methods to analyze all courses that have prerequisites, then save the simplified prerequisites
            self.changes = {}
            self.new_prereqs_dict = {}

            for (full_name, name) in self.fullnames_dict.items():
                if name in self.prereqs_dict:
                    prereqs = self.prereqs_dict[name]
                    new_prereqs = self.simplify_prereqs(prereqs, False)
                    self.new_prereqs_dict[full_name] = new_prereqs
                    if not prereqs.equals(new_prereqs):
                        self.changes[full_name] = {"old": str(
                            prereqs), "new": str(new_prereqs)}

                else:
                    self.new_prereqs_dict[full_name] = ""

            # save outputs
            with open('Catalogs/Updates/' + term + '.json', 'w') as fp:
                json.dump({n: str(p)
                          for (n, p) in self.new_prereqs_dict.items()}, fp)

            with open('Catalogs/Changes/' + term + '.json', 'w') as fp:
                json.dump(self.changes, fp)

    @staticmethod
    def parse_course_name(full_name):
        return "".join(full_name.split(" - ")[0].split(" "))
    
    
    @staticmethod
    # returns true if given prereq text is ambiguous
    def is_ambiguous(prereq_text):
        # see if the top level (outside paranthesis) has all same connector (| or &)
        connector = ""
        inside_brackets = False
        substatement = ""
        for c in prereq_text:
            if inside_brackets:
                if c == ")":
                    if is_ambiguous(substatement):
                        return True
                    inside_brackets = False
                    substatement = ""
                else:
                    substatement += c
            elif c == "(":
                inside_brackets = True
            elif c == "|" or c == "&":
                if connector:
                    if c != connector:
                        return True
                else:
                   connector = c
        return False
    
    # returns true if any cycles exist in the expr or prerequisites of expr
    def is_cyclic(self, expr, search, hist):
        print("searching if", search, "is cyclic in", expr, "seen", hist)

        subs_to_search = [
            sub_course 
            for sub_course 
            in expr.atoms()
            if isinstance(sub_course, Symbol) and sub_course.name in self.prereqs_dict
            ]
        
        # if there is a cycle in one of our sub-courses, we have a cycle in general
        for sub_course in subs_to_search:
            # if we are cycling back to search through a sub_course, we have a cycle
            try:
                hist.add(sub_course)
                if self.is_cyclic(self.prereqs_dict[sub_course.name], search, hist):
                    return True
            except RecursionError:
                return True


        return False

    # returns set of of (course >> prerequisites) for all needed prerequisites for a given course
    # "set of prerequisite expressions of all courses a given course depends on in any way"

    def get_all_prereqs(self, prerequisites, course=None, ret=set()):
        if not prerequisites:
            return ret

        if course:
            ret.add(course >> prerequisites)

        # get sub-prerequisites for every course in the prerequisites
        for sub_course_symbol in prerequisites.atoms():
            if isinstance(sub_course_symbol, Symbol) and sub_course_symbol.name in self.prereqs_dict:
                self.get_all_prereqs(
                    self.prereqs_dict[sub_course_symbol.name], sub_course_symbol, ret)
        return ret

    @staticmethod
    # checks if a given expression is satisfiable with given assumptions
    # givens should be a set of SymPy boolean expressions
    def satisfiable_with_givens(expr, givens):
        return satisfiable(And(expr, *givens))

    # checks if an arbitrary prerequisite expression (eg. "course & course & course") implies another
    # true if a >> b

    def prereq_implies_prereq(self, a, b):
        # a does not imply b if it is possible to have a=true b=false
        # check if (a&!b) is satisfiable
        # if it is satisfiable, implies is false. if it is not satisfiable, implies is true.
        res = Analyze.satisfiable_with_givens(
            a & ~b, self.get_all_prereqs(a) | self.get_all_prereqs(b))

        return not bool(res)

    def a_is_redundant(self, func, a, b):
        if func is Or:
            return self.prereq_implies_prereq(a, b)
        elif func is And:
            return self.prereq_implies_prereq(b, a)

    # returns A simplified prerequisite expression

    def simplify_prereqs(self, course_prerequisites, verbose=True):
        if not isinstance(course_prerequisites, BooleanFunction):
            return course_prerequisites

        parts = course_prerequisites.args

        # simplify all components of this prereq string before simplifying the whole thing
        parts = [self.simplify_prereqs(component, verbose)
                 for component in parts]
        if verbose:
            print("analysing:", course_prerequisites.args,
                  [(p, type(p)) for p in parts])

        for i in range(len(parts)):
            A = parts[i]
            B = course_prerequisites.func(*parts[0:i], *parts[i+1:len(parts)])
            if verbose:
                print(course_prerequisites.func, A, ",", B)

            # check if A is needed for this prerequisite
            p = self.a_is_redundant(course_prerequisites.func, A, B)

            # if A is redundant
            if p:
                if verbose:
                    print(Analyze.strike("("+str(A)+")"), sep="", end=" ")
                # remove A from the prereq string by making it the identity for this operation
                parts[i] = course_prerequisites.func.identity
        return course_prerequisites.func(*parts)

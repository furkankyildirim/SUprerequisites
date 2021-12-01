from bs4 import BeautifulSoup
import requests
import json
import re

PREREQUISITE_RE = re.compile("(\w+) level  ((\w+) ([0-9]+))( Minimum Grade of (\w))?")

def parse_prereq_string(prereqs):
  prereqs = prereqs.replace(" and ", "&")
  prereqs = prereqs.replace(" or ", "|")

  if "&" not in prereqs and "|" not in prereqs:
    # this is just one prereq, format it correctly
    match = PREREQUISITE_RE.search(prereqs)
    if not match: return ""
    return "".join(match.group(3,4))

  res = ""
  substr = ""
  in_brackets = False

  for i in range(len(prereqs)):
    c = prereqs[i]
    # if inside brackets: parse the insidesd recursively
    # parse insides of brackets recursively
    if c == ")":
      in_brackets = False
      res += "(" + parse_prereq_string(substr) + ")"
      substr = ""
      continue
    
    if c == "(":
      in_brackets = True
      continue

    if in_brackets:
      substr += c
      continue
    

    if c == "&" or c == "|":
      res+=parse_prereq_string(substr)+c
      substr = ""
      continue

    substr += c
  res+=parse_prereq_string(substr)
  return res

class CoursePrerequisites:

  def __init__(self, file, term) -> None:
    self.Prerequisites = {}
    link_list = self.getCoursesLink(file)

    for url in link_list:
        self.getCoursePrerequisites(url)

    self.savePrerequisites(term)


  # method: getCoursesLink
  # Gets all courses link from given file and returns as list
  # @file_name, str: The filename which will get courses link
  # @return, list: Return courses links
  # @completed
  def getCoursesLink(self, file) -> list:
    
    #: Opens and parses the file which is given filename  
    soup = BeautifulSoup(file, 'html.parser')

    #: Gets all courses tags as list
    title_list = soup.find_all('td', attrs={"class": "nttitle"})

    #: Defines the list will return
    courses_link_list = []

    #: Gets all courses urls and append to list
    for item in title_list:
      href = item.find('a').get('href')
      courses_link_list.append(href)

    #: returns response
    return courses_link_list


  # method: getCoursePrerequisites
  # Gets all course prerequisites and their links from given course url
  # @url, str: The url which get the prerequisites of the course
  # @return, None
  # @completed
  def getCoursePrerequisites(self, url: str) -> None:
    try:
      #: Opens and parses the page which is given url 
      page_content = requests.get(url, headers={"User-Agent": "XY"}).content
      soup = BeautifulSoup(page_content, 'html.parser')
        
      #: Gets course title and prerequisites title
      course_tag = soup.find('td', attrs={"class": "nttitle"}).text
      prerequisites_tag = soup.find('span', text='Prerequisites: ', attrs={
          "class": "fieldlabeltext"})

      print(course_tag)

      #: Defines the string will added to all Prerequisites 
      prerequisites = ''

      #: Make sure that the course has any prerequisites
      if prerequisites_tag != None:
        #: Finds all prerequisites
        prerequisites_texts = prerequisites_tag.next_siblings

        #: Cleans the prerequisites data
        prerequisites = parse_prereq_string("".join([item.text for item in prerequisites_texts if item.text != " "]))

      #: Appends to all Prerequisites dictionary
      self.Prerequisites[course_tag] = prerequisites        

    except:
      print('Broken url: ',url)

  
  # def cleanPrerequisites(self):
  #   for key in self.Prerequisites:
  #     for idx in range(0,len(self.Prerequisites[key])):
  #       if self.Prerequisites[key][idx]["course"] == ' ':
  #         self.Prerequisites[key].pop(idx)


  # method: savePrerequisites
  # Saves all course prerequisites
  # @return, None
  # @completed
  def savePrerequisites(self, term:str):
    with open('Catalogs/Originals/' + term + '.json', 'w') as fp:
      json.dump(self.Prerequisites, fp)


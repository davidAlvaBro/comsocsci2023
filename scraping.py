from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import urllib3

def get_2019_posters(verbose=False):
    """
    Get all names from the webpage : https://2019.ic2s2.org/posters/
    
    Returns:
        set: A set of all unique names occuring in the page
    """
    # Get the webpage data
    LINK = "https://2019.ic2s2.org/posters/"
    r = requests.get(LINK)
    soup = BeautifulSoup(r.content, features="html.parser")

    # Get each bullet point under class "col-md-8" (all the names are here)
    text = soup.find("div", {"class": "col-md-8"})
    items = text.find_all("li")
    item_list = [str(item) for item in items]

    # Get content between > and <, and seperate at , 
    regex_compiler = re.compile("(?<=\>)(.*?)(?=\<)")

    names = [regex_compiler.findall(item)[0] for item in item_list]
    ind_names = [re.split(', | and', name) for name in names]
    persons =  []
    
    # Collect to one list
    for list in ind_names:
        for name in list:
            persons.append(name)

    # Verbose 
    people_set = set(persons)
    if verbose: print(f"There are {len(people_set)} different people and {len(persons)} name occurences in {LINK}")
    return people_set

def get_2019_oral(verbose=False):
    """
    Get all names from the webpage : https://2019.ic2s2.org/oral-presentations/
    
    Returns:
        set: A set of all unique names occuring in the page
    """
    def find_between( s, first, last ):
        """
        Returns the part of a string that is in the middel of first and last (substrings)

        Args:
            s (String): The string
            first (String): the start "token"
            last (String): the end "token"

        Returns:
            _type_: Substring between "first" and "last"
        """
        try:
            start = s.index( first ) + len( first )
            end = s.index( last, start )
            return s[start:end]
        except ValueError:
            return ""
    
    # Get the webpage data
    LINK = "https://2019.ic2s2.org/oral-presentations/"
    r = requests.get(LINK)
    soup = BeautifulSoup(r.content) 
    
    # # All names are in <p> sections under the "div" "col-md-8", but the three first are useless
    # text = soup.find("div", "col-md-8")
    # lines = text.find_all("p")
    # lines_with_names = lines[3:] 
    
    # All names are between these two titles 
    bet = find_between(str(soup),"1A Misinformation","Evidence of Influence Hierarchies in GitHub’s Cryptocurrency Community" )
    spli = bet.split("<p>") # each <p> has it's own section with a chairname and a list of presenters
    
    # Get the chairname 
    chair_names = []
    for i in spli:
        e = find_between(i, "Chair:", "</em>")
        chair_names.append(e)
    
    # Get the other occupants 
    new_list = []
    for d in spli:
        new_list.append(find_between(d,"</em><br/>","</p>"))
    
    newer_list = []
    #Remove known non-name including files
    for i in range(20): 
        abe = new_list[i].split("<br/>")
        for x in abe:
            x = x[16:]
            if str(x) == "No Presentation":
                pass
            else:
                newer_list.append(x)
    
    # Seperate into two schools - the ones that end with .  and the ones with - 
    # Seperate names at , and remove empty names. 
    # If there is a : then it is not a name, only take what is after. 
    names_list = []
    for i in newer_list:
        if str(i[-1]) == "–":
            lol = str(i[:-2]).split(",")
            for m in lol:
                if m != "":
                    if ":" in m:
                        m = m[m.find(":")+1:]
                    names_list.append(m)
        else:
            imp_ful = 0
            for E in range(len(i)):
                if i[E] == "." and i[E-2] != " ":
                    imp_ful = E
                    break
            namees = i[:imp_ful].split(",")
            for O in namees:
                if O != "":
                    if ":" in O:
                        O = O[O.find(":")+2:]
                    names_list.append(O)
    
    # Delete "No presentation (cancelled)" entries 
    for i in range(len(names_list)):
        if names_list[i-1] == "No presentation (cancelled)":
            names_list.pop(i-1)
    
    # Merge the two lists 
    final_list = []
    for i in names_list+chair_names:
        if i[0] == " ":
            final_list.append(i[1:])
        else:
            final_list.append(i)
        
    return set(final_list)



#Setup - Lulz only if u b pleb 
# requests.packages.urllib3.disable_warnings()
# requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
# try:
#     requests.packages.urllib3.contrib.pyopenssl.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
# except AttributeError:
#     # no pyopenssl support used / needed / available
#     pass
def get_2020_all(verbose=False):
    """
    Get all names from the webpage : "https://ic2s2.mit.edu/program"
    
    Returns:
        set: A set of all unique names occuring in the page
    """
    # Get page content 
    LINK = "https://ic2s2.mit.edu/program"
    req = requests.get(LINK, verify= False)
    soup = BeautifulSoup(req.content, features="html.parser")
    
    # Scrape link to the page with the actuel content
    text = soup.find("div", {"class": "article-content"})
    str_text = str(text).split("src=")
    docs_link = str_text[-1].split(" ")[0][1:-1]
    
    # All names are stored in the table in the class "waffle" 
    r = requests.get(docs_link)
    soup = BeautifulSoup(r.content, features="html.parser")
    table = soup.find("table", {"class": "waffle"})
    table_rows = table.find_all("tr") # Get all rows 
    
    # Go through each row and put the data into a list (row of dataframe)
    rows = []
    for tr in table_rows[1:]:
        tds = tr.find_all('td')
        row = [td.text.replace("\n","") for td in tds]
        rows.append(row)
    
    # Make the dataframe 
    df = pd.DataFrame(rows, columns=header[0:5])
    # Extract names from column 2 (zero indexed) starting from the 1 (zero indexed) element
    names_plus = [name.split(', ') for name in list(df.iloc[:,2][1:])]
    names = []
    for name in names_plus:
        for n in name:
            if len(n) :
                names.append(n)
    if verbose: f"There are {len(set(names))} different people and {len(names)} name occurences in {LINK}"
    return list(set(names))

def get_2021_all(verbose=False): 
    """
    Get all names from the webpage : "https://easychair.org/smart-program/IC2S2-2021/talk_author_index.html"
    
    Returns:
        set: A set of all unique names occuring in the page
    """
    # Get page content 
    LINK = "https://easychair.org/smart-program/IC2S2-2021/talk_author_index.html"
    request = requests.get(LINK)
    soup = BeautifulSoup(request.content)
    
    # All names are in the table "index" and we split at "tr"; each containing one name
    contents = soup.find("table", "index")
    contents = contents.find_all("tr")
    
    # Regex compiler that finds elements between > < (not including)
    regex_compiler = re.compile("\>(.*?)\<")
    names = set()
    counter = 0
    
    # Go through each tr (statement) and split at each td find the first name and surname
    for content in contents: 
        person = str(content.find_all("td")[0])
        titles = regex_compiler.findall(person)[2:-1]
        if len(titles) == 2: # There is not exactly two elements it is not a name (but a Alphabetic code)
            name = titles[1] + " " + titles[0]
            name = name.replace(",", "")
            name = name.strip()
            
            names.add(name) 
            counter +=1

    if verbose: f"There are {len(names)} different people and {counter} name occurences in {LINK}"
    return names

def get_all_names(verbose=False):
    """
    Collects all four datasets's names into one set 

    Args:
        verbose (bool, optional): True -> prints comments about how many times names appear and how many there are
    """
    # Run the previous four methods
    names_2019_poster = get_2019_posters(verbose)
    names_2019_oral = get_2019_oral(verbose)
    names_2020_all = get_2020_all(verbose)
    names_2021_all = get_2021_all(verbose)
    
    # Collect into one set
    names_all = set()
    names_all.add(names_2019_poster)
    names_all.add(names_2019_oral)
    names_all.add(names_2020_all)
    names_all.add(names_2021_all)
    
    return names_all
    
    

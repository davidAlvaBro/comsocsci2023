from bs4 import BeautifulSoup
import requests
import re

LINK = "https://2019.ic2s2.org/posters/"
r = requests.get(LINK)
soup = BeautifulSoup(r.content, features="html.parser")

text = soup.find("div", {"class": "col-md-8"})
items = text.find_all("li")
item_list = [str(item) for item in items]

regex_compiler = re.compile("(?<=\>)(.*?)(?=\<)")

names = [regex_compiler.findall(item.split('strong')[0])[0] for item in item_list]
ind_names = [re.split(', | and', name) for name in names]
persons =  []

for list in ind_names:
    for name in list:
        persons.append(name)

print(len(persons))

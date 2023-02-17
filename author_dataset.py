import requests
import pandas as pd
import requests
import time
import numpy as np

# Get all names from week one 
import scraping
# science_people = scraping.get_all_names()

def get_ids_and_coauthors(names):
    """
    Takes in a set of names and returns a set of ids of the author and the coauthors to the authors papers

    Args:
        names (set): names of the authors
        
    Returns: 
        Set of author ids for all "names" and coauthors on all papers of "names"
    """ 
    
    # Base address for requests
    BASE_URL = "https://api.semanticscholar.org/graph/"
    VERSION  = "v1/"
    RESOURCE = "author/search?query="
    ADDITION = "&fields=papers.authors"
    complete_url = BASE_URL + VERSION + RESOURCE

    # # Temporary check if there are more than 100 authors (we don't know batching)
    # if len(ids) > 100: 
    #     return None 
    
    ids = set()
    
    # Loop over authors 
    for name in names: 
        # Make request 
        # print(complete_url + name + ADDITION) # Debugging
        response = requests.get(complete_url + name + ADDITION).json()
        
        # If something goes wrong, it will be reported here 
        try: 
            for paper in response["data"][0]["papers"]: 
                for author in paper["authors"]: 
                    ids.add(author["authorId"]) 
        except: # Usually only occurs if the author has not realeased any papers or is not found 
            print(response)
            print(name)
    
    return ids 
    
    
def save_data(data, file_name): 
    """
    A function to save a dictionary (or set) 

    Args:
        ids (data): data/set that needs to be stored
        file_name (str): file name 
    """
    np.save(f"{file_name}.npy", data)
    

def load_data(file_name):
    """
    Loads a data object (dict or set) 

    Args:
        file_name (str): file_name (without prefix)
    Returns:
        set or dict: data in the file
    """
    
    data = np.load(f"{file_name}.npy", allow_pickle=True).item()
    
    return data

def format_authors(ids_dict):
    """
    Formats a dictionary with all data of the authors into a simple dataframe

    Args:
        ids_dict (dict): a dictionary with author ids and their papers

    Returns:
        df: a dataframe of the given authors with the data; id, name, alias, citationCount, field
    """
    # Create people dataframe 
    zero_data = np.zeros((len(ids_dict.keys()), 5))
    zero_data[:] = np.nan
    df = pd.DataFrame(zero_data, columns=["id", "name", "aliases", "citationCount", "field"])

    for i, id in enumerate(ids_dict.keys()):
        # ID
        df["id"][i] = id 
        information = ids_dict[str(id)]
        # Name
        df["name"][i] = information["name"]
        # Aliases
        df["aliases"][i] = information["aliases"] 
        # citation count 
        citation_count = 0
        for paper in information["papers"]: 
            citation_count += paper["citationCount"]
        df["citationCount"][i] = citation_count
        # field - count each occurence and take the maximum 
        potential_fields = {}
        for paper in information["papers"]: 
            for fields in paper["s2FieldsOfStudy"]:
                field = fields["category"]
                try:
                    potential_fields[field] += 1
                except: 
                    potential_fields[field] = 1
        if potential_fields == {}: 
            pass
        else: 
            # This is a spicy way to do this o.0
            df["field"][i] = max(potential_fields, key=potential_fields.get)

    return df


def format_papers(ids_dict):
    """
    Formats a dictionary with all data of the authors into a simple dataframe

    Args:
        ids_dict (dict): a dictionary with author ids and their papers

    Returns:
        df: a dataframe of the given authors's papers with the data; id, title, year, DOI, citationCount, field, authors
    """
    # Start by making a dictionary of papers instead of authors
    papers = {}
    for id in ids_dict.keys():
        # get the papers 
        information = ids_dict[str(id)]
        for paper in information["papers"]:
            if paper["paperId"] in papers:
                pass
            else: 
                # Find the author id's
                authors = set()
                for author in paper["authors"]:
                    authors.add(author["authorId"])
                # Make new elements in the dictionary 
                papers[paper["paperId"]] = {"id": paper["paperId"],
                                            "title": paper["title"], 
                                            "year": paper["year"], 
                                            "doi": paper["externalIds"],
                                            "citationCount": paper["citationCount"], 
                                            "field": paper["s2FieldsOfStudy"], 
                                            "authors": authors}
    # Create the paper dataframe 
    zero_data = np.zeros((len(papers.keys()), 7))
    zero_data[:] = np.nan
    df = pd.DataFrame(zero_data, columns=["id", "title", "year", "doi", "citationCount", "field", "authors"])

    for i, id in enumerate(papers.keys()):
        # ID
        df["id"][i] = id
        information = papers[str(id)]
        # title
        df["title"][i] = information["title"]
        # Aliases
        df["year"][i] = information["year"] 
        # DOI 
        df["doi"][i] = [information["doi"]] # Can't have a dict, but it is okay to wrap it with list
        # citation count 
        df["citationCount"][i] = information["citationCount"]
        # field 
        df["field"][i] = information["field"] # Does this work? Yes somehow 
        # authors 
        df["authors"][i] = list(information["authors"])

    return df


def get_data_from_ids(ids): 
    """
    Returns a complete data frame of 
    authors (id, name, alias, citationCount, field) and
    papers (id, title, year, DOI, citationCount, field, authors)

    Args:
        ids (set): ids of the authors in question

    Returns:
        df_author: The above specified dataframe for authors
        df_paper: The above specified dataframe for papers
    """
    ids_dict = {}
    
    for id in ids:
        # Make a request for the authors aliases, name, and papers 
        BASE_URL = "https://api.semanticscholar.org/graph/"
        VERSION  = "v1/"
        full_url = BASE_URL + VERSION + "author/" + str(id)
        params = "fields=aliases,name,papers.title,papers.abstract,papers.year,papers.externalIds,papers.s2FieldsOfStudy,papers.citationCount,papers.authors"
        
        # Make request 
        request = requests.get(full_url, params=params)  
        
        # Update dictionary 
        # If something goes wrong, it will be reported here 
        try: 
            ids_dict[id] = {"name": request.json()["name"], 
                    "aliases": request.json()["aliases"],
                    "papers": request.json()["papers"]}
        except: # Usually only occurs if the author has not realeased any papers or is not found 
            print(f"The request that went wrong (id {id}): \n {request.json()}")
    
    # Just for debugging or if something goes wrong
    save_data(ids_dict, "ids_dict") # Why is this being stored in the wrong place?
    
    # Create dataframes 
    df_author = format_authors(ids_dict)
    df_paper = format_papers(ids_dict)
    
    return df_author, df_paper



if __name__=="__main__": 
    # Get names from week one 
    science_people = scraping.get_all_names()
    print("DONE WITH WEEK 1")
    
    # Get coauthors 
    ids = get_ids_and_coauthors(list(science_people)[:2]) # the [:5] is only there until we find out how to handle batching
    
    # Get dataframes of papers and authors
    if len(ids) > 200: 
        df_author, df_paper = get_data_from_ids(list(ids)[:200])
    else: 
        df_author, df_paper = get_data_from_ids(ids)
    
    pd.DataFrame.to_csv(df_author, "df_author.csv")
    pd.DataFrame.to_csv(df_paper, "df_paper.csv")
    
    





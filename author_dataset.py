import requests
import pandas as pd
import requests
import time
import numpy as np
import os 

# Get all names from week one 
import scraping
# science_people = scraping.get_all_names()
   
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

def get_ids_and_coauthors(names, file_name, load_previous=False, verbose=False):
    """
    Takes in a set of names and returns a set of ids of the author and the coauthors to the authors papers

    Args:
        names (set): names of the authors
        file_name (str): file name of where to save progress
        verbose (Boolean): whether the function should speak or not
        
    Returns: 
        ids (set): Set of author ids for all "names" and coauthors on all papers of "names"
        nin_names (set): Set of names that was not in the sematic scholar database 
    """ 
    
    # Base address for requests
    BASE_URL = "https://api.semanticscholar.org/graph/"
    VERSION  = "v1/"
    RESOURCE = "author/search?query="
    ADDITION = "&fields=papers.authors"
    complete_url = BASE_URL + VERSION + RESOURCE
    
    # The set of ids 
    ids = set()
    evaluated_names = set() 
    nin_names = set()
    
    # Check if the problem has been worked on previously 
    if load_previous:
        ids = load_data(file_name=file_name)
        evaluated_names = load_data(file_name=file_name + "_evaluated_names")
        nin_names = load_data(file_name=file_name + "_nin_names")
        if verbose: 
            print(f"{len(evaluated_names)} already evaluated of {len(names)}") 
        names = names - evaluated_names
        if verbose: 
            print(f"Hence there are {len(names)} left ")
        
    
    # Loop over authors 
    for i, name in enumerate(names):
        # We can only do 150 request each five minuts, use the down time to save progress 
        if i % 150 == 149: 
            start_time = time.time()
            # printing 
            if verbose: 
                print(f"Completed searches for {i} out of {len(names)}, but reached limit")
            # Save prograss 
            save_data(ids, file_name=file_name)
            save_data(evaluated_names, file_name=file_name + "_evaluated_names")
            save_data(nin_names, file_name=file_name + "_nin_names")
            time.sleep(60*5+10 + start_time - time.time()) # the +10 is a buffer 
        
        # Make request 
        # print(complete_url + name + ADDITION) # Debugging
        response = requests.get(complete_url + name + ADDITION).json()
        
        # If something goes wrong, it will be reported here 
        try: 
            for paper in response["data"][0]["papers"]: 
                for author in paper["authors"]: 
                    ids.add(author["authorId"]) 
        except: # Usually only occurs if the author has not realeased any papers or is not found 
            print(f"The error occured at search number {i}, the name {name} and the response is: \n {response}")
            nin_names.add(name)
        # In either case the name has been evaluated
        evaluated_names.add(name) 
               
    # Just to not mess whith the other parts of the code (amount of requests)
    if len(names) % 150 > 50: 
        time.sleep(60*5) 
    
    # Save progress for next time 
    save_data(ids, file_name=file_name)
    save_data(evaluated_names, file_name=file_name + "_evaluated_names")
    save_data(nin_names, file_name=file_name + "_nin_names")
            
    return ids, nin_names

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


def get_data_from_ids(ids, verbose=False, load_previous=True, file_name="ids_enumerated_dict"): 
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
    evaluated_ids = set()
    nin_ids = set()
    
    # Check if the problem has been worked on previously 
    if load_previous:
        ids_dict = load_data(file_name=file_name)
        evaluated_ids = load_data(file_name=file_name + "_evaluated_ids")
        nin_ids = load_data(file_name=file_name + "_nin_ids")
        if verbose: 
            print(f"{len(evaluated_ids)} already evaluated of {len(ids)}") 
        ids = ids - evaluated_ids
        if verbose: 
            print(f"Hence there are {len(ids)} left ")
    
    # Partition the ids into batches of 20 ids, because semantic scholar can only take that many 
    ids = list(ids) # temporary to get results
    default_batch_size = 64
    batch_size = default_batch_size
    n_batches = len(ids) // batch_size + 1
    batches_left = True 
    sent_requests = 0
    index = 0 
    if verbose: 
        print(f"Total number of batches are {n_batches}")
        
    #  Current file name extension
    file_extension = 0 
    file_start = 0 
    
    # Using a while loop so that we can change the sizes of the batches dynamically
    while(batches_left):
        # To avoid memory overflow save in file and move on 
        if index > file_start + 10000: 
            save_data(ids_dict, file_name=file_name+str(file_extension))
            file_start += 10000
            file_extension += 1
            ids_dict = {}
        
        # Make request for batch 
        batch_url = "https://api.semanticscholar.org/graph/v1/author/batch"
        data = {"ids": ids[index:min(index + batch_size, len(ids))]}
        # params = {"fields": "aliases,papers.title,papers.year,papers.externalIds,papers.s2FieldsOfStudy,papers.citationCount,papers.abstract,name,papers.authors"}
        params = {"fields": "aliases,papers.title,papers.year,papers.externalIds,papers.s2FieldsOfStudy,papers.citationCount,name,papers.authors"}
        response = requests.post(batch_url, json=data, params=params).json()
        sent_requests += 1
        
        # Assert the response
        if response == {'message': 'Internal server error'}:
            if verbose:
                print(f"Server error for index {index} with batch size {batch_size}")
            batch_size = batch_size // 2 
            if batch_size == 0: 
                # Save that these indexed will be removed? Dunno what else to do
                if verbose:
                    print(f"Had to remove {index} which is {ids[index]}")
                batch_size = 1 
                evaluated_ids.update(set(ids[index:min(index + batch_size, len(ids))]))
                nin_ids.update(set(ids[index:min(index + batch_size, len(ids))]))
                index += batch_size 
        else: 
            # If there is something wrong with the request
            try: 
                for person in response: 
                    # Update dictionary 
                    # If something goes wrong, it will be reported here 
                    try: 
                        ids_dict[person["authorId"]] = {"name": person["name"], 
                                "aliases": person["aliases"],
                                "papers": person["papers"]}
                    except: # Usually only occurs if the author has not realeased any papers or is not found 
                        print(response)
                        print(person)
                        print("Something is wrong with this person")
                        print(f"The index is {index} with batch size {batch_size}")
            except: 
                # If it messes up print the request and put the ids in nin 
                if verbose:  
                    print(response)
                    print(f"The index is {index} with batch size {batch_size}")
                nin_ids.update(set(ids[index:min(index + batch_size, len(ids))]))
            
            # Update processed ids 
            evaluated_ids.update(set(ids[index:min(index + batch_size, len(ids))]))
            index += batch_size
            batch_size = default_batch_size
        
        # If there has been too many request we need to break 
        if sent_requests % 150 == 149: 
            start_time = time.time()
            # printing 
            if verbose: 
                print(f"Completed searches for {index} out of {len(ids)}, but reached limit")
            # Save prograss 
            save_data(ids_dict, file_name=file_name)
            save_data(evaluated_ids, file_name=file_name + "_evaluated_ids")
            save_data(nin_ids, file_name=file_name + "_nin_ids")
            time.sleep(max(60*5+10 + start_time - time.time(), 0)) # the +10 is a buffer
        
    # Create dataframes 
    df_author = format_authors(ids_dict)
    df_paper = format_papers(ids_dict)
    
    return df_author, df_paper # Just as a test 
    
    # for batch in range(n_batches):
    #     # If there are are more than 150 batches we need breaks
    #     if batch % 150 == 149: 
    #         start_time = time.time()
    #         # printing 
    #         if verbose: 
    #             print(f"Completed searches for {batch} out of {n_batches}, but reached limit")
    #         # Save prograss 
    #         save_data(ids_dict, file_name=file_name)
    #         save_data(evaluated_ids, file_name=file_name + "_evaluated_ids")
    #         save_data(nin_ids, file_name=file_name + "_nin_ids")
    #         time.sleep(60*5+10 + start_time - time.time()) # the +10 is a buffer
        
    #     # Make request for batch 
    #     batch_url = "https://api.semanticscholar.org/graph/v1/author/batch"
    #     data = {"ids": ids[batch:min(batch + batch_size, len(ids))]}
    #     params = {"fields": "aliases,papers.title,papers.year,papers.externalIds,papers.s2FieldsOfStudy,papers.citationCount,papers.abstract,name,papers.authors"}
    #     response = requests.post(batch_url, json=data, params=params).json()
        
    #     # Save things 
    #     evaluated_ids.update(set(ids[batch:min(batch+batch_size, len(ids))]))
    #     if response == {'message': 'Internal server error'}:
    #         if verbose:
    #             print("God fucking damn it, you trash server")
    #             nin_ids.update(set(ids[batch:min(batch+batch_size, len(ids))]))
    #     else:
    #         for person in response: 
    #             # Update dictionary 
    #             # If something goes wrong, it will be reported here 
    #             try: 
    #                 ids_dict[person["authorId"]] = {"name": person["name"], 
    #                         "aliases": person["aliases"],
    #                         "papers": person["papers"]}
    #             except: # Usually only occurs if the author has not realeased any papers or is not found 
    #                 print(response)
    #                 print(f"The request that went wrong (id {person['authorId']}): \n {person}")
    
    # # Create dataframes 
    # df_author = format_authors(ids_dict)
    # df_paper = format_papers(ids_dict)
    
    # return df_author, df_paper

def create_dataframes(ids_dict):
    """A function that takes in a dictionary of authors and their papers and generates two datasets

    Args:
        ids_dict (dict): The key is an auther id, the contents is a dictionary with three atributes, "name", "aliases" and "papers".
    
    Return: 
        df_author: The above specified dataframe for authors
        df_paper: The above specified dataframe for papers
    """
    # Create dataframes 
    df_author = format_authors(ids_dict)
    df_paper = format_papers(ids_dict)
    
    return df_author, df_paper
    

if __name__=="__main__": 
    # Get names from week one if they have not been computed before 
    science_people_file_name = "names_week_1"
    if os.path.isfile(science_people_file_name + ".npy"):
        science_people = load_data(science_people_file_name)
    else: 
        science_people = scraping.get_all_names()
        save_data(science_people, science_people_file_name)
    print("DONE WITH WEEK 1")
    
    # Get coauthors 
    ids, nin_names = get_ids_and_coauthors(science_people, file_name="ids_dict", load_previous=True, verbose=True) 
    print("ALL AUTHORS COLLECTED")
    
    # Get dataframes of papers and authors
    # df_author, df_paper = get_data_from_ids(ids, load_previous=False, verbose=True)
    print("DATASET COMPLETE")
    ids_dict = load_data("ids_enumerated_dict")
    df_author, df_paper = create_dataframes(ids_dict)
    
    pd.DataFrame.to_csv(df_author, "df_author.csv")
    pd.DataFrame.to_csv(df_paper, "df_paper.csv")
    
    
# CS122: Linking restaurant records in Zagat and Fodor's data sets
#
# Jake Underland


import numpy as np
import pandas as pd
import jellyfish
import util

def find_matches(mu, lambda_, block_on_city=False):
    '''
    Takes zagat and fodors restaurant information and sorts restaurants into 
    a dataframe showing matches, unmatches, and possible matches.
    Inputs:
      mu (float): maximum false positive
      lambda_ (float): maximum false negative
      block_on_city: boolean indicating whether to block city or not.
    Returns:
      matches_df, possible_df, unmatches_df
    '''
    zagat, fodors, matches, unmatches = read_data()
    
    # Using testing data to produce tuple_partitions 
    match_freq = create_tuple_freq_dic(matches)
    unmatch_freq = create_tuple_freq_dic(unmatches)
    tuples_u_m = map_tuples_to_um(match_freq, unmatch_freq)
    match_tuples, unmatch_tuples = \
        partition_tuples(tuples_u_m, mu, lambda_)

    # Produce final dataframes 

    return produce_dfs(zagat, fodors, match_tuples, unmatch_tuples, block_on_city)


def read_data(name_z_file="zagat.csv", name_f_file="fodors.csv", known_links_file="known_links.csv"):
    '''
    Reads in data from csv files and returns the main objects we manipulate
    in this project. 

    Inputs:
      name_z_file (optional): the name of the zagat restaurant file
      name_f_file (optional): the name of the fodors restaurant file
      known_links_file (optional): the name of the known_links file 
    Returns:
      zagat: pandas dataframe conatinaing zagat restaurant info
      fodors: pandas dataframe conatinaing fodors restaurant info
      matches: pandas dataframe containing information from all known matches
      unmatches: pandas dataframe of a random sample of unmatched restaurants
    '''
    zagat = pd.read_csv(name_z_file, names = ["rname_z", "city_z", "address_z"])
    fodors = pd.read_csv(name_f_file, names = ["rname_f", "city_f", "address_f"])

    known_links = pd.read_csv(known_links_file, names = ["zagat", "fodors"], 
                            index_col=False)
    merged_df = pd.merge(left = known_links, right = zagat, left_on = "zagat", 
                        right_index = True)
    merged_df = pd.merge(left = merged_df, right = fodors, left_on = "fodors", 
                        right_index = True)
    matches = merged_df.loc[:, "rname_z":"address_f"]

    zs = zagat.sample(1000, replace = True, random_state = 1234)
    fs = fodors.sample(1000, replace = True, random_state = 5678)
    unmatches = pd.concat([zs.reset_index().rename(columns={"index": "index_z"}), 
                        fs.reset_index().rename(columns={"index": "index_f"})], 
                        axis = 1)
    return zagat, fodors, matches, unmatches


def create_tuple_freq_dic(df):
    '''
    Given a dataframe containing information from both restaurant databases, 
    computes a dictionary that maps all the jaro-wrinkler tuples that appeared 
    among the pair of restaurants to their frequency.
    Inputs:
      df: a pandas dataframe 
    Returns:
      tuple_frequency: a dictionary that maps jaro-wrinkler tuples to frequency
    '''
    tuple_frequency = {}
    for row in df.itertuples(index=False):
        jw_tuple = convert_jw_tuple(row, row)
        tuple_frequency[jw_tuple] = tuple_frequency.get(jw_tuple, 0) + 1
    
    return tuple_frequency

def convert_jw_tuple(row_z, row_f):
    '''
    Given two row objects from a pandas dataframe, each containing 
    information of a restaurant, computes the jaro_winkler tuple of 
    the two restaurants from each row. 
    Inputs:
      row_z: Row from zagat
      row_f: row from fodors
    Returns tuple with jarowrinkler for the categories (name, city, address)
    '''
    name_jw = jellyfish.jaro_winkler(row_z.rname_z, row_f.rname_f)
    city_jw = jellyfish.jaro_winkler(row_z.city_z, row_f.city_f)
    addr_jw = jellyfish.jaro_winkler(row_z.address_z, row_f.address_f)
    jw_tuple = tuple(map(util.get_jw_category, (name_jw, city_jw, addr_jw)))
    return jw_tuple

def map_tuples_to_um(match_freq, unmatch_freq):
    '''
    Given dictionaries mapping tuples of matches to their frequencies and 
    tuples of unmatches to their frequencies, creates a dictionary mapping 
    each tuple to its u(w), m(w), and m(w)/u(w) values. Absence of a key
    indicates that value is nonexistent, or zero. 
    Inputs:
      match_freq: dictionary mapping tuples of matches to their frequencies
      unmatch_freq: dictionary 
    Returns dictionary mapping jaro_winkler tuples to its u(w), m(w), m(w)/u(w)
    '''
    tuples_u_m = {}
    matches_sum = sum(match_freq.values())
    unmatches_sum = sum(unmatch_freq.values())

    for tup, freq in unmatch_freq.items():
        tuples_u_m[tup] = {"u": freq / unmatches_sum, "m/u": 0}  # initialize m/u to zero
    for tup, freq in match_freq.items():
        if tuples_u_m.get(tup):
            tuples_u_m[tup]["m"] = freq / matches_sum
            tuples_u_m[tup]["m/u"] = tuples_u_m[tup]["m"] / tuples_u_m[tup]["u"]
        else:
            tuples_u_m[tup] = {"m": freq / matches_sum}
            tuples_u_m[tup]["m/u"] = float('inf')
    
    return tuples_u_m


def partition_tuples(tuples_u_m, mu, lambda_):
    '''
    Partition tuples into match_tuples and unmatch_tuples. 
    Whatever tuples are not in the above two will be sorted into 
    possible_tuples later, but no such list is necessary for this, and has been 
    omitted here. 
    Inputs:
      tuples_u_m (dic): maps jaro_winkler tuples (appearing in the testing data)
       to its u(w), m(w), m(w)/u(w)
      mu(float): mu value
      lambda_(float): lambda value
    Returns:
      match_tuples (list): list of match tuples
      unmatch_tuples(list) : lsit of unmatch tuples
    '''
    match_tuples = []
    unmatch_tuples = []

    sorted_tuples_um = sorted(tuples_u_m.items(), key=lambda tup: tup[1]["m/u"], 
                              reverse=True)
    remaining_tups = []  # to avoid double counting in matches and unmatches
    cum_u = 0  # cumulative u
    cum_m = 0

    for i, item in enumerate(sorted_tuples_um):
        tup, um_dic = item # unpack dictionary mapping m, u, m/u to values
        if um_dic["m/u"] == float('inf'):
            match_tuples.append(tup)
        elif cum_u + um_dic.get("u", 0) <= mu:
            match_tuples.append(tup)
            cum_u += um_dic.get("u", 0)
        else:
            remaining_tups = sorted_tuples_um[:i-1:-1]
            break

    for i, item in enumerate(remaining_tups):
        tup, um_dic = item
        if cum_m + um_dic.get("m", 0) <= lambda_:
            unmatch_tuples.append(tup)
            cum_m += um_dic.get("m", 0)
    
    return match_tuples, unmatch_tuples


def produce_dfs(zagat, fodors, match_tuples, unmatch_tuples, block_on_city):
    '''
    Produces final output dataframes given the zagat dataframe, fodors dataframe, 
    list of match_tuples, list of unmatch_tuples, and the boolean for block on 
    city. 
    Inputs:
      zagat: pandas dataframe with zagat info
      fodors: pandas dataframe with fodors info
      match_tuples (list): list of match tuples
      unmatch_tuples(list) : lsit of unmatch tuples
      block_on_city: boolean indicating whether to block city or not.
    Returns:
      matches_df, possible_df, unmatches_df
    '''
    match_z = []
    match_f = []
    unmatch_z = []
    unmatch_f = []
    possible_z = []
    possible_f = []
    for row_z in zagat.itertuples():
        i_z = row_z.Index
        for row_f in fodors.itertuples():
            i_f = row_f.Index
            if not (block_on_city and row_z.city_z != row_f.city_f):  # block_city
                jw_tuple = convert_jw_tuple(row_z, row_f)
                if jw_tuple in match_tuples:
                    match_z.append(i_z)
                    match_f.append(i_f)
                elif jw_tuple in unmatch_tuples:
                    unmatch_z.append(i_z)
                    unmatch_f.append(i_f)
                else:
                    possible_z.append(i_z)
                    possible_f.append(i_f)

    matches_df = pd.concat([zagat.loc[match_z].reset_index(drop=True), 
                           fodors.loc[match_f].reset_index(drop=True)], axis = 1)
    unmatches_df = pd.concat([zagat.loc[unmatch_z].reset_index(drop=True), 
                           fodors.loc[unmatch_f].reset_index(drop=True)], axis = 1)
    possible_df = pd.concat([zagat.loc[possible_z].reset_index(drop=True), 
                           fodors.loc[possible_f].reset_index(drop=True)], axis = 1)
    
    return matches_df, possible_df, unmatches_df
                
 



if __name__ == '__main__':
    matches, possibles, unmatches = \
        find_matches(0.005, 0.005, block_on_city=False)

    print("Found {} matches, {} possible matches, and {} "
          "unmatches with no blocking.".format(matches.shape[0],
                                               possibles.shape[0],
                                               unmatches.shape[0]))







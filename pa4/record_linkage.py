# CS122: Linking restaurant records in Zagat and Fodor's data sets
#
# Jake Underland


import numpy as np
import pandas as pd
import jellyfish
import util

def find_matches(mu, lambda_, block_on_city=False):
    zagat, fodors, matches, unmatches = read_data()
    
    # Using testing data to produce tuple_partitions 
    match_freq = create_tuple_freq_dic(matches)
    unmatch_freq = create_tuple_freq_dic(unmatches)
    tuples_u_m = map_tuples_to_um(match_freq, unmatch_freq)
    possible_tuple_combinations = create_combinations(["high", "medium", "low"], 3)
    match_tuples, possible_tuples, unmatch_tuples = \
        partition_tuples(possible_tuple_combinations, tuples_u_m, mu, lambda_)

    # Produce final dataframes 

    return produce_dfs(zagat, fodors, match_tuples, possible_tuples, unmatch_tuples)


def read_data(name_z="zagat.csv", name_f="fodors.csv", know_links="known_links.csv"):
    zagat = pd.read_csv("zagat.csv", names = ["rname_z", "city_z", "address_z"])
    fodors = pd.read_csv("fodors.csv", names = ["rname_f", "city_f", "address_f"])
    known_links = pd.read_csv("known_links.csv", names = ["zagat", "fodors"], 
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
    tuple_frequency = {}
    for row in df.itertuples(index=False):
        jw_tuple = convert_jw_tuple(row, row)
        tuple_frequency[jw_tuple] = tuple_frequency.get(jw_tuple, 0) + 1
    
    return tuple_frequency

def convert_jw_tuple(row_z, row_f):
    name_jw = jellyfish.jaro_winkler(row_z.rname_z, row_f.rname_f)
    city_jw = jellyfish.jaro_winkler(row_z.city_z, row_f.city_f)
    addr_jw = jellyfish.jaro_winkler(row_z.address_z, row_f.address_f)
    jw_tuple = tuple(map(util.get_jw_category, (name_jw, city_jw, addr_jw)))
    return jw_tuple

def map_tuples_to_um(match_freq, unmatch_freq):
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


def partition_tuples(combinations, tuples_u_m, mu, lambda_):
    match_tuples = []
    unmatch_tuples = []
    possible_tuples = [tup for tup in combinations if not tuples_u_m.get(tup)]

    sorted_tuples_um = sorted(tuples_u_m.items(), key=lambda tup: tup[1]["m/u"], 
                              reverse=True)
    remaining_tups = []  # to avoid double counting in matches and unmatches
    cum_u = 0  # cumulative u
    cum_m = 0

    for i, item in enumerate(sorted_tuples_um):
        tup, um_dic = item
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
        else:
            possible_tuples += [tup for tup, _ in remaining_tups[:i-1:-1]]
    
    return match_tuples, possible_tuples, unmatch_tuples
    

def create_combinations(pattern_lst, len_row):
    if len_row == 1:
        return [(element,) for element in pattern_lst]
    else:
        final_product = []
        for element in pattern_lst:
            for sub_element in create_combinations(pattern_lst, len_row - 1):
                final_product.append((element,) + sub_element)
        
        return final_product

def produce_dfs(zagat, fodors, match_tuples, possible_tuples, unmatch_tuples):
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
                

    



# iterating through, use apply (where one of the data frames will be expanded to iterate through), 
# add column with possible, match, unmatch, seed each with an index and combine? 
# or, as suggested by prof, take indices, record, then slice them. Can groupby be used by any chance? 


# add to list of indices: one for z and the other for f. then slice and merge to get final dataframe. 

# test_merge = pd.concat([zagat.loc[[1, 2, 3, 5, 6]].reset_index(drop=True), fodors.loc[[87, 24, 3, 1, 5]].reset_index(drop=True)], axis = 1) 






if __name__ == '__main__':
    matches, possibles, unmatches = \
        find_matches(0.005, 0.005, block_on_city=False)

    print("Found {} matches, {} possible matches, and {} "
          "unmatches with no blocking.".format(matches.shape[0],
                                               possibles.shape[0],
                                               unmatches.shape[0]))







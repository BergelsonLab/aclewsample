import sys
import pandas as pd

corpora_file = "data/ACLEW_list_of_corpora.csv"

def unique_n_children(df, n, exclude_ids=[]):
    selected = pd.DataFrame(columns = df.columns.values)
    while selected.shape[0] < n:
        picked = _uniform_category_sample(df, n=1, cat='std_mat_ed')
        picked_id = picked.iloc[0]['child_level_id']

        # if picked child not already picked from previous session
        # (when picking the 2x 9mo < age < 14mo), passed in as exclude_ids,
        # then...
        if picked_id not in exclude_ids:
                # add to selected
                selected = selected.append(picked)
                # remove records from selection pool with the same child_level_id,
                # child has been selected once, out of the pool for future selections
                df = df.drop(df.index[df['child_level_id'] == picked_id])
    return selected

def _uniform_category_sample(df, n, cat):
    """
    Normalize P(x_i), where x_i is the i'th member of category x
    so that the distribution across categories is uniform. Solution is
    to set

    P(x_i) = (1/K) / |x|

    where K is the # of categories and |x| is the frequency of
    elements of category x.

    :param df:
    :return:
    """

    df['weight'] = 0
    categories = df[cat].unique()
    K = categories.shape[0]

    # calculate weights
    for name, group, in df.groupby(cat):
        n_x = group.shape[0] # |x| (number of records with this category)
        p_i = (1/float(K))/n_x
        df.loc[df[cat] == name, 'weight'] = p_i

    # pick n samples, given the weights
    picked = df.sample(n, weights='weight')

    return picked


def _sample(corpus):
    '''
    :param corpus: the df containing just 1 lab's entries in the ACLEW corpora spreadsheet
    :return: 2 unique entries from 09-14mo and 8 unique entries from 0-36mo,
             as separate df's. The combined 10 entries are all unique children
    '''
    # just the entries between 09 and 14 months
    within_09_14 = corpus.query('(age_mo_round >= 9) & (age_mo_round <= 14)')
    # sample a random unique 2 from within_09_14
    the_2 = unique_n_children(within_09_14, 2)
    # remove those already sampled 2 from the original corpus
    without_the2 = corpus.drop(the_2.index)
    # filter without_the2 for only 0-36mo olds
    the_rest_in_agerange = without_the2.query('(age_mo_round >= 0) & (age_mo_round <= 36)')
    # get a unique 8 recordings (keeping in mind the previous 2 already
    # selected, passed as "exclude_ids") from the_rest_in_agerange
    the_8 = unique_n_children(the_rest_in_agerange, 8, exclude_ids=the_2['child_level_id'].values.tolist())
    return the_2, the_8

def sample(aclew_corpora_file, output_csv=""):
    corpora = pd.read_csv(aclew_corpora_file)
    selected = pd.DataFrame(columns = corpora.columns.values)
    # group by corpus and sample
    for name, corpus in corpora.groupby('corpus'):
        if name == "Seedlings":
            print
        the_2, the_8 = _sample(corpus)
        selected = selected.append([the_2, the_8])
    if output_csv:
        selected.to_csv(output_csv, index=False)
    return selected


if __name__ == "__main__":
    aclew_csv = sys.argv[1]
    output_csv = sys.argv[2]
    sample(aclew_csv, output_csv)

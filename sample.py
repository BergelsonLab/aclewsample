import sys
import pandas as pd

corpora_file = "data/ACLEW_list_of_corpora.csv"

def unique_n_children(df, n, exclude_ids=[]):
    selected = pd.DataFrame(columns = df.columns.values)
    # loop until you've picked out n recordings,
    # selecting one at a time
    while selected.shape[0] < n:
        # sample 1 recording using uniform std_mat_ed
        # categorical distribution
        picked = _uniform_category_sample(df, n=1, cats=['std_mat_ed', 'child_sex'])
        picked_id = picked.iloc[0]['child_level_id']
        # if picked child not already picked from previous session
        # (from when picking the 2x 9mo < age < 14mo, passed in as exclude_ids list),
        # then...
        if picked_id not in exclude_ids:
                # add to selected
                selected = selected.append(picked)
                # remove records from selection pool with the same child_level_id,
                # child has been selected once, out of the pool for future selections
                df = df.drop(df.index[df['child_level_id'] == picked_id])
    return selected


def _uniform_category_sample(df, n, cats):
    """
    P(X) is the probability mass function over the set of recordings.

    We need to normalize P(x_i), where x_i is the i'th instance belonging to category x,
    so that the prob distribution across categories is uniform. Solution is
    to set

    P(x_i) = (1/K) / |x|

    where K is the # of categories and |x| is the frequency of
    elements in category x.

    If you're only normalizing against a single categorical variable, you do this
    once and you're done. Given multiple category constraints (e.g. maternal education
    as well as gender), You calculate separate distributions P(X) for each
    categorical variable, multiply them together, and normalize against the summed
    probabilities so everything adds up to 1 again. Those normalized numbers are your
    final weights.
    """
    df['weight'] = 1
    for cat in cats:
        weight_col = 'weight_{}'.format(cat)
        df[weight_col] = 0
        K = df[cat].unique().shape[0]
        for name, group, in df.groupby(cat):
            n_x = group.shape[0]  # |x| (number of records with this category)
            p_i = (1 / float(K)) / n_x
            df.loc[df[cat] == name, 'weight_{}'.format(cat)] = p_i
        df['weight'] = df['weight'] * df[weight_col]
        # get rid of single category weight col, it's already
        # multiplied into the aggregated 'weight' col
        df = df.drop(weight_col, axis=1)

    # normalize the final weight so all probabilities add up to 1
    df['weight'] = df['weight'] / df['weight'].sum()

    # pick n samples, given the weights
    return df.sample(n, weights='weight')


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
        the_2, the_8 = _sample(corpus)
        selected = selected.append([the_2, the_8])
    selected = selected.drop('weight', axis=1) # get rid of weight column
    if output_csv:
        selected.to_csv(output_csv, index=False)
    return selected


if __name__ == "__main__":
    aclew_csv = sys.argv[1]
    output_csv = sys.argv[2]
    sample(aclew_csv, output_csv)

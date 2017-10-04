import sys
import pandas as pd
import math

corpora_file = "data/ACLEW_list_of_corpora.csv"

# tuple of (df, score) where score is the score returned by
#  _objective_func() (i.e. the number we're minimizing)
best_run = (None, 10000)

# weights on normalizing variables
w_age = 1.0 # child age
w_gen = 0.9 # child gender
w_med = 0.5 # maternal education

def unique_n_children(df, n, exclude_ids=[], zero=False):
    selected = pd.DataFrame(columns = df.columns.values)
    # loop until you've picked out n recordings,
    # selecting one at a time
    while selected.shape[0] < n:
        # sample 1 recording using uniform std_mat_ed
        # categorical distribution
        if zero and not selected.empty:
            prev_gender = selected.iloc[0].child_sex
            picked = _uniform_category_sample(df, n=1, cats=['std_mat_ed', 'child_sex'], zero_gender=prev_gender)
            picked_id = picked.iloc[0]['child_level_id']
        else:
            picked = _uniform_category_sample(df, n=1, cats=['std_mat_ed', 'child_sex'])
            picked_id = picked.iloc[0]['child_level_id']
        # if picked child not already picked from previous session
        # (from when picking the 2x 9mo < age < 14mo, passed in as exclude_ids list),
        # then...
        if picked_id not in exclude_ids:
                # add to selected
                selected = selected.append(picked)[picked.columns.tolist()]
                # remove records from selection pool with the same child_level_id,
                # child has been selected once, out of the pool for future selections
                df = df.drop(df.index[df['child_level_id'] == picked_id])
    return selected


def _uniform_category_sample(df, n, cats, zero_gender=""):
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

    # if zero_gender is passed in, set that gender's weight really low (can't use 0
    # because of cases where the other gender is not left in the remaining pool)
    if zero_gender:
        df.loc[df['child_sex'] == zero_gender, 'weight'] = 0.0000001

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
    the_2 = unique_n_children(within_09_14, n=2, zero=True)
    # remove those already sampled 2 from the original corpus
    without_the2 = corpus.drop(the_2.index)
    # filter without_the2 for only 0-36mo olds
    the_rest_in_agerange = without_the2.query('(age_mo_round >= 0) & (age_mo_round <= 36)')
    # get a unique 8 recordings (keeping in mind the previous 2 already
    # selected, passed as "exclude_ids") from the_rest_in_agerange
    the_8 = unique_n_children(the_rest_in_agerange, n=8, exclude_ids=the_2['child_level_id'].values.tolist())
    return the_2, the_8

def sample(corpora, output_csv=""):
    selected = pd.DataFrame(columns = corpora.columns.values)
    # group by corpus and sample
    for name, corpus in corpora.groupby('corpus'):
        # if name == "Seedlings":
        #     print
        the_2, the_8 = _sample(corpus)
        selected = selected.append([the_2, the_8])[the_2.columns.tolist()]
    selected = selected.drop('weight', axis=1) # get rid of weight column
    if output_csv:
        selected.to_csv(output_csv, index=False)
    return selected

def optimize(full, output_csv="", n=50):
    """
    The goal is to minimize the number in best_run[1], where best_run
    is a tuple of (df, score).

    :param full: the full corpora dataframe
    :param output_csv:
    :param n: number of rounds of optimization passes (default = 50)
    :return: the optimal (so far, given n) sampled dataframe
    """
    global best_run
    for i in range(n):
        # perform a sample
        result = sample(full)
        # score it against the objective function
        score = _objective_func(full, result)
        # if the score is lower than the best_run so far...
        if score < best_run[1]:
            # set best run to this latest sample
            best_run = (result, score)
        print "optim #{}: {:.4f},   best so far: {:.4f}".format(i+1, score, best_run[1])
    if output_csv:
        best_run[0].to_csv(output_csv)
    return best_run[0]


def _objective_func(full, sampled):
    """
    :param full: the full corpora list
    :param sampled: the sampled set
    :return: the score for how far away the given sample is
            from the ideally uniform sample. Here it's the weighted
            sum of the KL-Divergences of each lab's sample relative
            to the hypothetical uniform distribution, for each
            categorical variable
    """
    kl_sum = 0
    for corpus, df in sampled.groupby('corpus'):
        child_age_kl = _kl_diverge('age_mo_round', full[full['corpus']==corpus], df)
        child_sex_kl = _kl_diverge('child_sex', full[full['corpus'] == corpus], df)
        mat_ed_kl    = _kl_diverge('std_mat_ed', full[full['corpus']==corpus], df)

        # the sum of the weighted D_kl() for each categorical variable
        kl_sum += w_age*child_age_kl + w_gen*child_sex_kl + w_med*mat_ed_kl
    return kl_sum


def _kl_diverge(categ, full, df):
    """
    The KL-divergence between the sampled distribution
    and the hypothetical uniform distribution given an alphabet
    of N categories and channel size of whatever the per corpus
    sample size is.

    :param categ: the categorical variable
    :param full: full pre-sampled dataset
    :param df: sampled subset
    :return: D_kl(P||U), where P is the probability of a category,
            and U is the hypothetical uniform distribution over categories
    """
    cats = full[categ].unique()
    # prob distribution of category in sample
    p_cat = [df[df[categ] == x].shape[0] / float(df.shape[0])
             for x in cats]
    # the uniform distribution
    u_cat = [1 / float(len(cats))
             for x in cats]

    # can't take log(0), add constant (in this case 1) to avoid that
    kl = sum((p+1) * math.log((p+1) / (u+1), 2) for p, u in zip(p_cat, u_cat))
    return kl


if __name__ == "__main__":
    aclew_full = pd.read_csv(sys.argv[1])
    output_csv = sys.argv[2]
    if "--optimize" in sys.argv:
        optimize(aclew_full, output_csv=output_csv, n=150)
    else:
        sample(aclew_full, output_csv)

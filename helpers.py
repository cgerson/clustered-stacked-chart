import pandas as pd

def rename_labels(df, column, mapping):

    """
    mapping: ex - {'Even': 'Light', "Odd": "Dark"}
    """

    df[column] = df[column].map(mapping)

    return df

def transform_for_clustered_chart(df, values, column1, column2 = None, demo = None):

    if demo:
        subset_by = [values, column1]
    else:
        subset_by = [values, column1, column2]

    sub = df[df['question'].isin(subset_by)][['answer','question','sessionId']].set_index('sessionId')
    pivot_all = sub.pivot(columns='question',values='answer')

    if demo:
        column2 = demo
        demos = df[['sessionId',demo]].drop_duplicates().set_index('sessionId')
        pivot_all = pivot_all.merge(demos, how='inner', left_index=True, right_index=True)

    pivoted = pivot_all[[column1,column2,values]].copy()

    pivoted.dropna(how='any', inplace=True)

    print "sample_size", len(pivoted)

    df_sub = pd.DataFrame(pivoted.groupby([column2,
                                           column1,
                                           values]).size()).reset_index()

    df_sub = df_sub.rename(columns={0:'values'})

    df_sub_pivoted = df_sub.pivot_table(values='values',index=[column1,column2], columns=values, fill_value=0)

    df_sub_pivoted = df_sub_pivoted.apply(lambda x: x*100/sum(x), axis=1)

    return df_sub_pivoted.reset_index()

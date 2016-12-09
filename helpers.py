import pandas as pd

def rename_labels(df, column, mapping):

    """
    mapping: ex - {'Even': 'Light', "Odd": "Dark"}
    """

    df[column] = df[column].map(mapping)

    return df

def transform_for_clustered_chart(df, values, column1, column2):

    sub = df[df['question'].isin([values, column1, column2])][['answer','question','sessionId']].set_index('sessionId')

    pivoted = sub.pivot(columns='question',values='answer')

    df_sub = pd.DataFrame(pivoted.groupby([column2,
                                           column1,
                                           values]).size()).reset_index()

    df_sub = df_sub.rename(columns={0:'values'})

    df_sub_pivoted = df_sub.pivot_table(values='values',index=[column1,column2], columns=values)

    df_sub_pivoted = df_sub_pivoted.apply(lambda x: x*100/sum(x), axis=1)

    return df_sub_pivoted.reset_index()

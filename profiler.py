import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

#  scoping helper functions
#  pep 8
#  doc string
#  commenting
#  read me

#  todo type checker function
#  todo field relationship finder

def table_summary(df):
    columns = df.shape[1]
    rows = df.shape[0]
    population_rate = abs((df.isnull().sum().sum()) /                         (df.shape[0] * df.shape[1]) - 1)
    population_rate = "{:.2%}".format(population_rate)
    duplicate_records = len(df[df.duplicated() == True])
    dtype_list = df.dtypes
    int_count = (
        len(dtype_list[dtype_list == 'int64']) +                            len(dtype_list[dtype_list == 'int32']) +
        len(dtype_list[dtype_list == 'int16']) +                            len(dtype_list[dtype_list == 'int8'])
                 )
    float_count = (
        len(dtype_list[dtype_list == 'float64']) +                          len(dtype_list[dtype_list == 'float32']) +
        len(dtype_list[dtype_list == 'float16'])
                    )
    categorical_count = len(dtype_list[dtype_list == 'object'])
    datetime_count = len(dtype_list[dtype_list == 'datetime64[ns]'])
    if (int_count + float_count + categorical_count + datetime_count)         != columns:
        raise TypeError('Some columns ignored - investigate additional column types!')

    names = (
            ["columns", "rows", "population_rate", "duplicate_records",       "int_count", "float_count",
             "categorical_count", "datetime_count"]
            )
    tbl_summary = pd.Series(
        [columns, rows, population_rate, duplicate_records, int_count,float_count, categorical_count, datetime_count], index=names
                            )

    unique_list = []
    counter = 0
    index = []
    for col in df.columns:
        if df[col].isnull().sum() == 0 and df[col].count()                   == df[col].nunique():
            unique_list.append(col)
            counter += 1
            index.append('possible_key_' + str(counter))
        elif df[col].isnull().sum() != 0 and df[col].count()                 == df[col].nunique():
            pass  # todo could add as potential primary key with nulls - consider
        else:
            pass

    possible_keys = pd.Series(unique_list, index=index, dtype='object')
    tbl_summary = pd.DataFrame(pd.concat([tbl_summary, possible_keys]), columns=['result'])
    return tbl_summary


def field_summary(df):
    percentiles = [.01, .05, .25, .5, .75, .9, .95, .99]
    numeric_index = (
            ["count", "nulls", "count unique", "mean", "sum", "std",          "skewness", "kurtosis", "min"] +                              ["{:.0%}".format(x) for x in percentiles] + ['max']
                    )
    object_index = ["count", "nulls", "count unique", "top", "frequency"]
    datetime_index = ["count", "nulls", "count unique", "top", "frequency",   "min", "max"]
    stats = pd.Series(dtype='object')  # this is default type for empty series - avoiding warnings

    def is_int(column):  # helper function
        return (df[column].dtype == 'int64' or df[column].dtype == 'int32'   or df[column].dtype == 'int16' or df[column].dtype == 'int8')

    def is_float(column):  # helper function
        return (df[column].dtype == 'float64' or df[column].dtype == 'float32' or df[column].dtype == 'float16')

    for col in df.columns:
        if is_int(col):
            result = (
                    [df[col].count(), df[col].isnull().sum(),                df[col].nunique(), df[col].mean(),
                     df[col].sum(), df[col].std(), df[col].skew(),           df[col].kurtosis(),
                     df[col].min()] + df[col].quantile(percentiles).tolist()  + [df[col].max()]
                    )
            result_srs = pd.Series(result, index=numeric_index,             name=df[col].name)
            summary = pd.concat([stats, result_srs], axis=1)
            stats = summary

        elif is_float(col):
            result = (
                      [df[col].count(), df[col].isnull().sum(),              df[col].nunique(), df[col].mean(),
                       df[col].sum(), df[col].std(), df[col].skew(),          df[col].kurtosis(),
                       df[col].min()] + df[col].quantile(percentiles).tolist() + [df[col].max()]
                      )
            result_srs = pd.Series(result, index=numeric_index,             name=df[col].name)
            summary = pd.concat([stats, result_srs], axis=1)
            stats = summary

        elif df[col].dtype == 'object':
            result = (
                      [df[col].count(), df[col].isnull().sum(),              df[col].nunique(), df[col].value_counts().index[0], df[col].value_counts()[0]]
                      )
            result_srs = pd.Series(result, index=object_index,              name=df[col].name)
            summary = pd.concat([stats, result_srs], axis=1)
            stats = summary

        elif df[col].dtype == 'datetime64[ns]':
            result = (
                     [df[col].count(), df[col].isnull().sum(),               df[col].nunique(), df[col].value_counts().index[0], df[col].value_counts()[0], df[col].min(),            df[col].max()]
                     )
            result_srs = pd.Series(result, index=datetime_index,            name=df[col].name)
            summary = pd.concat([stats, result_srs], axis=1)
            stats = summary

        else:
            raise TypeError(f'fields including {col} of type {df[col].dtype} cannot be summarized')

    stats = stats.drop(columns=[0])
    return stats


def correlation_scores(df):
    corr = df.corr()
    correlation_df = pd.DataFrame()

    for index, value in enumerate(corr.columns):
        corr_column = pd.DataFrame(corr.iloc[:,index])
        corr_column['column2'] = value
        corr_column.rename(columns = {f'{value}':'correlation_score'},   inplace=True)
        correlation_df = pd.concat([correlation_df, corr_column])

    correlation_df.reset_index(inplace=True)
    correlation_df.rename(columns = {'index':'column1'}, inplace=True)
    correlation_df = correlation_df[['column1', 'column2',                    'correlation_score']]
    correlation_df = correlation_df[(correlation_df['correlation_score'].isnull() != True) & (correlation_df['correlation_score'] != 1)].sort_values('correlation_score', ascending=False)
    return correlation_df


def visual_profiling(df, num_values =  None):

    max_values = 50 if num_values == None else num_values

    folders = ['int_histograms', 'float_histograms', 'object_counts', 'datetime_counts']

    for folder in folders:
        if not os.path.exists(os.path.join(os.getcwd(), folder)):
            os.mkdir(folder)

    def is_int(column):
        return (df[column].dtype == 'int64' or df[column].dtype == 'int32' or
            df[column].dtype == 'int16' or df[column].dtype == 'int8')

    def is_float(column):
        return (df[column].dtype == 'float64' or df[column].dtype == 'float32' or df[column].dtype == 'float16')

    for col in df.columns:
        if is_int(col):
            if df[col].isnull().sum() < len(df[col]):
                fig = plt.figure(figsize=(10, 8));
                sns.distplot(df[col], kde=False)
                fig.savefig(f"int_histograms\{col}.png")
                plt.close()

        elif is_float(col):
            if df[col].isnull().sum() < len(df[col]):
                fig = plt.figure(figsize=(10, 8));
                sns.distplot(df[col], kde=False)
                fig.savefig(f"float_histograms\{col}.png")
                plt.close()

        elif df[col].dtype == 'object':
            if df[col].isnull().sum() < len(df[col]):
                if df[col].nunique() <= max_values:
                    fig = plt.figure(figsize=(10, 8));
                    val_counts = df[col].value_counts()
                    sns.barplot(x=val_counts.index, y=val_counts)
                    plt.xticks(rotation=90)
                    fig.savefig(f"object_counts\{col}.png")
                    plt.close()

        elif df[col].dtype == 'datetime64[ns]':
            if df[col].isnull().sum() < len(df[col]):
                year_month = pd.DataFrame(df[col].dt.to_period('M')) # getting high level period: year-month
                year_month = year_month.groupby(col)[col].count()
                fig = plt.figure(figsize=(10, 8));
                year_month.plot(figsize = (10,8))
                fig.savefig(f"datetime_counts\{col}.png")
                plt.close()

        else:
            raise TypeError('Type Not Accounted For')


def overall_summary(df, num_values = None):
    writer = pd.ExcelWriter("data_summary.xlsx", engine='xlsxwriter')
    table_summary(df).to_excel(writer, sheet_name='table_summary')
    field_summary(df).to_excel(writer, sheet_name='field_summary')
    correlation_scores(df).to_excel(writer, sheet_name='correlation_scores', index=False)
    writer.save()

    print('... data summary complete')

    print('... working on visual profiling')

    visual_profiling(df, num_values)

    print('... visual profiling complete')


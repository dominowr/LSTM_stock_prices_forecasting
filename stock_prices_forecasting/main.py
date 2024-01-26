import pandas as pd
import datetime
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv('KWHIY.csv')
df = df[['Date', 'Close']]
df['Date'] = pd.to_datetime(df['Date'])
df.index = df.pop('Date')


#
# plt.plot(df.index, df['Close'])
# plt.show()


def df_to_windowed_df(dataframe, first_date_str, last_date_str, n=3):
    first_date = pd.to_datetime(first_date_str)
    last_date = pd.to_datetime(last_date_str)

    target_date = first_date

    dates = []
    X, Y = [], []

    last_time = False
    while True:
        df_subset = dataframe.loc[:target_date].tail(n + 1)

        if len(df_subset) != n + 1:
            print(f'Error: Window of size {n} is too large for date {target_date}')
            return

        values = df_subset['Close'].to_numpy()
        x, y = values[:-1], values[-1]

        dates.append(target_date)
        X.append(x)
        Y.append(y)

        next_week = dataframe.loc[target_date:target_date + datetime.timedelta(days=7)]
        next_datetime_str = str(next_week.head(2).tail(1).index.values[0])
        next_date_str = (next_datetime_str.split('T')[0])
        year_month_day = next_date_str.split('-')

        year, month, day = year_month_day
        next_date = datetime.datetime(day=int(day), month=int(month), year=int(year))

        if last_time:
            break
        target_date = next_date

        if target_date == last_date:
            last_time = True

    ret_df = pd.DataFrame({})
    ret_df['Target Date'] = dates

    X = np.array(X)
    for i in range(0, n):
        ret_df[f'Target-{n - i}'] = X[:, i]

    ret_df['Target'] = Y

    return ret_df


windowed_df = df_to_windowed_df(df,
                                '2020-03-25',
                                '2022-03-23',
                                n=3)

print(windowed_df)

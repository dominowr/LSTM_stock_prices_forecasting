import pandas as pd
import datetime
import matplotlib.pyplot as plt
import numpy as np
from keras.models import Sequential, load_model
from keras.callbacks import ModelCheckpoint
from keras.optimizers import Adam
from keras import layers
from copy import deepcopy

df = pd.read_csv('KWHIY.csv')
df = df[['Date', 'Close']]
df['Date'] = pd.to_datetime(df['Date'])
df.index = df.pop('Date')

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
                                '2014-05-30',
                                '2023-12-27',
                                n=3)
print(windowed_df)

def windowed_df_to_date_X_Y(windowed_dataframe):
    df_as_np = windowed_dataframe.to_numpy()
    dates = df_as_np[:, 0]

    middle_matrix = df_as_np[:, 1:-1]
    X = middle_matrix.reshape((len(dates), middle_matrix.shape[1], 1))
    Y = df_as_np[:, -1]

    return dates, X.astype(np.float32), Y.astype(np.float32)


dates, X, y = windowed_df_to_date_X_Y(windowed_df)

# # print(dates.shape)
# # print(X.shape)
# # print(y.shape)
#
q_80 = int(len(dates) * .8)
q_90 = int(len(dates) * .9)

dates_train, X_train, y_train = dates[:q_80], X[:q_80], y[:q_80]
dates_val, X_val, y_val = dates[q_80:q_90], X[q_80:q_90], y[q_80:q_90]
dates_test, X_test, y_test = dates[q_90:], X[q_90:], y[q_90:]
#
# # plt.plot(dates_train, y_train)
# # plt.plot(dates_val, y_val)
# # plt.plot(dates_test, y_test)
# #
# # plt.legend(['Train', 'Validation', 'Test'])
# # plt.show()
#
# # Model creation and training
#
# # model = Sequential([
# #     layers.Input((3, 1)),
# #     layers.LSTM(64),
# #     layers.Dense(32, activation='relu'),
# #     layers.Dense(32, activation='relu'),
# #     layers.Dense(1)
# # ])
# #
# # model.compile(
# #     loss='mse',
# #     optimizer=Adam(learning_rate=0.001),
# #     metrics=['mean_absolute_error']
# # )
# #
# # cp = ModelCheckpoint('model/', save_best_only=True)
# #
# # model.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=100, callbacks=[cp])
# #
model = load_model('model/')
# #
train_predictions = model.predict(X_train).flatten()
# #
# # plt.plot(dates_train, train_predictions)
# # plt.plot(dates_train, y_train)
# # plt.legend(['Training Predictions', 'Training Observations'])
#
val_predictions = model.predict(X_val).flatten()
# #
# # plt.plot(dates_val, val_predictions)
# # plt.plot(dates_val, y_val)
# # plt.legend(['Validation Predictions', 'Validation Observations'])
#
test_prediction = model.predict(X_test).flatten()
#
# # plt.plot(dates_test, test_prediction)
# # plt.plot(dates_test, y_test)
# # plt.legend(['Testing Predictions', 'Testing Observations'])
# #
# # # plt.plot(dates_train, train_predictions)
# # # plt.plot(dates_train, y_train)
# # # plt.plot(dates_val, val_predictions)
# # # plt.plot(dates_val, y_val)
# # # plt.plot(dates_test, test_prediction)
# # # plt.plot(dates_test, y_test)
# # #
# # # plt.legend([
# # #     'Training Predictions',
# # #     'Training Observations',
# # #     'Validation Predictions',
# # #     'Validation Observations',
# # #     'Testing Predictions',
# # #     'Testing Observations',
# # # ])
# #
# Prediction

recursive_predictions = []
recursive_dates = np.concatenate([dates_val, dates_test])

for target_date in recursive_dates:
    last_window = deepcopy(X_train[-1])
    next_prediction = model.predict(np.array([last_window])).flatten()
    recursive_predictions.append(next_prediction)
    last_window[-1] = next_prediction

plt.plot(dates_train, train_predictions)
plt.plot(dates_train, y_train)
plt.plot(dates_val, val_predictions)
plt.plot(dates_val, y_val)
plt.plot(dates_test, test_prediction)
plt.plot(dates_test, y_test)
plt.plot(recursive_dates, recursive_predictions)

plt.legend([
    'Training Predictions',
    'Training Observations',
    'Validation Predictions',
    'Validation Observations',
    'Testing Predictions',
    'Testing Observations',
    'Recursive Predictions'
])

plt.show()

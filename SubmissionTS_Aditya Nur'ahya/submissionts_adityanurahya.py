# -*- coding: utf-8 -*-
"""SubmissionTS_AdityaNurahya

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Eh2KUi7lPjhsW7jhO9S2AqxT91wTKFD2

## Time Series submission - Dicoding Academy
#### Aditya Nur'ahya

### Import library yang dibutuhkan
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime
from sklearn.model_selection import train_test_split

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Bidirectional, Dropout

"""### Dataset menggunakan US Pollution dari tahun 2000 - 2016

Data yang tercatat terlalu besar dan saya memutuskan untuk memakai 184381 Baris dari dataset
"""

df1 = pd.read_csv('/content/pollution_us_2000_2016.csv')
df1

df1.info()

df1.isnull().sum()

"""#### Drop baris yang memiliki value Null"""

df1 = df1.dropna(axis=0)

df1.isnull().sum()

df1

"""#### Mengambil data dengan range 1 tahun, pemilihan pada tahun 2000 dari Januari s.d Desember. Dengan begitu saya memakai 22881 baris"""

get_data = (df1['Date Local'] > '2000-01-01') & (df1['Date Local'] <= '2000-12-31')
df1.loc[get_data]

df1['Date Local'] = pd.to_datetime(df1['Date Local'])

df1.dropna(subset=['SO2 Mean'],inplace=True)

date = df1['Date Local'].values
so2 = df1['SO2 Mean'].values

date = np.array(date)
so2 = np.array(so2)

plt.figure(figsize=(80,40))
plt.plot(date, so2)
plt.title('SO2 Mean',
          fontsize=72);

x_train, x_valid, y_train, y_valid = train_test_split(so2, date, train_size=0.8, test_size = 0.2, shuffle = False )

def windowed_dataset(series, window_size, batch_size, shuffle_buffer):
    series = tf.expand_dims(series, axis=-1)
    ds = tf.data.Dataset.from_tensor_slices(series)
    ds = ds.window(window_size + 1, shift=1, drop_remainder=True)
    ds = ds.flat_map(lambda w: w.batch(window_size + 1))
    ds = ds.shuffle(shuffle_buffer)
    ds = ds.map(lambda w: (w[:-1], w[-1:]))
    return ds.batch(batch_size).prefetch(1)

tf.keras.backend.set_floatx('float64')

train_set = windowed_dataset(x_train, window_size=64, batch_size=200, shuffle_buffer=1000)
val_set = windowed_dataset(x_valid, window_size=64, batch_size=200, shuffle_buffer=1000)

model = tf.keras.models.Sequential([
  tf.keras.layers.LSTM(256, return_sequences=True),
  tf.keras.layers.LSTM(64),
  tf.keras.layers.Dense(30, activation="relu"),
  tf.keras.layers.Dense(10, activation="relu"),
  tf.keras.layers.Dense(1),
])

Mae = (df1['SO2 Mean'].max() - df1['SO2 Mean'].min()) * 10/100
print(Mae)

class myCallback(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs={}):
    if(logs.get('mae')<2.9 and logs.get('val_mae')<2.9):
      print("\nMAE dari model < 10% skala data")
      self.model.stop_training = True
callbacks = myCallback()

optimizer = tf.keras.optimizers.SGD(lr=1.0000e-04, momentum=0.9)
model.compile(loss=tf.keras.losses.Huber(),
              optimizer=optimizer,
              metrics=["mae"])

history = model.fit(train_set, validation_data=val_set, epochs=50, callbacks=[callbacks])

# Plot Accuracy
plt.plot(history.history['mae'])
plt.plot(history.history['val_mae'])
plt.title('Akurasi Model')
plt.ylabel('Mae')
plt.xlabel('epoch')
plt.legend(['Train', 'Val'], loc='upper left')
plt.show()

# Plot Loss
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Loss Model')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['Train', 'Val'], loc='upper left')
plt.show()
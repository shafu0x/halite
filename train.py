import time
from keras.models import Sequential
from keras.layers import Dense
import h5py
import pandas as pd
from sklearn import preprocessing, model_selection
import keras
import numpy

df_X = pd.read_csv('ship_data_all.txt')
df_y = pd.read_csv('ship_label_all.txt')

X = df_X.iloc[:, :].values
y = df_y.iloc[:, :].values

X = preprocessing.scale(X)
print(X[0])

X_train, X_test, y_train, y_test = model_selection.train_test_split(X, y, test_size=0.2)

model = Sequential()

model.add(Dense(units=128, activation='relu', input_dim=len(X_train[0])))
model.add(Dense(units=3, activation='relu'))

model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

model.fit(X_train, y_train, epochs=2, batch_size=10)

loss_and_metrics = model.evaluate(X_test, y_test, batch_size=128)
#
model.save('nn.h5')
# now = time.time()
# print(time.time())
# model = keras.models.load_model('nn.h5')
# print(time.time() - now)
#
# pred = model.predict(X_train[0].reshape(1, 12))
# print(pred)

print(loss_and_metrics)

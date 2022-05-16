import numpy as np
import pandas as pd
import tensorflow as tf
import matplotlib.pyplot as plt

# load the data
df = pd.read_csv('winequality-red.csv')

# split dataset into training/testing
train_df = df.sample(frac=0.75, random_state=4)
test_df = df.drop(train_df.index)

#normalize data into range of (0,1)
max_val = train_df.max(axis= 0)
min_val = train_df.min(axis= 0)
 
range = max_val - min_val
train_df = (train_df - min_val)/(range)
test_df =  (test_df - min_val)/range

# separate data into inputs and targets
X_train = train_df.drop('quality',axis=1)
X_test = test_df.drop('quality',axis=1)
y_train = train_df['quality']
y_test = test_df['quality']
 
input_shape = [X_train.shape[1]]
print(input_shape,"\n") # number of features passed as input

# setup done, now build the model - Note this this example is for classification, not regression, and is not a CNN

# complex model with 3 layers, 1 input layer, 1 hidden with 64 units, and 1 output layer
# relu is the activation function, (google what these mean especially on geeksforgeeks which is this tutorial)

model = tf.keras.Sequential([
    tf.keras.layers.Dense(units=64, activation='relu',
                          input_shape=input_shape),
    tf.keras.layers.Dense(units=64, activation='relu'),
    tf.keras.layers.Dense(units=1)
])
print(model.summary(), "\n")

# In keras, after setting up model you need to compile it this adds hyperparameters basically
model.compile(optimizer='adam', 
              loss='mse',
              metrics=['mse']) 

# model is created now, next is training it
losses = model.fit(X_train, y_train,
				validation_data=(X_test, y_test),		
                #batch size is used to split up the training data, saves on RAM and CPU consumption when training
				batch_size=256,
				epochs=15, 
				)

# model is trained now, so here we try prediction
print(model.predict(X_test.iloc[0:3, :])) # start with first 3 rows of test data
# compare predictions to target value
print(y_test.iloc[0:3])

# visualization of training vs validation loss
loss_df = pd.DataFrame(losses.history) # history stores the loss/val for each epoch
loss_df.loc[:,['loss','val_loss']].plot()
plt.show()

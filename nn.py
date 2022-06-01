import pandas as pd
import tensorflow as tf
import matplotlib.pyplot as plt
import scipy.stats as sp
import custom_tf_metrics as custom_metrics

df = pd.read_csv('live-nrqe.csv')

#remove video title, since this is not necessary for training
df.drop('video',axis=1, inplace=True)

# split dataset into training/testing
train_df = df.sample(frac=0.75, random_state=4)
test_df = df.drop(train_df.index)

print( train_df.head() )
#normalize data into range of (0,1)
max_val = train_df.max(axis= 0)
min_val = train_df.min(axis= 0)
range = max_val - min_val
train_df = (train_df - min_val)/(range)
test_df =  (test_df - min_val)/range

# separate data into inputs and targets
X_train = train_df.drop('mos',axis=1)
X_test = test_df.drop('mos',axis=1)
y_train = train_df['mos']
y_test = test_df['mos']

print( X_train.head() )

# number of features passed as input (metrics)
input_shape = [X_train.shape[1]]
print(input_shape,"\n")

# set up the model with 2 layers, 1 hidden sigmoid with 10 neurons, one linear output layer
model = tf.keras.Sequential()
model.add(tf.keras.Input(shape=input_shape))
model.add(tf.keras.layers.Dense(input_shape[0], activation='sigmoid'))
model.add(tf.keras.layers.Dense(1, activation='linear'))
print(model.summary(), "\n")

# compile model specifying optimizer and evaluation metrics
model.compile(optimizer='adam', 
              loss='mae',
              metrics=['mae', custom_metrics.PearsonCorrelation(), custom_metrics.SpearmanCorrelation()]) 

# model is created now, next is training it
losses = model.fit(X_train, y_train,
				validation_data=(X_test, y_test),		
                #batch size is used to split up the training data, saves on RAM and CPU consumption when training
				batch_size=256,
				epochs=30, 
				)

# model is trained now, try prediction with first 3 rows of test data
print("Predictions: ")
print(model.predict(X_test.iloc[0:3, :]))
print("Truth: ")
print(y_test.iloc[0:3])

# visualization of training vs validation loss
# history stores the loss/val for each epoch
loss_df = pd.DataFrame(losses.history)
loss_df.loc[:,['loss','val_loss']].plot()
plt.title("Training Results") 
plt.xlabel("Epoch")
plt.ylabel("Loss")
plt.show()

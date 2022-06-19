import pandas as pd
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import scipy.stats as sp
import custom_tf_metrics as custom_metrics
import os
import datetime
from sklearn.model_selection import KFold
from sklearn.model_selection import train_test_split

def buildModel(input_shape):
    # set up the model with 2 layers, 1 hidden sigmoid with one neurons per input metric, one linear output layer
    model = tf.keras.Sequential()
    model.add(tf.keras.Input(shape=input_shape))
    model.add(tf.keras.layers.Dense(input_shape[0], activation='sigmoid'))
    model.add(tf.keras.layers.Dense(1, activation='linear'))
    print(model.summary(), "\n")

    # compile model specifying optimizer and evaluation metrics
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001), 
                loss='mae',
                metrics=['mae', custom_metrics.PLCC, custom_metrics.SpearmanCorrelation()])
    return model

def fitModel(model, X_train, y_train):
    losses = model.fit(X_train, y_train,
                validation_split= 0.2,
                batch_size = 256,
                epochs=300,
                )
    return losses

def saveModel(model, losses, eval_results, save_folder):
    # timestamp to uniquely identify the model
    ts = datetime.datetime.now( ).strftime("%Y-%m-%d_%H-%M-%S")
    # Save the entire model as a SavedModel.
    savefile = f"{save_folder}/feedfw-nn-{ts}/"
    if not os.path.isdir(savefile):
        os.makedirs(savefile)
    model.save(savefile)

    with open(f"{save_folder}/metrics/feedfw-nn-{ts}.log", 'w', newline='') as metricFile:
        num_epochs = len(losses.history['loss'])
        metricFile.write(f"Epochs: {num_epochs}\n")
        for i in range(num_epochs):
            metricFile.write(f"Epoch {i} : [ MAE: {losses.history['mae'][i]}, PLCC: {losses.history['PLCC'][i]} SROCC: {losses.history['spearman_correlation'][i]}")
            metricFile.write(f" Validation: Val_MAE: {losses.history['val_mae'][i]}, Val_PLCC: {losses.history['val_PLCC'][i]} Val_SROCC: {losses.history['val_spearman_correlation'][i]} ]\n")
        metricFile.write(f"Evaluation results: [ MAE: {eval_results[1]}, PLCC: {eval_results[2]} SROCC: {eval_results[3]} ]\n")

    # visualization of training vs validation loss
    # history stores the loss/val for each epoch
    loss_df = pd.DataFrame(losses.history)
    loss_df.loc[:,['loss','val_loss']].plot()
    plt.title("Training Results") 
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plotfile = f"{save_folder}/plots/feedfw-nn-{ts}.png"
    plt.savefig(plotfile)

def kFoldCV(modelFunction, trainDF, valDF, k):
    # Do K-fold cross validation
    results = np.array([0,0,0,0], dtype=np.float32)
    for train_index,test_index in KFold(k).split(trainDF):
        X_train,X_test = trainDF.iloc[train_index],trainDF.iloc[test_index]
        y_train,y_test = valDF.iloc[train_index],valDF.iloc[test_index]
    
        #normalize input data into range of (0,1) (already done for live-nrqe-wk4)
    #    max_val = X_train.max(axis= 0)
    #    min_val = X_train.min(axis= 0)
    #    data_range = max_val - min_val
    #    X_train = (X_train - min_val)/(data_range)
    #    X_test =  (X_test - min_val)/data_range

        #normalize target data into range of (0,1)
        max_val = y_train.max(axis= 0)
        min_val = y_train.min(axis= 0)
        data_range = max_val - min_val
        y_train = (y_train - min_val)/(data_range)
        y_test =  (y_test - min_val)/(data_range)

        # number of features passed as input (metrics)
        input_shape = [X_train.shape[1]]
        print(input_shape,"\n")
        
        model = modelFunction(input_shape)
        losses = fitModel(model, X_train, y_train)

        # store evaluation results for averaging
        results = np.add(results, model.evaluate(X_test, y_test))
    # k-fold cross validation is done now, print evaluation results
    print('results: ', results)
    print('Test loss, test mae, test PLCC, test SROCC: ', np.divide(results, 10))

df = pd.read_csv('live-nrqe.csv')

# split dataset into inputs and targets ( metrics/MOS )
X_df = df.drop('mos', axis=1)
y_df = df['mos']

# Do K-fold cross validation
#kFoldCV(buildModel, X_df.drop('video',axis=1), y_df, 10)

# further split dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X_df, y_df, test_size=0.2, random_state=4)

#remove video title, since this is not necessary for training. 
# store it separately though for easier performance analysis
label_train, label_test = X_train['video'], X_test['video']
X_train.drop('video',axis=1, inplace=True)
X_test.drop('video',axis=1, inplace=True)

#normalize target data into range of (0,1)
max_val = y_train.max(axis= 0)
min_val = y_train.min(axis= 0)
data_range = max_val - min_val
y_train = (y_train - min_val)/(data_range)
y_test =  (y_test - min_val)/(data_range)

# number of features passed as input (metrics)
input_shape = [X_train.shape[1]]
print(input_shape,"\n")

# actually build and train the model
model = buildModel(input_shape)
losses = fitModel(model, X_train, y_train)

# model is trained now, print evaluation results
eval_results = model.evaluate(X_test, y_test)
print('Test loss, test mae, test PLCC, test SROCC: ', eval_results)

# try prediction with first 3 rows of test data
print("Predictions: ")
print(model.predict(X_test.iloc[0:3, :]))
print("Truth: ")
print(y_test.iloc[0:3])
print("Videos used: ")
print(label_test.iloc[0:3])

# save the model
saveModel(model, losses, eval_results, save_folder="./savedModels")

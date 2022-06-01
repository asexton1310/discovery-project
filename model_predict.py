import pandas as pd
import tensorflow as tf
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
data_range = max_val - min_val
train_df = (train_df - min_val)/(data_range)
test_df =  (test_df - min_val)/data_range

# separate data into inputs and targets
X_train = train_df.drop('mos',axis=1)
X_test = test_df.drop('mos',axis=1)
y_train = train_df['mos']
y_test = test_df['mos']

new_model = tf.keras.models.load_model("./savedModels/feedfw-nn-1/", 
                                        custom_objects={"PearsonCorrelation":custom_metrics.PearsonCorrelation,
                                                        "SpearmanCorrelation":custom_metrics.SpearmanCorrelation})

# Check its architecture
print(new_model.summary())

# verify loaded model can make predictions
print("Predictions: ")
print(new_model.predict(X_test.iloc[0:3, :]))
print("Truth: ")
print(y_test.iloc[0:3])


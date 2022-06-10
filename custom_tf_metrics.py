import tensorflow as tf
import numpy as np
from scipy import stats as sp
from keras import backend as K

class PearsonCorrelation(tf.keras.metrics.Metric):
    """
    Code by stackoverflow user DankMasterDan, available at: 
    https://stackoverflow.com/questions/46619869/how-to-specify-the-correlation-coefficient-as-the-loss-function-in-keras

    Standalone usage:
    
    m = SomeMetric(...)
    for input in ...:
        m.update_state(input)
    print('Final result: ', m.result().numpy())
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cov = tf.metrics.Sum()
        self.sq_yt = tf.metrics.Sum()
        self.sq_yp = tf.metrics.Sum()
        self.mean_yp = tf.metrics.Mean()
        self.mean_yt = tf.metrics.Mean()
        self.count = tf.metrics.Sum()

    def update_state(self, y_true, y_pred, sample_weight=None):
        self.cov(y_true * y_pred)
        self.sq_yp(y_pred**2)
        self.sq_yt(y_true**2)
        self.mean_yp(y_pred)
        self.mean_yt(y_true)
        self.count(tf.reduce_sum(tf.shape(y_true)))

    def result(self):
        count = self.count.result()
        mean_yp = self.mean_yp.result()
        mean_yt = self.mean_yt.result()
        numerator = (self.cov.result() - count * mean_yp * mean_yt)
        denominator = tf.sqrt(self.sq_yp.result() - count * mean_yp**2) * \
                      tf.sqrt(self.sq_yt.result() - count * mean_yt**2)
        r = numerator / denominator
        r = tf.maximum(tf.minimum(r, 1.0), -1.0)
        return r

    def reset_state(self):
        self.cov.reset_state()
        self.sq_yt.reset_state()
        self.sq_yp.reset_state()
        self.mean_yp.reset_state()
        self.mean_yt.reset_state()
        self.count.reset_state()

class SpearmanCorrelation(tf.keras.metrics.Metric):
    """
    Standalone usage:
    
    m = SomeMetric(...)
    for input in ...:
        m.update_state(input)
    print('Final result: ', m.result().numpy())
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def update_state(self, y_true, y_pred, sample_weight=None):
        self.y_pred = tf.cast(y_pred, tf.float32)
        self.y_true = tf.cast(y_true, tf.float32)

    def result(self):   
        return ( tf.py_function(sp.spearmanr, [self.y_pred, self.y_true], Tout = tf.float32) )

def PLCC(y_true, y_pred):
    """
    Calculates Pearson Linear Correlation Coefficient

    Code by stackoverflow user Julio Daniel Reyes, available at: 
    https://stackoverflow.com/questions/46619869/how-to-specify-the-correlation-coefficient-as-the-loss-function-in-keras

    """
    x = tf.cast(y_pred, tf.float32)
    y = tf.cast(y_true, tf.float32) 
    mx = K.mean(x)
    my = K.mean(y)
    xm, ym = x-mx, y-my
    r_num = K.sum(tf.multiply(xm,ym))
    r_den = K.sqrt(tf.multiply(K.sum(K.square(xm)), K.sum(K.square(ym))))
    r = r_num / r_den

    r = K.maximum(K.minimum(r, 1.0), -1.0)
    return r

if __name__ == "__main__":

    """
    Verification of PLCC based on Julio Daniel Reyes code at:
    https://stackoverflow.com/questions/46619869/how-to-specify-the-correlation-coefficient-as-the-loss-function-in-keras
    """

    inputa = np.array([[3,1,2,3,4,5],
                        [1,2,3,4,5,6],
                        [1,2,3,4,5,6]])
    inputb = np.array([[3,1,2,3,4,5],
                        [3,1,2,3,4,5],
                        [6,5,4,3,2,1]])

    f1 = SpearmanCorrelation()
    f2 = PearsonCorrelation()

    for i in range(inputa.shape[0]):
        f1.update_state(inputa[i], inputb[i])
        f2.update_state(inputa[i], inputb[i])
        f3_res = PLCC(inputa[i],inputb[i]).numpy()
        scipy_result = sp.pearsonr(inputa[i], inputb[i])[0]
        scipy_spear = sp.spearmanr(inputa[i], inputb[i])[0]
        np_res = np.corrcoef(inputa[i], inputb[i])
        print("a: "+ str(inputa[i]) + " b: " + str(inputb[i]))
        print("correlation_coefficient: ",f2.result().numpy())
        print("scipy.stats.pearsonr: " + str(scipy_result)) 
        print("np.corrcoef: " + str(np_res))
        print("PLCC: ",f3_res)
        print()
        print("spearman_coefficient: ",f1.result().numpy())
        print("scipy.stats.spearman: " + str(scipy_spear)) 
        print()
        f1.reset_state()
        f2.reset_state()

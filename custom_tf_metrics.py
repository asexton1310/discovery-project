import tensorflow as tf
import numpy as np
from scipy import stats as sp

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
        numerator = (self.cov.result() - count * self.mean_yp.result() * self.mean_yt.result())
        denominator = tf.sqrt(self.sq_yp.result() - count * mean_yp**2) * \
                      tf.sqrt(self.sq_yt.result() - count * mean_yt**2)
        return numerator / denominator

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
        scipy_result = sp.pearsonr(inputa[i], inputb[i])[0]
        scipy_spear = sp.spearmanr(inputa[i], inputb[i])[0]
        np_res = np.corrcoef(inputa[i], inputb[i])
        print("a: "+ str(inputa[i]) + " b: " + str(inputb[i]))
        print("correlation_coefficient: ",f2.result().numpy())
        print("scipy.stats.pearsonr: " + str(scipy_result)) 
        print("np.corrcoef: " + str(np_res))
        print("spearman_coefficient: ",f1.result().numpy())
        print("scipy.stats.spearman: " + str(scipy_spear)) 
        print()
        f2.reset_state()

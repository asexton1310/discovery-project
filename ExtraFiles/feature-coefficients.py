import tensorflow as tf
import numpy as np
from scipy import stats as sp
from keras import backend as K
import pandas as pd
import csv
import os


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
        self.sq_yp(y_pred ** 2)
        self.sq_yt(y_true ** 2)
        self.mean_yp(y_pred)
        self.mean_yt(y_true)
        self.count(tf.reduce_sum(tf.shape(y_true)))

    def result(self):
        count = self.count.result()
        mean_yp = self.mean_yp.result()
        mean_yt = self.mean_yt.result()
        numerator = self.cov.result() - count * mean_yp * mean_yt
        denominator = tf.sqrt(self.sq_yp.result() - count * mean_yp ** 2) * tf.sqrt(
            self.sq_yt.result() - count * mean_yt ** 2
        )
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
        return tf.py_function(sp.spearmanr, [self.y_pred, self.y_true], Tout=tf.float32)


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
    xm, ym = x - mx, y - my
    r_num = K.sum(tf.multiply(xm, ym))
    r_den = K.sqrt(tf.multiply(K.sum(K.square(xm)), K.sum(K.square(ym))))
    r = r_num / r_den

    r = K.maximum(K.minimum(r, 1.0), -1.0)
    return r


def get_coefficients():
    col_list = [
        "avg_blockiness",
        "max_blockiness",
        "min_blockiness",
        "avg_blur",
        "max_blur",
        "min_blur",
        "avg_contrast",
        "max_contrast",
        "min_contrast",
        "avg_color",
        "max_color",
        "min_color",
        "avg_ltp",
        "max_ltp",
        "min_ltp",
        "avg_noise",
        "max_noise",
        "min_noise",
        "avg_brisque",
        "max_brisque",
        "min_brisque",
        "avg_flickering_agh",
        "avg_blockiness_agh",
        "avg_letterBox_agh",
        "avg_pillarBox_agh",
        "avg_blockloss_agh",
        "avg_blur_agh",
        "avg_blackout_agh",
        "avg_freezing_agh",
        "avg_exposure_agh",
        "avg_contrast_agh",
        "avg_interlace_agh",
        "avg_noise_agh",
        "avg_si_agh",
        "avg_ti_agh",
        "mos",
    ]
    csv_label = ["Metric", "Pearson", "Spearman"]
    if os.path.exists("feature-coefficients.csv"):
        os.remove("feature-coefficients.csv")
    with open("feature-coefficients.csv", "a", newline="") as csvfile:
        metric_writer = csv.writer(csvfile, delimiter=",")
        metric_writer.writerow(csv_label)

    x = pd.read_csv("live-ls-nrqe-wk7.csv",
                    usecols=col_list)  # Read CSV File

    mos_list = x["mos"].tolist()
    mos_list = np.array([mos_list])  # Gather MOS into List
    for a in range(len(col_list) - 1):
        print(f"Name of Metric: {col_list[a]}")
        metric_list = x[col_list[a]].tolist()
        metric_list = np.array([metric_list])
        for i in range(metric_list.shape[0]):
            # Gather Pearson and Spearman Coefficients
            scipy_result = sp.pearsonr(metric_list[i], mos_list[i])[0]
            scipy_spear = sp.spearmanr(metric_list[i], mos_list[i])[0]
        print(f"Pearson Correlation for {col_list[a]}: {scipy_result}")
        print(f"Spearman Correlation for {col_list[a]}: {scipy_spear}")
        csv_output = [col_list[a], scipy_result, scipy_spear]
        with open("feature-coefficients.csv", "a", newline="") as csvfile:
            metric_writer = csv.writer(csvfile, delimiter=",")
            metric_writer.writerow(csv_output)
    print("CSV file named 'feature-coefficients.csv' is created")


if __name__ == "__main__":
    get_coefficients()

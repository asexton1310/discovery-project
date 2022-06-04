import random

def weightedAvg(quality_estimates, weights):
    return sum([quality_estimates[i]*weights[i] for i in range(len(quality_estimates))]) / sum(weights)

if __name__ == "__main__":
    num_estimators = 10
    qe = [round(random.random() * 100) for _ in range(num_estimators)]
    viewers = [round(random.random() * 10000) + 50 for _ in range(num_estimators)]
    print( "QE: ", qe)
    print( "Viewers: ", viewers)
    print()

    print( "The weighted result: " ,weightedAvg(qe, viewers))
    print( "The simple result: ", sum(qe) / num_estimators)
 
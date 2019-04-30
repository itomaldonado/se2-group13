# -*- coding: utf-8 -*-

"""
Bayesian Curve Fitting:

p(t | x, x, t) = N(t | m(x), s^2(x))

where the mean and variance are:

m(x) = β (Φ(x)^T) (S) (sum n=1..N: Φ(xn)tn)
s^2(x) = (1/β) + (Φ(x)^T) (S) (Φ(x))

β represents the precision or (1 / variance):
β = (1/σ^2)

S is given by:
S^-1 = αI + β (sum n=1..N: Φ(xn)Φ(xn)^T)

where I is the unit matrix, and the vector φ(x) is defined as:
Φ(x) = (Φ0(x) ... ΦM(x))^T --> (x^0 x^1 x^2 ... x^M)^T
"""
import logging
import math
import numpy

logger = logging.getLogger(__name__)


def get_phi(x, m):
    """Generates Φ(x) with polynomial M"""
    phi = numpy.zeros((m, 1), float)
    for i in range(m):
        phi[i][0] = math.pow(x, float(i))
    return phi


def predict(data, alpha=0.005, beta=11.100, mth=6):
    logging.debug(f'Parameters - α:{alpha}, β:{beta}, Data: {data}, Mth:{mth}')
    N = len(data)
    x = numpy.arange(N)
    t = data

    # prediction is the next Data point
    predict = N + 1
    polynomial = mth + 1
    logging.debug(f'Inferred Parameters - N:{N}, Predict: {predict}, Polynomial:{polynomial}')

    # Calculate sums (Φ(x).t) and (φ(x).φ(x)^T)
    phi_sum = numpy.zeros((polynomial, 1), float)
    phi_sum_t = numpy.zeros((polynomial, 1), float)
    for i in range(N):
        phi = get_phi(x[i], polynomial)
        phi_sum = numpy.add(phi_sum, phi)
        phi_sum_t = numpy.add(phi_sum_t, (phi * t[i]))

    logging.debug(f'Phi Sum: {phi_sum}')
    logging.debug(f'Phi Sum T: {phi_sum_t}')

    # Get phi for 'prediction'
    phi = get_phi(predict, polynomial)
    logging.debug(f'Phi: {phi}')

    # Calculate the predicted variance / standard deviation
    S = alpha * numpy.identity(polynomial) + beta * numpy.dot(phi_sum, phi.T)
    S = numpy.linalg.inv(S)
    predicted_variance = (float(1.0 / beta) + numpy.dot(numpy.dot(phi.T, S), phi))[0][0]

    # Calculate the predicted mean
    predicted_mean = (beta * numpy.dot(phi.T, numpy.dot(S, phi_sum_t)))[0][0]

    # predicted range at 3 deviations
    predicted_range = [
        round(predicted_mean - 3 * predicted_variance, 2),
        round(predicted_mean + 3 * predicted_variance, 2)
    ]

    # Print prediction values
    logging.debug(f'Data mean: {numpy.mean(t[:N])}')
    logging.debug(f'Mean: {round(predicted_mean, 3)}')
    logging.debug(f'Variance: {round(predicted_variance, 3)}')
    logging.debug(
        f'The predicted range: [${predicted_range[0]}'
        f' - ${predicted_range[1]}]'
    )

    # return predicted mean and variance
    return predicted_mean, predicted_variance, predicted_range

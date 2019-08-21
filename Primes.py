import time
import math
import sys
print(sys.version)
"""Return 'True' if 'n' is a prime number. False otherwise"""


def is_prime_v1(n):
    if n == 1:
        return False		# 1 in not prime

    for d in range(2, n):
        # print(n % d)
        if n % d == 0:
            return False
    return True


def is_prime_v2(n):
    if n == 1:
        return False		# 1 in not prime

    max_divisor = math.floor(math.sqrt(n))
    for d in range(2, 1 + max_divisor):
        if n % d == 0:
            return False
    return True


def is_prime_v3(n):
    if n == 1:
        return False

    if n == 2:
        return True

    if n % 2 == 0:
        return False

    max_divisor = math.floor(math.sqrt(n))
    for d in range(3, 1 + max_divisor, 2):
        if n % d == 0:
            return False
    return True


# Time Fuction
t0 = time.time()
for n in range(1, 10000001):
    is_prime_v3(n)
    # print(n, is_prime_v3(n))
t1 = time.time()

print("Time required: ", t1 - t0)

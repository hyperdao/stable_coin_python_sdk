import decimal

def convertCoinWithPrecision(amount, precision=8):
    dAmount = decimal.Decimal(amount) / (10 ** precision)
    return "{0:f}".format(dAmount)

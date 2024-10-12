## This file contains the miscellaneous functions related to mortgage calculations

def payments(mortgage_amount:int, interest_rate:float, mortgage_period:int)->float:
    """Computes the montly payment cost"""
    interest_rate=normalise_interest_rate(interest_rate)
    temp = pow((1+interest_rate/12),(mortgage_period*12))
    monthly_payment = mortgage_amount*(interest_rate*temp/12)/(temp-1)
    return approx(monthly_payment)

def current_interest_paid(principal:float, interest_rate:float)->float:
    """Computes the cost of borrowing the money"""
    interest_rate=normalise_interest_rate(interest_rate)
    return principal*interest_rate/12    

def clean(amount:float)->str:
    """Prepares the money amount for printing purposes"""
    return "{:,.2f}".format(approx(amount))

def approx(amount:float)->float:
    """Rounds the number"""
    return round(amount, 2)

def normalise_interest_rate(interest_rate:float)->float:
    """Converts the interest rate from percentage to decimal"""
    if interest_rate > 0.25: # we need to convert it
        interest_rate=interest_rate/100
    return interest_rate

def denormalise_interest_rate(interest_rate:float)->float:
    """Converts the interest rate from decimal to percentage"""
    if interest_rate <= 0.25: # we need to convert it
        interest_rate=interest_rate*100
    return interest_rate
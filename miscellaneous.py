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

def convert_recurring_repayments(periods:list)->dict:
    """Converts the recurring repayments from list of periods to a dictionary that expresses the repayments over the months"""
    repayments_adj = {month:period["amount_paid"] for period in periods for month in range(period["start"],period["end"]+1)}
    return repayments_adj

def check_recurring_repayments(periods:list)->bool:
    """Checks whether there are overlapping periods in the recurring payments"""
    periods = [period for period in sorted(periods, key=lambda item: item["start"])] #sorting
    len_periods = len(periods)
    for idx in range(len_periods):
        if periods[idx]["start"] > periods[idx]["end"]:
            print(f"ERROR: For a time period set in repayments the end date (Month {periods[idx]['end']}) preceeds the start date (Month {periods[idx]['start']})")
            return False
        if idx < len_periods-1:
            if periods[idx+1]["start"] <= periods[idx]["end"]:
                print(f"ERROR: There is a clash between repayment periods. A new period starts (Month {periods[idx+1]['start']}) before another ends (Month {periods[idx]['end']})")
                return False
    
    return True
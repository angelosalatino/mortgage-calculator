# Mortgage Calculator


This repository helps you understand your mortgage and potentially save money.  It breaks down your payments to show how much goes towards your loan balance (equity) versus interest, so you can explore ways to pay off your mortgage faster and reduce interest costs.


## Mortgage Payment Formula

Please note this does not account for variable rates, which can change.

$$
r = interest\\_rate/12
$$


$$
n = \text {Number of payments in total}  (total\\_instalments)
$$


$$
\text { Monthly Payment }= \text { Mortgage Amount}\frac{r(1+r)^n}{(1+r)^n-1}
$$


## Scripts available

- ```mortgage-calculator.ipynb``` calculates how much of your mortgage payments go towards interest and how much goes towards building equity (ownership) in your home. It's designed for mortgages with fixed payments, not those with early repayment options.
- ```mortgage-calculator-with-one-off-payments.ipynb``` calculates your mortgage payments based on one-off payments. Helps you understanding how much you will save with one-off repayments.
- ```mortgage-calculator-with-recurring-early-payments.ipynb``` calculates your mortgage payments based on recurring increased repayments. Helps you understanding how much you will save with recurring repayments.


## Scripts to develop

- script to track re-mortgaging (i.e., different interest rates are applied through the process)



## Streamlit use

Run

```streamlit run Mortgage_Calculator.py```
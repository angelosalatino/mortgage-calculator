import sys
import subprocess
import pkg_resources

required = {'streamlit', 'pandas', 'xlsxwriter'}
installed = {pkg.key for pkg in pkg_resources.working_set}
missing = required - installed

if missing:
    python = sys.executable
    subprocess.check_call([python, '-m', 'pip', 'install', *missing], stdout=subprocess.DEVNULL)
# else:
    # print("All required packages are available!")

import streamlit as st
import pandas as pd
import numpy as np
import xlsxwriter
from io import BytesIO


from miscellaneous import *




def calculate(mortgage_amount:int, interest_rate:float, mortgage_period:int, total_instalments:int)->pd.DataFrame():
    """
    Calculates all the instalments

    Parameters
    ----------
    mortgage_amount : int
        Amount borrowed.
    interest_rate : float
        interest rate in percentage.
    mortgage_period : int
        Lenght of mortgage in years.
    total_instalments : int
        Number of repayments (typically months).

    Returns
    -------
    DataFrame
        Full table with all details.

    """
    monthly_payment = payments(mortgage_amount,interest_rate,mortgage_period)
    columns=['Principal to date','Payment','Paid to date','Interest charged', 'Interest charged to date', 'Principal repaid', 'Principal repaid to date', 'Remaining principal']
    table = pd.DataFrame(columns=columns, index=[x for x in range(1, total_instalments+1)])
    remaining_principal = mortgage_amount
    payment_to_date = 0
    interest_paid_to_date = 0
    principal_repaid_to_date = 0
    for instalment in range(1, total_instalments+1):
        principal_to_date = remaining_principal
        payment_to_date += monthly_payment
        curr_interest_paid = current_interest_paid(principal_to_date, interest_rate)
        interest_paid_to_date += curr_interest_paid
        principal_repaid = monthly_payment - curr_interest_paid
        principal_repaid_to_date += principal_repaid
        remaining_principal -= principal_repaid
        table.loc[instalment] = pd.Series({columns[0]:clean(principal_to_date),
                                              columns[1]:clean(monthly_payment),
                                              columns[2]:clean(payment_to_date),
                                              columns[3]:clean(curr_interest_paid),
                                              columns[4]:clean(interest_paid_to_date),
                                              columns[5]:clean(principal_repaid),
                                              columns[6]:clean(principal_repaid_to_date),
                                              columns[7]:clean(remaining_principal)})
    return table

def main():
    ### WEBAPP
    
    st.title('Calculate and Analyse your Mortgage')    
    
    # Sidebar content
    with st.sidebar:
        with st.form("settings"):
            # Using object notation
            st.title('Settings')
            mortgage_amount = st.text_input(f"Mortgage Amount", "250000")
            interest_rate   = st.text_input("Interest Rate (%)", "3.4")
            mortgage_period = st.text_input("Mortgage Period (in years)", "30")
            currency = st.selectbox(
                "Currency",
                ("£", "€", "$")
            )
            submitted = st.form_submit_button("Submit")

    
    
    # Main content 
    st.write('## Mortgage Payment Formula')
    st.write('Please note this does not account for variable rates, which can change.')
    st.latex(r'''r = \text {interest rate}/12''')
    st.latex(r'''n = \text {Number of payments in total (total\_instalments)}''')
    st.latex(r'''\text {Monthly Payment }= \text { Mortgage Amount}\frac{r(1+r)^n}{(1+r)^n-1}''')
    
    
    if submitted:
        # casting values
        mortgage_amount = int(mortgage_amount)
        mortgage_period = int(mortgage_period)
        interest_rate   = float(interest_rate)
        
        
        total_instalments = mortgage_period*12
        monthly_payment = payments(mortgage_amount,interest_rate,mortgage_period)
        total_given = approx(monthly_payment*mortgage_period*12) 
        st.write("### Summary")
        st.write(f"Total amount borrowed {currency}{clean(mortgage_amount)}, with and interest rate of {clean(denormalise_interest_rate(interest_rate))}, and a repayment over {mortgage_period} ({mortgage_period*12} instalments)")
        st.write(f"Montly payments set to {currency}{clean(monthly_payment)}")
        st.write(f"Total payments {currency}{clean(total_given)}")
        st.write(f"For each \{currency}1 borrowed you are will pay back \{currency}{clean(total_given/mortgage_amount)}")
        
        table = calculate(mortgage_amount, interest_rate, mortgage_period, total_instalments)
        st.write("### Monthly instalments")
        st.dataframe(table)
        st.write("""### Details
- __Principal to date__:  This is the amount of the loan at a given time.

- __Payment__: This refers to the total amount of money paid toward the loan in a given period (usually monthly). This payment typically includes both principal and interest.

- __Paid to date__:  The total amount of money paid towards the loan since it originated. This includes both principal and interest portions of all payments made.

- __Interest charged__: The amount of interest that accrues on the loan for a specific period (e.g., a month). This is the cost of borrowing the money.

- __Interest charged to date__: The total amount of interest that has accrued on the loan since it originated.

- __Principal repaid__: The portion of a specific payment that goes towards reducing the original loan amount (the principal).

- __Principal repaid to date__: The total amount of the original loan amount that has been paid back since the loan originated.

- __Remaining principal__: The outstanding balance on the loan; this is the amount still owed. It's calculated as "Principal to date" minus "Principal repaid to date".
                 """)
                 
        
        # buffer to use for excel writer
        buffer = BytesIO()
        
        export_file = st.text_input(f"Filename (exluding xlsx)", "My_Mortgage_Analysis")

        
        # download button to download dataframe as xlsx
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            # Write each dataframe to a different worksheet.
            table.to_excel(writer, sheet_name='Sheet1', index=True)
            writer.save()
            download2 = st.download_button(
                label="Download data as Excel",
                data=buffer,
                file_name=f"{export_file}.xlsx",
                mime='application/vnd.ms-excel'
            )
    
    
    
    
if __name__ == '__main__':
    main()
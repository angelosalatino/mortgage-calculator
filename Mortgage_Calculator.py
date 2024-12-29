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

def remote(url):
    st.markdown(f'<link href="{url}" rel="stylesheet">', unsafe_allow_html=True)
    
def local(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)



def calculate(mortgage_amount:int, interest_rate:float, mortgage_period:int, total_instalments:int, repayments_adj:dict={})->pd.DataFrame():
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
    columns=['Principal to date','Payment','One-off','Paid to date','Interest charged', 'Interest charged to date', 'Principal repaid', 'Principal repaid to date', 'Remaining principal']
    table = pd.DataFrame(columns=columns, index=[x for x in range(1, total_instalments+1)])
    remaining_principal = mortgage_amount
    payment_to_date = 0
    interest_paid_to_date = 0
    principal_repaid_to_date = 0
    to_break = False
    for instalment in range(1, total_instalments+1):
        one_off_repayment = False
        this_month_payment = monthly_payment
        if instalment in repayments_adj:
            one_off_repayment = True
            this_month_payment += repayments_adj[instalment]
        
        principal_to_date = remaining_principal  
        curr_interest_paid = current_interest_paid(principal_to_date, interest_rate)
        if principal_to_date <= this_month_payment:
            this_month_payment = principal_to_date + curr_interest_paid
            to_break = True
        
        payment_to_date += this_month_payment
        
        interest_paid_to_date += curr_interest_paid
        principal_repaid = this_month_payment - curr_interest_paid
        principal_repaid_to_date += principal_repaid
        remaining_principal -= principal_repaid
        table.loc[instalment] = pd.Series({columns[0]:clean(principal_to_date),
                                             columns[1]:clean(this_month_payment),
                                             columns[2]:"Y" if one_off_repayment else "",
                                             columns[3]:clean(payment_to_date),
                                             columns[4]:clean(curr_interest_paid),
                                             columns[5]:clean(interest_paid_to_date),
                                             columns[6]:clean(principal_repaid),
                                             columns[7]:clean(principal_repaid_to_date),
                                             columns[8]:clean(remaining_principal)})
        
        if to_break:
            table = table.drop(range(instalment+1, total_instalments+1))
            break
        
    if len(repayments_adj) == 0:
        table = table.drop(['One-off'],axis=1)
            
    return table

def card(description, value="", color="#f0f2f6"):
    st.html(f"""<div class="card text-center mb-3" style="background-color: {color};">
          <div class="card-body">
              <p class="card-text">{description}</p>
            <h5 class="card-title">{value}</h5> 
          </div>
        </div>
        """)

def main():
    ### WEBAPP
    local('assets/css/bootstrap.min.css')
    
    st.title('Calculate and Analyse your Mortgage')  
    

        
    # Sidebar content
    with st.sidebar:
            
        data = dict()
        # Using object notation
        st.title('Initial Settings')
        mortgage_amount = st.text_input(f"Mortgage Amount", "250000")
        currency_toggle = st.toggle("Not in British Sterling (£)?")
        currency = "£"
        if currency_toggle:
            currency = st.selectbox(
                "Currency",
                ("£", "€", "$")
            )

            
        interest_rate   = st.text_input("Interest Rate (%)", "3.4")
        mortgage_period = st.text_input("Mortgage Period (in years)", "30")
        st.divider()
        
        over_toggle = st.toggle("One-off lump sum overpayments?")
        # inspired from https://mathcatsand-examples.streamlit.app/add_data#not-using-form-submission
        if over_toggle:
            st.title('One-off Overpayment')
            
            if 'dataop' not in st.session_state:
                dataop = pd.DataFrame({'Payment':[],'Month':[]})
                st.session_state.dataop = dataop
            
            dataop = st.session_state.dataop
            
            st.dataframe(dataop)
            
            def add_dfForm():
                row = pd.DataFrame({'Payment':[st.session_state.input_colA],
                        'Month':[st.session_state.input_colB]})
                st.session_state.dataop = pd.concat([st.session_state.dataop, row])
            
            
            dfForm = st.form(key='dfForm')
            with dfForm:
                dfColumns = st.columns(2)
                with dfColumns[0]:
                    st.text_input('Payment', key='input_colA')
                with dfColumns[1]:
                    st.text_input('Month', key='input_colB')
                st.form_submit_button(label="Add payment",on_click=add_dfForm)
                
            st.divider()
            
        mon_over_toggle = st.toggle("Montly overpayments?")

        if mon_over_toggle:
            st.title('Monthly Overpayments')
            if 'datamop' not in st.session_state:
                datamop = pd.DataFrame({'Payment':[],'Start Month':[],'End Month':[]})
                st.session_state.datamop = datamop
            
            datamop = st.session_state.datamop
            
            st.dataframe(datamop)
            
            def add_dfForm_mon():
                row = pd.DataFrame({'Payment':[st.session_state.input_colAmo],
                        'Start Month':[st.session_state.input_colBmo],
                        'End Month':[st.session_state.input_colCmo]})
                st.session_state.datamop = pd.concat([st.session_state.datamop, row])
            
            
            dfForm_mon = st.form(key='dfForm_mon')
            with dfForm_mon:
                dfColumns = st.columns(3)
                with dfColumns[0]:
                    st.text_input('Payment', key='input_colAmo')
                with dfColumns[1]:
                    st.text_input('Start Month', key='input_colBmo')
                with dfColumns[2]:
                    st.text_input('End Month', key='input_colCmo')
                st.form_submit_button(label="Add monthly payments",on_click=add_dfForm_mon)
        
        submitted = st.button("Calculate")
            

    
    

    
    
    if submitted:
        
        
        
        
        # casting values
        mortgage_amount = int(mortgage_amount)
        mortgage_period = int(mortgage_period)
        interest_rate   = float(interest_rate)
        
        
        total_instalments = mortgage_period*12
        monthly_payment = payments(mortgage_amount,interest_rate,mortgage_period)
        total_given = approx(monthly_payment*mortgage_period*12) 
        

        dfColumns = st.columns(3)
        with dfColumns[0]:
            card("Montly payments",f"{currency}{clean(monthly_payment)}")
        with dfColumns[1]:
            card("Total payments",f"{currency}{clean(total_given)}")
        with dfColumns[2]:
            card(f"For each {currency}1 borrowed you are will pay back {currency}{clean(total_given/mortgage_amount)}")
        
        dfColumns = st.columns([2, 1])
        with dfColumns[0]:
            card(f"Total amount borrowed {currency}{clean(mortgage_amount)}, with and interest rate of {clean(denormalise_interest_rate(interest_rate))}, and a repayment over {mortgage_period} ({mortgage_period*12} instalments)")
        
        repayments_adj = {}
        if over_toggle:
            dataop = st.session_state.dataop
            # st.dataframe(dataop)
            repayments_adj = {int(row["Month"]):float(row["Payment"]) for index, row in dataop.iterrows()}
            
        
        table = calculate(mortgage_amount, interest_rate, mortgage_period, total_instalments, repayments_adj)
        st.write("### Monthly instalments")
        st.dataframe(table)
        
        
        st.html("""
                <div class="card">
                  <h5 class="card-header">Details</h5>
                  <div class="card-body">
                    <p class="card-text"><b>Principal to date</b>:  This is the amount of the loan at a given time.</p>
                    <p class="card-text"><b>Payment</b>: This refers to the total amount of money paid toward the loan in a given period (usually monthly). This payment typically includes both principal and interest.</p>
                    <p class="card-text"><b>Paid to date</b>:  The total amount of money paid towards the loan since it originated. This includes both principal and interest portions of all payments made.</p>
                    <p class="card-text"><b>One-off</b>: Whether for this month there was a one-off repayment. (if available)
                    <p class="card-text"><b>Interest charged</b>: The amount of interest that accrues on the loan for a specific period (e.g., a month). This is the cost of borrowing the money.</p>
                    <p class="card-text"><b>Interest charged to date</b>: The total amount of interest that has accrued on the loan since it originated.</p>
                    <p class="card-text"><b>Principal repaid</b>: The portion of a specific payment that goes towards reducing the original loan amount (the principal).</p>
                    <p class="card-text"><b>Principal repaid to date</b>: The total amount of the original loan amount that has been paid back since the loan originated.</p>
                    <p class="card-text"><b>Remaining principal</b>: The outstanding balance on the loan; this is the amount still owed. It's calculated as "Principal to date" minus "Principal repaid to date".</p>
                   </div>
                </div>
                """)
#         st.write("""### Details
# - __Principal to date__:  This is the amount of the loan at a given time.

# - __Payment__: This refers to the total amount of money paid toward the loan in a given period (usually monthly). This payment typically includes both principal and interest.

# - __Paid to date__:  The total amount of money paid towards the loan since it originated. This includes both principal and interest portions of all payments made.

# - __Interest charged__: The amount of interest that accrues on the loan for a specific period (e.g., a month). This is the cost of borrowing the money.

# - __Interest charged to date__: The total amount of interest that has accrued on the loan since it originated.

# - __Principal repaid__: The portion of a specific payment that goes towards reducing the original loan amount (the principal).

# - __Principal repaid to date__: The total amount of the original loan amount that has been paid back since the loan originated.

# - __Remaining principal__: The outstanding balance on the loan; this is the amount still owed. It's calculated as "Principal to date" minus "Principal repaid to date".
#                  """)
                 
        
        # buffer to use for excel writer
        buffer = BytesIO()
        
        export_file = st.text_input(f"Filename (exluding xlsx)", "My_Mortgage_Analysis")

        
        # download button to download dataframe as xlsx
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            # Write each dataframe to a different worksheet.
            table.to_excel(writer, sheet_name='Sheet1', index=True)
            # writer.close()
            download2 = st.download_button(
                label="Download data as Excel",
                data=buffer,
                file_name=f"{export_file}.xlsx",
                mime='application/vnd.ms-excel'
            )
    
    
    
    
if __name__ == '__main__':
    main()
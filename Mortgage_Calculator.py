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



def calculate(mortgage_amount:int, interest_rate:float, mortgage_period:int, total_instalments:int, currency:str, repayments_oop:dict={}, repayments_mop:dict={})->pd.DataFrame():
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
    columns=['Principal to date','Payment','Paid to date','Interest charged', 'Interest charged to date', 'Principal repaid', 'Principal repaid to date', 'Remaining principal','One-off','Increased']
    table = pd.DataFrame(columns=columns, index=[x for x in range(1, total_instalments+1)])
    remaining_principal = mortgage_amount
    payment_to_date = 0
    interest_paid_to_date = 0
    principal_repaid_to_date = 0
    to_break = False
    for instalment in range(1, total_instalments+1):
        this_month_payment = monthly_payment
        
        ## MONTLY REPAYMENTS
        increased_payment = False
        if instalment in repayments_mop:
            increased_payment = True
            this_month_payment = repayments_mop[instalment]
            if this_month_payment < monthly_payment:
                st.write(f"ERROR: For month {instalment} your repayment is set to {currency}{clean(this_month_payment)} instead of the original {currency}{clean(monthly_payment)}")
        

        ## ONE OFF PAYMENT
        one_off_repayment = False
        if instalment in repayments_oop:
            one_off_repayment = True
            this_month_payment += repayments_oop[instalment]
        

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
                                             columns[2]:clean(payment_to_date),
                                             columns[3]:clean(curr_interest_paid),
                                             columns[4]:clean(interest_paid_to_date),
                                             columns[5]:clean(principal_repaid),
                                             columns[6]:clean(principal_repaid_to_date),
                                             columns[7]:clean(remaining_principal),
                                             columns[8]:"Y" if one_off_repayment else "",
                                             columns[9]:"Y" if increased_payment else "",
                                             })
        
        if to_break:
            table = table.drop(range(instalment+1, total_instalments+1))
            break
        
    if len(repayments_oop) == 0:
        table = table.drop(['One-off'],axis=1)
    
    if len(repayments_mop) == 0:
        table = table.drop(['Increased'],axis=1)
            
    return table, instalment, payment_to_date

def card(description, value="", color="#f0f2f6"):
    st.html(f"""<div class="card text-center mb-3" style="background-color: {color};">
          <div class="card-body">
              <p class="card-text">{description}</p>
            <h4 class="card-title" style="padding: 0;">{value}</h4> 
          </div>
        </div>
        """)
        
def cardb(description, color="#f0f2f6"):
    st.html(f"""<div class="card text-center mb-3" style="background-color: {color};">
          <div class="card-body">
              <p class="card-text" style="padding: 0;">{description}</p>
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
        
        
        #########################
        ###### OVERPAYMENTS - OOP
        #########################
        over_toggle = st.toggle("One-off lump sum overpayments?")
        # inspired from https://mathcatsand-examples.streamlit.app/add_data#not-using-form-submission
        if over_toggle:
            st.title('One-off Overpayment')
            
            if 'dataop' not in st.session_state:
                dataop = pd.DataFrame({'Payment':[],'Month':[]})
                st.session_state.dataop = dataop
            
            st.write("This table describes all the one-off lump sum overpayments made on a certain month.")
            st.session_state.dataop = st.data_editor(st.session_state.dataop)
            
            def add_dfForm_oop_f():
                row = pd.DataFrame({'Payment':[st.session_state.input_colAoop],
                                    'Month':[st.session_state.input_colBoop]})
                st.session_state.dataop = pd.concat([st.session_state.dataop, row],ignore_index=True)
            
            def delete_last_row_oop_f():
                if len(st.session_state.dataop) > 0:
                    st.session_state.dataop = st.session_state.dataop.drop(st.session_state.dataop.tail(1).index)
            
            dfForm_oop = st.form(key='dfForm_oop')
            with dfForm_oop:
                dfColumns = st.columns(2)
                with dfColumns[0]:
                    st.text_input('Payment', key='input_colAoop')
                with dfColumns[1]:
                    st.text_input('Month', key='input_colBoop')
                st.form_submit_button(label="Add payment",on_click=add_dfForm_oop_f)
                st.form_submit_button(label="Delete last row",on_click=delete_last_row_oop_f)
                
            st.divider()
            
            
        #########################
        ###### MONTHLY OVERPAYMENTS - MOP
        ######################### 
        mon_over_toggle = st.toggle("Montly overpayments?")

        if mon_over_toggle:
            st.title('Monthly Overpayments')
            if 'datamop' not in st.session_state:
                datamop = pd.DataFrame({'Payment':[],'Start':[],'End':[]})
                st.session_state.datamop = datamop
            
            st.write("This table describes all the overpayments made over a period of time, from Start Month to End Month.")
            st.session_state.datamop = st.data_editor(st.session_state.datamop)
            
            def add_dfForm_mon_f():
                row = pd.DataFrame({'Payment':[st.session_state.input_colAmop],
                                    'Start':[st.session_state.input_colBmop],
                                    'End':[st.session_state.input_colCmop]})
                st.session_state.datamop = pd.concat([st.session_state.datamop, row],ignore_index=True)
            
            def delete_last_row_mop_f():
                if len(st.session_state.datamop) > 0:
                    st.session_state.datamop = st.session_state.datamop.drop(st.session_state.datamop.tail(1).index)
            
            dfForm_mon = st.form(key='dfForm_mon')
            with dfForm_mon:
                dfColumns = st.columns(3)
                with dfColumns[0]:
                    st.text_input('Payment', key='input_colAmop')
                with dfColumns[1]:
                    st.text_input('Start Month', key='input_colBmop')
                with dfColumns[2]:
                    st.text_input('End Month', key='input_colCmop')
                st.form_submit_button(label="Add monthly payments",on_click=add_dfForm_mon_f)
                st.form_submit_button(label="Delete last row",on_click=delete_last_row_mop_f)
        
        submitted = st.button("Calculate")
            

    
    

    
    
    if submitted:
        
        
        
        #########################
        ###### COMPUTING
        ######################### 
        
        # casting values
        mortgage_amount = int(mortgage_amount)
        mortgage_period = int(mortgage_period)
        interest_rate   = float(interest_rate)
        
        
        total_instalments = mortgage_period*12
        monthly_payment = payments(mortgage_amount,interest_rate,mortgage_period)
        total_given = approx(monthly_payment*mortgage_period*12) 
        
        repayments_oop = {}
        if over_toggle:
            repayments_oop = {int(row["Month"]):float(row["Payment"]) for index, row in st.session_state.dataop.iterrows()}
            
        repayments_mop = {}
        if mon_over_toggle:
            repayments_mop = {month:float(row["Payment"]) for index, row in st.session_state.datamop.iterrows() for month in range(int(row["Start"]),int(row["End"])+1)}
            
        table, instalment, payment_to_date = calculate(mortgage_amount, interest_rate, mortgage_period, total_instalments, currency, repayments_oop, repayments_mop)
        
        
        #########################
        ###### DISPLAYING
        ######################### 
        cardb(f"""Total amount borrowed {currency}{clean(mortgage_amount)}, with and interest rate of {clean(denormalise_interest_rate(interest_rate))}, and a repayment over {mortgage_period} years, and {mortgage_period*12} instalments.<br>
             For each {currency}1 borrowed you are will pay back {currency}{clean(payment_to_date/mortgage_amount)}""")
        
        dfColumns = st.columns(2)
        with dfColumns[0]:
            card("Montly payments",f"{currency}{clean(monthly_payment)}")
        with dfColumns[1]:
            card("Total payments",f"{currency}{clean(payment_to_date)}")
        
        # dfColumns = st.columns(2)
        # with dfColumns[0]:
        #     card(f"Total amount borrowed {currency}{clean(mortgage_amount)}, with and interest rate of {clean(denormalise_interest_rate(interest_rate))}, and a repayment over {mortgage_period} ({mortgage_period*12} instalments)")
        if len(repayments_oop) > 0 or len(repayments_mop) > 0:
            card(f"Early repayments reduced your mortgage to {instalment} instalments.",f"{(total_instalments-instalment)/12:.0f} year(s) and {(total_instalments-instalment)% 12} months earlier!","#8297ea")
        
        st.write("### Monthly instalments")
        st.dataframe(table)
        
        
        st.html("""
                <div class="card">
                  <h5 class="card-header">Details</h5>
                  <div class="card-body">
                    <p class="card-text"><b>Principal to date</b>:  This is the amount of the loan at a given time.</p>
                    <p class="card-text"><b>Payment</b>: This refers to the total amount of money paid toward the loan in a given period (usually monthly). This payment typically includes both principal and interest.</p>
                    <p class="card-text"><b>Paid to date</b>:  The total amount of money paid towards the loan since it originated. This includes both principal and interest portions of all payments made.</p>
                    <p class="card-text"><b>Interest charged</b>: The amount of interest that accrues on the loan for a specific period (e.g., a month). This is the cost of borrowing the money.</p>
                    <p class="card-text"><b>Interest charged to date</b>: The total amount of interest that has accrued on the loan since it originated.</p>
                    <p class="card-text"><b>Principal repaid</b>: The portion of a specific payment that goes towards reducing the original loan amount (the principal).</p>
                    <p class="card-text"><b>Principal repaid to date</b>: The total amount of the original loan amount that has been paid back since the loan originated.</p>
                    <p class="card-text"><b>Remaining principal</b>: The outstanding balance on the loan; this is the amount still owed. It's calculated as "Principal to date" minus "Principal repaid to date".</p>
                    <p class="card-text"><b>One-off</b>: Whether for this month there was a one-off repayment. (if available)</p>
                    <p class="card-text"><b>Increased</b>: Whether for this month there was an increased payment. (if available)</p>
                  </div>
                </div>
                """)
        
        if len(repayments_oop) > 0 or len(repayments_mop) > 0:
            
            repayments_text = ""
            if len(repayments_oop): repayments_text+=f"Then you performed {len(repayments_oop)} one-off lump sum repayments, of a total of {currency}{clean(sum([rep for _,rep in repayments_oop.items()]))}. "
            if len(repayments_mop): repayments_text+=f"Then you performed {len(repayments_mop)} monthly repayments, of a total of {currency}{clean(sum([rep for _,rep in repayments_mop.items()]))}. "  
            st.html(f"""
                    <div class="card">
                      <h5 class="card-header">Report on changes</h5>
                      <div class="card-body">
                        <p class="card-text">Total amount borrowed {currency}{clean(mortgage_amount)}, with an initial interest rate of {clean(denormalise_interest_rate(interest_rate))}. Repayments were set over {mortgage_period} years, and {mortgage_period*12} instalments.</p>
                        <p class="card-text">Thanks to early repayments you shortened your mortgage to {instalment} instalments, meaning {(total_instalments-instalment)/12:.0f} year(s) and {(total_instalments-instalment)% 12} months earlier than planned.</p>
                        <p class="card-text">Montly payments was initially set to {currency}{clean(monthly_payment)}</p>
                        <p class="card-text">{repayments_text}</p>
                        <p class="card-text">Your total repayment is {currency}{clean(payment_to_date)} (instead of the original {currency}{clean(total_given)}), saving a total of {currency}{clean(total_given-payment_to_date)} in interests!</p>
                        <p class="card-text">For each £1 borrowed you are will pay back {currency}{clean(payment_to_date/mortgage_amount)}, instead of {currency}{clean(total_given/mortgage_amount)}</p>
                      </div>
                    </div>
                    """)


                 
        
        # buffer to use for excel writer
        buffer = BytesIO()
        
        export_file = st.text_input(f"Filename (exluding xlsx)", "My_Mortgage_Analysis")

        
        # download button to download dataframe as xlsx
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            # Write each dataframe to a different worksheet.
            table.to_excel(writer, sheet_name='Sheet1', index=True)
            writer._save()
            download2 = st.download_button(
                label="Download data as Excel",
                data=buffer,
                file_name=f"{export_file}.xlsx",
                mime='application/vnd.ms-excel'
            )
    
    
    
    
if __name__ == '__main__':
    main()
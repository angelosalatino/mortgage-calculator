# -*- coding: utf-8 -*-

import streamlit as st
import time
import numpy as np

st.title('Calculate and Analyse your Mortgage') 

# Main content 
st.write('## Mortgage Payment Formula')
st.write('Please note this does not account for variable rates, which can change.')
st.latex(r'''r = \text {interest rate}/12''')
st.latex(r'''n = \text {Number of payments in total (total\_instalments)}''')
st.latex(r'''\text {Monthly Payment }= \text { Mortgage Amount}\frac{r(1+r)^n}{(1+r)^n-1}''')
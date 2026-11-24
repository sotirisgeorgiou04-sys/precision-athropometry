import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.stats import norm

st.set_page_config(page_title='Precision Anthropometry', layout='wide')
st.title('Precision Anthropometry – Protocol 3')
scenario = st.sidebar.radio('Scenario Selector', ['A – Intra-Tester', 'B – Inter-Tester'])
a = scenario.startswith('A')
x = np.array([12.5,8,15,10.5,9] if a else [12.2,8.2,14.7,10.7,9])
y = np.array([12,8.5,14.5,11,9] if a else [15.5,11,18.2,13.5,12])
d = x-y
m = (x+y)/2
tem = np.sqrt(np.sum(d**2)/(2*len(d)))
pct = 100*tem/m.mean()
bias = d.mean()
loa = norm.ppf(.975)*d.std(ddof=1)
limit = 5 if a else 7.5
label = 'Intra' if a else 'Inter'
t1,t2,t3 = st.tabs(['Data & Reliability Metrics','Bland-Altman Metrology','Diagnostic Alerts'])
with t1:
    st.dataframe(pd.DataFrame({'ID':[f'S{i}' for i in range(1,6)], 'Trial 1' if a else 'Tester A':x,'Trial 2' if a else 'Tester B':y,'Difference':d}),hide_index=True)
    c1,c2 = st.columns(2)
    c1.metric(label+'_TEM',f'{tem:.3f} mm')
    c2.metric(label+'_PctTEM',f'{pct:.2f}%')
    st.subheader('Body Density & Pct_Fat')
    st.info('The supplied scenarios do not include age, sex or the required three-site skinfold sum. Enter these separately to calculate estimates.')
    sex=st.selectbox('Sex',['Male','Female'])
    age=st.number_input('Age (years)',min_value=18,max_value=100,value=None)
    s=st.number_input('Sum of three appropriate skinfold sites (mm)',min_value=0.1,value=None)
    st.caption('Uses the coefficients printed in the laboratory protocol, including the female coefficient. Verify the female equation and site selection with your instructor before clinical use.')
    if age is not None and s is not None:
        density=(1.109380-.0008267*s+.0000016*s*s-.0002574*age) if sex=='Male' else (1.0994921-.00009929*s+.0000023*s*s-.0001392*age)
        st.metric('Body_Density',f'{density:.5f} g/cm³')
        st.metric('Pct_Fat',f'{(4.95/density-4.5)*100:.2f}%')
with t2:
    fig=go.Figure(go.Scatter(x=m,y=d,mode='markers',text=[f'S{i}' for i in range(1,6)],marker=dict(size=11)))
    for val,name in [(bias,'Mean Bias'),(bias+loa,'Upper 95% LOA'),(bias-loa,'Lower 95% LOA')]:
        fig.add_hline(y=val,line_dash='dash',annotation_text=f'{name}: {val:.3f}')
    fig.update_layout(xaxis_title='Mean of paired measurements (mm)',yaxis_title='First − second measurement (mm)')
    st.plotly_chart(fig,use_container_width=True)
with t3:
    if pct>=limit:
        st.error(f'{label}_PctTEM = {pct:.2f}% ≥ {limit:.1f}%: Failed')
    else:
        st.success(f'{label}_PctTEM = {pct:.2f}% < {limit:.1f}%: Passed')
    st.caption('Thresholds follow the supplied laboratory protocol.')

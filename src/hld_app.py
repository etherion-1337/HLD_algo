import sys
import streamlit as st
# To make things easier later, we're also importing numpy and pandas for
# working with sample data.
import numpy as np
import pandas as pd
from hld_fun import second_hdl_filter, first_hld_filter
sys.path.append("..")
st.title('Coronary Disease Risk Stratification')
st.text("This demo is based on the MOH Clinical Practice Guidelines 2/2016 on Lipids")

# data
m_age = pd.read_csv("data/m_age.csv")
m_tc = pd.read_csv("data/m_tc.csv")
m_smoker = pd.read_csv("data/m_smoker.csv")
m_hdl = pd.read_csv("data/m_hdl.csv")
m_sbp = pd.read_csv("data/m_sbp.csv")
m_total = pd.read_csv("data/m_total.csv")

w_age = pd.read_csv("data/w_age.csv")
w_tc = pd.read_csv("data/w_tc.csv")
w_smoker = pd.read_csv("data/w_smoker.csv")
w_hdl = pd.read_csv("data/w_hdl.csv")
w_sbp = pd.read_csv("data/w_sbp.csv")
w_total = pd.read_csv("data/w_total.csv")


comorbids_dict = {
    #Prognostic factors taken from MOH HTN CPG 2017 pg 34
    'HTNgrade1&2': False,
    'age': False, #Age >80
    'smoking': False,
    'FHx_CVD': False,
    'dyslipidaemia': False, #Total cholesterol > 6.2 mmol/L, Triglycerides > 1.7, HDL < 1.0, LDL > 4.1 
    
    'obesity': False, #BMI >= 27.5kg/m2 in Asians 
    'stroke_TIA': False,
    'LVH': False, #Left ventricular hypertrophy: ECG, echo or chest XR evidence
    'angina': False, 
    'heart_failure': False, 
    'proteinuria': False, # KDIGO moderate: ACR > 3-30 mg/mmol; PCR > 50 mg/mmol; TUP > 500 mg/24 hours
    
    'hypertensive_retinopathy': False,
    #Drug selection taken from MOH HTN CPG 2017 pg 35-36 if not in above list 
    'atrial_fibrillation': False,
    'isolated_systolic_hypertension': False,
    'asthma': False,
    'gout': False,
    'bilateral_renal_artery_stenosis': False, 
    #BP for patient at present
    'currentBP': {'SBP': "NA", 'DBP': "NA"},
    
    
    #This is same list as hypertension logic
    #Below is the list of risks specific for HLD following MOH CPG lipids 2016
    #Very high risk group:
    'AMI': False, #Previous myocardial infarction 
    'coronary_revasc': False, #Previous coronary revascularisation 
    'aortic_aneursym': False,
    'peripheral_arterial_disease': False,
    'atherosclerosis': False, #Ultrasound or radiological artherosclerotic plaque (carotid, iliac, femoral, peripheral arteries and aorta)
    'diabetes': False, #for lipids CPG high risk if DM with CKD 
    'CKD_3to5': False, #at least stage 3 eGFR <60
    'CKD_1to2': False, #CKD based on the KDIGO guidelines on eGFR/proteinuria
    'fam_hypercholesterolaemia': False,
    #High risk group:
        #mod to severe CKD eGFR <60 or 
        #DM only without end organ damage or atherosclerosis
}

hld_risk_dict = {
    "v_high" : 2.1,
    "high": 2.6,
    "inter": 3.4,
    "low": 4.1
}

############################################
st.markdown("**FIRST Evaluation**")        

# AMI
ami_select = st.radio(
                "Previous Acute Myocardial Infarction (AMI) ?",
                ("Yes", "No"))
if ami_select == "Yes":
    comorbids_dict['AMI'] = True
else:
    comorbids_dict['AMI'] = False

# coronary_revasc
cr_select = st.radio(
                "Previous Coronary Revascularisation ?",
                ("Yes", "No"))
if cr_select == "Yes":
    comorbids_dict['coronary_revasc'] = True
else:
    comorbids_dict['coronary_revasc'] = False

# aortic aneurysm
aa_select = st.radio(
                "Aortic Aneurysm ?",
                ("Yes", "No"))
if aa_select == "Yes":
    comorbids_dict['aortic_aneursym'] = True
else:
    comorbids_dict['aortic_aneursym'] = False

# peripheral arterial disease
pad_select = st.radio(
                "Peripheral Arterial Disease (PAD) ?",
                ("Yes", "No"))
if pad_select == "Yes":
    comorbids_dict['peripheral_arterial_disease'] = True
else:
    comorbids_dict['peripheral_arterial_disease'] = False

# atherosclerosis
ath_select = st.radio(
                "Atherosclerosis ?",
                ("Yes", "No"))
if ath_select == "Yes":
    comorbids_dict['atherosclerosis'] = True
else:
    comorbids_dict['atherosclerosis'] = False

# Familial hypercholesterolemia (FH) 
fh_select = st.radio(
                "Familial Hypercholesterolemia (FH) ?",
                ("Yes", "No"))
if fh_select == "Yes":
    comorbids_dict['fam_hypercholesterolaemia'] = True
else:
    comorbids_dict['fam_hypercholesterolaemia'] = False

# diabetes
diabetes_select = st.radio(
                "Diabetes ?",
                ("Yes", "No"))
if diabetes_select == "Yes":
    comorbids_dict['diabetes'] = True
else:
    comorbids_dict['diabetes'] = False

# Chronic Kidney Disease 1-2 (CKD)
ckd12_select = st.radio(
                "Chronic Kidney Disease (CKD) Stage 1 or 2 ?",
                ("Yes", "No"))
if ckd12_select == "Yes":
    comorbids_dict['CKD_1to2'] = True
else:
    comorbids_dict['CKD_1to2'] = False

# Chronic Kidney Disease 3-5 (CKD)
ckd35_select = st.radio(
                "Chronic Kidney Disease (CKD) Stage 3 and above ?",
                ("Yes", "No"))
if ckd35_select == "Yes":
    comorbids_dict['CKD_3to5'] = True
else:
    comorbids_dict['CKD_3to5'] = False

risk_status = first_hld_filter(comorbids_dict)
if risk_status == "v_high":
    st.markdown("This patient is **very high** risk category. Target LDL < 2.1")
elif risk_status == "high":
    st.markdown("This patient is **high** risk category. Target LDL < 2.6")
else:
    st.write("This patient's risk category has to be further accessed in the Second Evaluation below")

############################################
st.markdown("**SECOND Evaluation**")
st.text("If the first evaluation is not conclusive, please enter the following patient's information")

#gender
gender_select = st.radio(
                "Gender",
                ("Male", "Female"))
if gender_select == "Male":
    gender = "male"
else:
    gender = "female"

#race
race_select = st.radio(
                "Race",
                ("Chinese", "Malay", "Indian"))
if race_select == "Chinese":
    race = "Chinese"
elif race_select == "Malay":
    race = "Malay"
else:
    race = "Indian"

#smoke
smoke_select = st.radio(
                "Smoker ?",
                ("Yes", "No"))
if smoke_select == "Yes":
    smoke = "Yes"
else:
    smoke = "No"

#age
age = st.number_input('What is the age?', min_value=1, max_value=100, value = 40)

# tc
tc = st.number_input('What is the Total Cholesterol? (<5.2-normal, >6.2-high)', min_value=0.0, max_value=30.0, value = 4.1 ,step = 0.1)

# hdl 
hdl = st.number_input('What is the HDL Cholesterol? (Desirable ≥1.6)', min_value=0.0, max_value=10.0, value = 1.80, step = 0.1)

# sbp
sbp = st.number_input('What is the Systolic BP ? (90-210mmHg)', min_value=0, max_value=300, value = 150, step = 1)        

# sbp treat
treat_select = st.radio(
                "Is patient on treatment for HTN ?",
                ("untreated", "treated"))
if treat_select == "untreated":
    treat = False
else:
    treat = True

total_point, cad_percent = second_hdl_filter(gender, age, tc, smoke, hdl, sbp, treat, race,
                     m_age, m_tc, m_smoker, m_hdl, m_sbp, m_total,
                     w_age, w_tc, w_smoker, w_hdl, w_sbp, w_total)


cad_percent_str = str(cad_percent) + "%"

st.write("Patient has scored", total_point)
st.write("Patient's 10-years Coronary Artery Disease Risk is",  cad_percent_str)

if cad_percent < 10:
    st.write("This patient is low risk (<10% risk) category. Target LDL <4.1")
if 10 <= cad_percent <= 20:
    st.write("This patient is intermediate (10-20% risk) category. Target LDL <3.4")
if cad_percent>20:
    st.write("This patient is high (>20% risk) category. Target LDL <2.6")

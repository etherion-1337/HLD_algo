import sys
import numpy as np
import pandas as pd
import re

# data
#m_age = pd.read_csv("../data/m_age.csv")
#m_tc = pd.read_csv("../data/m_tc.csv")
#m_smoker = pd.read_csv("../data/m_smoker.csv")
#m_hdl = pd.read_csv("../data/m_hdl.csv")
#m_sbp = pd.read_csv("../data/m_sbp.csv")
#m_total = pd.read_csv("../data/m_total.csv")

#w_age = pd.read_csv("../data/w_age.csv")
#w_tc = pd.read_csv("../data/w_tc.csv")
#w_smoker = pd.read_csv("../data/w_smoker.csv")
#w_hdl = pd.read_csv("../data/w_hdl.csv")
#w_sbp = pd.read_csv("../data/w_sbp.csv")
#w_total = pd.read_csv("../data/w_total.csv")

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

def first_hld_filter(comorbids_dict):
    if comorbids_dict['AMI'] or comorbids_dict['coronary_revasc'] \
    or comorbids_dict['aortic_aneursym'] or comorbids_dict['peripheral_arterial_disease'] \
    or comorbids_dict['atherosclerosis'] \
    or comorbids_dict['fam_hypercholesterolaemia']\
    or (comorbids_dict['diabetes'] and (comorbids_dict['CKD_3to5'] or comorbids_dict['CKD_1to2'])) == True:
        hld_risk = 'v_high'
    elif ((comorbids_dict['CKD_3to5'] or comorbids_dict['CKD_1to2']) == True and comorbids_dict['diabetes'] == False) \
    or (comorbids_dict['diabetes'] == True and (comorbids_dict['CKD_3to5'] or comorbids_dict['CKD_1to2'])) == False:
        hld_risk = "high"
    else:
        hld_risk = "NA"
    return hld_risk

def age_split(row_age):
    """
    convert the age str into a list
    e.g.
    "40-44" => [40,41,42,43,44] 
    """
    age_gap = row_age.split("-")
    # cast list element into int
    age_gap = [int(x) for x in age_gap]
    # age_list = [i for i in range(age_gap[0], age_gap[1]+1)]
    return age_gap

def age_score(age, age_table):
    age_table["age_list"] = age_table["age"].apply(age_split)
    ans = age_table[age_table["age_list"].apply(lambda x: x[0]<= age <= x[1])]["points"].values
    return ans[0]

def age_band(age):
    age_band_dict = {
    '20-39':[i for i in range (20, 40)],
    '40-49':[i for i in range (40, 50)],
    '50-59':[i for i in range (50, 60)],
    '60-69':[i for i in range (60, 70)],
    '70-79':[i for i in range (70, 80)]
    }
    
    for k,v in age_band_dict.items():
        if age in v:
            band = k
            break
        else:
            band = "None"
    return band

def tc_split(row_tc):
    tc_list = re.findall(r"[+]?\d*\.\d+|\d+", row_tc)
    tc_list = [float(x) for x in tc_list]
    if tc_list[0] == 4.1 and len(tc_list) == 1:
        tc_list = [-10.0, 4.0]
    if tc_list[0] == 7.3:
        tc_list.append(30.0)
    return tc_list

def tc_score(tc,age, tc_table):
    ageband = age_band(age)
    tc_table["tc_list"] = tc_table["Total Cholesterol mmol/L"].apply(tc_split)
    ans = tc_table[tc_table["tc_list"].apply(lambda x: x[0] <= tc <= x[1])][ageband].values
    return ans[0]

def smoke_score(smoker_table, sm_status, age):
    ageband = age_band(age)
    ans = smoker_table[smoker_table["Smoker"] == sm_status][ageband].values
    return ans[0]

def hdl_split(row_hdl):
    hdl_list = re.findall(r"[+]?\d*\.\d+|\d+", row_hdl)
    hdl_list = [float(x) for x in hdl_list]
    if hdl_list[0] == 1.6 and len(hdl_list) == 1:
        hdl_list = [1.6, 10.0]
    if hdl_list[0] == 1.0 and len(hdl_list) == 1:
        hdl_list = [-10.0, 1.0]
    return hdl_list

def hdl_score(hdl, hdl_table):
    hdl_table["HDL_list"] = hdl_table["HDL"].apply(hdl_split)
    ans = hdl_table[hdl_table["HDL_list"].apply(lambda x: x[0]<= hdl <= x[1])]["points"].values
    return ans[0]

def sbp_split(row_sbp):
    sbp_list = re.findall(r"[+]?\d*\.\d+|\d+", row_sbp)
    sbp_list = [int(x) for x in sbp_list]
    if sbp_list[0] == 120 and len(sbp_list) == 1:
        sbp_list = [0, 120]
    if sbp_list[0] == 160 and len(sbp_list) == 1:
        sbp_list = [160, 500]
    return sbp_list

def sbp_score(sbp, treat_status, sbp_table):
    sbp_table["sbp_list"] = sbp_table["Systolic BP"].apply(sbp_split)
    if treat_status == True:
        col = "If treated"
    else:
        col = "If untreated"
    ans = sbp_table[sbp_table["sbp_list"].apply(lambda x: x[0]<= sbp <= x[1])][col].values
    return ans[0]

def total_score_m(total, race, total_table):
    if total < -1:
        return 0
    elif total > 17:
        return 21
    else:
        ans = total_table[total_table["Total"] == total][race].values
        return ans[0]

def total_score_w(total, race, total_table):
    if total < 5:
        return 0
    elif total > 24:
        return 21
    else:
        ans = total_table[total_table["Total"] == total][race].values
        return ans[0]


def second_hdl_filter(gender, age, tc, smoke, hdl, sbp, treat_status, race,
                     m_age, m_tc, m_smoker, m_hdl, m_sbp, m_total,
                     w_age, w_tc, w_smoker, w_hdl, w_sbp, w_total):
    if gender == "male":
        point = age_score(age, m_age)
        point += tc_score(tc, age, m_tc)
        point += smoke_score(m_smoker, smoke, age)
        point += hdl_score(hdl, m_hdl)
        point += sbp_score(sbp, treat_status, m_sbp)
        percent = total_score_m(point, race , m_total)
    else:
        point = age_score(age, w_age)
        point += tc_score(tc, age, w_tc)
        point += smoke_score(w_smoker, smoke, age)
        point += hdl_score(hdl, w_hdl)
        point += sbp_score(sbp, treat_status, w_sbp)
        percent = total_score_w(point, race , w_total)
    return point,percent


#gender = "female"
#age = 65
#tc = 4.5
#smoke = "No"
#hdl = 1.3
#sbp = 129
#treat_status = False
#race = "Chinese"

#total_point, cad_percent = second_hdl_filter(gender, age, tc, smoke, hdl, sbp, treat_status, race,
#                     m_age, m_tc, m_smoker, m_hdl, m_sbp, m_total,
#                     w_age, w_tc, w_smoker, w_hdl, w_sbp, w_total)

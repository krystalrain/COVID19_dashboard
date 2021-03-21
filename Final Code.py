# -*- coding: utf-8 -*-
"""
Created on Fri Mar 12 15:26:37 2021

@author: Team : Alex Jackson, Himanshu Arora, Shubham Jain, William Jacobs
"""

import pandas as pd 
import numpy as np 
import os
import matplotlib
import matplotlib.pyplot as plt
import bs4

from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
from tabulate import tabulate


def fetchVaccineAtttitudeData():
    ###### WEBSCRAPPING BEGINS ######
    my_url = "https://news.gallup.com/poll/328415/readiness-covid-vaccine-steadies.aspx"

    #reads the page 
    uClient = uReq(my_url) 
    page_html = uClient.read() 

    uClient.close()


    #html parsing 
    page_soup = soup(page_html, "html.parser")
    #covert to a str
    page_txt = str(page_soup)

    with open('./{}.txt'.format("Cdata"), mode='wt', encoding='utf-8') as file_object:
        file_object.write(str(page_soup))

    #from the html page inspector I found the ID for the table I want to scrape using bs4 
    data_t = page_soup.findAll("div", {"id" : "caption-20210111152750"})


    ###### WEBSCRAPPING ENDS ######

    #wrote the entier txt to a file to parse as one bg string 
    with open('./{}.txt'.format("Cdata"), mode='wt', encoding='utf-8') as file_object:
        file_object.write(page_txt)

    ###### CLEANING BEGINS ######
    path = "Cdata.txt"

    trip = 0
    trip2 = 0
    table = []
    all_data = []
    table_titles = []
    date = []
    here = "no"
    #open the file and go line by line 
    for line in open(path):
        all_data.append(line)
        index = len(all_data)
        #check to find when we have reached the table 
        if line.find("Willingness to Be Vaccinated for COVID-19") != -1:
            trip = 1
            here = "yes"
        #once we reach the table get the row info     
        if trip == 1: 
            here = "yes"
            if line[0:3] == "<td":
                line = line.strip()
                table.append(line)
        if line.find("<th scope=\"row\"") != -1:
                table_titles.append(line)
        #grab the column name list 

        if line.find("</tr>") != -1:
            trip2 = 0

        if all_data[index-2].find("Total U.S. adults") != -1:
            trip2 = 1

        if trip2 == 1:
            date_end = line.find("data-thunit")
            date.append(line[13:date_end-2])



    def append_value(dic_new, key, value):
        if key in dic_new:
            if not isinstance(dic_new[key], list):
                dic_new[key] = [dic_new[key]]
            dic_new[key].append(value)
        else:
            dic_new[key] = value



    #parse out the percentage yes for taking the vaccine for each row 
    per = []

    for line in table:
        x = line.find("data-thunit=")
        if x != -1:
            per_s = x + 16
            per_e = per_s + 2 
            per.append(line[per_s:per_e])




    #parse out the table names 

    row = []
    for line in table_titles:
        title_s = line.find(">") + 1
        title_e = line.find("</th>")

        row.append(line[title_s:title_e])

    temp_d = {} 


    # for i in range(len(date)):
    #     temp_d[date[i]] = ""


    count = 0
    for index in range(len(per)):
        append_value(temp_d, date[count], per[index])
        count += 1 
        if count == 4:
            count = 0

    #create the final data frame
    df = pd.DataFrame(temp_d)

    df.index = row

    print(df)

    df.to_excel("AttData.xlsx", index=True, header=True)
    
    
#######################################################################################

def fetchStateVaccineData(state):
    path = "COVID_data/" + state + ".xlsx"

    file = state + ".xlsx"

    df = pd.read_excel(path)


    rows = []
    for i in df.iloc[6:69, 0]:
        rows.append(i)
#     print(rows)
    df.drop(df.columns[14:], axis=1, inplace=True)

    df.drop(df.index[69:], axis=0, inplace=True)
    df = df.iloc[6: , 1:]
#     print(df)
    df.columns = ["Total", "Concerned about possible side effects", "Don’t know if a vaccine will work", "Don’t believe I need a vaccine", "Don’t like vaccines", "Doctor has not recommended it", "Plan to wait and see if it is safe", "Other people need it more right now", "Concerned about the cost", "Don’t trust COVID-19 vaccines", "Don’t trust the government", "Other", "Did not report"]

    df = df.reset_index(drop=True)
    df.index = rows
#     print(df)


    #create a new file to be parsed to amke graphs 
    name = "data" + state + ".xlsx"
    df.to_excel(name, index=True, header=True)
    
    
    ##########Vaccine Project#################################################
    
    #Use a file generated above
    path = "data" + state + ".xlsx"


    df2 = pd.read_excel(path)


    #get rid of NaN values, commas, and slice the df to just what we need 

    # df2 = df2.dropna()
    df = df2.iloc[:, [2,3,7,8,10]]
    df.replace(',','', regex=True, inplace=True)
    df.reset_index(drop=True, inplace=True)



    #go through the data frame and find the percentages for each reaons by demogrpahics
    new_d = {}
    stats_for_demo = []
    for reason in df.columns:
        end = len(df[reason])
        for index in range(0, end):
            #if it's a Nan value keep it put don't perfrom math
            try:
                int(df[reason][index])
            except:
                new_list = "Nan"
                stats_for_demo.append(new_list)
            else:
                demo = int(df[reason][index])
                total = int(df[reason][0])

                new_list = demo/total * 100
                stats_for_demo.append(new_list)

        new_d[reason] = stats_for_demo
        stats_for_demo = []

#     print(new_d)
    #create a new df with percents
    df3 = pd.DataFrame.from_dict(new_d) 

    df3.index = df2.iloc[:, 0]
    
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    df3.fillna(0)
    
#     print(df3.iloc[11:16, 1])

    ### GRAPHING BEGINS HERE ### cite: https://www.geeksforgeeks.org/bar-plot-in-matplotlib/
#     print(df3)
    ### Age ###
    names = []
    for i in df2["Unnamed: 0"]:
          names.append(i)
    labels = names[2:7]
    values = []


    #create a unquie list for each top 5 reason type
    side_effects = []
    for x in df3.iloc[2:7, 0]:
        side_effects.append(round(x))

    will_work = []
    for x in df3.iloc[2:7, 1]:
        will_work.append(round(x))

    see_safe = []
    for x in df3.iloc[2:7, 2]:
        see_safe.append(round(x))

    altruism = []
    for x in df3.iloc[2:7, 3]:
        altruism.append(round(x))

    no_trust = []
    for x in df3.iloc[2:7, 4]:
        no_trust.append(round(x))



    # set width of bar 
    barWidth = 0.15
    fig = plt.subplots(figsize =(12, 8)) 



    br1 = np.arange(len(side_effects)) 
    br2 = [x + barWidth for x in br1] 
    br3 = [x + barWidth for x in br2] 
    br4 = [x + barWidth for x in br3] 
    br5 = [x + barWidth for x in br4] 


    plt.bar(br1, side_effects, color ='r', width = barWidth, 
            edgecolor ='grey', align="edge", label ='Concerned about possible side effects') 
    plt.bar(br2, will_work, color ='b', width = barWidth, 
            edgecolor ='grey',align="edge", label ="Don’t know if a vaccine will work") 
    plt.bar(br3, see_safe, color ='g', width = barWidth, 
            edgecolor ='grey', align="edge",label ="Plan to wait and see if it is safe") 
    plt.bar(br4, altruism, color ='y', width = barWidth, 
            edgecolor ='grey',align="edge", label ="Other people need it more right now") 
    plt.bar(br5, no_trust, color ='m', width = barWidth, 
            edgecolor ='grey',align="edge", label ="Don’t trust COVID-19 vaccines") 



    plt.ylim([0, 100])
    plt.xlabel('Age Groups', fontweight ='bold', fontsize = 10) 
    plt.ylabel('% of respondents', fontweight ='bold', fontsize = 10) 
    plt.xticks([r + barWidth for r in range(len(side_effects))], 
            labels)



    plt.legend()
    plt.show() 

    ### Gender ###

    labels = names[8:10]

    #create a unquie list for each top 5 reason type
    side_effects = []
    for x in df3.iloc[8:10, 0]:
        side_effects.append(round(x))

    will_work = []
    for x in df3.iloc[8:10, 1]:
        will_work.append(round(x))

    see_safe = []
    for x in df3.iloc[8:10, 2]:
        see_safe.append(round(x))

    altruism = []
    for x in df3.iloc[8:10, 3]:
        altruism.append(round(x))

    no_trust = []
    for x in df3.iloc[8:10, 4]:
        no_trust.append(round(x))




    # set width of bar 
    barWidth = 0.15
    fig = plt.subplots(figsize =(12, 8)) 




    br1 = np.arange(len(side_effects)) 
    br2 = [x + barWidth for x in br1] 
    br3 = [x + barWidth for x in br2] 
    br4 = [x + barWidth for x in br3] 
    br5 = [x + barWidth for x in br4] 


    plt.bar(br1, side_effects, color ='r', width = barWidth, 
            edgecolor ='grey', align="edge", label ='Concerned about possible side effects') 
    plt.bar(br2, will_work, color ='b', width = barWidth, 
            edgecolor ='grey',align="edge", label ="Don’t know if a vaccine will work") 
    plt.bar(br3, see_safe, color ='g', width = barWidth, 
            edgecolor ='grey', align="edge",label ="Plan to wait and see if it is safe") 
    plt.bar(br4, altruism, color ='y', width = barWidth, 
            edgecolor ='grey',align="edge", label ="Other people need it more right now") 
    plt.bar(br5, no_trust, color ='m', width = barWidth, 
            edgecolor ='grey',align="edge", label ="Don’t trust COVID-19 vaccines") 



    plt.ylim([0, 100])
    plt.xlabel('Gender', fontweight ='bold', fontsize = 15) 
    plt.ylabel('% of respondents', fontweight ='bold', fontsize = 15) 
    plt.xticks([r + barWidth for r in range(len(side_effects))], 
            labels)



    plt.legend()
    plt.show()


    ### Race ### 


    labels = names[11:16]

    #create a unquie list for each top 5 reason type
    side_effects = []
    for x in df3.iloc[11:16, 0]:
        side_effects.append(round(x))

    will_work = []
    for x in df3.iloc[11:16, 1]:
        will_work.append(round(x))

    see_safe = []
    for x in df3.iloc[11:16, 2]:
        see_safe.append(round(x))

    altruism = []
    for x in df3.iloc[11:16, 3]:
        altruism.append(round(x))

    no_trust = []
    for x in df3.iloc[11:16, 4]:
        no_trust.append(x)




    # set width of bar 
    barWidth = 0.15
    fig = plt.subplots(figsize =(12, 8)) 



    br1 = np.arange(len(side_effects)) 
    br2 = [x + barWidth for x in br1] 
    br3 = [x + barWidth for x in br2] 
    br4 = [x + barWidth for x in br3] 
    br5 = [x + barWidth for x in br4] 


    plt.bar(br1, side_effects, color ='r', width = barWidth, 
            edgecolor ='grey', align="edge", label ='Concerned about possible side effects') 
    plt.bar(br2, will_work, color ='b', width = barWidth, 
            edgecolor ='grey',align="edge", label ="Don’t know if a vaccine will work") 
    plt.bar(br3, see_safe, color ='g', width = barWidth, 
            edgecolor ='grey', align="edge",label ="Plan to wait and see if it is safe") 
    plt.bar(br4, altruism, color ='y', width = barWidth, 
            edgecolor ='grey',align="edge", label ="Other people need it more right now") 
    plt.bar(br5, no_trust, color ='m', width = barWidth, 
            edgecolor ='grey',align="edge", label ="Don’t trust COVID-19 vaccines") 


    plt.ylim([0, 100])
    plt.xlabel('Race', fontweight ='bold', fontsize = 15) 
    plt.ylabel('% of respondents', fontweight ='bold', fontsize = 15) 
    plt.xticks([r + barWidth for r in range(len(side_effects))], 
            labels, fontsize=6)



    plt.legend()
    plt.show()


    ### Education ### 


    labels = names[17:21]

    #create a unquie list for each top 5 reason type
    
    
    side_effects = []
    for x in df3.iloc[17:21, 0]:
        side_effects.append(round(x))

    will_work = []
    for x in df3.iloc[17:21, 1]:
        will_work.append(round(x))

    see_safe = []
    for x in df3.iloc[17:21, 2]:
        see_safe.append(round(x))

    altruism = []
    for x in df3.iloc[17:21, 3]:
        altruism.append(round(x))

    no_trust = []
    for x in df3.iloc[17:21, 4]:
        no_trust.append(round(x))


    # set width of bar 
    barWidth = 0.15
    fig = plt.subplots(figsize =(12, 8)) 



    br1 = np.arange(len(side_effects)) 
    br2 = [x + barWidth for x in br1] 
    br3 = [x + barWidth for x in br2] 
    br4 = [x + barWidth for x in br3] 
    br5 = [x + barWidth for x in br4] 


    plt.bar(br1, side_effects, color ='r', width = barWidth, 
            edgecolor ='grey', align="edge", label ='Concerned about possible side effects') 
    plt.bar(br2, will_work, color ='b', width = barWidth, 
            edgecolor ='grey',align="edge", label ="Don’t know if a vaccine will work") 
    plt.bar(br3, see_safe, color ='g', width = barWidth, 
            edgecolor ='grey', align="edge",label ="Plan to wait and see if it is safe") 
    plt.bar(br4, altruism, color ='y', width = barWidth, 
            edgecolor ='grey',align="edge", label ="Other people need it more right now") 
    plt.bar(br5, no_trust, color ='m', width = barWidth, 
            edgecolor ='grey',align="edge", label ="Don’t trust COVID-19 vaccines") 


    plt.ylim([0, 100])
    plt.xlabel('Education Level', fontweight ='bold', fontsize = 15) 
    plt.ylabel('% of respondents', fontweight ='bold', fontsize = 15) 
    plt.xticks([r + barWidth for r in range(len(side_effects))], 
            labels, fontsize=8)



    plt.legend()
    plt.show()


    ### Income ### 


    labels = names[40:48]
    # print(labels)
    #create a unquie list for each top 5 reason type
    side_effects = []
    for x in df3.iloc[40:48, 0]:
#         print(x)
        side_effects.append(round(x))

    will_work = []
    for x in df3.iloc[40:48, 1]:
        will_work.append(round(x))

    see_safe = []
    for x in df3.iloc[40:48, 2]:
        see_safe.append(round(x))

    altruism = []
    for x in df3.iloc[40:48, 3]:
        altruism.append(round(x))

    no_trust = []
    for x in df3.iloc[40:48, 4]:
        no_trust.append(round(x))


    # set width of bar 
    barWidth = 0.15
    fig = plt.subplots(figsize =(12, 8)) 



    br1 = np.arange(len(side_effects)) 
    br2 = [x + barWidth for x in br1] 
    br3 = [x + barWidth for x in br2] 
    br4 = [x + barWidth for x in br3] 
    br5 = [x + barWidth for x in br4] 


    plt.bar(br1, side_effects, color ='r', width = barWidth, 
            edgecolor ='grey', align="edge", label ='Concerned about possible side effects') 
    plt.bar(br2, will_work, color ='b', width = barWidth, 
            edgecolor ='grey',align="edge", label ="Don’t know if a vaccine will work") 
    plt.bar(br3, see_safe, color ='g', width = barWidth, 
            edgecolor ='grey', align="edge",label ="Plan to wait and see if it is safe") 
    plt.bar(br4, altruism, color ='y', width = barWidth, 
            edgecolor ='grey',align="edge", label ="Other people need it more right now") 
    plt.bar(br5, no_trust, color ='m', width = barWidth, 
            edgecolor ='grey',align="edge", label ="Don’t trust COVID-19 vaccines") 


    plt.ylim([0, 100])
    plt.xlabel('Income Group', fontweight ='bold', fontsize = 15) 
    plt.ylabel('% of respondents', fontweight ='bold', fontsize = 15) 
    plt.xticks([r + barWidth for r in range(len(side_effects))], 
            labels, fontsize=6)



    plt.legend()
    plt.show()

###########################################################################################

# How vaccine attidues have changed in the US overall, over time
def vaccineAttitudesChangedOverTime():
    
    ###################Scrapping Data#######################################
    
    my_url = "https://news.gallup.com/poll/328415/readiness-covid-vaccine-steadies.aspx"

    #reads the page 
    uClient = uReq(my_url) 
    page_html = uClient.read() 

    uClient.close()


    #html parsing 
    page_soup = soup(page_html, "html.parser")
    #covert to a str
    page_txt = str(page_soup)

    with open('./{}.txt'.format("Cdata"), mode='wt', encoding='utf-8') as file_object:
        file_object.write(str(page_soup))

    #from the html page inspector I found the ID for the table I want to scrape using bs4 
    data_t = page_soup.findAll("div", {"id" : "caption-20210111152750"})



    ###### WEBSCRAPPING ENDS ######

    #wrote the entier txt to a file to parse as one bg string 
    with open('./{}.txt'.format("Cdata"), mode='wt', encoding='utf-8') as file_object:
        file_object.write(page_txt)

    ###### CLEANING BEGINS ######
    path = "Cdata.txt"

    trip = 0
    trip2 = 0
    table = []
    all_data = []
    table_titles = []
    date = []
    here = "no"
    #open the file and go line by line 
    for line in open(path):
        all_data.append(line)
        index = len(all_data)
        #check to find when we have reached the table 
        if line.find("Willingness to Be Vaccinated for COVID-19") != -1:
            trip = 1
            here = "yes"
        #once we reach the table get the row info     
        if trip == 1: 
            here = "yes"
            if line[0:3] == "<td":
                line = line.strip()
                table.append(line)
        if line.find("<th scope=\"row\"") != -1:
                table_titles.append(line)
        #grab the column name list 

        if line.find("</tr>") != -1:
            trip2 = 0

        if all_data[index-2].find("Total U.S. adults") != -1:
            trip2 = 1

        if trip2 == 1:
            date_end = line.find("data-thunit")
            date.append(line[13:date_end-2])



    def append_value(dic_new, key, value):
        if key in dic_new:
            if not isinstance(dic_new[key], list):
                dic_new[key] = [dic_new[key]]
            dic_new[key].append(value)
        else:
            dic_new[key] = value



    #parse out the percentage yes for taking the vaccine for each row 
    per = []

    for line in table:
        x = line.find("data-thunit=")
        if x != -1:
            per_s = x + 16
            per_e = per_s + 2 
            per.append(line[per_s:per_e])




    #parse out the table names 

    row = []
    for line in table_titles:
        title_s = line.find(">") + 1
        title_e = line.find("</th>")

        row.append(line[title_s:title_e])

    temp_d = {} 


    # for i in range(len(date)):
    #     temp_d[date[i]] = ""


    count = 0
    for index in range(len(per)):
        append_value(temp_d, date[count], per[index])
        count += 1 
        if count == 4:
            count = 0

    #create the final data frame
    df = pd.DataFrame(temp_d)

    df.index = row

#     print(df)
    df.to_excel("AttData.xlsx", index=True, header=True)
    #########################################################################
    
    path = "AttData.xlsx"
    df = pd.read_excel(path)


    #get rid of NaN values, commas, and slice the df to just what we need 


    names = []
    for i in df["Unnamed: 0"]:
          names.append(i)

    ### Gender ###

    labels = names[1:3]

    #create a unquie list for each top 5 reason type
    per1 = []
    for x in df.iloc[1:3, 1]:
        per1.append(x)

    per2 = []
    for x in df.iloc[1:3, 2]:
        per2.append(x)

    per3 = []
    for x in df.iloc[1:3, 3]:
        per3.append(x)

    per4 = []
    for x in df.iloc[1:3, 4]:
        per4.append(x)




    # set width of bar 
    barWidth = 0.15
    fig = plt.subplots(figsize =(12, 8)) 



    br1 = np.arange(len(per1)) 
    br2 = [x + barWidth for x in br1] 
    br3 = [x + barWidth for x in br2] 
    br4 = [x + barWidth for x in br3] 



    plt.bar(br1, per1, color ='r', width = barWidth, 
            edgecolor ='grey', align="edge", label ='Jul 20-26') 
    plt.bar(br2, per2, color ='b', width = barWidth, 
            edgecolor ='grey',align="edge", label ="Sep 14-27") 
    plt.bar(br3, per3, color ='g', width = barWidth, 
            edgecolor ='grey', align="edge",label ="Nov 16-29") 
    plt.bar(br4, per4, color ='y', width = barWidth, 
            edgecolor ='grey',align="edge", label ="Dec 15-Jan 3") 



    plt.ylim([0, 100])
    plt.xlabel('Gender', fontweight ='bold', fontsize = 15) 
    plt.ylabel('% of respondents', fontweight ='bold', fontsize = 15) 
    plt.xticks([r + barWidth for r in range(len(per1))], 
            labels)



    plt.legend()
    plt.show()


    ### Age ###

    labels = names[3:6]

    #create a unquie list for each top 5 reason type
    per1 = []
    for x in df.iloc[3:6, 1]:
        per1.append(x)

    per2 = []
    for x in df.iloc[3:6, 2]:
        per2.append(x)

    per3 = []
    for x in df.iloc[3:6, 3]:
        per3.append(x)

    per4 = []
    for x in df.iloc[3:6, 4]:
        per4.append(x)




    # set width of bar 
    barWidth = 0.15
    fig = plt.subplots(figsize =(12, 8)) 



    br1 = np.arange(len(per1)) 
    br2 = [x + barWidth for x in br1] 
    br3 = [x + barWidth for x in br2] 
    br4 = [x + barWidth for x in br3] 



    plt.bar(br1, per1, color ='r', width = barWidth, 
            edgecolor ='grey', align="edge", label ='Jul 20-26') 
    plt.bar(br2, per2, color ='b', width = barWidth, 
            edgecolor ='grey',align="edge", label ="Sep 14-27") 
    plt.bar(br3, per3, color ='g', width = barWidth, 
            edgecolor ='grey', align="edge",label ="Nov 16-29") 
    plt.bar(br4, per4, color ='y', width = barWidth, 
            edgecolor ='grey',align="edge", label ="Dec 15-Jan 3") 



    plt.ylim([0, 100])
    plt.xlabel('Age Group', fontweight ='bold', fontsize = 15) 
    plt.ylabel('% of respondents', fontweight ='bold', fontsize = 15) 
    plt.xticks([r + barWidth for r in range(len(per1))], 
            labels)



    plt.legend()
    plt.show()

    ### Education ###

    labels = names[6:8]

    #create a unquie list for each top 5 reason type
    per1 = []
    for x in df.iloc[6:8, 1]:
        per1.append(x)

    per2 = []
    for x in df.iloc[6:8, 2]:
        per2.append(x)

    per3 = []
    for x in df.iloc[6:8, 3]:
        per3.append(x)

    per4 = []
    for x in df.iloc[6:8, 4]:
        per4.append(x)




    # set width of bar 
    barWidth = 0.15
    fig = plt.subplots(figsize =(12, 8)) 



    br1 = np.arange(len(per1)) 
    br2 = [x + barWidth for x in br1] 
    br3 = [x + barWidth for x in br2] 
    br4 = [x + barWidth for x in br3] 



    plt.bar(br1, per1, color ='r', width = barWidth, 
            edgecolor ='grey', align="edge", label ='Jul 20-26') 
    plt.bar(br2, per2, color ='b', width = barWidth, 
            edgecolor ='grey',align="edge", label ="Sep 14-27") 
    plt.bar(br3, per3, color ='g', width = barWidth, 
            edgecolor ='grey', align="edge",label ="Nov 16-29") 
    plt.bar(br4, per4, color ='y', width = barWidth, 
            edgecolor ='grey',align="edge", label ="Dec 15-Jan 3") 



    plt.ylim([0, 100])
    plt.xlabel('Education', fontweight ='bold', fontsize = 15) 
    plt.ylabel('% of respondents', fontweight ='bold', fontsize = 15) 
    plt.xticks([r + barWidth for r in range(len(per1))], 
            labels)



    plt.legend()
    plt.show()

    ### Race ###

    labels = names[8:10]

    #create a unquie list for each top 5 reason type
    per1 = []
    for x in df.iloc[8:10, 1]:
        per1.append(x)

    per2 = []
    for x in df.iloc[8:10, 2]:
        per2.append(x)

    per3 = []
    for x in df.iloc[8:10, 3]:
        per3.append(x)

    per4 = []
    for x in df.iloc[8:10, 4]:
        per4.append(x)




    # set width of bar 
    barWidth = 0.15
    fig = plt.subplots(figsize =(12, 8)) 



    br1 = np.arange(len(per1)) 
    br2 = [x + barWidth for x in br1] 
    br3 = [x + barWidth for x in br2] 
    br4 = [x + barWidth for x in br3] 



    plt.bar(br1, per1, color ='r', width = barWidth, 
            edgecolor ='grey', align="edge", label ='Jul 20-26') 
    plt.bar(br2, per2, color ='b', width = barWidth, 
            edgecolor ='grey',align="edge", label ="Sep 14-27") 
    plt.bar(br3, per3, color ='g', width = barWidth, 
            edgecolor ='grey', align="edge",label ="Nov 16-29") 
    plt.bar(br4, per4, color ='y', width = barWidth, 
            edgecolor ='grey',align="edge", label ="Dec 15-Jan 3") 



    plt.ylim([0, 100])
    plt.xlabel('White vs Non-White', fontweight ='bold', fontsize = 15) 
    plt.ylabel('% of respondents', fontweight ='bold', fontsize = 15) 
    plt.xticks([r + barWidth for r in range(len(per1))], 
            labels)



    plt.legend()
    plt.show()

#########################################################################################

class State:
    # Reads the input state from csv, and creates a dataframe of that state's information.
    def __init__(self, State):
        self.State = State
        self.data = None
        self.stateframe()
    # this will read a csv file, and create a pandas dataframe from it according to the state.
    def stateframe(self):
        self.data = pd.read_csv('State_data2', delimiter=',')
        self.data = self.data.drop(['Unnamed: 0'], axis=1)
        mask = (self.data['State'] == self.State)
        self.data = self.data[mask]
        #print(self.data)
    # creates the graphs from the dataframe of that state.
    #These are hard coded topics, but ideally you could pick the topics to compare based on the available data.
    def creategraphs(self):
        fig, axes = plt.subplots(2, 3, figsize=(15, 15))
        sexGroup = self.data.groupby(['Sex','State','Flu Vacc'])['Flu Vacc'].agg('count').to_frame('Count').reset_index()
        sexGroup['Perc'] = sexGroup.Count / sexGroup.groupby('Sex').Count.transform('sum')
        # #sexGroup['Perc'] = (sexGroup['Count']/sexGroup['Count'].sum())

        ageGroup = self.data.groupby(['Age Group','State','Flu Vacc'])['Flu Vacc'].agg('count').to_frame('Count').reset_index()
        ageGroup['Perc'] = ageGroup.Count / ageGroup.groupby('Age Group').Count.transform('sum')
        ethGroup = self.data.groupby(['Ethnicity','State','Flu Vacc'])['Flu Vacc'].agg('count').to_frame('Count').reset_index()
        ethGroup['Perc'] = ethGroup.Count / ethGroup.groupby('Ethnicity').Count.transform('sum')
        eduGroup = self.data.groupby(['Education','State','Flu Vacc'])['Flu Vacc'].agg('count').to_frame('Count').reset_index()
        eduGroup['Perc'] = eduGroup.Count / eduGroup.groupby('Education').Count.transform('sum')
        incGroup = self.data.groupby(['Family Income','State','Flu Vacc'])['Flu Vacc'].agg('count').to_frame('Count').reset_index()
        incGroup['Perc'] = incGroup.Count / incGroup.groupby('Family Income').Count.transform('sum')
        metGroup = self.data.groupby(['MSA','State','Flu Vacc'])['Flu Vacc'].agg('count').to_frame('Count').reset_index()
        metGroup['Perc'] = metGroup.Count / metGroup.groupby('MSA').Count.transform('sum')

        sexGroup.groupby(['State','Sex','Flu Vacc']).sum().unstack().plot(y='Perc',kind='bar', stacked=True, ax=axes[0][0])
        ageGroup.groupby(['Age Group','State', 'Flu Vacc']).sum().unstack().plot(y='Perc',kind='bar', stacked=True, ax=axes[0][1])
        ethGroup.groupby(['Ethnicity','State', 'Flu Vacc']).sum().unstack().plot(y='Perc',kind='bar', stacked=True, ax=axes[1][1])
        eduGroup.groupby(['Education','State', 'Flu Vacc']).sum().unstack().plot(y='Perc',kind='bar', stacked=True, ax=axes[1][0])
        incGroup.groupby(['Family Income','State', 'Flu Vacc']).sum().unstack().plot(y='Perc',kind='bar', stacked=True, ax=axes[0][2])
        metGroup.groupby(['MSA', 'State', 'Flu Vacc']).sum().unstack().plot(y='Perc', kind='bar',stacked=True, ax=axes[1][2])

        axes[0,0].set_xticklabels(np.unique(sexGroup['Sex'].values), rotation=0)
        axes[0,1].set_xticklabels(np.unique(ageGroup['Age Group'].values), rotation=45,ha='right')
        axes[1,0].set_xticklabels(np.unique(eduGroup['Education'].values), rotation=45,ha='right')
        axes[1,1].set_xticklabels(np.unique(ethGroup['Ethnicity'].values), rotation=45,ha='right')
        axes[0,2].set_xticklabels(np.unique(incGroup['Family Income'].values), rotation=45,ha='right')
        axes[1,2].set_xticklabels(np.unique(metGroup['MSA'].values), rotation=45, ha='right')
        axes[0,0].legend(title = 'Flu Vacc',loc='upper center', bbox_to_anchor=(0.5, .95),
          ncol=1, fancybox=True, shadow=True)
        axes[0,1].legend(title = 'Flu Vacc', loc='upper right', bbox_to_anchor=(0.85, .95),
          ncol=1, fancybox=True, shadow=True)
        axes[1,0].legend(title = 'Flu Vacc',loc='upper center', bbox_to_anchor=(0.85, .95),
          ncol=1, fancybox=True, shadow=True)
        axes[1,1].legend(title = 'Flu Vacc',loc='upper center', bbox_to_anchor=(0.85,.95),
          ncol=1, fancybox=True, shadow=True)
        axes[0,2].legend(title = 'Flu Vacc',loc='upper center', bbox_to_anchor=(0.85, .95),
          ncol=1, fancybox=True, shadow=True)
        axes[1,2].legend(title = 'Flu Vacc',loc='upper center', bbox_to_anchor=(0.85, .95),
          ncol=1, fancybox=True, shadow=True)

        axes[0,0].title.set_text('Sex')
        axes[0,1].title.set_text('Age Group')
        axes[0,2].title.set_text('Income')
        axes[1,0].title.set_text('Education')
        axes[1,1].title.set_text('Ethnicity')
        axes[1,2].title.set_text('Metropolitan')
        Title = self.State + ' Flu Vaccine \nInformation'
        plt.suptitle(Title, fontsize=16)
        plt.show()
        
########################################################################################################

#this reads the raw data and converts it to a readable form, and puts it into a CSV file to be read.
def createCSV(filename):
    file = open("LLCP2019.ASC")
    lineList = []
    # assuming the data is input randomly, 1/10 of the data is just as good as all of the data.

    line = file.readline()  # 418268
    count = 0
    while line:
        line = file.readline()
        lineList.append(line)
        # count += 1
    # use this to get the number of lines.This skips x number of lines
    records = lineList[::10]
    # print(len(records))
    file.close()

    # numhouse = i[69:71] 1,2,3,4,5 6=6 or more
    # sex = i[91] #1 = male, 2 female
    # genHealth = i[100]
    # maritalStat = i[172]
    # educ = i[173]
    # employStat = i[187]
    # numChildHouse = i[188:190]
    # famIncome = i[190:192]
    # weight = i[192:196] #7777 == don't know, #9___ indicates kg, #0___ indicates pounds
    # height = i[196:200] #9 indiciates metric/ else Notes: 0 _ / _ _ = feet / inches #7777 = don't know
    # oneHundCig = i[207] #have you ever smoked at least 100 cigarettes in your life
    # cigNow = i[208]
    # lastSmoke = i[210:212]
    # exerciseDict = i[223] 1=have exercised, 2= no, last 30 days
    # adultFluVacc = i[260] last 12months
    # fluDate = i[261:267]
    # MetropolStat = i[1401] 1 = metro, 2 = not
    # urbStat = i[1402] #1=urban, 2 = rural
    # metroStatCode = i[1408]
    # ageGrp = i[1980:1982]
    # ethnic = i[1470:1472]
    ageGrpDict = {
        '01': '18-24',
        '02': '25-29',
        '03': '30-34',
        '04': '35-39',
        '05': '40-44',
        '06': '45-49',
        '07': '50-54',
        '08': '55-59',
        '09': '60-64',
        '10': '65-69',
        '11': '70-74',
        '12': '75-79',
        '13': '80 or older',
        '14': 'Refused or missing'
    }
    stateDict = {
        '02': 'Alaska',
        '01': 'Alabama',
        '05': 'Arkansas',
        '04': 'Arizona',
        '06': 'California',
        '08': 'Colorado',
        '09': 'Connecticut',
        '11': 'DC',
        '10': 'Delaware',
        '12': 'Florida',
        '13': 'Georgia',
        '15': 'Hawaii',
        '19': 'Iowa',
        '16': 'Idaho',
        '17': 'Illinois',
        '18': 'Indiana',
        '20': 'Kansas',
        '21': 'Kentucky',
        '22': 'Louisiana',
        '25': 'Massachusetts',
        '24': 'Maryland',
        '23': 'Maine',
        '26': 'Michigan',
        '27': 'Minnesota',
        '29': 'Missouri',
        '28': 'Mississippi',
        '30': 'Montana',
        '37': 'North Carolina',
        '38': 'North Dakota',
        '31': 'Nebraska',
        '33': 'New Hampshire',
        '34': 'New Jersey',
        '35': 'New Mexico',
        '32': 'Nevada',
        '36': 'New York',
        '39': 'Ohio',
        '40': 'Oklahoma',
        '41': 'Oregon',
        '42': 'Pennsylvania',
        '44': 'Rhode Island',
        '45': 'South Carolina',
        '46': 'South Dakota',
        '47': 'Tennessee',
        '48': 'Texas',
        '49': 'Utah',
        '51': 'Virginia',
        '50': 'Vermont',
        '53': 'Washington',
        '55': 'Wisconsin',
        '54': 'West Virginia',
        '56': 'Wyoming',
        '66': 'Guam',
        '72': 'Puerto Rico'
    }
    healthDict = {'1': 'Excellent',
                  '2': 'Very Good',
                  '3': 'Good',
                  '4': 'Fair',
                  '5': 'Poor',
                  '7': 'Don\'t know\\Not Sure',
                  '9': 'Refused'

                  }
    maritalDict = {
        '1': 'Married',
        '2': 'Divorced',
        '3': 'Widowed',
        '4': 'Separated',
        '5': 'Never Married',
        '6': 'Member of unmarried Couple',
        '9': 'Refused'
    }
    educDict = {
        '1': 'Never Attended/Kindergarten',
        '2': 'Elementary',
        '3': 'Some Highschool',
        '4': 'High school Grad/GED',
        '5': 'Some college',
        '6': 'College Grad',
        '9': 'Refused'
    }
    empStatDict = {
        '1': 'Employed',
        '2': 'Self-Employed',
        '3': 'Out of Work >= 1year',
        '4': 'Out of Work < 1year',
        '5': 'Homemaker',
        '6': 'Student',
        '7': 'Retired',
        '8': 'Unable to work',
        '9': 'Refused'
    }
    famincDict = {'01': '$0-$10,000',
                  '02': '$10,001-$15,000',
                  '03': '$15,001-$20,000',
                  '04': '$20,001-$25,000',
                  '05': '$25,001-$35,000',
                  '06': '$35,001-$50,000',
                  '07': '$50,001-$75,000',
                  '08': '>$75,000',
                  '77': 'Don\'t Know/Not Sure',
                  '99': 'Refused'
                  }
    cigNowDict = {
        '1': 'Every day',
        '2': 'Some days',
        '3': 'Not at all',
        '7': 'Don\'t Know/Not Sure',
        '9': 'Refused',
    }
    lastSmokeDict = {
        '01': 'Less than 1 month ago',
        '02': 'Within 3 months',
        '03': 'Within 6 months',
        '04': 'Within 12 months',
        '05': 'Within past 5 years',
        '06': 'Within past 10 years',
        '07': 'More than 10 years',
        '08': 'Never smoked regularly',
        '77': 'Don\'t Know/Not Sure',
        '99': 'Refused'
    }
    metroStatCodeDict = {  # MSA = Metropolitan Stat Area = Area of 50,000 People
        '1': 'In the center of MSA',
        '2': 'Outside of center of MSA, but inside county containing metro center',
        '3': 'Inside suburban county of MSA',
        '5': 'Not in MSA',
    }
    ethnicDict = {'05': 'Hispanic',
                  '01': 'White',
                  '02': 'Black',
                  '03': 'Asian',
                  '04': 'American Indian/Alaskan Native',
                  '06': 'Non-Hispanic Other/Multiple Race'}
    sexDict = {'1': 'Male',
               '2': 'Female'}
    binaryDict = {'1': 'Yes',
                  '2': 'No'}
    BMIDict = {
        '1': 'Underweight',
        '2': 'Normal Weight',
        '3': 'Overweight',
        '4': 'Obese',
        '5': 'Don\'t Know/Refused'
    }
    urbanDict = {
        '1': 'Urban',
        '2': 'Rural'
    }
    column = ['State', 'Sex', 'Age Group', 'Ethnicity', 'Family Income', 'Education', 'Employment Status',
              'Health Status',
              'BMI', 'Total in House', 'Smoker', 'Last Cigarette', 'Does Exercise', 'Flu Vacc', 'Flu Vacc Date',
              'Metro Area'
        , 'Urban/Rural', 'MSA']
    data = pd.DataFrame(columns=column)

    pd.set_option('display.max_rows', 15)
    pd.set_option('display.max_columns', 15)
    pd.set_option('display.width', 100)
    # print(data.head())
    # start = time.time()
    count = 0
    for i in records:
        # print(count)
        # state = i[:2]
        # sex = i[90]
        # genHealth = i[100]
        # maritalStat = i[172]
        # educ = i[173]
        # employStat = i[187]
        # numChildHouse = i[188:190]
        # weight = i[192:196]
        # BMI = i[1997:2001]
        # height = i[196:200]
        # cigNow = i[208]
        # lastSmoke = i[210:212]
        # exercise = i[222]
        # faminc = i[190:192]
        # adultFluVacc = i[260]
        # isMetro = i[1401]
        # urbStat = i[1402]
        # metroStatCode = i[1408]
        # ageGrp = i[1980:1982]
        # ethnic = i[1470:1472]
        numhouse = i[69:71]
        fluDate = i[261:267]
        ethnic = ethnicDict.get(i[1470:1472])
        metroStatCode = metroStatCodeDict.get(i[1408])
        urbStat = urbanDict.get(i[1402])
        isMetro = binaryDict.get(i[1401])
        adultFluVacc = binaryDict.get(i[260])
        exercise = binaryDict.get(i[222])
        lastSmoke = lastSmokeDict.get(i[210:212])
        cigNow = cigNowDict.get(i[208])
        BMI = BMIDict.get(i[2001])
        employStat = empStatDict.get(i[187])
        educ = educDict.get(i[173])
        genHealth = healthDict.get(i[100])
        sex = sexDict.get(i[90])
        state = stateDict.get(i[:2])
        ageGrp = ageGrpDict.get(i[1980:1982])
        faminc = famincDict.get(i[190:192])
        data.loc[count] = [state, sex, ageGrp, ethnic, faminc, educ, employStat, genHealth, BMI, numhouse, cigNow,
                           lastSmoke, exercise
            , adultFluVacc, fluDate, isMetro, urbStat, metroStatCode]
        data.to_csv(filename)
        print(count)
        count = count + 1

pd.set_option('display.max_rows', 15)
pd.set_option('display.max_columns', 15)
pd.set_option('display.width', 100)
#this assumes that the state name is inputted exactly as it appears in the dictionary.
#Would be best as a DDL


####################################################################################################

def getChoice():
    choose=input("Enter Abbreviation of state or Enter 'q' to quit this sub-menu: " )
    choice=choose
    return choice

def printStates():
    print('\nMenu\n',
    'Select state : \n',
    '1. Alabama: ''AL\n',
    '2. Alaska : ''AK\n', 
    '3. Arizona: ''AZ\n',
    '4. Arkansas: ''AR\n',
    '5. California: ''CA\n',
    '6. Colorado: ''CO\n',
    '7. Connecticut: ''CT\n',
    '8. Delaware: ''DE\n',
    '9. District of Columbia: ''DC\n',
    '10. Florida: ''FL\n',
    '11. Georgia: ''GA\n',
    '12. Hawaii: ''HI\n',
    '13. Idaho: ''ID\n',
    '14. Illinois: ''IL\n',
    '15. Indiana: ''IN\n',
    '16. Iowa: ''IA\n',
    '17. Kansas: ''KS\n',
    '18. Kentucky: ''KY\n',
    '19. Louisiana: ''LA\n',
    '20. Maine: ''ME\n',
    '21. Maryland: ''MD\n',
    '22. Massachusetts: ''MA\n',
    '23. Michigan: ''MI\n',
    '24. Minnesota: ''MN\n',
    '25. Mississippi: ''MS\n',
    '26. Missouri: ''MO\n',
    '27. Montana: ''MT\n',
    '28. Nebraska: ''NE\n',
    '29. Nevada: ''NV\n',
    '30. New Hampshire: ''NH\n',
    '31. New Jersey: ''NJ\n',
    '32. New Mexico: ''NM\n',
    '33. New York: ''NY\n',
    '34. North Carolina: ''NC\n',
    '35. North Dakota: ''ND\n',
    '36. Ohio: ''OH\n',
    '37. Oklahoma: ''OK\n',
    '38. Oregon: ''OR\n',
    '39. Pennsylvania: ''PA\n',
    '40. Rhode Island: ''RI\n',
    '41. South Carolina: ''SC\n',
    '42. South Dakota: ''SD\n',
    '43. Tennessee: ''TN\n',
    '44. Texas: ''TX\n',
    '45. Utah: ''UT\n',
    '46. Vermont: ''VT\n',
    '47. Virginia: ''VA\n',
    '48. Washington: ''WA\n',
    '49. West Virginia: ''WV\n',
    '50. Wisconsin: ''WI\n',
    '51. Wyoming: ''WY\n'
    'Quit')
    
##################################################################################################

def getUSDict():
    us_state_abbrev = {
        'Alabama': 'AL',
        'Alaska': 'AK',
        'American Samoa': 'AS',
        'Arizona': 'AZ',
        'Arkansas': 'AR',
        'California': 'CA',
        'Colorado': 'CO',
        'Connecticut': 'CT',
        'Delaware': 'DE',
        'District of Columbia': 'DC',
        'Florida': 'FL',
        'Georgia': 'GA',
        'Guam': 'GU',
        'Hawaii': 'HI',
        'Idaho': 'ID',
        'Illinois': 'IL',
        'Indiana': 'IN',
        'Iowa': 'IA',
        'Kansas': 'KS',
        'Kentucky': 'KY',
        'Louisiana': 'LA',
        'Maine': 'ME',
        'Maryland': 'MD',
        'Massachusetts': 'MA',
        'Michigan': 'MI',
        'Minnesota': 'MN',
        'Mississippi': 'MS',
        'Missouri': 'MO',
        'Montana': 'MT',
        'Nebraska': 'NE',
        'Nevada': 'NV',
        'New Hampshire': 'NH',
        'New Jersey': 'NJ',
        'New Mexico': 'NM',
        'New York': 'NY',
        'North Carolina': 'NC',
        'North Dakota': 'ND',
        'Northern Mariana Islands':'MP',
        'Ohio': 'OH',
        'Oklahoma': 'OK',
        'Oregon': 'OR',
        'Pennsylvania': 'PA',
        'Puerto Rico': 'PR',
        'Rhode Island': 'RI',
        'South Carolina': 'SC',
        'South Dakota': 'SD',
        'Tennessee': 'TN',
        'Texas': 'TX',
        'Utah': 'UT',
        'Vermont': 'VT',
        'Virgin Islands': 'VI',
        'Virginia': 'VA',
        'Washington': 'WA',
        'West Virginia': 'WV',
        'Wisconsin': 'WI',
        'Wyoming': 'WY'
    }
    abbrev_us_state = dict(map(reversed, us_state_abbrev.items()))
    return us_state_abbrev, abbrev_us_state

##################################################################################################

def getTotalDeaths():
    d1, abbrev_us_state = getUSDict()
    df = pd.read_csv('death_counts_US.csv')
    pd.set_option('display.max_columns', 500)
    choice = getChoice()
    while choice!='q':
        if choice not in abbrev_us_state.keys():
            print("Invalid choice, please choose again")
            print("\n")
        elif choice in abbrev_us_state.keys():
            print('')
            df_display = df[df['State'] == choice].loc[:, ['County name', 'Deaths involving COVID-19', 'Deaths from All Causes']]
            df_display.reset_index(drop = True, inplace = True)
            df_display.index +=1
            print(tabulate(df_display, headers='keys', tablefmt='psql'))
        choice = getChoice()

##################################################################################################

def getDeathsBySex():
    us_state_abbrev,abbrev_us_state = getUSDict()
    df3 = pd.read_csv('death_counts_US_sex_state.csv')
    df3['COVID-19 Deaths'] = df3['COVID-19 Deaths'].fillna(0)
    df3['Total Deaths'] = df3['Total Deaths'].fillna(0)
    df4 = df3.iloc[:,:5]
    df5 = df4.groupby(['State','Sex']).agg({'COVID-19 Deaths':'sum', 'Total Deaths':'sum' }).reset_index()
    df5['State'] = df5['State'].map(us_state_abbrev)
    choice = getChoice()
    headers= ['State', 'Sex Category', 'COVID-19 Deaths', 'Total Deaths']
    pd.options.display.max_columns = None
    pd.options.display.width=None
    while choice!='q':
        if choice not in abbrev_us_state.keys():
            print("Invalid choice, please choose again")
            print("\n")
        elif choice in abbrev_us_state.keys():
            print('')
            df_display2 = df5[df5['State'] == choice]
            df_display2.reset_index(drop = True, inplace = True)
            df_display2.index +=1
            print(tabulate(df_display2,headers, floatfmt=".2f", tablefmt ='psql'))
        choice = getChoice()

##################################################################################################

def getAllCauseDistribution():
    headers = ["County\nName", "Total Deaths", "COVID-19\nDeaths", "Non-\nHispanic\nWhite", "Non-\nHispanic\nBlack", "Hispanic"]
    d1, abbrev_us_state = getUSDict()
    df2 = pd.read_csv('death_counts_US_race.csv')
    df2['Non-Hispanic White'].fillna((df2['Non-Hispanic White'].mean()), inplace=True)
    df2['Non-Hispanic Black'].fillna((df2['Non-Hispanic Black'].mean()), inplace=True)
    df2['Hispanic'].fillna((df2['Hispanic'].mean()), inplace=True)
    df2_allCause = df2.loc[df2['Indicator'] == 'Distribution of all-cause deaths (%)']
    choice = getChoice()
    pd.options.display.max_columns = None
    pd.options.display.width=None
    while choice!='q':
        if choice not in abbrev_us_state.keys():
            print("Invalid choice, please choose again")
            print("\n")
        elif choice in abbrev_us_state.keys():
            print('')
            df_display2 = df2_allCause[df2_allCause['State'] == choice].loc[:, list(df2.columns[1:2]) + list(df2.columns[3:7]) + list(df2.columns[10:11])]
            df_display2.reset_index(drop = True, inplace = True)
            df_display2.index +=1
            print(tabulate(df_display2,headers,floatfmt=".2f", tablefmt ='psql'))
        choice = getChoice()
        
##################################################################################################
        
def getCOVID19Distribution():
    headers = ["County\nName", "Total Deaths", "COVID-19\nDeaths", "Non-\nHispanic\nWhite", "Non-\nHispanic\nBlack", "Hispanic"]
    d1, abbrev_us_state = getUSDict()
    df2 = pd.read_csv('death_counts_US_race.csv')
    df2['Non-Hispanic White'].fillna((df2['Non-Hispanic White'].mean()), inplace=True)
    df2['Non-Hispanic Black'].fillna((df2['Non-Hispanic Black'].mean()), inplace=True)
    df2['Hispanic'].fillna((df2['Hispanic'].mean()), inplace=True)
    df2_COVID19 = df2.loc[df2['Indicator'] == 'Distribution of COVID-19 deaths (%)']
    choice = getChoice()
    pd.options.display.max_columns = None
    pd.options.display.width=None
    while choice!='q':
        if choice not in abbrev_us_state.keys():
            print("Invalid choice, please choose again")
            print("\n")
        elif choice in abbrev_us_state.keys():
            print('')
            df_display2 = df2_COVID19[df2_COVID19['State'] == choice].loc[:, list(df2.columns[1:2]) + list(df2.columns[3:7]) + list(df2.columns[10:11])]
            df_display2.reset_index(drop = True, inplace = True)
            df_display2.index +=1
            print(tabulate(df_display2,headers,floatfmt=".2f", tablefmt ='psql'))
        choice = getChoice()

##################################################################################################
    
def getPopulationDistribution():
    headers = ["County\nName", "Total Deaths", "COVID-19\nDeaths", "Non-\nHispanic\nWhite", "Non-\nHispanic\nBlack", "Hispanic"]
    d1, abbrev_us_state = getUSDict()
    df2 = pd.read_csv('death_counts_US_race.csv')
    df2['Non-Hispanic White'].fillna((df2['Non-Hispanic White'].mean()), inplace=True)
    df2['Non-Hispanic Black'].fillna((df2['Non-Hispanic Black'].mean()), inplace=True)
    df2['Hispanic'].fillna((df2['Hispanic'].mean()), inplace=True)
    df2_population = df2.loc[df2['Indicator'] == 'Distribution of population (%)']
    choice = getChoice()
    pd.options.display.max_columns = None
    pd.options.display.width=None
    while choice!='q':
        if choice not in abbrev_us_state.keys():
            print("Invalid choice, please choose again")
            print("\n")
        elif choice in abbrev_us_state.keys():
            print('')
            df_display2 = df2_population[df2_population['State'] == choice].loc[:, list(df2.columns[1:2]) + list(df2.columns[3:7]) + list(df2.columns[10:11])]
            df_display2.reset_index(drop = True, inplace = True)
            df_display2.index +=1
            print(tabulate(df_display2,headers,floatfmt=".2f", tablefmt ='psql'))
        choice = getChoice()
        
##################################################################################################
        
def menuDriven():
    print("\nSub-Option Menu\n 1. Analyze Total Deaths due to COVID 19 and other causes \
          \n 2. Analyze Total Deaths by Race \
          \n 3. Analyze Deaths by Sex distribution \
          \n 4. Press 4 to exit this sub-menu")
    try:
        option = int(input("Enter your choice: "))
    except:
        print("That's not a valid option! Enter again!")
        option = int(input("Enter your choice: "))

    while option!=4:
        if option == 1:
            getTotalDeaths()
            option = int(input("Enter your choice: "))
        
        elif option == 2:
                print("\nSub-Option Menu\n 1. View Deaths by Population Distribution \
                      \n 2. View Deaths by COVID 19 distribution \
                      \n 3. View Deaths by All Cause distribution \
                      \n 4. Press 4 to exit this sub-menu")
                try:
                    sub_option = int(input("Enter your choice for option 2 sub-menu: "))
                except:
                    print("That's not a valid option! Enter again!")
                    sub_option = int(input("Enter your choice: "))
                
                while(sub_option!=4):
                    if sub_option == 1:
                        getPopulationDistribution()
                        sub_option = int(input("Enter your choice for option 2 sub-menu: "))
                    elif sub_option == 2:
                        getCOVID19Distribution()
                        sub_option = int(input("Enter your choice for option 2 sub-menu: "))
                    elif sub_option == 3:
                        getAllCauseDistribution()
                        sub_option = int(input("Enter your choice for option 2 sub-menu: "))
                option = int(input("Enter your choice: "))
        elif option == 3:
            getDeathsBySex()
            option = int(input("Enter your choice: "))
        else:
            print('That\'s not an option!')
##################################################################################################
def mainMenu():
    print('###################################################################################')
    print("\nMain Menu\n 1. Table: U.S. Wide % 'Yes' to Taking a Vaccine Over Time by Demograpahics \
          \n 2. Visualize: U.S. Wide Vaccine Attitude Data Over Time by Demograpahics \
          \n 3. Visualize: State Vaccine Attitudes by Demographics \
          \n 4. Visualize: State Flu-Vaccine Attitudes (Enter complete State Name) \
          \n 5. Table: Analyze Death Statistics by Demographics \
          \n 6. Press 6 to quit")

    print('###################################################################################')
    try:
        option = int(input("Enter your choice: "))
    except:
        print("That's not a valid option! Enter again!")
        option = int(input("Enter Main Menu choice: "))

    while option!=6:
        if option == 1:
          fetchVaccineAtttitudeData()
          option = int(input("Enter Main Menu choice: "))
        elif option == 2:
          vaccineAttitudesChangedOverTime()
          option = int(input("Enter Main Menu choice: "))
        elif option == 3:
            state_abb = input('Enter state Abbreviation like PA for Pennsylvania, TX for Texas etc.: ')
            try:
                fetchStateVaccineData(state_abb)   
                option = int(input("Enter Main Menu choice: "))
            except: 
                print("That's not a valid option! Enter again!")
                option = int(input("Enter Main Menu choice: "))
        elif option == 4:
            state_name = input('Enter complete name of the state to look for Flu Vaccine data eg - Pennsylvania: ')
            try:
                st = State(state_name)
                st.creategraphs()
            except: 
                print("That's not a valid option! Enter again!")
                option = int(input("Enter Main Menu choice: "))
        elif option == 5:
            menuDriven()
            option = int(input("Enter Main Menu choice: "))
        else:
            print('That\'s not an option!')
            

if __name__ == "__main__":
    mainMenu()


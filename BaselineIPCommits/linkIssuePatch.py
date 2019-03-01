# -*- coding: utf-8 -*-
"""
Created on Thu Feb 24 20:52:58 2019

@author: Karan Singh Hundal
"""

import requests
import os

def load_data():
    list_tickets= []
    user = input("Enter Username")     # JIRA user
    pasw = input("Enter Password") # JIRA password
    jiraTicketURL = "https://issues.apache.org/jira/rest/api/2/search?jql=project%20%3D%20HBASE%20AND%20status%20%3D%20%22Patch%20Available%22%20AND%20resolution%20%3D%20Unresolved%20ORDER%20BY%20priority%20DESC%2C%20updated%20DESC"
    r = requests.get(jiraTicketURL, auth=(user, pasw),timeout=50)
    finalMap = []
    data = r.json()
    
    for i in data['issues']:
        issue_id = i['key']
        list_tickets.append(issue_id)
    
    for issueTicket in list_tickets:
        mapIssue = check_this_out(issueTicket,user,pasw)
        finalMap.append(mapIssue)
    return finalMap   
    
def check_this_out(myTicket,user,pasw) :
    print("You are checking ticket: ",myTicket)
    jiraURL = 'https://issues.apache.org/jira/rest/api/latest/issue/'
    attachment_final_url="" 
    status_attachment_name = ""
    fileName = ""
    mapIssue = {}
    mapIssue[myTicket] = []
    
    os.mkdir(myTicket)
    
    # Request Json from JIRA API
    r = requests.get(jiraURL+myTicket, auth=(user, pasw),timeout=5)

    # status of the request
    rstatus = r.status_code

    # If the status isn't 200 we leave
    if not rstatus == 200 :
        print("Error accesing JIRA:",str(rstatus))
        exit()
    else:
        data = r.json()

    if not data['fields']['attachment'] :            
      status_attachment_name = 'ERROR: Nothing attached to this Ticket'
      attachment_final_url=""
    else:
        for i in data['fields']['attachment']:
            attachment_final_url = ""
            fileName = ""
            attachment_final_url = i['content']
            attachment_name = i['filename']
            status_attachment_name = 'OK: Loading Patch : ' + attachment_name 
            if attachment_final_url != "" :
                print(status_attachment_name)
                mapIssue[myTicket].append(attachment_name)
                r = requests.get(attachment_final_url, auth=(user, pasw), stream=True)
                fileName = myTicket +'/'+ attachment_name
                with open(fileName, "wb") as f: 
                    f.write(r.content.decode('iso-8859-1').encode('utf8'))
                f.close()
            else: 
                print("Erroneous Content")
    return mapIssue

## Loading time
finalMap = load_data()
print(finalMap)
#Importing packages ...

import pandas as pd
from bs4 import BeautifulSoup as BS
import re

#Reading data ...

mails=pd.read_csv('email_message_excerpt.csv', encoding = "ISO-8859-1")  # utf-8 encoding doesn't handle certain types of columns present in the file.
mails.dtypes

#Let's only keep those columns which are of our interest

body=mails[['Id','TextBody','HtmlBody']]

##############################################################################################################################################################

sal=["from:","date:","to:","subject:","sent:","\xa0","\r",
    "\u200b","*x* external email *x*","url",
                              "sent from my iphone","please respond above this line.","prize update from:",'(concierge)',
    "(sr. concierge)"]
    
    
    # Key-words describing the email details
    
salutation = ["hi",
                                     "hi,",
                                     "dear",
                                     "hey",
                                     "hello",
                                     "good",'please respond above this line']
     
     # Salutation words in the email appearing at the introduction                   
                                     
signature = ["warm regards",
                              "kind regards",
                              "regards",
                              "cheers",
                              "many thanks",
                              "sincerely",
                              "best,",
                              "talk soon",
                              "cordially",
                              "yours truly",
                              "thanking You",
                          "thanks,","thank you,","thank you!"]
                          
          # Signature words in email appearing during conclusion
                          
##############################################################################################################################################################                     
### Reading body content from html body and writing it in HtmlSol column

for x in range(body.shape[0]):
    #print('#########################################################################################')
    trial=body['HtmlBody'][x]
    
    # Ignoring emails which doesn't have html body
    
    if pd.isnull(body['HtmlBody'][x]):
        t=sol='No mail'
        continue
    else:
        soup = BS(trial,'html.parser')            			# Reading htmlbody using beautifulsoup html parser
        for br in soup.find_all("br"):						# Removing <br> tags in the html and replacing them by newline
            br.replace_with("\n")							# Checking if body tag is present
        if soup.find_all('body'):
            try:
                if 'xmlns' in str(soup.find('html')):		# Checking files with css tags
                    t=soup.find('div').get_text()			# Get entire text from 1st div tag
                elif soup.find('div') is not None:			# If it doesn't have CSS tag,
                    t=soup.find('div').find_all('div')[-1].get_text()  # Read text from innermost div tag of the first div
                else:
                    t=soup.find('body').get_text()			# If 1st div doesn't have nested div tags, get text from whole body tag
            except IndexError:
                t=soup.find('body').get_text()  			# Handling exceptions
            keep=[]
            #t = t.replace('\r', '')
            t1=t.split('\n')								# Spliting text by newline
            flag=0
            for j in range(len(t1)):
                keep.append(t1[j])							# Append the element of list in another list
                for k in signature:
                    if k in t1[j].lower():					# If signature word is observed, stop the iteration for that row and return the result.
                        flag=1
                        keep.remove(t1[j])
                        break
                if flag==1:
                    break
                if len(t1[j])>3:							# Only consider the line if it has more than 3 words. (Assuming that a word will have minimum 3 words Noun + Verb + Object + special symbol 															like ,.!? etc)

                    #keep.append(t1[j])
                    for i in ( sal):
                        if i in t1[j].lower():

                            keep.remove(t1[j])
                            break							# This entire block of code checks if every line satisfies the condition of mail body format. If not, it is removed from keep list
                else:
                    keep.remove(t1[j])
            if len(keep)>0:
                if keep[0].split()[0].lower() in salutation:	# If first line of keep list has salutation word, remove the line
                    keep.remove(keep[0])
            if (len(keep)>5):									# Selecting 1st 3 lines of the list which contains the body content. This number can be dynamic depending on the mails. For this 																	dataset, 3 was the most suitable number so I have chosen that. Selecting only 1st line can remove some of the lines of body. In some 																	cases, 2 non-body lines are also added. But, as I didn't want to ignore any of the content of body, I chose this number on a safer side. 																	If non-body content is strictly to be avoided, only 1 should be considered.
                sol=('\n'.join((keep[:3])))
            else:
                sol=('\n'.join((keep)))							# Join elements of list to make it a continuous string
        else:
            sol='No mail'
#     print(sol)
#     print('********')
#     print(t)
#     print(x)

    body.loc[body.index[x], 'HtmlSol'] = sol					# Writing the result in the respective row of solution column


##############################################################################################################################################################   
### Reading body content from text body and writing it in TextSol column

for x in range((body.shape[0])):
    #print('##################################')
    sol=''
    trial=body['TextBody'][x]
    t = trial.replace('\r', '')
    keep=[]
    t1=t.split('\n')
    flag=0
    for j in range(len(t1)):
        keep.append(t1[j])
        if re.match('\d{2}/\d{2}/\d{4} \d{1}:\d{2} [A-Z]', t1[j]) or re.match('[A-Za-z]+ \d{2}, \d{4} \d{2}:\d{2} [A-Z]', t1[j]) or re.match('\d{2}/\d{2}/\d{4} \d{2}:\d{2} [A-Z]', t1[j]) or re.match('[A-Za-z]+ \d{2}, \d{4} \d{1}:\d{2} [A-Z]', t1[j]):						# Removing the line if it contains a date.
            keep.remove(t1[j])
        for k in signature:
            if k in t1[j].lower():
                flag=1
                keep.remove(t1[j])
                break
        if flag==1:
            break
        if len(t1[j])>3:										# The same logic which is used to get body content from html text is used here.

            #keep.append(t1[j])
            for i in ( sal):
                if i in t1[j].lower():
#                     print(t1[j])
#                     print(i)
                    keep.remove(t1[j])
                    break
        else:
            keep.remove(t1[j])
    if len(keep)>0:
        if keep[0].split()[0].lower() in salutation:
            keep.remove(keep[0])
    if (len(keep)>5):
        sol=('\n'.join((keep[:3])))
    else:
        sol=('\n'.join((keep)))
    body.loc[body.index[x], 'TextSol'] = sol
    

##############################################################################################################################################################  
body.head(5)


### Writing the results dataframe into a csv file

body.to_csv('Result.csv')
                                   

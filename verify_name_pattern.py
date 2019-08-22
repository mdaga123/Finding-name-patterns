
# coding: utf-8

# In[4]:

import os, sys
import getopt
import pandas as pd
import numpy as np
import re
import os
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import warnings
warnings.filterwarnings('ignore')
current_path=os.getcwd()
print(current_path)


def create_dict(names_unique):
    names_dict = dict()
    for name in names_unique:
        first_char = name[0]
        list_available = names_dict.get(first_char, None)
        if list_available is None:
            new_list = list()
            new_list.append(name)
            names_dict[first_char] = new_list
            continue

        list_available.append(name)

    return names_dict

# Importing dictionaries and its requirements
import json
lf_name_json_file_path =str(current_path)+'//Dictionaries//l_f.json'

with open(lf_name_json_file_path, 'r') as l_fdict:
    datal = l_fdict.read()
l_f = json.loads(datal)

fl_name_json_file_path =str(current_path)+'//Dictionaries//f_l.json'
with open(fl_name_json_file_path, 'r') as f_ldict:
    dataf = f_ldict.read()
f_l = json.loads(dataf)

# Importing first dictionary
first=pd.read_csv(str(current_path)+'//Dictionaries//FirstNames.csv')
first_names_unique = sorted([x.upper() for x in first['First_Names']])
first_names_unique_dict = create_dict(first_names_unique)

# Importing last dictionary
last=pd.read_csv(str(current_path)+'//Dictionaries//LastNames.csv')
last_names_unique = sorted([x.upper() for x in last['Last_Names']])
last_names_unique_dict = create_dict(last_names_unique)

#print("Length of full name dictionary: "+str(len(l_f)))
#print("Length of First name dictionary: "+str(len(first_names_unique)))
#print("Length of Last name dictionary: "+str(len(last_names_unique)))

threshold = 93  # Set threshold

# Function to find names in Full Name dictionaries to identify name patterns

def full_dict_check(name_with_space):
    if name_with_space in l_f.keys():
        status = 'l_f'
        score = [100, 100]
    elif name_with_space in f_l.keys():
        status = 'f_l'
        score = [100, 100]
    else:
        status = 'Not in full name'
        score = [0, 0]

    return status, score


def find_status(name_split):
    score = ''
    fpfn = name_split[0] in first_names_unique
    fpln = name_split[0] in last_names_unique

    lpfn = name_split[1] in first_names_unique
    lpln = name_split[1] in last_names_unique

    if fpfn == True:
        if lpln == True:
            status = 'F_L'
            score = [100, 100]
        elif lpfn == True:
            status = 'F_F'
        else:
            status = 'F_*'

    elif fpln == True:
        if lpfn == True:
            status = 'L_F'
            score = [100, 100]
        elif lpln == True:
            status = 'L_L'
        else:
            status = 'L_*'

    else:
        if lpfn == True:
            status = '*_F'
        elif lpln == True:
            status = '*_L'
        else:
            status = '*_*'

    # Using fuzzy logic if name/names not found in dictionary

    if status != 'F_L' or status != 'L_F':

        if status == 'F_*':
            first_char = name_split[1][0]
            last_percent = process.extractOne(name_split[1], last_names_unique_dict.get(first_char))[1]
            if last_percent > threshold:
                status = 'F_L'
                score = [100, last_percent]

        elif status == '*_F':
            first_char = name_split[0][0]
            last_percent = process.extractOne(name_split[0], last_names_unique_dict.get(first_char))[1]
            if last_percent > threshold:
                status = 'L_F'
                score = [last_percent, 100]

        elif status == 'L_*':
            first_char = name_split[1][0]
            first_percent = process.extractOne(name_split[1], first_names_unique_dict.get(first_char))[1]
            if first_percent > threshold:
                status = 'L_F'
                score = [100, first_percent]

        elif status == '*_L':
            first_char = name_split[0][0]
            first_percent = process.extractOne(name_split[0], first_names_unique_dict.get(first_char))[1]
            if first_percent > threshold:
                status = 'F_L'
                score = [first_percent, 100]

        elif status == '*_*':
            first_char_0 = name_split[0][0]
            first_char_1 = name_split[1][0]
            fpfn_percent = process.extractOne(name_split[0], first_names_unique_dict.get(first_char_0))[1]
            fpln_percent = process.extractOne(name_split[0], last_names_unique_dict.get(first_char_0))[1]
            lpfn_percent = process.extractOne(name_split[1], first_names_unique_dict.get(first_char_1))[1]
            lpln_percent = process.extractOne(name_split[1], last_names_unique_dict.get(first_char_1))[1]

            if fpfn_percent > fpln_percent:
                if fpfn_percent > threshold:

                    if lpln_percent > lpfn_percent:
                        if lpln_percent > threshold:
                            status = 'F_L'
                            score = [fpfn_percent, lpln_percent]

                    elif lpfn_percent > lpln_percent:
                        if lpfn_percent > threshold:
                            status = 'F_F'
                            score = [fpfn_percent, lpfn_percent]


                    else:
                        status = 'F_*'
                        score = [fpfn_percent, 0]

            if fpln_percent > fpfn_percent:
                if fpln_percent > threshold:

                    if lpfn_percent > lpln_percent:
                        if lpfn_percent > threshold:
                            status = 'L_F'
                            score = [fpln_percent, lpfn_percent]

                    if lpln_percent > lpfn_percent:
                        if lpln_percent > threshold:
                            status = 'L_L'
                            score = [fpln_percent, lpln_percent]

                    else:
                        status = 'L_*'
                        score = [fpln_percent, 0]

            else:

                if lpfn_percent > lpln_percent:
                    if lpfn_percent > threshold:
                        status = '*_F'
                        score = [0, lpfn_percent]

                elif lpln_percent > lpfn_percent:
                    if lpln_percent > threshold:
                        status = '*_L'
                        score = [0, lpln_percent]

                else:
                    status = '*_*'
                    score = [0, 0]

    return status, score


def status_one_word(name):
    if name in last_names_unique:
        status = 'L'
        score = 100
    elif name in first_names_unique:
        status = 'F'
        score = 100
    else:
        # Using fuzzy logic
        first_char = name[0]
        last_percent = process.extractOne(name, last_names_unique_dict.get(first_char))[1]
        first_percent = process.extractOne(name, first_names_unique_dict.get(first_char))[1]

        if last_percent > first_percent:
            if last_percent >= threshold:
                status = 'L'
                score = last_percent
            else:
                status = '*'
                score = 0
        elif last_percent < first_percent:
            if first_percent >= threshold:
                status = 'F'
                score = first_percent
            else:
                status = '*'
                score = 0
        else:
            status = '*'
            score = 0

    return status, score

 # Suffix List
suffix_list = ['JR', 'SR','III','I','II','IV']


# In[5]:


def processed_name_step(name):
    name = re.sub(r"[-()\"#/@;:<>{}`+=~|.!?*'῾′]", "", name)
    name = name.upper()
    nameformat = np.nan  # Identifying the string format
    one_character = np.nan  # Identifying if there is a one letter word in the player name,
    suffix = np.nan  # Suffix present in the name
    name_without_suffix = np.nan  #

    #STAGE 1
    if name.find(',') != -1:
        if name.find(' ') != -1:
            firstsplit = name.split(',')  # firstsplit is comma split
            lenfirst = len(firstsplit)

            if lenfirst > 2:  # More than 2 commas in the name
                nameformat = 'Unrecognized_morecommas'
            else:
                # Three word case with comma and space

                if firstsplit[0].find(' ') != -1:
                    # Name1 Name2, Name3
                    nameformat = '1 2,3'

                    secondsplit = firstsplit[0].split(' ')
                    allnames = [secondsplit[0], secondsplit[1], firstsplit[1]]

                    # If suffix is present or not
                    suffix = ''
                    for i in range(0, len(allnames)):
                        if allnames[i] in suffix_list:
                            # Suffix present
                            suffix = allnames[i]

                            break

                    # Suffix present case
                    if suffix != '':
                        allnames = [x for x in allnames if x != suffix]
                        nameformat = (",".join(allnames))
                        len0 = len(allnames[0])
                        len1 = len(allnames[1])
                        if len0 == 1:
                            one_character= 'Y1'
                        elif len1 == 1:
                            one_character = 'Y2'

                    # Suffix not present case

                    # elif suffix=='': Manual case for now

                elif firstsplit[1].find(' ') != -1:
                    # Name1, Name 2 Name3
                    nameformat = '1,2 3'
                    secondsplit = firstsplit[1].split(' ')
                    allnames = [firstsplit[0], secondsplit[0], secondsplit[1]]

                    # If suffix is present or not
                    suffix = ''
                    for i in range(0, len(allnames)):
                        if allnames[i] in suffix_list:
                            # Suffix present
                            suffix = allnames[i]

                            break

                    # Suffix present case
                    if suffix != '':
                        allnames = [x for x in allnames if x != suffix]
                        name_without_suffix = (",".join(allnames))
                        len0 = len(allnames[0])
                        len1 = len(allnames[1])
                        if len0 == 1:
                            one_character = 'Y1'
                        elif len1 == 1:
                            one_character = 'Y2'

                    # Suffix not present case

                    # elif suffix=='': Manual case for now



        else:
            # Two word case with comma
            # [Name1, Name2]

            firstsplit = name.split(',')  # firstsplit is comma split
            lenfirst = len(firstsplit)

            if lenfirst > 2:  # More than 2 commas
                nameformat = 'Unrecognized_morecommas'


            nameformat = '1,2'
            # Check for other word as one letter word
            len0 = len(firstsplit[0])
            len1 = len(firstsplit[1])
            if len0 == 1:
                one_character = 'Y1'
            elif len1 == 1:
                one_character = 'Y2'


    elif name.find(' ') != -1:

    # Space case- may be two or three or more words
    # Check for other word as one letter word

        firstsplit = name.split(' ')
        lenfirst = len(firstsplit)

        if lenfirst > 3:  # More than 2 spaces in a name
            nameformat = 'Unrecognized_morespaces'

        elif lenfirst == 2:
            nameformat = '1 2'
            # Checking for one character
            len0 = len(firstsplit[0])
            len1 = len(firstsplit[1])
            if len0 == 1:
                one_character = 'Y1'
            elif len1 == 1:
                one_character = 'Y2'

        elif lenfirst == 3:
            nameformat = '1 2 3'
            allnames = [firstsplit[0], firstsplit[1], firstsplit[2]]
            # Checking for suffix
            suffix = ''
            for i in range(0, len(allnames)):
                if allnames[i] in suffix_list:
                    # Suffix present
                    suffix = allnames[i]

                    # break

            # Suffix present case
            if suffix != '':
                allnames = [x for x in allnames if x != suffix]
                name_without_suffix = (",".join(allnames))
                len0 = len(allnames[0])
                len1 = len(allnames[1])
                if len0 == 1:
                    one_character = 'Y1'
                elif len1 == 1:
                    one_character = 'Y2'

            # Suffix not present case

            # elif suffix=='': Manual case for now

    else:  # One word case
        nameformat = '1'

    #STAGE 2
    # For one-word names
    if nameformat == '1':


        status, score = status_one_word(name)

        if status == 'L':
            case = 'Case 1a'
        else:
            case = 'Case 1b'

    # For two word names separated with comma
    elif nameformat == '1,2':


        name_with_space = name.replace(',', ' ')
        status, score = full_dict_check(name_with_space)

        if status == 'Not in full name':
            name_split = name.split(',')
            status, score = find_status(name_split)



        if one_character == 'Y1':
            statusind = status.split('_')
            if statusind[1] == 'L' or statusind[1] == 'l':
                case = 'Case 2a-1'
            else:
                case = 'Case 2a-2'

        if one_character == 'Y2':
            statusind = status.split('_')
            if statusind[0] == 'L' or statusind[0] == 'l':
                case = 'Case 2a-1'
            else:
                case = 'Case 2a-2'

        if np.isnan(one_character): #####################################
            if status == 'L_F' or status == 'l_f':
                case = 'Case 2b-1.1'

            elif status == 'F_L' or status == 'f_l':
                case = 'Case 2b-1.2'

            elif status == 'F_F' or status == 'L_L':
                case = 'Case 2b-1.3'

            elif status == 'L_*':
                case = 'Case 2b-2.1'

            elif status == 'F_*':
                case = 'Case 2b-2.2'

            elif status == '*_F':
                case = 'Case 2b-2.3'

            elif status == '*_L':
                case = 'Case 2b-2.4'
            elif status == '*_*':
                case = 'Case 2b-3'

    # For two word names separated by space
    elif nameformat == '1 2':
        name_with_space = name
        status, score = full_dict_check(name_with_space)

        if status == 'Not in full name':
            name_split = name.split(' ')
            status, score = find_status(name_split)



        if one_character == 'Y1':
            statusind = status.split('_')
            if statusind[1] == 'L' or statusind[1] == 'l':
                case = 'Case 2a-1'
            else:
                case = 'Case 2a-2'

        if one_character == 'Y2':
            statusind = status.split('_')
            if statusind[0] == 'L' or statusind[0] == 'l':
                case = 'Case 2a-1'
            else:
                case = 'Case 2a-2'

        if np.isnan(one_character):
            if status == 'L_F' or status == 'l_f':
                case = 'Case 2b-1.1'

            elif status == 'F_L' or status == 'f_l':
                case = 'Case 2b-1.2'

            elif status == 'F_F' or status == 'L_L':
                case = 'Case 2b-1.3'

            elif status == 'L_*':
                case = 'Case 2b-2.1'

            elif status == 'F_*':
                case = 'Case 2b-2.2'

            elif status == '*_F':
                case = 'Case 2b-2.3'

            elif status == '*_L':
                case = 'Case 2b-2.4'
            elif status == '*_*':
                case = 'Case 2b-3'

    # For three word names in the following three formats
    elif nameformat == '1 2 3' or nameformat == '1 2,3' or nameformat == '1,2 3':


        if np.isnan(suffix) == False:

            name = name_without_suffix
            name_with_space = name.replace(',', ' ')
            status, score = full_dict_check(name_with_space)

            if status == 'Not in full name':
                name_split = name.split(',')
                status, score = find_status(name_split)


            if one_character == 'Y1':
                statusind = status.split('_')
                if statusind[1] == 'L' or statusind[1] == 'l':
                    case = 'Case 3.1a-1'
                else:
                    case = 'Case 3.1a-2'

            if one_character == 'Y2':
                statusind = status.split('_')
                if statusind[0] == 'L' or statusind[0] == 'l':
                    case = 'Case 3.1a-1'
                else:
                    case = 'Case 3.1a-2'

            if np.isnan(one_character):

                if status == 'L_F' or status == 'l_f':
                    case = 'Case 3.1b-1.1'

                elif status == 'F_L' or status == 'f_l':
                    case = 'Case 3.1b-1.2'

                elif status == 'F_F' or status == 'L_L':
                    case = 'Case 3.1b-1.3'

                elif status == 'L_*':
                    case = 'Case 3.1b-2.1'

                elif status == 'F_*':
                    case = 'Case 3.1b-2.2'

                elif status == '*_F':
                    case = 'Case 3.1b-2.3'

                elif status == '*_L':
                    case = 'Case 3.1b-2.4'
                elif status == '*_*':
                    case = 'Case 3.1b-3'


        else:
            case = 'Case 3.2'

    # For all other name string patterns
    elif nameformat == 'Unrecognized_morespaces':
        case= 'Case 4.1'

    elif nameformat == 'Unrecognized_morecommas':
        case = 'Case 4.2'

    #STAGE 3
    if case == 'Case 1a':
        processed_name=name
        action = 'Identified as Last name'

    elif case == 'Case 2a-1':
        if name.find(',') != -1:
            name_split = name.split(',')
            if len(name_split[0]) == 1:
                processed_name = [name_split[1], name_split[0]]
                processed_name = (",".join(processed_name))
            elif len(name_split[1]) == 1:
                processed_name = [name_split[0], name_split[1]]
                processed_name = (",".join(processed_name))

        elif name.find(' ') != -1:
            name_split = name.split(' ')
            if len(name_split[0]) == 1:
                processed_name = [name_split[1], name_split[0]]
                processed_name = (",".join(processed_name))
            elif len(name_split[1]) == 1:
                processed_name = [name_split[0], name_split[1]]
                processed_name = (",".join(processed_name))

        action = 'Suggested Format printed'

    elif case == 'Case 2b-1.1' or case == 'Case 2b-2.1' or case == 'Case 2b-2.3':  # LF,L*,*F

        if name.find(',') != -1:
            name_split = name.split(',')
            processed_name = [name_split[0], name_split[1]]
            processed_name = (",".join(processed_name))

        elif name.find(' ') != -1:
            name_split = name.split(' ')
            processed_name = [name_split[0], name_split[1]]
            processed_name = (",".join(processed_name))

        if case == 'Case 2b-1.1':
            action = 'Suggested Format printed'
        else:
            action = 'Suggested Format printed'




    elif case == 'Case 2b-1.2' or case == 'Case 2b-2.2' or case == 'Case 2b-2.4':  # FL,F*,*L

        if name.find(',') != -1:
            name_split = name.split(',')
            processed_name = [name_split[1], name_split[0]]
            processed_name = (",".join(processed_name))

        elif name.find(' ') != -1:
            name_split = name.split(' ')
            processed_name = [name_split[1], name_split[0]]
            processed_name = (",".join(processed_name))

        if case == 'Case 2b-1.2':
            action = 'Suggested Format printed'
        else:
            action = 'Suggested Format printed'



    elif case == 'Case 3.1a-1':

        name = name_without_suffix
        name_split = name.split(',')
        if len(name_split[0]) == 1:
            processed_name = str(name_split[1]) + " " + str(suffix) + "," + str(name_split[0])

        elif len(name_split[1]) == 1:
            processed_name = str(name_split[0]) + " " + str(suffix) + "," + str(name_split[1])

        action = 'Suggested Format printed'


    elif case == 'Case 3.1b-1.1' or case == 'Case 3.1b-2.1' or case == 'Case 3.1b-2.3':  # LF,L*,*F
        name = name_without_suffix
        name_split = name.split(',')
        processed_name = str(name_split[0]) + " " + str(suffix) + "," + str(name_split[1])

        if case == 'Case 3.1b-1.1':
            action = 'Suggested Format printed'
        else:
            action = 'Suggested Format printed'


    elif case == 'Case 3.1b-1.2' or case == 'Case 3.1b-2.2' or case == 'Case 3.1b-2.4':  # FL,F*,*L
        name = name_without_suffix
        name_split = name.split(',')
        processed_name = str(name_split[1]) + " " + str(suffix) + "," + str(name_split[0])

        if case == 'Case 3.1b-1.2':
            action = 'Suggested Format printed'
        else:
            action = 'Suggested Format printed'


    else:
        action = 'Not able to identify the name pattern'

    return(processed_name,nameformat,case,status,action)


# In[ ]:


def help():
    print('verify_name_pattern.py -n <name>')
    
    
def main(argv):
    filename=''
      
    try:
        opts, args = getopt.getopt(argv, "n:", ["name="])
    except getopt.GetoptError:
        print("Error invald options")
        help()
        sys.exit(2)
        
    for opt, arg in opts:
        if opt == '-h':
            print("Help Usage: ")
            help()
            sys.exit()
        elif opt in ("-n","--name"):
           # print(arg)
            name = arg
            
        else:
            print("Error invalid options")
            help()
            sys.exit(2)
            
    if name=="": 
        print("Error in getting file")
        help()
        sys.exit(2)
    
   
    
    processed_name,nameformat,case,status,action=processed_name_step(name)
    print("-----------------OUTPUT------------------------------")
    print("Processed Name Output will always be in [Last Name, First Name Suffix] format")
    print("Original Name: ", name)
    print("Processed Name: ",processed_name)
    print("Action: ",action)
    
    
if __name__ == "__main__":
    main(sys.argv[1:])


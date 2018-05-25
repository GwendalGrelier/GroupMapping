
try:
    import pandas as pd
except:
    print("Error: No module named pandas.")
    print('Please open a terminal and type: "pip install pandas"')
    print('If pandas is already installed, please open a terminal and type: "pip uninstall pandas" then "pip install pandas==0.22"')
    input("Press enter to Quit")
    sys.exit() 
try:
    import csv
except:
    print("Error: No module named csv.")
    print('Please open a terminal and type: "pip install csv"')
    input("Press enter to Quit")
    sys.exit() 
import os, sys, re


export_file_name = "new_excel_file.xls"



def getDataFileName():
    file_list = [f for f in os.listdir() if f.endswith('.xls') or f.endswith('.csv')]
    
    if not file_list:
        print("Error : No files were found in the directory. Try again.")
        input("Press enter to Quit")
        sys.exit()

    print("Please select one of the following data-containing files (from MZmine):")
    for i, file in enumerate(file_list):
        print(str(i) + " = " + file) 
    isValidNumber = False
    while not isValidNumber:
        file_selection = input("File number : ")
        try:
            file_selection = int(file_selection)
            if file_selection > len(file_list)-1 or file_selection < 0:
                print('This number is out of range.')
            else:
                isValidNumber = True
        except:  
            print("This is not a number.")
    return file_list[file_selection]

def getGroupMapFileName():
    file_list = [f for f in os.listdir() if f.endswith('.txt')]
    
    if not file_list:
        print("Error : No files were found in the directory. Try again.")
        os.system("pause")
        sys.exit()
    print("Please select one of the following group mapping files:")
    for i, file in enumerate(file_list):
        print(str(i) + " = " + file) 
    isValidNumber = False
    while not isValidNumber:
        file_selection = input("File number : ")
        try:
            file_selection = int(file_selection)
            if file_selection > len(file_list)-1 or file_selection < 0:
                print('This number is out of range.')
            else:
                isValidNumber = True
        except:  
            print("This is not a number.")
    return file_list[file_selection]

def openDataFile(file_name):
    try:
        with open(file_name, 'r') as f:
            line = f.read(2048)
        sniffer = csv.Sniffer()
        delimiter = sniffer.sniff(line).delimiter
    except (OSError, FileNotFoundError, UnicodeDecodeError):
        print("Error while reading the csv file. Please make sure it's not corrupted.")
        input("Press enter to Quit")
        sys.exit()

    if file_name.endswith(".csv"):
        data = pd.read_csv(file_name, sep=delimiter)

    elif file_name.endswith(".xls"):
        data = pd.read_excel(file_name)
        
    new_columns = data.columns.values
    new_columns[0] = 'ID'
    data.columns = new_columns
    data = data.set_index('ID')
    return data

def getGroupList(file):
    group_mapping = {}
    for line in file:
        if line.startswith("GROUP_"):
            result = re.search("GROUP_([a-zA-Z0-9-\s+_\/\.:\\\[\]']+)=([a-z\sA-Z0-9-+_\/\.:\\\[\]';]+)", line)        
            group_name, grouped_file_list = result.group(1) , result.group(2)          
            file_list = grouped_file_list.split(";")
            group_mapping[group_name] = file_list
    return group_mapping


def cleanGroupMapping(group_mapping, MZmine_sample_list):
    to_process_groups = {}
    for group in group_mapping:
        for sample in MZmine_sample_list:
            if sample.endswith("Peak area"):
                sample = sample[:-10]
            if sample in group_mapping[group]:
                to_process_groups[group] = group_mapping[group]
    
    to_return_group_list = {}
    for group in to_process_groups:
        file_list = []
        for file in to_process_groups[group]:
            if file in MZmine_sample_list:
                if file not in file_list:
                    file_list.append(file)
        to_return_group_list[group] = file_list

    return to_return_group_list

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    # Print New Line on Complete
    if iteration == total: 
        print()

if __name__ == "__main__":

    print("Welcome in the Group Mapping Script.")


    # Select a csv/xls file containing the "MZmine" data
    # and extract the sample names in sample_list 
    data_file_name = getDataFileName()
    data = openDataFile(data_file_name)
    sample_list = [column_name for column_name in data if ".mzXML" in column_name or "Peak area" in column_name]

    print("The {0} file was selected. {1} samples were found.".format(data_file_name, str(len(sample_list))))
    print("############################################", "\n")
    

    # Select a groupMapping .txt file
    # and extract a dict of {group_name:(sample_list)} 
    group_mapping_file_name = getGroupMapFileName()
    group_mapping_file = open(group_mapping_file_name, "r")
    global_group_list = getGroupList(group_mapping_file)
    group_mapping_file.close()
    
    # Cleans the global_group_list to contain only groups that shares samples with the "MZmine data"
    group_mapping = cleanGroupMapping(global_group_list, sample_list)
    print("{} group(s) will be added to the xls file.".format(len(group_mapping)))
    print("############################################", "\n")
    print("Adding group mapping columns into the data frame, Please wait.")
    l = len(group_mapping)

    # Add columns to the "MZmine data" for each group mapping 
    sum_list = []
    for i, group in enumerate(group_mapping):
        for IDs in data.index:
            value = 0
            for file in group_mapping[group]:
                file = file + " Peak area"
                value = value + data.loc[IDs, file]
            data.loc[IDs, group] = value
    data.to_excel(export_file_name, index=True)

    print("{} was created successfully. Thank you =p".format(export_file_name))
    input("Press enter to exit.")

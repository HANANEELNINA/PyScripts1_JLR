import shutil,os,re
import glob
import pandas as pd
import tkinter as tk
from tkinter import simpledialog, messagebox,ttk
import sys
import calendar, datetime
from datetime import datetime as dt
import JLR_CSV_NOK as get_ng_data
import logging

dpath = "C:/Users/F6CHA02/Desktop/JLR/ForDataLogs"
root = tk.Tk()
root.withdraw()  # Hide the root window

root.title("JLR CSV SN MM")
root.geometry("300x200")  # Set the size of the window

def NoInput(entry):
    if entry is None:
        sys.exit("No input provided, exiting...")


def get_option(options):
    win = tk.Toplevel()
   
    width = 250 
    height = 100 

    x = root.winfo_screenwidth()//2 - 150
    y = root.winfo_screenheight()//2 -50

    win.geometry(f"{width}x{height}+{x}+{y}")
    win.title("Select ")

    model_var = tk.StringVar()
    combo = ttk.Combobox(win, textvariable= model_var,values=options, state = "readonly")
    combo.pack(pady=20)
    combo.current(0)  # Set default selection

    def submit():
        win.destroy()

    tk.Button(win, text="OK", command= submit).pack(pady=5)
    
    win.wait_window()  # Wait for the window to close 
    selected = model_var.get()   
    print("Selected:", selected)

    return selected



try:
    today = datetime.date.today()
    strtoday = today.strftime("%m")
    now = dt.now()
    timestamp = now.strftime("%H%M%S")
    inttoday = int(strtoday)
    monthslist = []
    for i in range(1, inttoday+1) : 
        if i < 10:
            monthslist.append('0' + str(i)) 
        else:
            monthslist.append(str(i)) 

    mm = get_option(monthslist)
    models = ['DFC', 'CMC']
    model = get_option(models)


    data_type = ['MTF','BDF' , 'BOTH']
    str_var = get_option(data_type)
    if str_var == "MTF":
        var = 1
    elif str_var == "BDF":
        var = 2
    elif str_var == "BOTH":
        var = 3
    else:
        messagebox.showerror("Error", "Wrong Entry of Test Log Type")
        sys.exit("Wrong Entry of Test Log Type")
    SPATH =[]
    match var :
        case 1: 
            path ='//f6cp-cam-0249/D/TS_Logs/SITE4/2025/'+  mm 
            SPATH.append(path)
            NAME = [model + "_MTF2" ]
        case 2:
            path ='//f6cp-cam-0248/D/TS_Logs/SITE3/2025/' + mm 
            SPATH.append(path)
            NAME = [model + "_Darkfield" , model + "_Brightfield" ]
        case 3:
            path1 = '//f6cp-cam-0248/D/TS_Logs/SITE3/2025/' + mm 
            path2 = '//f6cp-cam-0249/D/TS_Logs/SITE4/2025/' + mm 
            SPATH.append(path1)
            SPATH.append(path2)
            NAME = [model + "_Darkfield" , model + "_Brightfield" , model + "_MTF2"]
        case _: 
            messagebox.showerror("Error", "Wrong Entry of Test Log Type")
            raise ValueError("'Wrong Entry of Test Log Type'")


    #get the list of SNs
    SNlist = []
    sn_input = simpledialog.askstring("Serial Numbers", "Enter serial numbers separated by commas or spaces:")
    NoInput(sn_input)
    SNlist = [sn.strip() for sn in re.split(r'[,\s]+', sn_input) if sn.strip()]
    
    for sn in SNlist:
        if len(sn) != 13 :
            SNlist.remove(sn)


    label = tk.Label(root , text="SNs to search: " )


   

    for spath in SPATH : 
        if os.path.exists(spath):
            for yymmjj in os.listdir(spath) : 
                if os.path.isdir(os.path.join(spath, yymmjj)):
                    sspath =  spath + '/' + yymmjj +'/'
                    for tst in os.listdir(sspath) :
                        fpath = sspath + tst + "/UUT single"
                        if os.path.exists(fpath) :
                            
                            for x in os.listdir(fpath):
                            
                                for sn in SNlist:
                                    targetPattern = rf'.*{sn}.*\.csv$'
                                    if re.search(targetPattern, x) : 
                                        print(x)
                                        nwpath = fpath + '/' + x
                                        shutil.copy(nwpath,dpath)
                                    else : continue
                        else : continue
                else : continue
                    
    
                   
        else : raise ValueError("path not correct ", spath)



    os.chdir(dpath)
    print(NAME)
    for name in NAME:
        pattern = os.path.join(dpath , name + "*.csv")
        joinedList= glob.glob(pattern)
        if not joinedList:
            print(f"No files found for pattern: {pattern}")
            continue
        df = pd.concat(map(pd.read_csv, joinedList), ignore_index=True) 
        merged_name = name +'_'+ timestamp
        df.to_csv(dpath + '/merged/' + merged_name +".csv",index=False)
    csv_files = glob.glob(os.path.join(dpath, "*.csv"))
    for file in csv_files:
        os.remove(file)
    
    nok = tk.messagebox.askyesno("NOK Data", "Do you want to get NOK data?")
    if nok :   
        NG_List = []  
        spath = os.path.join (dpath, 'merged')
        for file in os.listdir(spath ):
            res = get_ng_data.GetFailInfo(file, spath)
            if res != None :
                print(f"Parsing -------------------------------------------------------{file}")

                NG_List.append(res )
            else : continue
    
except Exception as error:
    messagebox.showerror("Error", str(error))
root.destroy()  # Close the Tkinter window
sys.exit("Process completed")
#Goal: Provide Automated text messages to Rick and Victor, to let him know what units need what
# (1) Pulls Data From Google Forms (Property Manager Input)
# (2) Send automated text to Rick (perhaps email to managers?), whenever Google Forms are updated
import ezsheets,os
import datetime
from datetime import datetime, timedelta
os.chdir(r'C:\Users\Lenovo\PycharmProjects\Appliances')

#We will have 2 dictionaries, the first of which is organized like such:
#The second of which is organized in reverse order
d1 = {'Washer (Side by Side)':[],
        'Dryer (Side by Side)':[],
        'Washer & Dryer (Stackable)':[],
        'Fridge':[],
        'Stove':[],
        'Outside Cleanup':[],
        'Tub/Counter Glazing':[],
        'Stairs built':[],
        'Stairs Repaired/Painted':[],
        'Awning':[],
        'Windows':[],
        'AC unit':[],
        'All done! (Take Off Txt Msg List)':[]
      }

#any new rows at bottom of spreadsheet get lumped into this list
NewRows = []
#a condensed version of NewRows, shows only Complex & Unit Num
NewUnits = []

#This dic is organized (in reverse) like: {'Westwind 34': 'Washer (Side By Side), Dryer (Side by Side), Fridge, Stove',
# 'Westwind 55': 'Dryer (Side by Side)', 'Westwind 50': 'Washer & Dryer (Stackable), Stairs Repaired/Painted'}
d2 = {}
ss = ezsheets.Spreadsheet('1is9UPTV4tmL1vLLg6AbSyiO1iWPMgCrE7jJmlIU8BzI')
sheet = ss[0]

#(1) iterate through entire spreadsheet

#helper: given a datetime '8/25/2022 9:30:10', return whether it falls within the last 5 min
def istimewithinlast5min(cell_i0):
        now = datetime.now()
        fiveminago = now - timedelta(minutes=5)
        obj = datetime.strptime(cell_i0, '%m/%d/%Y %H:%M:%S')
        if obj > fiveminago:
                return True
        return False

istimewithinlast5min('8/25/2022 9:30:10')

#First we must fill D2 to get the cleanest version.
#For instance, if we have 3 rows on the Gsheet of the same unit, D2 will show only the most updated iteration
def Filld2():
        for i in sheet:
                #only deal with rows with relevant information
                if len(i[0]) > 15:
                        time = i[0]
                        unit = i[1]+" "+i[2]
                        thingsneeded = i[3]
                # (1a) Throw everything in D2
                        d2[unit] = thingsneeded
        # (1b) Throw only the new rows into "NewRows" list
                        if istimewithinlast5min(time):
                                NewRows.append(i)
                                NewUnits.append(unit)

#Only after we fill Dic2 can we fill Dic1
def Filld1():
        Filld2()
        for todoitem in d1:
                for unit in d2:
                        if todoitem in d2[unit]:
                                d1[todoitem].append(unit)
Filld1()
print(d1)

#(3) time to construct txt msg (using d1)

#(4) if NewRows != empty, send out the txt msg
#(4a) In line 1 of txt msg, say something like "updates made to: Hol 18, HP 20" (Whatever Units can be found in NewRows)


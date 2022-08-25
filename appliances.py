#to do: left off line 88
#Goal: Provide Automated text messages to Rick and Victor, to let him know what units need what
# (1) Pulls Data From Google Forms (Property Manager Input)
# (2) Send automated text to Rick (perhaps email to managers?), whenever Google Forms are updated
import ezsheets,os, datetime, ezgmail
from datetime import datetime, timedelta
from twilio.rest import Client
from pathlib import Path
os.chdir(r'C:\Users\Lenovo\PycharmProjects\Appliances')

#We will have 2 dictionaries, the first of which is organized like such:
#The second of which is organized in reverse order
d1 = {'Washer (Side by Side)':[],
        'Dryer (Side by Side)':[],
        'Washer & Dryer (Stackable)':[],
        'Fridge':[],
        'Stove':[],
        'Outside Cleanup':[],
        'Glazing':[],
        'Stairs':[],
        # 'Stairs Repaired/Painted':[],
        'Awning':[],
        # 'Windows':[],
        'AC unit':[],
        'All done! (Take Off Txt Msg List)':[]
      }

#any new rows at bottom of spreadsheet get lumped into this list
NewRows = []
#a condensed version of NewRows, shows only Complex & Unit Num
NewUnits = []
#a condensed version of NewPeople, shows only name of people who made recent updates
NewPeople = []

#This dic is organized (in reverse) like: {'Westwind 34': 'Washer (Side By Side), Dryer (Side by Side), Fridge, Stove',
# 'Westwind 55': 'Dryer (Side by Side)', 'Westwind 50': 'Washer & Dryer (Stackable), Stairs Repaired/Painted'}
d2 = {}
ss = ezsheets.Spreadsheet('1is9UPTV4tmL1vLLg6AbSyiO1iWPMgCrE7jJmlIU8BzI')
sheet = ss[0]

#helper: given a datetime '8/25/2022 9:30:10', return whether it falls within the last 5 min
def istimewithinlast5min(cell_i0):
        now = datetime.now()
        fiveminago = now - timedelta(minutes=5)
        obj = datetime.strptime(cell_i0, '%m/%d/%Y %H:%M:%S')
        if obj > fiveminago:
                return True
        return False

def abbr_complex(complex):
        d = {'Holiday':'Hol', 'Mt Vista':'MtV', 'Westwind':'West', 'Wilson Gardens':'Wilson', 'Crestview':'Crest', \
         'Hitching Post':'HP', 'SFH':'SFH', 'Patrician':'Pat','Wishing Well':'Wish',\
             'Chestnut': 'Chestnut', 'Elm': 'Elm', '12398 4th': '12398 4th', '12993 2nd': '12993 2nd', 'Reedywoods': 'Reedywd', 'North Grove': 'Grove', \
             'Massachusetts': 'Massachu', 'Michigan': 'Mich', '906 N 4th': '906 N 4th', 'Indian School': 'Indian School', 'Cottonwood': 'Cottonwd'
             }
        return d[complex]

#First we must fill D2 to get the cleanest version.
#For instance, if we have 3 rows on the Gsheet of the same unit, D2 will show only the most updated iteration
def Filld2():
        for i in sheet:
                #only deal with rows with relevant information
                if len(i[0]) > 15:
                        time = i[0]
                        unit = abbr_complex(i[1])+" "+i[2]
                        thingsneeded = i[3]
                        person = i[4]
                # (1a) Throw everything in D2
                        d2[unit] = thingsneeded
        # (1b) Throw only the new rows into "NewRows" list
                        if istimewithinlast5min(time):
                                NewRows.append(i)
                                if unit not in NewUnits:
                                    NewUnits.append(unit)
                                if person not in NewPeople:
                                    NewPeople.append(person)

#Only after we fill Dic2 can we fill Dic1
def Filld1():
        Filld2()
        for todoitem in d1:
                for unit in d2:
                        if todoitem in d2[unit]:
                                d1[todoitem].append(unit)
        del d1['All done! (Take Off Txt Msg List)']
Filld1()

#Construct txt msg (using d1)
def header():
        s=''
        if len(NewRows)==0:
                return ''
        else:
                for i in NewPeople:
                    s+= i + ", "
                s += 'Recently Updated: '
                for i in NewUnits:
                    s+= i + ", "
                s+="\n"
        return s

def txtmsg():
        s = """"""
        s+= header() + "\n"
        s += """This is a new txt msg thread! Plz update list with what your units need done. \n \n"""

        for todoitem in d1:
                s += todoitem + "\n"
                s += "-  -  -  -  -  -  -  -  -  -  -\n"
                if len(d1[todoitem])>0:
                    for unit in d1[todoitem]:
                        s += unit +", "
                    s+="\n \n"
                else:
                    s += "\n"
        s+= "https://forms.gle/pxtLTzNwjVGrUEZHA"
        return s
print(txtmsg())

#return list of numbers to message
def numberstomessage():
    # d = {'Victor':'+19098163161','Jian':'+19092101491','Karla':'+19097677208','Brian':'+19097140840',
    #     'Richard':'+19516639308','Jeff':'+19092228209','Tony':'+16269991519','Hector':'+19094897033',
    #      'Charles':'+19095507143','Amanda':'+19094861526','Rick':'9092541913'
    # }
    d = {'Victor':'+19098163161'}
    L = []
    for i in d:
        L.append(d[i])
    return L
def emailstomessage():
    d = {'Victor':'vchen2120@gmail.com'}
    L = []
    for i in d:
        L.append(d[i])
    return L

def readtxtfile():
    #return dictionary of {'sid':x,'token':y,'from':z,'to':a}
    #hiding my keys from you github mf's
    p = Path('twiliocreds.txt')
    text = p.read_text()
    #hard coding the shit out of this bby
    start = text.index('sid')
    sid = text[start+5: start+4+35]
    start = text.index('token')
    token = text[start+7: start+6+33]
    start = text.index('phone_from')
    phone_from = text[start+11: start+11+13]
    start = text.index('phone_to')
    phone_to = text[start+9: start+9+13]
    d = {'sid':sid,'token':token,'from':phone_from,'to':phone_to}
    return d

def sendemail():
    L = emailstomessage()
    ezgmail.init()

def calltwilio():
        # call twilio api to print
        L = numberstomessage()
        account_sid = readtxtfile()['sid']
        auth_token = readtxtfile()['token']
        client = Client(account_sid, auth_token)

        text = txtmsg()
        numbers_to_message = L
        print(L)

        if len(NewRows)>0:
            for number in numbers_to_message:
                client.messages.create(
                    body=text,
                    from_=readtxtfile()['from'],
                    to=number
                )

            print('txt msg sent!')
        else:
            print('txt msg should not have sent: there are no updates so no need for a txt msg')
        return 'nothing'
calltwilio()

#next steps: submit a bunch of Gform entries, and see if the txt msg is generating what you want
#Sept 9th: add foam to this list! add mini splits to list?, add granite to list


#to do: put windows on this list -- and link to an external Gsheet for further details, foaming, granite
#to do: (1) troubleshoot instances where (make sure nothing crashes)
#(1a): someone submits the form, but clicks none of the boxes
#(1b): someone removes something that was never there in the first place
#(1c): someone adds something that already exists in the txt msg
#2: work in option to remove something from txt msg list


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
        'ReGlazing':[],
        'Stairs':[],
        # 'Stairs Repaired/Painted':[],
        'Awning':[],
        # 'Windows':[] - expected date of arrival
        'AC unit':[],
        'Roof Foaming':[],
        'Granite Countertops':[]
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

#Helper (for Filld2()) -- Given a Gsheet row, return which case it is
#Case 1: Need Thing, no things done (to check off on)
#case 2: don't need thing, things done (to check off on)
#case 3: need thing, things done (to check off on)
#row being: [timestamp,complex,unit,thingsneeded,person,thingsdone] *the Gsheet has to be in this EXACT order
def entrytype(row):
    #helper: remove all empty strings from the row
    def skim(row):
        return [x for x in row if x]
    #helper: make sure row has at least length 4
    def rowhasstuffinit(row):
        if len(row)<4:
            return False
        return True

    # helper: determine if row has any things needed
    def things_needed(row):
        for i in d1:
            if i in row[3]:
                return True
        return False
    #helper: determine if row has any things done
    def things_done(row):
        for i in d1:
            if i in row[-1]:
                return True
        return False

    row = skim(row)
    if rowhasstuffinit(row):
        if things_needed(row)==True and things_done(row)==False:
            return 'Things Needed'
        if things_needed(row) == False and things_done(row) == True:
            return 'Things Done'
        if things_needed(row) == True and things_done(row) == True:
            return 'Things Needed & Things Done'
    return 'Empty Row'

#1a: things needed: if there is no existing entry, throw into the dictionary
#(1b:Things Needed) if there is a new row updating a unit that already has an entry,
#   helper function to check every item in the old entry, and add the new entries that don't already exist
#2b things done: if there is no existing entry, do nothing
#2a things done: if there is an existing entry, helper function to check every item in old entry, remove the necesary ones
#3 if 'Empty Row', do nothing, keep iterating

#First we must fill D2 to get the cleanest version.
#For instance, if we have 3 rows on the Gsheet of the same unit, D2 will show only the most updated iteration
def Filld2():
    # helper
    def isthereanexistingentry(unit):
        if unit in d2:
            return True
        return False
    #helper
    def things_needed(row, unit):
        thingsneeded = i[3]
        # 1a: things needed: if there is no existing entry, throw into the dictionary
        if not isthereanexistingentry(unit):
            d2[unit] = thingsneeded
        # (1b:Things Needed) if there is a new row updating a unit that already has an entry,
        # check if new entry is in old list of todos, and add the new entries that don't already exist
        else:
            for new in thingsneeded:
                if new not in d2[unit]:
                    d2[unit].append(new)
        return None
    #helper
    def things_done(row, unit):
        thingsdone = i[-1]
        # 2a things done: if there is an existing entry, check if new entry is in old list of todos, and remove those new entries
        if isthereanexistingentry(unit):
            for new in thingsdone:
                if new in d2[unit]:
                    d2[unit].remove(new)
        # 2b things done: if there is no existing entry, do nothing
        else:
            return None

    for i in sheet:
        # only deal with rows with relevant information
        if len(i[0]) > 15:
            time = i[0]
            unit = abbr_complex(i[1]) + " " + i[2]
            if entrytype(i) == 'Things Needed':
                things_needed(i, unit)
                person = i[4]
            if entrytype(i) == 'Things Done':
                things_done(i, unit)
                person = i[-2]
            if entrytype(i) == 'Things Needed & Things Done':
                things_needed(i, unit)
                things_done(i, unit)
                person = i[-2]
            # [WE CAN KEEP THIS CODE] Throw only the new rows into "NewRows" list
            if istimewithinlast5min(time):
                NewRows.append(i)
                if unit not in NewUnits:
                    NewUnits.append(unit)
                if person not in NewPeople:
                    NewPeople.append(person)
    return None

#Only after we fill Dic2 can we fill Dic1
def Filld1():
        Filld2()
        for todoitem in d1:
                for unit in d2:
                        if todoitem in d2[unit]:
                                d1[todoitem].append(unit)
Filld1()
# print(d2)
# print(d1)

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

for i in d1:
    print(i)
    print(d1[i])

#Oct 6th firestore code baby!

#helper: convert "Washer (Side by Side)" to "Washer_(Side_by_Side)"
def reformat(string):
    return string.replace(" ","_")

def firestore():
    import firebase_admin
    from firebase_admin import credentials
    from firebase_admin import firestore
    cred = credentials.Certificate(r'C:\Users\Lenovo\PycharmProjects\firebase\venv\serviceaccountkey.json')
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    #to be deleted: this is only for initially setting up firestore
    # for i in d1:
    #     db.collection('Appliances').document(reformat(i)).set({"type": reformat(i)})

    #first: delete all existing documents (Hierarchy: collection ('appliances') --> document ('washer/dryers') --> fields )
    for i in d1:
        db.collection('Appliances').document(reformat(i)).delete()
    #second: (A) create new documents & (B) fill new docs with unit information (fields)
    for i in d1:
        db.collection('Appliances').document(reformat(i)).set({"type": reformat(i)})
        for unit in d1[i]:
            key = reformat(unit)
            value = ''
            db.collection('Appliances').document(reformat(i)).update({key:value})
    print('successfully ran!')
firestore()

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
# calltwilio()
import imaplib
import sys
import traceback
import datetime
import re
from getpass import getpass

"""
PyPurge Email V1.0
This program will scan an email account using IMAP for messages older than
a certain age and delete them.

Old email can be deleted from all folders or each folder.

Because of the length of time bulikng deleting takes, folders can be scanned first
then the deletions can be left running (which might take several hours for many
thousands of messages.

After running this, you may need to "empty" your deleted items/Trash folder to recover the space.
With hotmail/live/outlook accounts (i.e. online Microsoft ones) you will need to manually empty "recoverable items" too.
This is done within the "deleted items" folder when viewing your webmail.

Version 1.0
Andrew Johnson
ad.johnson@ntlworld.com
06 Nov 2019
"""

#You can hardcode your IMAP settings here, or they can be entered interactively.
#If "user" is set to a non-empty value, it is assumed the other values are set
#and so they are not requested  interactively.
host = ''
#Port 993 is normally the port for SSL comms for IMAP
port = 993
user=''
password = ''

#This is a list of the 3 most common email providers.
imap_hosts=[["GMail","imap.gmail.com","Trash"],
            ["Hotmail, Live, Outlook","imap-mail.outlook.com","Deleted"],
            ["Yahoo","imap.mail.yahoo.com","Trash"]]
#We default to checking for email that is older than 1 year.
days_old=365
deleted_mail_folder_name="Trash"



#This expression and function parse the mailbox data returned by the IMAP server
list_response_pattern = re.compile(r'\((?P<flags>.*?)\) "(?P<delimiter>.*)" (?P<name>.*)')
def parse_list_response(line):
    
    flags, delimiter, mailbox_name = list_response_pattern.match(line).groups()
    mailbox_name = mailbox_name.strip('"')
    if flags.lower().find("noselect") >= 0:
        mailbox_name=""  
    return (flags, delimiter, mailbox_name)

#This function will iterate through the folders on the IMAP server and check
#or delete email.
def do_folders(imap,days_old,check_or_del,deletion_list):
    #Confirm any deletion of emails.
    if check_or_del != "check":
        resp = input ("Are you sure you want to delete emails? (Enter 'Yes') to confirm)>>>")
        if resp.lower()!="yes":
            return
        
    #Get the folder list from the server
    resp, data = imap.list()
    totalMsgs = 0
    actioned= "Nothing to do!"
    if resp == 'OK':
        #Iterate through folders
        for mbox in data:
            flags, separator, name = parse_list_response(bytes.decode(mbox))
            #If mailbox name returned is empty, go to next entry.
            if name == "":
                continue
            # Select the mailbox for checking or deleting messages.
            print ("Checking folder: ",name)
            imap.select('"{0}"'.format(name), (check_or_del=="check"))
            
            #Search for messages older than the given date.
            before_date = (datetime.date.today() - datetime.timedelta(days_old)).strftime("%d-%b-%Y")  # date string, 
            resp, msgnums = imap.search(None, '(BEFORE {0})'.format(before_date))
            msg_count = len(msgnums[0].split())

            #Print the results
            print('{:<30} : {: d}'.format(name, msg_count))
            
            #Shall we check or delete?
            if (msg_count > 0):
                if (check_or_del=="check"):
                    #Ask the user if they want mail deleted from the folder found.
                    print ("Delete mail older than {0} in {1} folder? (Enter y to delete)>>> ".format(before_date, name))
                    resp=input("")

                    if resp.lower()=='y':
                        #Add the folder name to a list.
                        deletion_list.append (name)
                        totalMsgs = totalMsgs + msg_count

                    actioned="Total found to Delete:"
                    continue
                else:
                    actioned="Deleted: "
                    #Print a message telling the user about the time it might take!
                    if name in deletion_list or len(deletion_list) == 0:
                        totalMsgs = totalMsgs + msg_count                        
                        print (msg_count, "messages found with date before ", before_date, "will be moved to trash")
                        if (msg_count > 50000):
                            print ("This could take several hours!")
                        elif (msg_count > 5000):
                            print ("This could take an hour or more!")
                        elif (msg_count > 500):
                            print ("This could take a few minutes")
                            
                        #Now mark the "found" messages as deleted using the IMAP library.    
                        imap.store("1:{0}".format(msg_count), '+FLAGS', '\\Deleted') 
                        continue
            else:
                #No messages found to delete so continue to next folder.
                continue

        print('{:<30} : {: d}'.format(actioned, totalMsgs))
        return (deletion_list)



folder = ''
deletion_list=[]


#Sign on message.
print ("*********--------****-----***************")
print ("* Python Email Purger - V1.0 - Nove 2019 *")
print ("*********--------****-----***************")
print (" ")

#Set some flags
exit_prog=False
input_needed=True

#Start a loop in case the user wants to have repeated runs of deleting messages!
while exit_prog==False:


    #Check if we already have some values from previous loop iteration
    if user != "":
        print ("Server:\t\t", host)
        print ("Username:\t",user)
        print ("Message Age:\t",days_old) 
        resp=input("Enter 'y' to use the values above>>> ")
        if resp != "y":
            user=""

    #Check if input values are already set and if they are not set,
    #read them in from the keyboard
    if user == "":
        while input_needed:
            #Get the host IMAP server domain etc.
            for i in range (0,len (imap_hosts)):
                print (i+1,imap_hosts[i][0], " - ",imap_hosts[i][1])
            input_needed=True            
            host_input=input("Enter imap server name number, as given above, or type the address>>> ")
            max_host_index=str(len(imap_hosts))
            if len (host_input)==1 and (host_input >"0") and (host_input <= max_host_index):
                host=imap_hosts[int(host_input)-1][1]
                #Set deleted items folder name.
                deleted_mail_folder_name=imap_hosts[int(host_input)-1][2]
                input_needed=False
            else:
                if len(host_input) < 10:
                    print ("Please enter a valid host address.")
                    input_needed=True
                else:
                    host=host_input
        user=input ("Username:")
        print ("Password:")
        #This is an attempt to read in the password without echo, but it
        #does not work when running in Windows GUI/IDLE
        password=getpass()
        
        #Get the required age of messages.
        input_needed=True
        while input_needed:
            input_needed=False
            resp = input("Deleted messages older than how many days? Default is '365'>>> ")
            if len (resp) > 0:
                days_old = int (resp)
                
            if days_old == 0:
                print ("You must enter a value greater than 0.")
                input_needed=True

    #Now connect to the server                              
    print ("Connecting to ",host,"...")
    imap = None

    try:
        # Create the IMAP Client
        imap = imaplib.IMAP4_SSL(host, port)
        # Login to the IMAP server
        resp, data = imap.login(user, password)
        #Check the server response.
        if resp == 'OK':
            print ("Logged in... Looking for messages older than", days_old, "days.")
            #Ask the user whether they want to delete messages in all folders, or
            #in selected folders.
            while not resp in ["c","a"]:
                resp = input ("Enter 'c' to check each folder, or 'a' to delete from all folders >>>")
                
            #Now call the function to check for and delete messages.
            if resp=="c":
                #Get folders and search for messages.
                deletion_list = do_folders(imap,days_old,"check", deletion_list)
                deletion_list = do_folders(imap,days_old,"delete", deletion_list)
            else:
                #Delete messages in selected folders
                deletion_list = do_folders(imap,days_old,"delete", deletion_list)
                
            if deleted_mail_folder_name!="":
                print("Emptying Trash & Expunge...")
                imap.select(deleted_mail_folder_name)  # select all trash
                imap.store("1:*", '+FLAGS', '\\Deleted')  #Flag all Trash as Deleted
                imap.expunge() 
    except:
        resp = input ("Something went wrong... enter 'd' to see details, otherwise just press 'Enter' to exit...")
        if resp=='d':
            print('Error was : {0}'.format(sys.exc_info()[0]))
            traceback.print_exc()
            print ("Are you any the wiser? :-)")
            
#    finally:
        
        resp = input ("Enter 'Y' to delete more messages.")
        if resp.lower()!='y':
            exit_prog=True;
            if imap != None:
                imap.logout()
            imap = None
            print ("Finished...")
        

#!/usr/bin/python

#TODO: We need a timeout on digit collection otherwise it loops forever and ties up the channel

import MySQLdb.cursors
from asterisk.agi import *

def main():

     agi = AGI()
     agi.answer()
     agi.verbose("Support IVR Started")

     #Determine if we should play the greeting
     play_greeting = True

     while(1):
	  
	  #init variables
          digit = ''; 
	  interrupt_digit = '';
          ticket_id = []
          
          if (play_greeting):
	       interrupt_digit = agi.stream_file("support_audio/support_greeting", '123456789')
	       agi.verbose("Interrupt digit: " + interrupt_digit)
	       if (interrupt_digit):
	            ticket_id.append(interrupt_digit)
	       else:
          	    interrupt_digit = agi.stream_file("support_audio/support_tprompt", '123456789') 
		    if (interrupt_digit):
                         ticket_id.append(interrupt_digit)

	  else:
	       interrupt_digit = agi.stream_file("support_audio/support_tprompt", '123456789') 
	       if (interrupt_digit):
	            ticket_id.append(interrupt_digit)

	  play_greeting = False

          while(1): 
               digit = agi.wait_for_digit(5000)
	       if (str(digit) != '#'):
	            ticket_id.append(digit)
	       else:
                    break

          #confirm digits	
	  agi.stream_file("support_audio/support_youentered")
	  agi.say_digits(ticket_id)

	  #confirm instructions
	  confirm = agi.stream_file("support_audio/support_confirm", '12')
	  if (confirm == 0):
               confirm = agi.wait_for_digit(5000)
	  if (confirm == "1"):
		break

     try:
          db = MySQLdb.connect(db="", host="", user="", passwd='', cursorclass=MySQLdb.cursors.DictCursor)

          cur = db.cursor()
          query_string = ''.join(str(x) for x in ticket_id)
     
          cur.execute("SELECT tickets.ticketid AS tickets_ticketid, departments.title AS tickets_departmentid FROM swtickets AS tickets LEFT JOIN swusers AS users ON (tickets.userid = users.userid) LEFT JOIN swdepartments AS departments ON (tickets.departmentid = departments.departmentid) WHERE tickets.ticketid = %s", (query_string))
          results = cur.fetchone()

     except MySQLdb.Error:

         agi.stream_file("support_audio/support_error")
	 agi.hangup()

     if (results is not None):
	     if (results['tickets_departmentid'] == "Vega Appliances"):
	          agi.stream_file("transfer")
	          #agi.appexec("Dial", )
	          agi.hangup()
	     else:
                  agi.stream_file("support_audio/support_nosupport")
     		  agi.appexec("GOTO", "from-pstn,9054741990,1")

     else:
          agi.stream_file("support_audio/support_notfound")

     agi.appexec("GOTO", "from-pstn,9054741990,1")
     #agi.hangup()



main()

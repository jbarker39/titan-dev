#!/usr/bin/python
import os
import sys
import subprocess
import string
#import mysql.connector
import re
import time
import argparse
debug = False
parser = argparse.ArgumentParser()

FN = 0
LN = 1

Agents1Name = 0
Agents1Email = 1
Agents1Phone = 2

AziListGroup = 0
AziListLN = 1
AziListFN = 2
AziListEmail = 3
AziListPhone = 4

KeyETC_Date = 0
KeyAddress = 1
KeyPurchasePrice = 2
KeyLoanAmount = 3
KeyName = 4
KeyEmail = 5
KeyPhone = 6
KeyNotes = 7

KeyPAName = 0
KeyPAEmail = 1
KeyPAPhone = 2
KeyPASalesPrice = 3
KeyPANotes = 4

USBName = 0
USBEmail = 1
USBPhone = 2
USBSalesPrice = 3
USBCustomerAgent = 4

TBDName = 0
TBDEmail = 1
TBDPhone = 2
TBDSalesPrice = 3
TBDAgent = 4

AziFriendList_Name = 0
AziFriendList_Phone = 1
AziFriendList_Email = 2
AziFriendList_Type = 3
AziFriendList_Rate = 4

AziFriendList1_Name = 0
AziFriendList1_Phone = 1
AziFriendList1_Email = 2
AziFriendList1_Type = 3
AziFriendList1_Rate = 4

WFName = 0
WFEmail = 1
WFPhone = 2

class azi_list:
	def __init__(self,fields):

		l = fields.strip()
		line = l.split(",")
		self.azi_list_group = line[AziListGroup]
		self.azi_list_lastname = line[AziListLN].capitalize()
		self.azi_list_firstname = line[AziListFN].capitalize()
		self.azi_list_email = line[AziListEmail]
		self.azi_list_phone = line[AziListPhone]

class wflist:
	def __init__(self,fields):
		l = fields.strip()
		line = l.split(",")
		self.wf_name = line[WFName]
		self.wf_email = line[WFEmail]
		self.wf_phone = line[WFPhone]

class book1_USB_PA:
	def __init__(self,fields):
		l = fields.strip()
		line = l.split(",")
		#print(line)
		self.usb_name = line[USBName]
		self.usb_email = line[USBEmail]
		self.usb_phone = line[USBPhone]
		self.usb_sales_price = line[USBSalesPrice]
		self.usb_customer_agent = line[USBCustomerAgent]

class azi_friends:
	def __init__(self, fields):
		l = fields.strip()
		line = l.split(",")
		#print("{}".format(line))
		self.azi_list_name = line[AziFriendList_Name]
		self.azi_list_phone = line[AziFriendList_Phone]
		self.azi_list_email = line[AziFriendList_Email]
		self.azi_list_type = line[AziFriendList_Type]
		self.azi_list_rate = line[AziFriendList_Rate]

class azi_friends_1:
	def __init__(self, fields):
		l = fields.strip()
		line = l.split(",")
		#print("{}".format(line))
		self.azi_list_1_name = line[AziFriendList1_Name]
		self.azi_list_1_phone = line[AziFriendList1_Phone]
		self.azi_list_1_email = line[AziFriendList1_Email]
		self.azi_list_1_type = line[AziFriendList1_Type]
		self.azi_list_1_rate = line[AziFriendList1_Rate]


class book1_agents:
	def __init__(self,fields):
		l = fields.strip()
		line = l.split(",")
		self.agents_name = line[Agents1Name]
		self.agents_email = line[Agents1Email]
		self.agents_phone = line[Agents1Phone]

class book1_Key_Clients:
	def __init__(self,fields):
		l = fields.strip()
		line = l.split(",")
		#print(line)
		self.key_etc_date = line[KeyETC_Date]
		self.key_address = line[KeyAddress]
		self.key_purchase_price = line[KeyPurchasePrice]
		self.key_loan_amount = line[KeyLoanAmount]
		self.key_name = line[KeyName]
		self.key_email = line[KeyEmail]
		self.key_phone = line[KeyPhone]
		self.key_notes = line[KeyNotes]



class book1_TBD:
	def	__init__(self,fields):
		l = fields.strip()
		line = l.split(",")
		self.tbd_name = line[TBDName]
		self.tbd_email = line[TBDEmail]
		self.tbd_phone = line[TBDPhone]
		self.tbd_sales_price = line[TBDSalesPrice]
		self.tbd_agent = line[TBDAgent]

class book1_Key_PA:
	def	__init__(self,fields):
		l = fields.strip()
		line = l.split(",")
		self.key_pa_name = line[KeyPAName]
		self.key_pa_email = line[KeyPAEmail]
		self.key_pa_phone = line[KeyPAPhone]
		self.key_pa_sales_price = line[KeyPASalesPrice]
		self.key_pa_notes = line[KeyPANotes]

class azi_files:
	def __init__(self,fields):
		line = fields.split(",")

		


# use python contacts.py filename

parser.add_argument("file", help="excel cvs file")
parser.add_argument("actor", help='actor requested')
#parser.add_argument('password', help="MySQL password")
#parser.add_argument("--debug", help="debug")
args = parser.parse_args()
s = args.actor
filename = args.file
#filename = table = switch = rack_name = passwd = args.password


################################################################################
#
# Globals
#
################################################################################
run = True
if debug:
	#if args.verbosity >=1:
	#if args.verbosity >= 3:
	#start_ip = table = switch = args.arg2
	#	end_ip = filename = nodetype = datacenter = args.arg3
	#print(f's: {s} arg1: {args.arg1} arg2: {args.arg2} arg3: {args.arg3}')
	print(f's: {s} actor: {args.actor} ')
	print(filename)

if s != "all":
	f0 = open(filename)

if s == "azilist":
	for i in f0:
		f = azi_list(i)
		print("{},{},{},{},{}".format(f.azi_list_group,f.azi_list_lastname,f.azi_list_firstname,f.azi_list_email,f.azi_list_phone))

elif s == "book1_agents":
	for i in f0:
		f = book1_agents(i)
		n = f.agents_name.split(" ")
		print ("{},{},{},{},{}".format("Agent",n[FN],n[LN],f.agents_email,f.agents_phone))
		
elif s == "wflist":
	for i in f0:
		f = wflist(i)
		n = f.wf_name.split(" ")
		print("{},{},{},{},{}".format("customer",n[FN],n[LN],f.wf_email,f.wf_phone))

elif s == "book1_key_clients":
	for i in f0:
		f = book1_Key_Clients(i)
		n0 = f.key_name.strip('"')
		n1 = n0.split(" ")
		n2 = n1[1] + " " + n1[0]
		print("{},{},{},{},{}".format("Customer",n1[0],n1[1],f.key_email,f.key_phone))
		#print("{},{},{},{},{},{},{},{}".format(f.key_etc_date,f.key_address,f.key_purchase_price,f.key_loan_amount,f.key_name,f.key_email,f.key_phone,f.key_notes))

elif s == "azi_friends":
	for i in f0:
		f = azi_friends(i)
		n = f.azi_list_name.split(" ")
		print("{},{},{},{},{}".format("customer",n[LN],n[FN],f.azi_list_email,f.azi_list_phone))

elif s == "azi_friends_1":
	for i in f0:
		f = azi_friends_1(i)
		n = f.azi_list_1_name.split(" ")
		print("{},{},{},{},{}".format("customer",n[LN],n[FN],f.azi_list_1_email,f.azi_list_1_phone))
#		print("{},{},{},{},{}".format(f.azi_list_1_name,f.azi_list_1_email,f.azi_list_1_phone,f.azi_list_1_type,f.azi_list_1_rate))

elif s == "book1_Key_PA":
	for i in f0:
		f = book1_Key_PA(i)
		n0 = f.key_pa_name.strip('"')
		n1 = n0.split(" ")
		n2 = n1[1] + " " + n1[0]
		print("{},{},{},{},{}".format("customer",n1[1],n1[0],f.key_pa_email,f.key_pa_phone))

elif s == "book1_USB_PA":
	for i in f0:
		f = book1_USB_PA(i)
		n0 = f.usb_name.strip('"')
		n1 = n0.split(" ")
		if len(n1) == 2:
			n2 = n1[1] + " " + n1[0]
			ln = n1[0]
			fn = n1[1]
		elif len(n1) == 3:
			n2 = n1[1] + " " + n1[2] + " " +  n1[0]
			ln = n1[0]
			fn = n1[1] + " " + n1[2]
		sp0 = f.usb_sales_price.strip(' ')
		#sp1 = sp0.split(",")
		#print(sp0)
		#print("{}".format(len(n1)))
		#print("{}".format(f.usb_sales_price))
		
		print("{},{},{},{},{}".format("customer",ln,fn,f.usb_email,f.usb_phone))
#		print("{},{},{},{},{}".format(n2,f.usb_email,f.usb_phone,f.usb_sales_price,f.usb_customer_agent))

elif s == "book1_TBD":
	for i in f0:
		f = book1_TBD(i)
		n0 = f.tbd_name.strip('"')
		n1 = n0.split(" ")
		if len(n1) == 2:
			n2 = n1[1] + " " + n1[0]
			ln = n1[0]
			fn = n1[1]
		elif len(n1) == 3:
			n2 = n1[1] + " " + n1[2] + " " +  n1[0]
			ln = n1[0]
			fn = n1[1] + " " + n1[2]
		print("{},{},{},{},{}".format("customer",ln,fn,f.tbd_email,f.tbd_phone))

elif s == "all":
	print("{},{},{},{},{}".format("Group","Last Name","First Name","Email","Phone"))
	f0 = open("book1-agents.csv")
	for i in f0:
		f = book1_agents(i)
		n = f.agents_name.split(" ")
		print ("{},{},{},{},{}".format("Agent",n[FN],n[LN],f.agents_email,f.agents_phone))
	f0.close()
	f0 = open("WFList.csv")	
	for i in f0:
		f = wflist(i)
		n = f.wf_name.split(" ")
		print("{},{},{},{},{}".format("customer",n[FN],n[LN],f.wf_email,f.wf_phone))
	f0.close()
	f0 = open("book1.KeyClients_closing-Nov-Dec-Jan.csv")
	for i in f0:
		f = book1_Key_Clients(i)
		n0 = f.key_name.strip('"')
		n1 = n0.split(" ")
		n2 = n1[1] + " " + n1[0]
		print("{},{},{},{},{}".format("Customer",n1[0],n1[1],f.key_email,f.key_phone))
#		print("{},{},{},{},{},{},{},{}".format(f.key_etc_date,f.key_address,f.key_purchase_price,f.key_loan_amount,f.key_name,f.key_email,f.key_phone,f.key_notes))
	f0.close()
	f0 = open("Azi Friend List.csv")
	for i in f0:
		f = azi_friends(i)
		n = f.azi_list_name.split(" ")
		print("{},{},{},{},{}".format("customer",n[LN],n[FN],f.azi_list_email,f.azi_list_phone))
#		print("{},{},{},{},{}".format(f.azi_list_name,f.azi_list_email,f.azi_list_phone,f.azi_list_type,f.azi_list_rate))
	f0.close()
	f0 = open("Azi Friend List1.csv")
	for i in f0:
		f = azi_friends_1(i)
		n = f.azi_list_1_name.split(" ")
		print("{},{},{},{},{}".format("customer",n[LN],n[FN],f.azi_list_1_email,f.azi_list_1_phone))
#		print("{},{},{},{},{}".format(f.azi_list_1_name,f.azi_list_1_email,f.azi_list_1_phone,f.azi_list_1_type,f.azi_list_1_rate))
	f0.close()
	f0 = open("book1-Key-Preapproval-Sept-to-Oct.csv")
	for i in f0:
		f = book1_Key_PA(i)
		n0 = f.key_pa_name.strip('"')
		n1 = n0.split(" ")
		n2 = n1[1] + " " + n1[0]
		print("{},{},{},{},{}".format("customer",n1[1],n1[0],f.key_pa_email,f.key_pa_phone))
	f0.close()
	f0 = open("book1-ppreapproval-USBank.csv")
	for i in f0:
		f = book1_USB_PA(i)
		n0 = f.usb_name.strip('"')
		n1 = n0.split(" ")
		if len(n1) == 2:
			n2 = n1[1] + " " + n1[0]
			ln = n1[0]
			fn = n1[1]
		elif len(n1) == 3:
			n2 = n1[1] + " " + n1[2] + " " +  n1[0]
			ln = n1[0]
			fn = n1[1] + " " + n1[2]
		sp0 = f.usb_sales_price.strip(' ')
		print("{},{},{},{},{}".format("customer",ln,fn,f.usb_email,f.usb_phone))
#12		print("{},{},{},{},{}".format(n2,f.usb_email,f.usb_phone,f.usb_sales_price,f.usb_customer_agent))
	f0.close()
	f0 = open("book1-TBD.csv")
	for i in f0:
		f = book1_TBD(i)
		n0 = f.tbd_name.strip('"')
		if len(n1) == 2:
			n2 = n1[1] + " " + n1[0]
			ln = n1[0]
			fn = n1[1]
		elif len(n1) == 3:
			n2 = n1[1] + " " + n1[2] + " " +  n1[0]
			ln = n1[0]
			fn = n1[1] + " " + n1[2]
		print("{},{},{},{},{}".format("customer",ln,fn,f.tbd_email,f.tbd_phone))
	f0.close()


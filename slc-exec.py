#!/usr/bin/python
import os
import sys
import subprocess
import string
#import mysql.connector
import re
import time
from sfrDBobj import *
#from ipmanage import *
#from DNSsubs import *
import argparse
debug = False
parser = argparse.ArgumentParser()

Customer = 0
OrderQty = 1
ServiceTag = 2
SubCategory = 3
ProcessorDesc = 4
ProcessorSpeedMHz = 5
AdditionalProcDesc = 6
Memory1Desc = 7
Memory1UnitQty = 8
Memory2Desc = 9
Memory2UnitQty = 10
HardDrive1Desc = 11
HardDrive1UnitQty = 12
WarrantyEndDate = 13

nodetype=1

class DellQpass08172010:
	def __init__(self,fields):
		memvals = {
			"512":512,"512MB":512,"1G":1024,"1GB":1024,"2G":2048,"4G":4096,"8G":8192,"16G":16384
		}

		s1 = False
		ofield = ""
		l = 0
		while l < len(fields):
			#print l
			if not s1:
				if fields[l] == '"':
					s1 = True
				else:
					ofield += fields[l]
			else:
				if fields[l] == ",":
					ofield += ":"
				elif fields[l] == '"':
					s1 = False
				else:
					ofield += fields[l]
			l += 1
		line = ofield.split(",")
		self.serial_number = line[ServiceTag]
		self.model = line[SubCategory]
		self.processor_desc = line[ProcessorDesc]
		self.processor_speed = line[ProcessorSpeedMHz]
		self.additional_proc_desc = line[AdditionalProcDesc]
		self.mem_1_desc = line[Memory1Desc]
		self.mem_1_qty = line[Memory1UnitQty]
		self.mem_2_desc = line[Memory2Desc]
		self.mem_2_qty = line[Memory2UnitQty]
		self.hd_1_desc = line[HardDrive1Desc]
		self.hd_1_qty = line[HardDrive1UnitQty]
		self.wed = line[WarrantyEndDate]
		
		cpuinfo = line[ProcessorDesc].split(":")
		#print line[ProcessorDesc]
		if cpuinfo[0] == "A":
			self.cpumfg = "AMD"
			self.cpumodel = cpuinfo[2]
			self.cpuspeed = cpuinfo[3]
		elif cpuinfo[0] =="XEON":
			self.cpumfg = "Intel"
			self.cpumodel = cpuinfo[2]
			ctemp = cpuinfo[3].split("/")
			self.cpuspeed = ctemp[0]
		elif cpuinfo[0] == "XUW" or cpuinfo[0] == "XKF":
			self.cpumfg = "Intel"
			self.cpumodel = cpuinfo[1]
			ctemp = cpuinfo[2].split("/")
			self.cpuspeed = ctemp[0]
		else:
			self.cpumfg = "N/A"
			self.cpumodel = "N/A"
			self.cpuspeed = "N/A"
		
		if re.search("DIMM",line[Memory1Desc]):
			meminfo = line[Memory1Desc].split(":")
			self.memqty = line[Memory1UnitQty]
			self.memsize = memvals[meminfo[1]]
		elif re.search("PWA",line[Memory1Desc]):
			meminfo = line[Memory2Desc].split(":")
			self.memqty = line[Memory2UnitQty]
			self.memsize = memvals[meminfo[1]]
		else:
			self.memqty = 0
			self.memsize = 0

class	merge_Dell_assets:
	#      0          1                2                   3                 4                       5
	#assets.fqdn,racks.rack_name,models.manufacturer,models.model_name,assets.serial_number,customers.customer_name
	def __init__(self,assets,sn):
		self.fqdn = ""
		self.rack_name = ""
		self.mfg = ""
		self.model_name = ""
		self.serial_number = sn
		self.customer_name = ""
		self.warranty_date = ""
		
		for i in assets:
			if re.search(sn,i[5]):
				print (sn,i[1])
				self.fqdn = i[1]
				self.rack_name = i[2]
				self.mfg = i[3]
				self.model_name = i[5]
				self.serial_number = i[5]
				self.customer_name = i[6]
				self.warranty_date = i[7]

class slcrecord:
		def __init__(self,line):
				linein = line.split(",")
				#print linein
				#Starting U Asset Tag Model Name Rack Name Serial Number
				self.starting_u = linein[0].strip()
				self.asset_tag = linein[1].strip()
				self.model_name = linein[2].strip()
				self.rack_name = linein[3].strip()
				self.serial_number = linein[4].strip()
				


class QwestScan:
	def	__init__(self,fields):
		self.sn = fields[0].strip('"')
		self.rack_name = fields[1].strip('"')
		self.model_name = fields[2].strip('"')

class assets_db:
	def	__init__(self,fields):
		#asset_id,fqdn,serial_number,model_id,verified
		self.asset_id = fields[0]
		self.fqdn = fields[1]
		self.serial_number = fields[2]
		self.model_id = fields[3]
		self.rack_id = fields[4]
		self.verified = fields[5]


class vm_detail:
	def	__init__(self,fields):
		f = fields.split(":")
		self.fqdn = f[0]
		

def	ignore(model):
	m = ["CATALYST","Cyclades","Cisco","FAS3","FAS2","Integrity","DECRU","C6506","PX15","Brocade","Netgear","SILKWORM","AlterPath","WSC3750G","NETAPP","Silkworm",\
		 "SOURCE","SUN","CISCO","515E","Source","380","385","365","360","Infoblox","SR1500","Sun","Catalyst","ADIC","INFOBLOX","EYE"]
	for i in m:
		if re.search(i,model): return True
	return False

def ping(hostname):
	cmd = "ping c2 " + hostname
	result = subprocess.getoutput(cmd)
	if re.search("2 received",result):
		return True
	else:
		return False
	
def	dns(hn):
#	DNS.ParseResolvConf()
#	r=DNS.Request(qtype='soa')
#	res = r.req('sea2.qpass.net')
#	res.show()

#	try:
#		hn = DNS.revlookup(ip)
#		return hn
#	except:
#		return None
	try:
#		s = DNS.Request(hn)
		resolve = s.req().answers
		#print resolve,hn
		if (resolve) :
			ip = resolve[0]['data']
			if re.search(".net",ip):
				ip = resolve[1]['data']
			return ip
	except:
		ip = "not found"
	
#	def status(self,s):
#		self.s = s
class slcrecord_confirm:
		def __init__(self,line):
				l = line.split(",")
				self.model = l[0].strip()
				self.asset_tag = l[1].strip()
				self.fqdn = string.lower(l[2].strip())
				self.serial_number = l[3].strip()
				
class BTG_confirm:
	def __init__(self,line):
			l = line.split(",")
			self.model = l[0].strip()
			self.location = l[1].strip()
			self.asset_tag = l[2].strip()
			self.serial_number = l[3].strip()
			self.fqdn = l[4].strip()
			self.record = l[5].strip()


#Full name (Model),Location,Bar code/RFID (Asset),Serial # (Asset),Quantity,System Host name,Record origination - BTG			

class MFS_confirm:
	def __init__(self,line):
			l = line.split(",")
			self.model = l[0].strip()
			self.asset_tag = l[1].strip()
			self.serial_number = l[2].strip()
			self.fqdn = l[3].strip()
			self.qty = l[4].strip()
			self.record = l[5].strip()
			#print ("Len {}. {}".format(len(l),l))

#Full name (Model),Bar code/RFID (Asset),Serial # (Asset),Quantity,System Host name,Record origination - MFS

class BTG_ML_asset:
	def __init__(self,line):
		l = line.split("/")
		if (len(l) < 7):
			self.rack = "BAD"
		else:
			self.rack = l[5].strip()

class	asset_record:
	def __init__(self,line):
		#    0      1       2         3           4            5            6          7          8
		#asset_id,fqdn,rack_name,model_name,serial_number,asset_tag,customer_name,starting_u,manufacturer
		self.asset_id = line[0]
		self.fqdn = line[1]
		self.rack_name = line[2]
		self.model_name = line[3]
		self.serial_number = line[4]
		self.asset_tag = line[5]
		self.customer_name = line[6]
		self.starting_u = line[7]
		self.manufacturer = line[8]

class	oldar:
	def __init__(self,line):
		#       0          1        2            3          4              5               6               7          8
		#assets.asset_id,fqdn,serial_number,asset_tag,assets.rack_id,assets.model_id,assets.cust_id,warranty_date,starting_u
		self.asset_id = line[0]
		self.fqdn = line[1]
		self.serial_number = line[2]
		self.asset_tag = line[3]
		self.rack_id = line[4]
		self.model_id = line[5]
		self.cust_id = line[6]
		self.warranty_date = line[7]
		self.starting_u = line[8]
		  
def	sysinfo(assets,rn,su,nodetype):
		#print rn,su
		for i in assets:
			j = asset_record(i)
			if j.rack_name == rn and j.starting_u == su:
				if nodetype == 'FQDN':
					info = j.asset_tag + " " + " " + j.model_name + " " + j.fqdn
					return info
				elif nodetype == 'MODEL':
					info = j.asset_tag + " " + j.model_name + " "  + j.model_name
					return info
				else:
					return ""
		return ""

# use python slc-exec.py action mysql_password
parser.add_argument("host", help="database host")
parser.add_argument("actor", help='actor requested')
parser.add_argument('password', help="MySQL password")
#parser.add_argument("--debug", help="debug")
args = parser.parse_args()
s = args.actor
host = args.host
filename = table = switch = rack_name = passwd = args.password


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
	print(f's: {s} actor: {args.actor} password: {args.password}')
	print(f'passwd: {passwd}')
	print(host)
#host = 'db-2'
if (host == '20-04ltsdev'):
	#20-04ltsdev is the primary mysql server 
	dbnameA = "20-04ltsdev.endofdays-2012.dev","jbarker",passwd,"titan"
	dbnameB = "20-04ltsdev.endofdays-2012.dev","jbarker",passwd,"newslc"
	dbname6 = "20-04ltsdev.endofdays-2012.dev","jbarker",passwd,"titan"
	dbname7 = "20-04ltsdev.endofdays-2012.dev","jbarker",passwd,"newslc"	

elif (host == 'localhost'): 	#localhost contains database
	dbname1 = "localhost","root",passwd,"newqwest"
	dbname2 = "localhost","root",passwd,"qahmcons"
	dbname3 = "localhost","root",passwd,"slc"
	dbname4 = "localhost","root",passwd,"newslc"
	dbname5 = "localhost","root",passwd,"qahm2"
	dbname6 = "localhost","root",passwd,"titan"
	dbname7 = "localhost","root",passwd,"newslc"
	dbnameA = "localhost","root",passwd,"titan"
	dbnameB = "localhost","root",passwd,"newslc"

elif (host == 'util-3'):
	dbnameA = "util-3.endofdays-2012.dev","jbarker",passwd,"titan"
	dbnameB = "util-3.endofdays-2012.dev","jbarker",passwd,"newslc"

elif (host == 'util-1'):
	dbnameA = "util-1.endofdays-2012.dev","jbarker",passwd,"titan"
	dbnameB = "util-1.endofdays-2012.dev","jbarker",passwd,"newslc"

elif (host == 'macbook'):
	dbnameA = "macbook.endofdays-2012.dev","jbarker",passwd,"titan"
	dbnameB = "macbook.endofdays-2012.dev","jbarker",passwd,"newslc"

elif (host == 'macstudio'):
	dbnameA = "macstudio.endofdays-2012.dev","jbarker",passwd,"titan"
	dbnameB = "macstudio.endofdays-2012.dev","jbarker",passwd,"newslc"

elif (host == 'db-1'):
	dbnameA = "db-1.endofdays-2012.dev","jbarker",passwd,"titan"
	dbnameB = "db-1.endofdays-2012.dev","jbarker",passwd,"newslc"

elif (host == 'dev1'):
	dbnameA = "dev1.endofdays-2012.dev","jbarker",passwd,"titan"
	dbnameB = "dev1.endofdays-2012.dev","jbarker",passwd,"newslc"
else:
	print("OOPS {}".format(host))
	exit()


if s == "MLBTG":
	print (s)
	f0 = open('JOE_BARKER_BTG.csv')
	db = DBobj(dbnameA)
	
	for i in f0:
		f = BTG_confirm(i)
		if (re.search ("USA.WA.MOS",f.location)):
			s1 = BTG_ML_asset(f.location)
			if (f.serial_number !=""):
				fqdn=db.getHostname_For_SerialNumber(f.serial_number)
				if (fqdn):
					print ("{},{}".format(f.serial_number,fqdn[0]))
				else:
					print ("{} not found in rack {}".format(f.serial_number,s1.rack))
elif s == "MLMFS":
	print (s)
	f0 = open('JOE_BARKER_MFS.csv')
	db = DBobj(dbnameA)
	
	for i in f0:
		f = MFS_confirm(i)
		if (f.serial_number !=""):
			fqdn=db.getHostname_For_SerialNumber(f.serial_number)
			if (fqdn):
				print ("{},{},{},{}".format(f.model,f.serial_number,f.asset_tag,fqdn[0]))
			else:
				print ("{}  ,  {}  ,  {}  ,  {}  ,  {} not found".format(f.model,f.serial_number,f.asset_tag,f.fqdn,f.record))

elif s == "completeslc":
	f0 = open('slcassets.csv')
	db = DBobj(dbname3)
	for i in f0:
		f = slcrecord_confirm(i)
		db.update_fqdn_by_asset_tag(f.asset_tag,f.fqdn)
		#print "{}  {}" % (f, db.get_aid(f))
		#print ( "{},{},{}".format (curar.asset_tag,curar.fqdn,newar.fqdn))

elif s == "decom_repair": #single time use - DO NOT RUN again
	db = DBobj(dbname6)
	db1= DBobj(dbname7)
	titan = db.get_decom()
	titan1 = db1.get_decom()
	for i in titan1:
		# update_decom(self,aid,d,wd)
		#print "update titan with: {} {} {}" % (i)
		#for j in titan1:
		#	if i[0] == j[0]:
		#		print "titan: {} titan1: {} {} {}" % (i[0],j[0],j[1],j[2])
		db.update_decom_1(i[0],i[1],i[2])
elif s == "updateARM":
	db = DBobj(dbname4)
	f1 = open ('ARMupdate.csv')
	for l in f1:
		line = l.split(',')
		#print line[0]
		if line:
			f = db.get_asset_by_asset_tag_v1(line[1].strip())
			if f: print ("{} {} Found" .format (line[0],line[1].strip()))
			else:
				r1 = db.update_from_ARMupdate(line)
				#print "{} {} updated" % (line[0],line[1].strip())
		#print ("{},{},{}") % (f.asset_tag,f.fqdn,f.fqdn)
		
elif s == "updateSLC":
	db = DBobj(dbname4)
	f0 = open("updates816.csv")
	for line in f0:
		#    0         1        2        3            4            5        6             7
		#Customer, Location, System, Asset Tag, Serial Number, Host name, Status, Decommisson Date
		l = line.split(',')
		if l[3] and l[0] != 'Customer':
			r = db.get_asset_by_asset_tag_v1(l[3])
			#r   0         1            2        3
			#  fqdn,serial_number,rack_name,model_name
			if r:
				r1 = db.update_rack_id(l[3],l[1])
				#r1 = db.update_decom(l[3],l[7])
				#need to update decommissioned date yet
				#continue
				#
				
				
				#print "%10s %50s %10s %10s %10s" % (l[3],r[0],r[1],r[2],r[3])
			else: 
				#r1 = db.update_from_update816(l)
				print ("updated {} host {}" .format (l[3],l[5]))
					

elif s == "updateModels  do not use again":
	db1 = DBobj(dbname3)
	db2 = DBobj(dbname4)
	r1 = db1.get_models_from_db()
	for r in r1:
		db2.insert_model(r)

elif s == "rackableUpdate":
	db1 = DBobj(dbname4) #newslc
	f = open("SLCRackableDecomm.csv")
	for l in f:
		line  = l.split(',')
		#print line
		r = db1.updateRackable(l)
		#r1 = db2.qham2_update_rackable(line[0],line[1])
		#print r1

elif s == "serials":
	db1 = DBobj(dbnameA)
	f = open("serials.csv")
	for l in f:
		sn = l.strip()
		db1.Feb_2021_update(sn)
		db1.Feb_2021_confirm(sn)
		#print('{}'.format(sn))

elif s == "decomreport":
	db1 = DBobj(dbname7)
	results  = db1.decom_report()
	print("fqdn,asset_tag,serial_number,model_name,rack_name,decom,warranty_date,vcpu,ramGB,CPU")
	for r in results:
		if (re.search('to be removed',(r[4]))):
			print ('{},{},{},{},{},{},{},{},{},{}'.format(r[0],r[1],r[2],r[3],r[4],r[5],r[6],r[7],r[8],r[9]))

elif s == "report_SLC":
	db1 = DBobj(dbnameB)
	results  = db1.all_assets()
	#    0      1       2         3           4            5            6          7       8             9      10
	#asset_id,fqdn,rack_name,model_name,serial_number,asset_tag,customer_name,starting_u,manufacturer,decom,warranty_date	
	print ('Asset_id,FQDN,rack,model,serial_number,asset_tag,Customer,starting U,Mfg,decom,warranty')
	for r in results:
		#print (len(r))
		#print( r)
		#if (not (re.search( 'decom',r[1])) ):
			#print r
			#if (r[2] != 'decom'):
				#if (r[8] != 'NetApp'):
		print ('{},{},{},{},{},{},{},{},{},{},{}'.format(r[0],r[1],r[2],r[3],r[4],r[5],r[6],r[7],r[8],r[9],r[10]))
				#else:
					#print (r[8])

elif s == "filter":
	db1 = DBobj(dbnameA)
	f = open("assetlist02152021.csv")
	for i1 in f:
		i = re.sub('"',"",i1)
		l = i.split(",")
		#print(len(l))
		if re.search(" CHASSIS ",l[2]) or l[2] == '' or l[3] == "Serial # (Asset)":
			pass
		else:
			j = l[1].split('/')
			#print(j)
			print(l[3])
			r = db1.getAsset_id_For_SerialNumber(l[3])
			#r = db1.getHostname_For_SerialNumber(l[3])
			#print("SN: {} , FQDN {}".format(l[3],r))

elif s == "report_titan":
	db1 = DBobj(dbnameA)
	results  = db1.all_assets()
	print ('Asset_id,FQDN,rack,model,serial_number,asset_tag,Customer,starting U,Mfg,decom,warranty')
	for r in results:
		#print len(r)
		print ('{},{},{},{},{},{},{},{},{},{},{}'.format(r[0],r[1],r[2],r[3],r[4],r[5],r[6],r[7],r[8],r[9],r[10]))

		#    0      1       2         3           4            5            6          7       8              9           10
		#asset_id,fqdn,rack_name,model_name,serial_number,asset_tag,customer_name,starting_u,manufacturer,warranty_date,decom

elif s == "report_titan_support":
	db1 = DBobj(dbnameA)
	results  = db1.full_assets()
	print ('Asset_id,Rack,model,FQDN,serial_number,asset_tag,Customer,starting U,Mfg,warranty,decom')
	for r in results:
		#print (len(r))
		#print (r)
		if (r[10] == 'in service'):
			print ('{},{},{},{},{},{},{},{},{},{},{}'.format(r[0],r[2],r[3],r[1],r[4],r[5],r[6],r[7],r[8],r[9],r[10]))
	db1 = DBobj(dbnameB)
	results  = db1.full_assets()
	print ('Asset_id,Rack,model,FQDN,serial_number,asset_tag,Customer,starting U,Mfg,warranty,decom')
	for r in results:
		#print (len(r))
		#print (r)
		if (r[10] == 'in service'):
			print ('{},{},{},{},{},{},{},{},{},{},{}'.format(r[0],r[2],r[3],r[1],r[4],r[5],r[6],r[7],r[8],r[9],r[10]))

elif s == "report_titan_assets":
	db1 = DBobj(dbnameA)
	results  = db1.get_ALL_assets()
	print ('Asset_id,FQDN,Model ID,Rack ID,Cust ID,Serial Number,Starting U,Warranty Date,Asset Tag,OS,Decom,Hyperthreading On')
	for r in results:
		#print len(r)
		print ('{},{},{},{},{},{},{},{},{},{},{},{}'.format(r[0],r[1],r[2],r[3],r[4],r[5],r[6],r[7],r[8],r[9],r[10],r[11]))

elif s == "report_slc_assets":
	db1 = DBobj(dbnameB)
	results  = db1.get_ALL_assets()
	print ('Asset_id,FQDN,Model ID,Rack ID,Cust ID,Serial Number,Starting U,Warranty Date,Asset Tag,OS,Decom,Hyperthreading On')
	for r in results:
		#print len(r)
		print ('{},{},{},{},{},{},{},{},{},{},{},{}'.format(r[0],r[1],r[2],r[3],r[4],r[5],r[6],r[7],r[8],r[9],r[10],r[11]))

#         0       1         2         3
#select fqdn,rack_name,model_name,serial_number
elif s == "fiberchannel":
	print ("Moses Lake, WA")
	db = DBobj(dbnameA)
	results = db.get_fc_switches()
	for r in results:
		#print (r)
		print('{},{},{},{}'.format(r[0],r[1],r[2],r[3]))
	print ("Salt Lake City, UT")
	db = DBobj(dbnameB)
	results = db.get_fc_switches()
	for r in results:
		#print (r)
		print('{},{},{},{}'.format(r[0],r[1],r[2],r[3]))

elif s == "report_titan_by_racks":
	db = DBobj(dbnameA)
	results = db.get_by_racks()
	#    0         1          2        3      4             5
	#starting_u,rack_name,model_name,fqdn,serial_number,customer_name
	print ("Starting U,Rack Name,Model,FQDN,Serial Number,Customer")
	for i in results:
		print ('{},{},{},{},{},{}'.format(i[0],i[1],i[2],i[3],i[4],i[5]))

elif s == "report_SLC_by_racks":
	db = DBobj(dbnameB)
	results = db.get_by_racks()
	print ("Starting U,Rack Name,Model,FQDN,Serial Number,Customer")
	for i in results:
		print ('{},{},{},{},{},{}'.format(i[0],i[1],i[2],i[3],i[4],i[5]))

elif s == "report_titanA":
	db1 = DBobj(dbname6)
	results  = db1.all_assets()
	print ('asset_id,FQDN,Decom,rack,model,serial_number,asset_tag,Customer,starting U,Mfg')
	for r in results:
		#print '{},{},{},{},{},{},{},{},{}'.format(r[1],r[2],r[3],r[4],r[5],r[6],r[7],r[8],r[9])				
		if  r[2] == None:
			print ('{},{},{},{},{},{},{},{},{},{}'.format(r[0],r[1],'in service',r[3],r[4],r[5],r[6],r[7],r[8],r[9]))
		if (r[2] == 'in service'):
			print ('{},{},{},{},{},{},{},{},{},{}'.format(r[0],r[1],r[2],r[3],r[4],r[5],r[6],r[7],r[8],r[9]))

elif s == "updateNetApp":
	db1 = DBobj(dbname4)
	f = open("NetApp82416.csv")
	for l in f:
		line = l.split(',')
		if line[0]:
			aid = db1.get_asset_by_asset_tag_v1(line[2])
			print ("asset_tag {} has asset_id {}" .format (line[2],aid))
			
			
elif s == "auditSLC":
	db1 = DBobj(dbname4)
	f = open("ERP.csv")
	for i in f:
		iout = i.strip()
		values = i.split(",")
		if values[3]:
			m = db1.check_inv(values[3])
			if m:
				print ("{},{}" .format (m[0],iout))
			else:
				print ("no serial number,{}" .format (iout))
		else:
			print ("decommissioned,{}" .format (iout))
			
elif s == "netapp":
	db = DBobj(dbname4)
	netapp = db.get_netApp()
	for i in netapp:
		print ("{},{},{},{}" .format (i[1],i[2],i[3],i[5]))
		
elif s == "AOP18":
	d = ["120.23","120.24","106.31","106.32"]
	print ("Manf,model,serial number,asset tag")
	db = DBobj(dbname4)
	for k in d:
		i = db.AOP18(k)
		for item in i:
			print ("{},{},{},{}" .format (item[1],item[0],item[2],item[3]))
#useage
#dump table
#python slcexec.py dumptable <assets,models,racks,cages,facilities> <titan,titan1,newslc>

#load table
#python slcexec.py 12 tablename filename	

if s == 'dumptable': #hostname,username,passed,usedb
	db = DBobj(dbnameA)
	print (dbnameA)
	results = db.dump_db(table)
elif s == '10.5': #python qwestexec.py switch [qwest/newqwest]
	if switch == "qwest":
		db = DBobj(dbnameA)
	else:
		db = DBobj(dbname1)
	results = db.print_qwest()
	for i in results:
		print (i)
 
elif s == '11':#python qwestexec.py 11 "rack_name"
	db = DBobj(dbnameA)
	assets = db.return_all_assets(rack_name)
	db1 = DBobj(dbname1)
	for i in assets:
		ar = oldar(i)
		#print ar.asset_tag,ar.starting_u
		# db1.update_su_newqwest(ar.asset_tag,ar.starting_u)
 
elif s == '12':
	db = DBobj(dbnameA)
	results = db.load_db(table,filename)
 
elif s == '14':
	db = DBobj(dbnameA)
	assets = db.return_all_assets(rack_name)
	db1 = DBobj(dbname1)
	for i in assets:
		db1.insert_newqwest(i)
		#print i
elif s == '16':	 #python qwestexec.py 16 <dbname [qwest:newqwest]> <nodetype [FQDN:MODEL]
		rowb = ("SU","B098","B099","B100","B101","B102","B103","B104","B105","B106","B107","B108\n")
		rowc = ("\nSU","C098","C099","C100","C101","C102","C103","C104","C105","C106","C107","C108\n")
		rowd = ("\nSU","D098","D099","D100","D101","D102","D103","D104","D105","D106","D107","D108\n")
		if switch == 'oldqwest':
			db = DBobj(dbnameA)
		elif switch == 'newqwest':
			db = DBobj(dbname1)
		assets = db.all_assets()
 
		print ("{},{},{},{},{},{},{},{},{},{},{},{}" .format (rowb))
		r = 1
		s = 42
		f = ["","","","","","","","","","","",""]
		while s > 4:
			while r < 12:
				f[r] = sysinfo(assets,rowb[r],s,nodetype)
				r += 1
				f[0] = s
				print ("{},{},{},{},{},{},{},{},{},{},{},{}".format (f[0],f[1],f[2],f[3],f[4],f[5],f[6],f[7],f[8],f[9],f[10],f[11]))
				s = 1
				r = 1
 
		print ("{},{},{},{},{},{},{},{},{},{},{},{},{},{}" .format (rowc))
		r = 1
		s = 42
		f = ["","","","","","","","","","","",""]
		while s > 4:
			while r < 12:
				f[r] = sysinfo(assets,rowc[r],s,nodetype)
				r += 1
				f[0] = s
				print ("{},{},{},{},{},{},{},{},{},{},{},{}" .format (f[0],f[1],f[2],f[3],f[4],f[5],f[6],f[7],f[8],f[9],f[10],f[11]))
				s = 1
				r = 1
 
		print ("{},{},{},{},{},{},{},{},{},{},{},{},{},{}" .format (rowd))
		r = 1
		s = 42
		f = ["","","","","","","","","","","",""]
		while s > 4:
			while r < 12:
				f[r] = sysinfo(assets,rowd[r],s,nodetype)
				r += 1
				f[0] = s
				print ("{},{},{},{},{},{},{},{},{},{},{},{}" .format (f[0],f[1],f[2],f[3],f[4],f[5],f[6],f[7],f[8],f[9],f[10],f[11]))
				s = 1
				r = 1
elif s == 'RowB':
	current_rack=0
	current_starting_u=1
	new_rack=2
	new_starting_u=3
	new_fqdn=4
	current_serial_number=5
	current_model_name=6
	mfg = 7
	move = {}
	db = DBobj(dbnameA)
	current = db.all_assets()
	db1 = DBobj(dbname1)
	newqwest = db1.all_assets()
	for i in current:
		curar = asset_record(i)
		if re.search("B",curar.rack_name):
			for j in newqwest:
				newar = asset_record(j)
				# if curar.asset_tag == newar.asset_tag and curar.rack_name != newar.rack_name:
					# move.setdefault(curar.asset_tag,[]).append(curar.rack_name)
					# move.setdefault(curar.asset_tag,[]).append(curar.starting_u)
					# move.setdefault(curar.asset_tag,[]).append(newar.rack_name)
					# move.setdefault(curar.asset_tag,[]).append(newar.starting_u)
					# move.setdefault(curar.asset_tag,[]).append(newar.fqdn)
					# move.setdefault(curar.asset_tag,[]).append(curar.serial_number)
					# move.setdefault(curar.asset_tag,[]).append(curar.model_name)
	# print "Asset tag,fqdn,from rn,from SU,to rn,to SU\n"
	# for i in move: #remove the EOL servers from B100
		# if move[i][new_rack] == "PILE" and move[i][current_rack] == "B100":
			# print "{},{},{},{},{},{}" % (i,move[i][new_fqdn],move[i][current_rack],move[i][current_starting_u],move[i][new_rack],move[i][new_starting_u])
	# for i in move: #move the required servers to B100
		# if move[i][new_rack] != "PILE" and move[i][new_rack] == "B100":
			# print "{},{},{},{},{},{}" % (i,move[i][new_fqdn],move[i][current_rack],move[i][current_starting_u],move[i][new_rack],move[i][new_starting_u])
	#for i in move: #turn off EOL servers
		# if move[i][new_rack] == "PILE" and move[i][current_rack] != "B100":
			# print "{},{},{},{},{},{}" % (i,move[i][new_fqdn],move[i][current_rack],move[i][current_starting_u],move[i][new_rack],move[i][new_starting_u])
	# for i in move: #need to be moved later to other than B100
		# if move[i][new_rack] != "PILE" and move[i][new_rack] != "B100":
			# print "{},{},{},{},{},{}" % (i,move[i][new_fqdn],move[i][current_rack],move[i][current_starting_u],move[i][new_rack],move[i][new_starting_u])
 
elif s == 'AllRows':
	current_rack=0
	current_starting_u=1
	new_rack=2
	new_starting_u=3
	new_fqdn=4
	current_serial_number=5
	current_model_name=6
 
	move = {}
	db = DBobj(dbname3)
	current = db.all_assets()
	db1 = DBobj(dbname4)
	newslc = db1.all_assets()
	for i in current:
		curar = asset_record(i)
		for j in newslc:
			newar = asset_record(j)
			# if curar.asset_tag == newar.asset_tag and curar.rack_name != newar.rack_name:
				# move.setdefault(curar.asset_tag,[]).append(curar.rack_name)
				# move.setdefault(curar.asset_tag,[]).append(curar.starting_u)
				# move.setdefault(curar.asset_tag,[]).append(newar.rack_name)
				# move.setdefault(curar.asset_tag,[]).append(newar.starting_u)
				# move.setdefault(curar.asset_tag,[]).append(newar.fqdn)
				# move.setdefault(curar.asset_tag,[]).append(curar.serial_number)
				# move.setdefault(curar.asset_tag,[]).append(curar.model_name)
	# print "Asset tag,fqdn,from rn,from SU,to rn,to SU,Model Name"
	# for i in move: #need to be moved later to other than B100
		# if move[i][new_rack] != "PILE" and move[i][new_rack] != "UATdiscard":
			# print "{},{},{},{},{},{},{}" % (i,move[i][new_fqdn],move[i][current_rack],move[i][current_starting_u],move[i][new_rack],move[i][new_starting_u],move[i][current_model_name])
 
elif s == 'B100Cons':
	current_rack=0
	current_starting_u=1
	new_rack=2
	new_starting_u=3
	new_fqdn=4
	current_serial_number=5
	current_model_name=6
 
	move = {}
	db = DBobj(dbnameA)
	current = db.all_assets()
	db1 = DBobj(dbname1)
	newqwest = db1.all_assets()
	for i in current:
		curar = asset_record(i)
		if re.search("B101",curar.rack_name) or re.search("B103",curar.rack_name) or re.search("B102",curar.rack_name) or re.search("B100",curar.rack_name):
			for j in newqwest:
				newar = asset_record(j)
				if curar.asset_tag == newar.asset_tag and newar.rack_name == 'B100':
					move.setdefault(curar.asset_tag,[]).append(curar.rack_name)
					move.setdefault(curar.asset_tag,[]).append(curar.starting_u)
					move.setdefault(curar.asset_tag,[]).append(newar.rack_name)
					move.setdefault(curar.asset_tag,[]).append(newar.starting_u)
					move.setdefault(curar.asset_tag,[]).append(newar.fqdn)
					move.setdefault(curar.asset_tag,[]).append(curar.serial_number)
					move.setdefault(curar.asset_tag,[]).append(curar.model_name)
	print ("Asset tag,fqdn,from rn,from SU,to rn,to SU\n")
	for i in move: #remove the EOL servers from B100
		print ("{},{},{},{},{},{}" .format (i,move[i][new_fqdn],move[i][current_rack],move[i][current_starting_u],move[i][new_rack],move[i][new_starting_u]))
 
 
elif s == 'Pile': #python qwestexec.py Pile <rack_name>
	current_rack=0
	current_starting_u=1
	new_rack=2
	new_starting_u=3
	new_fqdn=4
	current_serial_number=5
	current_model_name=6
 
	move = {}
	db = DBobj(dbnameA)
	current = db.all_assets()
	db1 = DBobj(dbname1)
	newqwest = db1.all_assets()
	for i in current:
		curar = asset_record(i)
		for j in newqwest:
			newar = asset_record(j)
			if curar.asset_tag == newar.asset_tag and newar.rack_name == 'PILE' and re.search(rack_name,curar.rack_name):
				move.setdefault(curar.asset_tag,[]).append(curar.rack_name)
				move.setdefault(curar.asset_tag,[]).append(curar.starting_u)
				move.setdefault(curar.asset_tag,[]).append(newar.rack_name)
				move.setdefault(curar.asset_tag,[]).append(newar.starting_u)
				move.setdefault(curar.asset_tag,[]).append(newar.fqdn)
				move.setdefault(curar.asset_tag,[]).append(curar.serial_number)
				move.setdefault(curar.asset_tag,[]).append(curar.model_name)
	print ("Asset tag,fqdn,from rn,from SU,to rn,to SU\n")
	for i in move:
		print ("{},{},{},{},{},{}" .format (i,move[i][new_fqdn],move[i][current_rack],move[i][current_starting_u],move[i][new_rack],move[i][new_starting_u]))
 
 
elif s == 'Cons':  #python qwestexec.py Cons <rack_name>
	current_rack=0
	current_starting_u=1
	new_rack=2
	new_starting_u=3
	new_fqdn=4
	current_serial_number=5
	current_model_name=6
 
	move = {}
	db = DBobj(dbnameA)
	current = db.all_assets()
	db1 = DBobj(dbname1)
	newqwest = db1.all_assets()
	for i in current:
		curar = asset_record(i)
		for j in newqwest:
			newar = asset_record(j)
			# if curar.asset_tag == newar.asset_tag and newar.rack_name == rack_name:
				# move.setdefault(curar.asset_tag,[]).append(curar.rack_name)
				# move.setdefault(curar.asset_tag,[]).append(curar.starting_u)
				# move.setdefault(curar.asset_tag,[]).append(newar.rack_name)
				# move.setdefault(curar.asset_tag,[]).append(newar.starting_u)
				# move.setdefault(curar.asset_tag,[]).append(newar.fqdn)
				# move.setdefault(curar.asset_tag,[]).append(curar.serial_number)
				# move.setdefault(curar.asset_tag,[]).append(curar.model_name)
	print ("Asset tag,fqdn,from rn,from SU,to rn,to SU\n")
	for i in move:
		print ("{},{},{},{},{},{}" .format (i,move[i][new_fqdn],move[i][current_rack],move[i][current_starting_u],move[i][new_rack],move[i][new_starting_u]))
 
elif s == 'Evac': #python qwestexec.py Evac <rack_name>
	current_rack=0
	current_starting_u=1
	new_rack=2
	new_starting_u=3
	new_fqdn=4
	current_serial_number=5
	current_model_name=6
 
	move = {}
	db = DBobj(dbnameA)
	current = db.all_assets()
	db1 = DBobj(dbname1)
	newqwest = db1.all_assets()
	for i in current:
		curar = asset_record(i)
		for j in newqwest:
			newar = asset_record(j)
			# if curar.asset_tag == newar.asset_tag and (newar.rack_name == 'PILE' or newar.rack_name == 'UATdiscard') and re.search(rack_name,curar.rack_name):
				# move.setdefault(curar.asset_tag,[]).append(curar.rack_name)
				# move.setdefault(curar.asset_tag,[]).append(curar.starting_u)
				# move.setdefault(curar.asset_tag,[]).append(newar.rack_name)
				# move.setdefault(curar.asset_tag,[]).append(newar.starting_u)
				# move.setdefault(curar.asset_tag,[]).append(newar.fqdn)
				# move.setdefault(curar.asset_tag,[]).append(curar.serial_number)
				# move.setdefault(curar.asset_tag,[]).append(curar.model_name)
	# print "Asset tag,fqdn,from rn,from SU,to rn,to SU\n"
	for i in move:
		print ("{},{},{},{},{},{}" .format (i,move[i][new_fqdn],move[i][current_rack],move[i][current_starting_u],move[i][new_rack],move[i][new_starting_u]))
 
elif s == 'EOL':
	db = DBobj(dbname3)
	cur = db.all_assets()
	db1 = DBobj(dbname4)
	for i in cur:
		n = asset_record(i)
		# if not db1.get_asset_by_asset_tag(n.asset_tag):
			# print "{},{},{},{},{}" % (n.fqdn,n.manufacturer,n.serial_number,n.asset_tag,n.model_name)
 
elif s == 'EOLFqdn':
	db = DBobj(dbname1)
	newqwest = db.all_assets()
	# print "FQDN,Serial Number,Asset Tag,Rack Name,Model Name"
	for i in newqwest:
		n = asset_record(i)
		# if n.rack_name == "PILE" or n.rack_name == "UATdiscard":
			# print "{},{},{},{}" % (n.fqdn,n.serial_number,n.asset_tag,n.model_name)
 
elif s == 'EOL2': #python qwestexec.py Evac <rack_name>
	current_rack=0
	current_starting_u=1
	new_rack=2
	new_starting_u=3
	new_fqdn=4
	current_serial_number=5
	current_model_name=6
 
	move = {}
	db = DBobj(dbnameA)
	current = db.all_assets()
	db1 = DBobj(dbname1)
	newqwest = db1.all_assets()
	for i in current:
		curar = asset_record(i)
		for j in newqwest:
			newar = asset_record(j)
			# if curar.asset_tag == newar.asset_tag and (newar.rack_name == 'PILE' or newar.rack_name == 'UATdiscard') and re.search("C",curar.rack_name):
				# move.setdefault(curar.asset_tag,[]).append(curar.rack_name)
				# move.setdefault(curar.asset_tag,[]).append(curar.starting_u)
				# move.setdefault(curar.asset_tag,[]).append(newar.rack_name)
				# move.setdefault(curar.asset_tag,[]).append(newar.starting_u)
				# move.setdefault(curar.asset_tag,[]).append(newar.fqdn)
				# move.setdefault(curar.asset_tag,[]).append(curar.serial_number)
				# move.setdefault(curar.asset_tag,[]).append(curar.model_name)
	# print "Asset Tag,FQDN,Old Rack Name,Model Name\n"
	for i in move:
		print ("{},{},{},{}" .format (i,move[i][new_fqdn],move[i][current_rack],move[i][current_model_name]))
 
 
elif s == 'SLCAllRows':
	db = DBobj(dbname3)
	racks = db.all_rack_names();
	for rn in racks:
		current = db.all_assets_rack_audit(rn)
		print ("RACK: {}" .format (rn))
		for i in current:
			curar = asset_record(i)
			# #asset_id,fqdn,rack_name,model_name,serial_number,asset_tag,customer_name,starting_u,manufactuer
			# print "{},{},{},{},{},{}" % (curar.starting_u,curar.asset_tag,curar.fqdn,curar.serial_number,curar.model_name,curar.rack_name)
 
elif s == "fixslc":
	f0 = open("120racks.csv")
	for i in f0:
		srec = slcrecord(i)
		# #print ("{} {} {} {} {}") % (srec.starting_u,srec.model_name,srec.rack_name,srec.serial_number,srec.asset_tag)
		db = DBobj(dbname3)
		rec =  db.update_slc(srec)
 
				

		

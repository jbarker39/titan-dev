import os,sys,string
import mysql.connector
import re
#from ipaddr import *
#import commands removed in 3

states = {}
states["ON"] = 0
states["OFF"] = 1
hostname_Index = 0
manufacturer_Index = 1
product_name_Index = 2
serial_number_Index = 3
ip_Index = 4
version_Index = 5
uuid_Index = 6
wake_Index = 7


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

		
class asset_values:
		#fqdn,model_id,rack_id,serial_number
		def __init__(self,linein):
				#print linein
				self.fqdn = linein[1]
				self.model_id = linein[2]
				self.rack_id = linein[3]
				self.serial_number = linein[4].strip()
				self.warranty_date = linein[5]
				self.cust_id = linein[6]
				
class asset_values_1:
		#serial_number,fqdn,starting_u,asset_tag,model_name,rack_name
		def __init__(self,linein):
				l = linein.split(",")
				self.serial_number = l[0].strip()
				self.fqdn = l[1].strip()
				self.starting_u = l[2].strip()
				self.asset_tag = l[3].strip()
				self.model_name = l[4].strip()
				self.rack_name = l[5].strip()

class asset_values_rowb:
		#starting_u,asset_tag,rack_name
		def __init__(self,linein):
				l = linein.split(",")
				self.starting_u = l[0].strip()
				self.asset_tag = l[1].strip()
				self.rack_name = l[2].strip()

class asset_values_rowbsn:
		#starting_u,serial_number
		def __init__(self,linein):
				l = linein.split(",")
				self.starting_u = l[0].strip()
				self.serial_number = l[1].strip()
				self.rack_name = l[2].strip()
				
class asset_load_values:
		def __init__(self,linein):
				#print linein
				l = linein.split(',')
				#print l
				self.model_name = l[0].strip("'")
				self.asset_tag = l[1].strip("'")
				self.fqdn = l[2].strip("'")
				self.serial_number = l[3].strip("'")
				rn = l[5].strip()
				self.rack_name = rn.rstrip("//")
				
class asset_load_values_slc:
		#model_name,asset_tag,fqdn,serial_number,last_scan,rack_name
		def __init__(self,linein):
				l = linein.split(',')
				self.model_name = l[0].strip()
				self.asset_tag = l[1].strip()
				self.fqdn = l[2].strip()
				self.serial_number = l[3].strip()
				self.last_scan = l[4].strip()           
				self.rack_name = l[5].strip()
				
class rack_load_power:
		#service,receptacle,partner
		def __init__(self,linein):
				l = linein.split(':')
				#print l
				ltmp  = l[0].strip('"')
				self.service = ltmp.strip()
				ltmp = l[1].strip('"')
				self.receptacle = ltmp.strip()
				ltmp = l[2].strip('"')
				self.partner = ltmp.strip()
				ltmp = l[3].strip('"')
				self.rack_name = ltmp.strip()
class newqwest_update:
				#assets.asset_id,fqdn,serial_number,asset_tag,rack_id,model_id,assets.cust_id,warranty_date,starting_u
		def __init__(self,linein):
				self.asset_id = linein[0]
				self.fqdn = linein[1]
				self.serial_number = linein[2]
				self.asset_tag = linein[3]
				self.rack_id = linein[4]
				self.model_id = linein[5]
				self.cust_id = linein[6]
				self.warranty_date = linein[7]
				self.starting_u = linein[8]
#      0             1        2       3           4          5          6
#Serial Number , Asset tag, FQDN, Starting U, Model Name, Rack Name, Customer
class titan_update:
		def __init__(self,linein):
				self.fqdn = linein[2]
				self.serial_number = linein[0]
				self.asset_tag = linein[1]
				self.rack_id = linein[5]
				self.model_id = linein[4]
				self.cust_id = linein[6]
				self.starting_u = linein[3]				
				
class DBobj:
		conn = 0
		cursor = 0
		
		def     __init__(self,dbname):
				self.hostname = dbname[0].strip()
				self.username = dbname[1].strip()
				self.passwd = dbname[2].strip()
				self.usedb = dbname[3].strip()

				try:
						print ("db-1: hostname: {} username: {} password: {} db: {}" .format (self.hostname,self.username,self.passwd,self.usedb))
						self.conn = mysql.connector.connect (host=self.hostname,user=self.username,password=self.passwd,database=self.usedb,auth_plugin='mysql_native_password')
						self.cursor = self.conn.cursor()
				except mysql.connector.Error as e:
						print ("Error {}: {}".format(e.args[0],e.args[1]))
						sys.exit(1)


		def     dump_db(self,table):
				#print table;
				if table == 'assets':
						self.cursor.execute("""SELECT asset_id,fqdn,model_id,rack_id,serial_number,warranty_date,cust_id from assets order by rack_id""")
						t = self.cursor.fetchall()
						if t:
								for i in t:
										asset = asset_values(i)
										if not asset.rack_id:
												rid = 1
										else:
												rid = asset.rack_id
										#print "fqdn: %s model_id: %s rack_id: %s sn: %s" % (asset.fqdn,asset.model_id,rid,asset.serial_number)
										self.cursor.execute("""SELECT model_name,manufacturer from models where model_id = %s""",(asset.model_id))
										model_info = self.cursor.fetchone()
										if model_info:
												mn = model_info[0]
												mfg = model_info[1]
										else:
												mn = "None"
												mfg = "unknown"
												#print asset.fqdn,asset.model_id,mn
										self.cursor.execute("""SELECT rack_name from racks where rack_id = %s""",(rid))
										rack_name = self.cursor.fetchone()
										if rack_name:
												rn = rack_name[0]
										else:
												rn = "None"
										#print "%s%s:" % (asset.fqdn,asset.serial_number)
										if asset.serial_number:
												sn = asset.serial_number
										else:
												sn = "None"
										if asset.cust_id:
												self.cursor.execute("""SELECT customer_name from customers where cust_id = %s""",(asset.cust_id))
												cn = self.cursor.fetchone()
												if cn:
														customer_name = cn[0]
										else:
												customer_name = "TBD"
										print ("{},{},{},{},{},{},{}".format(asset.fqdn,mfg,mn,rn,sn,asset.warranty_date,customer_name))
								
				elif table == 'racks':
						self.cursor.execute("""SELECT racks.rack_name,racks.height_in_u,racks.description,cages.cage_name from racks,cages where racks.cage_id = cages.cage_id""")
				elif table == 'models':
						self.cursor.execute("""SELECT model_id,manufacturer,model_name,height_in_u,description from models""")
				elif table == 'cages':
						self.cursor.execute("""SELECT cage_id,cage_name,facility_id from cages""")
				elif table == 'facilities':
						self.cursor.execute("""SELECT facility_id,short_designation,address1,address2,city,state,zipcode,support_number,support_email from facilities""")
				elif table == 'qwestRacks':
						racknames = ["D098","D099","D100","D102","D103","D104","B098","B099","B100","B101","B102","B103","B104","B105","B106","B107","B108"]
						print ("starting_u,asset_id,fqdn,serial_number,asset_tag,warranty_date,model_name,rack_name")
						for r in racknames:                                             
								self.cursor.execute("""SELECT starting_u,assets.asset_id,fqdn,serial_number,asset_tag,warranty_date,model_name,rack_name \
											from assets,racks,models \
											where \
											assets.rack_id=racks.rack_id and \
											assets.model_id = models.model_id and \
											racks.rack_name like %s order by starting_u DESC""",(r))
								r1 = self.cursor.fetchall()
								for n in r1:
										print ("{},{},{},{},{},{},{},{}" .format (n))
				elif table == 'amx-perf':
						print ("fqdn,serial_number,asset_tag,warranty_date,model_name,rack_name")
						self.cursor.execute("""SELECT fqdn,serial_number,asset_tag,warranty_date,model_name,rack_name \
									from assets,racks,models \
									where \
									assets.rack_id=racks.rack_id and \
									assets.model_id = models.model_id and \
									racks.rack_name like %s and fqdn like %s""",("C%","amx-perf%"))
						r1 = self.cursor.fetchall()
						for n in r1:
								print ("{},{},{},{},{},{}".format(n))
				elif table == 'all-qwest':
						print ("customer_name,starting_u,fqdn,serial_number,asset_tag,warranty_date,model_name,rack_name")
						self.cursor.execute("""SELECT customer_name,starting_u,fqdn,serial_number,asset_tag,warranty_date,model_name,rack_name \
									from assets,racks,models,customers \
									where \
									assets.cust_id=customers.cust_id and \
									assets.rack_id=racks.rack_id and \
									assets.model_id = models.model_id  \
									order by customer_name""")
						r1 = self.cursor.fetchall()
						for n in r1:
								print ("{},{},{},{},{},{},{},{}".format(n))

				else:
						return False            
				return self.cursor.fetchall()

		def     load_db(self,table,filename):
				if table == 'assets':
						f0 = open(filename)
						for l in f0:
								asset = asset_load_values(l)
								if asset.model_name != "VM":
										self.cursor.execute("""SELECT model_id from models where model_name like %s""",(asset.model_name))
										mid = self.cursor.fetchone()
										if not mid:
												use_mid = 0
												print ("model name: {} not found".format(asset.model_name))
										else:
												use_mid = mid[0]
										self.cursor.execute("""SELECT rack_id from racks where rack_name like %s""",(asset.rack_name))
										rid = self.cursor.fetchone()
										if not rid:
												use_rid = 0
												print ("{} rack name: {} not found" .format(asset.fqdn,asset.rack_name))
										else:
												use_rid = rid[0]
										#print asset.fqdn,use_mid,use_rid,asset.serial_number,asset.asset_tag,asset.rack_name,asset.model_name
										
										#
										if use_mid != 0 and use_rid != 0:
												self.cursor.execute("""INSERT into assets (fqdn,rack_id,model_id,serial_number,asset_tag) values ({},{},%s,%s,%s)""",(asset.fqdn,use_rid,use_mid,asset.serial_number,asset.asset_tag))
												statsus = self.conn.commit()
				elif table == 'fixassets':
						f0 = open(filename)
						for l in f0:
								asset = asset_load_values(l)
								self.cursor.execute("""UPDATE assets set asset_tag = %s where serial_number like %s""",(asset.asset_tag,asset.serial_number))
								self.conn.commit()

				elif table == 'assets_rowb':
						f0 = open(filename)
						for l in f0:
								asset = asset_values_rowb(l)
								self.cursor.execute("""UPDATE assets set starting_u = %s where asset_tag like %s""",(asset.starting_u,asset.asset_tag))
								self.conn.commit()
								self.cursor.execute("""SELECT rack_id from racks where rack_name like %s""",(asset.rack_name))
								rid = self.cursor.fetchone()
								if not rid:
										print ("rack name: {} not found".format(asset.rack_name))
								else:
										self.cursor.execute("""UPDATE assets set rack_id = %s where asset_tag like %s""",(rid[0],asset.asset_tag))
										self.conn.commit()

				elif table == 'assets_rowbsn':
						f0 = open(filename)
						for l in f0:
								asset = asset_values_rowbsn(l)
								self.cursor.execute("""UPDATE assets set starting_u = %s where serial_number like %s""",(asset.starting_u,asset.serial_number))
								self.conn.commit()
								self.cursor.execute("""SELECT rack_id from racks where rack_name like %s""",(asset.rack_name))
								rid = self.cursor.fetchone()
								if not rid:
										print ("rack name: {} not found".format (asset.rack_name))
								else:
										self.cursor.execute("""UPDATE assets set rack_id = %s where serial_number like %s""",(rid[0],asset.serial_number))
										self.conn.commit()                                              
						
				elif table == 'assets-slc':
						f0 = open(filename)
						for l in f0:
								asset = asset_load_values_slc(l)
								if asset.model_name != "VM":
										self.cursor.execute("""SELECT model_id from models where model_name like %s""",(asset.model_name))
										mid = self.cursor.fetchone()
										if not mid:
												use_mid = 0
												print ("model name: {} not found" .format( asset.model_name))
										else:
												use_mid = mid[0]
										self.cursor.execute("""SELECT rack_id from racks where rack_name like %s""",(asset.rack_name))
										rid = self.cursor.fetchone()
										if not rid:
												use_rid = 0
												print ("%s rack name: {} not found" .format (asset.fqdn,asset.rack_name))
										else:
												use_rid = rid[0]
										#print asset.fqdn,use_mid,use_rid,asset.serial_number,asset.asset_tag,asset.rack_name,asset.model_name
										
										#
										#if use_mid != 0 and use_rid != 0:
										#       self.cursor.execute("""INSERT into assets (fqdn,rack_id,model_id,serial_number,asset_tag) values (%s,%s,%s,%s,%s)""",(asset.fqdn,use_rid,use_mid,asset.serial_number,asset.asset_tag))
										#       statsus = self.conn.commit()
				elif table == 'assets1':
						f0 = open(filename)
						for l in f0:
								asset = asset_values_1(l)
								self.cursor.execute("""SELECT model_id from models where model_name like %s""",(asset.model_name))
								mid = self.cursor.fetchone()
								if not mid:
										use_mid = 0
										#print l
										print ("model_name: {} not found" .format (asset.model_name))
								else:
										use_mid = mid[0]
								self.cursor.execute("""SELECT rack_id from racks where rack_name like %s""",(asset.rack_name))
								rid = self.cursor.fetchone()
								if not rid:
										use_rid = 0
										print (l)
										print ("rack_name: {} not found" .format (asset.rack_name))
								else:
										use_rid = rid[0]
								self.cursor.execute("""SELECT asset_id,fqdn,serial_number from assets where asset_tag like %s""",(asset.asset_tag))
								arecord = self.cursor.fetchone()
								if arecord:
										taid = arecord[0]
										tfqdn = arecord[1]
										tsn = arecord[2]
										print ("LOOKUP by asset_tag:: asset_id: {} fqdn: {} asset_tag: {} serial_number: {} starting_u: {}" .format (taid,tfqdn,asset.asset_tag,tsn,asset.starting_u))
										#self.cursor.execute("""UPDATE assets set starting_u = %s where asset_id = %s""",(asset.starting_u,taid))
										#self.conn.commit()
										if not tfqdn:
												print ("ERROR: {} is NULL should be {} -- UPDATED".format (tfqdn,asset.fqdn))
												self.cursor.execute("""UPDATE assets set fqdn = %s where asset_id = %s""",(asset.fqdn,taid))
												self.conn.commit()
								else:
										self.cursor.execute("""SELECT asset_id,fqdn,asset_tag from assets where serial_number like %s""",(asset.serial_number))
										arecord = self.cursor.fetchone()
										if arecord:
												taid = arecord[0]
												tfqdn = arecord[1]
												tsn = arecord[2]
												print ("LOOKUP by serial_number:: asset_id: {} fqdn: {} asset_tag: {} serial_number: {} starting_u: {}" .format (taid,tfqdn,asset.asset_tag,tsn,asset.starting_u))
												#self.cursor.execute("""UPDATE assets set starting_u = %s where asset_id = %s""",(asset.starting_u,taid))
												#self.conn.commit()
												if not tfqdn:
														print ("ERROR: {} is NULL should be {} -- UPDATED" .format (tfqdn,asset.fqdn))
														#self.cursor.execute("""UPDATE assets set fqdn = %s where asset_id = %s""",(asset.fqdn,taid))
														#self.conn.commit()
										else:   
												taid = 0
												tfqdn = "NA"
												tsn = "NA"
												print ("asset_tag: {} not found" .format (asset.asset_tag))

						
				elif table == 'rack_power':
						f0 = open(filename)
						for l in f0:
								rack_info = rack_load_power(l)
								#print "%s %s %s %s" % (rack_info.rack_name,rack_info.receptacle,rack_info.partner,rack_info.service)
								self.cursor.execute("""SELECT rack_id from racks where rack_name like %s""",(rack_info.rack_name))
								rid = self.cursor.fetchone()
								if not rid:
										use_rid = 0
										print ("rack name: {} not found" .format (rack_info.rack_name))
								else:
										use_rid = rid[0]
										self.cursor.execute("""UPDATE racks set receptacle = %s where rack_id = %s""",(rack_info.receptacle,use_rid))
										self.cursor.execute("""UPDATE racks set partner = %s where rack_id = %s""",(rack_info.partner,use_rid))
										self.cursor.execute("""UPDATE racks set service = %s where rack_id = %s""",(rack_info.service,use_rid))
										self.conn.commit()

								
				elif table == 'asset_model_id':
						f0 = open(filename)
						for l in f0:
								f = SLCphysical(l)
								self.cursor.execute("""SELECT model_id from models where model_name like %s""",(f.model_name))
								mid = self.cursor.fetchone()
								if mid:
										print ("{},{},{},{}".format(f.fqdn,f.model_name,f.sn,mid))
										self.cursor.execute("""UPDATE assets set model_id = %s where serial_number like %s""",(mid[0],f.sn))
										self.conn.commit()
										
				elif table == 'asset_rack_id':
						f0 = open(filename)
						for l in f0:
								f = SLCphysical(l)
								self.cursor.execute("""SELECT rack_id from racks where rack_name like %s""",(f.rack_name))
								rid = self.cursor.fetchone()
								if rid:
										#pass
										print ("{},{},{},{}".format(f.rack_name,f.fqdn,f.sn,rid))
										self.cursor.execute("""UPDATE assets set rack_id = %s where serial_number like %s""",(rid[0],f.sn))
										self.conn.commit()
								else:
										print ("{} {} not found" .format (f.fqdn,f.rack_name))
										
				elif table == 'asset_warranty':
						f0 = open(filename)
						print (filename)
						for line in f0:
								f = warranty(line)
								#print "serial number: %s " % (f.serial_number)
								self.cursor.execute("""SELECT assets.fqdn,assets.warranty_date,models.model_name,racks.rack_name from assets,models,racks where assets.serial_number like %s \
													and models.model_id = assets.model_id and racks.rack_id = assets.rack_id""",(f.serial_number))
								r = self.cursor.fetchone()
								if r:
										#print r
										print ("{},{},{},{},{}".format (f.serial_number,r[1],r[3],r[2],r[0]))
								#else:
								#       print "serial number: %s not found" % (f.serial_number)
								#self.cursor.execute("""UPDATE assets set warranty_date = %s where serial_number like %s""",(f.warranty,f.serial_number))
								#result = self.conn.commit()
								#print "serial number: %s result: %s" % (f.serial_number,result)
						return r
				
				elif table == 'racks':
						f0 = open(filename)
						for line in f0:
								r = rack_values(line)
								#print r.rack_name,r.height_in_u,r.description,r.cage_name
								self.cursor.execute("""SELECT cage_id from cages where cage_name like %s""",(r.cage_name))
								t = self.cursor.fetchone()
								if t:
										self.cursor.execute("""REPLACE into racks (rack_name,height_in_u,description,cage_id) VALUES (%s,%s,%s,%s)""",(r.rack_name,r.height_in_u,r.description,t[0]))
										status = self.conn.commit()
								else:
										status = False
								
				elif table == 'models':
						f0 = open(filename)
						for line in f0:
								r = model_values(line)
								#print r.mfg,r.model_name,r.height_in_u,r.description
								self.cursor.execute("""REPLACE into models (manufacturer,model_name,height_in_u,description) VALUES (%s,%s,%s,%s)""",(r.mfg,r.model_name,r.height_in_u,r.description))
								self.conn.commit()
								
				elif table == 'hostclasses':
						pass
				elif table == 'networks':
						f0 = open(filename)
						for line in f0:
								r = network_values(line)
								#print r.network,r.netmask,r.gateway
								self.cursor.execute("""REPLACE into networks (network,netmask,gateway) VALUES (%s,%s,%s)""",(r.network,r.netmask,r.gateway))
								self.conn.commit()
								
				elif table == 'cages':
						f0 = open(filename)
						for line in f0:
								r = cages_values(line)
								print (r.cn)
								self.cursor.execute("""SELECT facility_id from facilities where short_designation like %s""",(r.cn))
								t = self.cursor.fetchone()
								if t:
										print ("facility_id: {}" .format(t[0]))
										self.cursor.execute("""REPLACE into cages (cage_name,facility_id) VALUES (%s,%s)""",(r.cn,t[0]))
										status = self.conn.commit()
								else:
										status = False
						
				elif table == 'facilities':
						f0 = open(filename)
						for line in f0:
								r = facilities_values(line)
								self.cursor.execute("""REPLACE into facilities (short_designation,address1,address2,city,state,zipcode,support_number,support_email) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",\
													 (r.sd,r.a1,r.a2,r.c,r.s,r.z,r.n,r.e))
								status = self.conn.commit()
				else:
						status = False


		def all_assets(self):
			#    0      1       2         3           4            5            6          7       8             9      10
			#asset_id,fqdn,rack_name,model_name,serial_number,asset_tag,customer_name,starting_u,manufacturer,decom,warranty_date
			self.cursor.execute("""select asset_id,fqdn,rack_name,model_name,serial_number,asset_tag,customer_name,starting_u,manufacturer,decom,warranty_date \
										from assets,racks,models,customers where \
										assets.rack_id=racks.rack_id and \
										assets.model_id = models.model_id and \
										assets.cust_id = customers.cust_id \
										order by racks.rack_name""")
			c = self.cursor.fetchall()
			return c

		def full_assets(self):
			#    0      1       2         3           4            5            6          7       8              9           10
			#asset_id,fqdn,rack_name,model_name,serial_number,asset_tag,customer_name,starting_u,manufacturer,warranty_date,decom
			self.cursor.execute("""select asset_id,fqdn,rack_name,model_name,serial_number,asset_tag,customer_name,starting_u,manufacturer,warranty_date,decom \
										from assets,racks,models,customers where \
										assets.rack_id=racks.rack_id and \
										assets.model_id = models.model_id and \
										assets.cust_id = customers.cust_id \
										order by racks.rack_name""")
			c = self.cursor.fetchall()
			return c

			#select asset_id,fqdn,rack_name,model_name,asset_tag,serial_number,decom,warranty_date from assets,models,racks where assets.rack_id=racks.rack_id and 
			#assets.model_id=models.model_id  and models.manufacturer like "Brocade";
		def get_fc_switches(self):
			self.cursor.execute("""SELECT fqdn,rack_name,model_name,serial_number from assets,models,racks where \
				assets.rack_id=racks.rack_id and assets.model_id=models.model_id  and \
				models.manufacturer like 'Brocade'""")
			c = self.cursor.fetchall()
			return c

		def all_starting_u(self):
				self.cursor.execute("""SELECT serial_number,starting_u from assets order by starting_u desc""")
				return self.cursor.fetchall()

		def update_starting_u(self,sn,su):
				self.cursor.execute("""UPDATE assets set starting_u = %s where serial_number like %s""",(su,sn))
				self.conn.commit()
				

		def all_rack_names(self):
				self.cursor.execute("""SELECT rack_name,rack_id from racks order by rack_name""")
				return self.cursor.fetchall()

		def all_customer_names(self):
				self.cursor.execute("""SELECT customer_name,cust_id from customers order by customer_name""")
				return self.cursor.fetchall()


		def     all_assets_rack_audit(self,rn):
				#    0      1       2         3           4            5            6          7       8
				#asset_id,fqdn,rack_name,model_name,serial_number,asset_tag,customer_name,starting_u,manufacturer
				self.cursor.execute("""select asset_id,fqdn,rack_name,model_name,serial_number,asset_tag,customer_name,starting_u,manufacturer \
										from assets,racks,models,customers where \
										assets.rack_id=racks.rack_id and \
										assets.model_id = models.model_id and \
										assets.cust_id = customers.cust_id and \
										rack_name like %s \
										order by starting_u desc""",(rn))
				c = self.cursor.fetchall()
				return c


		def     return_all_assets(self,rn):
				self.cursor.execute("""select assets.asset_id,fqdn,serial_number,asset_tag,assets.rack_id,assets.model_id, \
									assets.cust_id,warranty_date,starting_u \
									from assets,racks,models where racks.rack_id=assets.rack_id and \
									models.model_id = assets.model_id and rack_name like %s \
									order by starting_u""",(rn))
				c = self.cursor.fetchall()
				return c
		
		def update_slc(self,rec):
				#rec = slcrecord(line)
				print (rec.asset_tag,rec.model_name,rec.starting_u)
				if not rec.asset_tag:
						print ("No asset tag")
						return False
				self.cursor.execute("""SELECT rack_id from racks where rack_name like %s""",(rec.rack_name))
				rid = self.cursor.fetchone()
				if rid:
						self.cursor.execute("""SELECT model_id from models where model_name like %s""",(rec.model_name))
						mid = self.cursor.fetchone()
						if not mid:
								print ("model name: {} not found".format (rec.model_name))
								return False
						self.cursor.execute("""SELECT asset_id from assets where asset_tag like %s""",(rec.asset_tag))
						aid = self.cursor.fetchone()
						if aid:
								#print rid,mid,aid
								#print "Updating asset id: %s with Rack Name: %s and starting_u %s rid: %s" % (rec.asset_tag,rec.rack_name,rec.starting_u,rid)
								self.cursor.execute("""UPDATE assets set rack_id = %s,model_id = %s,starting_u=%s where asset_id like %s""", \
										(rid[0],mid[0],rec.starting_u,aid[0]))
								self.conn.commit()
						else:
								#print rid,mid
								#print "Inserting asset tag: %s,%s,%s,%s " % (rec.asset_tag,rec.starting_u,rid,mid)
								self.cursor.execute("""INSERT into assets (asset_tag,serial_number,starting_u,rack_id,model_id) \
										VALUES (%s,%s,%s,%s,%s)""", \
										(rec.asset_tag,rec.serial_number,rec.starting_u,rid[0],mid[0]))
								self.conn.commit()
				else:
						print ("Rack Name: {} not found" .format (rec.rack_name))
						return False
				return True
		
		def print_qwest(self):
			self.cursor.execute("""SELECT starting_u,fqdn,serial_number,asset_tag,model_name,warranty_date,rack_name,customer_name from \
					assets,racks,models,customers where \
					assets.rack_id=racks.rack_id and \
					assets.model_id=models.model_id and \
					assets.cust_id=customers.cust_id \
					order by rack_name""")
			return self.cursor.fetchall()


		def update_newqwest(self,line):
			#print line
			newupdate = titan_update(line)
			print (\
									newupdate.fqdn, \
									newupdate.serial_number, \
									newupdate.asset_tag, \
									newupdate.rack_id, \
									newupdate.model_id, \
									newupdate.cust_id, \
									newupdate.starting_u)
									
			if self.cursor.execute("""insert into assets \
														   (fqdn,serial_number,asset_tag,rack_id,model_id,cust_id,starting_u) \
														   values \
														   (%s,%s,%s,%s,%s,%s,%s)""", \
								(newupdate.fqdn,\
																			 newupdate.serial_number,\
																			 newupdate.asset_tag, \
																			 newupdate.rack_id[0], \
																			 newupdate.model_id[0],\
																			 newupdate.cust_id[0], \
																			newupdate.starting_u)):
					self.conn.commit()

		def update_su_newqwest(self,asset_tag,su):
			print (asset_tag,su)
			if self.cursor.execute("""UPDATE assets set starting_u = %s where asset_tag like %s""",(su,asset_tag)):
					self.conn.commit()
			else:
					print ("asset_tag: {} not found" .format (asset_tag))
						
#assets.asset_id,fqdn,serial_number,asset_tag,rack_id,model_id,assets.cust_id,warranty_date,starting_u
#Serial Number , Asset tag, FQDN, Starting U, Model Name, Rack Name, Customer
#assets.asset_id,fqdn,serial_number,asset_tag,rack_id,model_id,assets.cust_id,warranty_date,starting_u
		def     insert_newqwest(self,line):
				nup = newqwest_update(line)
				#print nup.fqdn,nup.asset_tag,nup.serial_number,nup.warranty_date,nup.starting_u
				if self.cursor.execute("""update assets \
                                                set fqdn=%s,serial_number=%s,warranty_date=%s,starting_u=%s,rack_id=%s where asset_tag like %s""", \
						(nup.fqdn,nup.serial_number,nup.warranty_date,nup.starting_u,"26",nup.asset_tag)):
						#(nup.fqdn,nup.asset_tag,nup.serial_number,nup.warranty_date,nup.starting_u,"45"))
						self.conn.commit()

		def     return_sn_warranty(self):
				self.cursor.execute("""SELECT asset_id,serial_number,warranty_date from assets""")
				return self.cursor.fetchall()
				
		def     update_warranty(self,sn,wd):
				if self.cursor.execute("""update assets set warranty_date = %s where serial_number like %s""",(wd,sn)):
						self.conn.commit()

		def     update_warranty_sold(self,at):
				if self.cursor.execute("""update assets set warranty_date = %s where asset_tag like %s""",("SOLD",at)):
						self.conn.commit()
				
		
		def getHostname_For_SerialNumber(self,sn):
				self.cursor.execute("""select fqdn from assets where serial_number like %s""",(sn,))
				c = self.cursor.fetchall()
				if c:
						#print(c)
						return c[0]
				else:
						return False

		def getAsset_id_For_SerialNumber(self,sn):
				self.cursor.execute("""select asset_id from assets where serial_number like %s""",(sn,))
				c = self.cursor.fetchall()
				if c:
						return c
				else:
						return False
				
		def delete_asset_by_asset_id(self,aid):
				self.cursor.execute("""DELETE from assets where asset_id = %s""",(aid))
				self.conn.commit()
		
		def	update_fqdn_by_asset_tag(self,at,fqdn):
				self.cursor.execute("""UPDATE assets set fqdn=%s where asset_tag like %s""",(fqdn,at))
				self.conn.commit()

		
		def get_fqdn(self,asset_id):
				self.cursor.execute("""SELECT fqdn from assets where asset_id = %s""",asset_id)
				c = self.cursor.fetchone()
				return c
		
		def     get_aid(self,fqdn):
				print (fqdn)
				self.cursor.execute("""SELECT asset_id from assets where fqdn like %s""",fqdn)
				c = self.cursor.fetchone()
				return c
		
				
		def     get_by_racks(self):
			#    0         1          2        3      4             5
			#starting_u,rack_name,model_name,fqdn,serial_number,customer_name
				self.cursor.execute("""SELECT starting_u,rack_name,model_name,fqdn,serial_number,customer_name from \
									assets,racks,models,customers where \
									racks.rack_id = assets.rack_id and \
									models.model_id = assets.model_id and \
									customers.cust_id = assets.cust_id order by rack_name""")
				c = self.cursor.fetchall()
				return c
		
		
		def get_assets_by_cust(self):
				self.cursor.execute("""SELECT customer_name,fqdn from assets,customers where  customers.cust_id = assets.cust_id""")
				results = self.cursor.fetchall()
				return results
			
		def get_models_from_db(self):
			self.cursor.execute("""SELECT model_id,model_name,manufacturer,height_in_u,description from models""")
			results = self.cursor.fetchall()
			return results
			
		def insert_model(self,m):
			self.cursor.execute("""INSERT into models (model_name,manufacturer,height_in_u,description) values (%s,%s,%s,%s)""",(m[0],m[1],m[2],m[3]))
			self.conn.commit()
			return
			

		def get_asset_by_asset_tag_v1(self,at):
				#print at
				self.cursor.execute("""SELECT asset_id from assets where  asset_tag like %s""",(at))
				result = self.cursor.fetchone()
				if result: return result
				return False
				
		def get_asset_by_asset_tag_v2(self,at):
				#print at
				self.cursor.execute("""SELECT asset_id from assets where  asset_tag like %s""",(at))
				result = self.cursor.fetchone()
				if result: return result
				return False
		
		def	update_from_update816(self,linein):
			#    0         1        2        3            4            5        6             7
			#Customer, Location, System, Asset Tag, Serial Number, Host name, Status, Decommisson Date
			#print "%s" % linein[2]
			
			self.cursor.execute("""Select model_id from models where model_name like %s""",(linein[2]))
			model_id = self.cursor.fetchone()
			self.cursor.execute("""SELECT rack_id from racks where rack_name like %s""",(linein[1]))
			rack_id = self.cursor.fetchone()
			self.cursor.execute("""INSERT into assets (fqdn,model_id,rack_id,asset_tag,serial_number,decom) VALUES (%s,%s,%s,%s,%s,%s)""",(linein[5],model_id[0],rack_id[0],linein[3],linein[4],linein[7]))
			self.conn.commit()
			
		def	update_from_ARMupdate(self,linein):
			#    0         1
			#Model_name, Asset Tag
			#print "%s" % linein[2]
			
			self.cursor.execute("""Select model_id from models where model_name like %s""",(linein[0]))
			model_id = self.cursor.fetchone()
			if model_id:
				self.cursor.execute("""INSERT into assets (model_id,asset_tag,decom) VALUES (%s,%s,%s)""",(model_id[0],linein[1].strip(),"8/15/2015"))
				self.conn.commit()
				print ("model_id {} model_name {} asset_tag {}" .format (model_id[0],linein[0],linein[1].strip()))
			else: print ("model_name: {} not found" .format (linein[0]))
			#
		def decom_report(self):
			self.cursor.execute("""SELECT fqdn,asset_tag,serial_number,model_name,rack_name,decom,warranty_date,vcpu,ramGB,CPU from assets,racks,models where \
			assets.rack_id=racks.rack_id and assets.model_id=models.model_id and decom not like %s and decom not like %s order by fqdn""",("in service","available"))
			return self.cursor.fetchall()
			
			
			#
		def	qham2_update_rackable(self,sn,at): #get information from qahm2
			#print "sn: %s" % (sn)
			self.cursor.execute("""SELECT asset_id from assets where assets.serial_number like %s""",(sn))
			r = self.cursor.fetchone()
			if r:
				self.cursor.execute("""Update assets set asset_tag=%s, decom = %s where asset_id = %s""",(at,"2012",r[0]))
				self.conn.commit()
				print ("asset_id: {} updated with asset_tag: {} and decom: {}" .format (r[0],at,"2012"))

		def	updateRackable(self,line): #get information from qahm2
			l = line.split(",")
			sn = l[0].strip()
			at = l[1].strip()
			mn = l[2].strip()
			#print "sn: %s" % (sn)
			self.cursor.execute("""SELECT asset_id,model_id from assets where assets.serial_number like %s""",(sn))
			assetInfo = self.cursor.fetchone()
			if assetInfo:
				print ("asset_id: {}" .format (assetInfo[1]))
				#self.cursor.execute("""SELECT model_name from models where model_id = %s""",(assetInfo[1]))
				#model_name = self.cursor.fetchone()
				#self.cursor.execute("""SELECT rack_name from racks where rack_id = %s""",(assetInfo[2]))
				#rack_name = self.cursor.fetchone()
				#return assetInfo, model_name[0], rack_name[0]
				return assetInfo
			else:
				self.cursor.execute("""SELECT model_id from models where model_name like %s """,(mn))
				m = self.cursor.fetchone()
				print (m)
				fqdn = "decommissioned 2010"
				#print "inserting recoed with FQDN: %s Asset Tag: %s SN: %s model_id: %s model_name: %s" % (fqdn,at,sn,m[0],mn)
				self.cursor.execute("""INSERT into assets (fqdn,asset_tag,serial_number,model_id,rack_id,decom) values (%s,%s,%s,%s,%s,%s)""", \
								(fqdn,at,sn,m[0],"252","2010"))
				self.conn.commit()
		
		def	qham2_newslc_part2(self,line): #update the information in newslc
			#     0          1         2      3       4          5      6
			#asset_tag,serial_number,fqdn,model_id,rack_id,starting_u,decom
			self.cursor.execute("""SELECT asset_id from assets where assets.asset_tag like %s""",(line[0]))
			r = self.cursor.fetchone()
			if r:
				print ("asset_d: {} line {} {} {} {} {} {} {}" .format (r[0],line[0],line[1],line[2],line[3], line[4],line[5],line[6]))
			else:
				print ("asset_tag {} not found" .format (line[0]))
		
		def check_inv(self,sn):
			self.cursor.execute("""SELECT decom from assets where serial_number like %s""",(sn))
			m1 = self.cursor.fetchone()
			#print m1
			return m1
				
		
	
		
		def update_decom(self,at,dcom):
			self.cursor.execute("""UPDATE assets set decom = %s where asset_tag like %s""",(dcom,at))
			self.conn.commit()
			
		def get_rack_id_from_rack_name(self,rack_name):
			self.cursor.execute("""SELECT rack_id from racks where rack_name like %s """,(rack_name,))
			return self.cursor.fetchone()
			
		def get_model_id_from_model_name(self,model_name):
			self.cursor.execute("""SELECT model_id from models where model_name like %s """,(model_name))
			r = self.cursor.fetchone()
			if r: return r
			return (48,)
		
		def get_cust_id_from_customer_name(self,customer_name):
				self.cursor.execute("""SELECT cust_id from customers where customer_name like %s """,(customer_name))
				return self.cursor.fetchone()
		
		def     insert_titan(self,line):
						nup = newqwest_update(line)
						#print nup.fqdn,nup.asset_tag,nup.serial_number,nup.warranty_date,nup.starting_u
						if self.cursor.execute("""update assets \
											   set fqdn=%s,serial_number=%s,warranty_date=%s,starting_u=%s,rack_id=%s where asset_tag like %s""", \
											   (nup.fqdn,nup.serial_number,nup.warranty_date,nup.starting_u,"26",nup.asset_tag)):
											   #(nup.fqdn,nup.asset_tag,nup.serial_number,nup.warranty_date,nup.starting_u,"45"))
								self.conn.commit()
				
		def insert_asset(self,sn,at,model ):
				print (sn,at,model)
				if model == "M1000e":
					self.cursor.execute("""INSERT into assets(model_id,serial_number,asset_tag) values("159",%s,%s)""",(sn,at))
				else:
					self.cursor.execute("""INSERT into assets(model_id,serial_number,asset_tag) values("144",%s,%s)""",(sn,at))
				self.conn.commit()

		def update_rack_id(self,at,rack_name):
			#print "asset_tag: %s rack_name: %s" % (at,rack_name)
			self.cursor.execute("""SELECT rack_id from racks where rack_name like %s """,(rack_name))
			rack_id = self.cursor.fetchone()
			if rack_id:
				self.cursor.execute("""UPDATE assets set rack_id = %s where assets.asset_tag like %s""",(rack_id[0],at))
				self.conn.commit()
				print ("Updated rack_id {} for rack_name {} at asset_tag {}" .format (rack_id[0],rack_name,at))
		def update_asset_id(self,oaid,aid):
				self.cursor.execute ("""UPDATE assets set asset_id = %s where asset_id = %s""",(oaid,aid))
				self.conn.commit()  
		
		
		def get_ALL_assets(self):
				self.cursor.execute("""SELECT asset_id,fqdn,model_id,rack_id,cust_id,serial_number,starting_u,warranty_date,asset_tag,os_version,decom,hyperthreadingON from assets where 1""")
				c = self.cursor.fetchall()
				return c

		def get_au_assets(self):
				self.cursor.execute("""SELECT fqdn,serial_number,asset_tag,decom,warranty_date from assets where rack_id = 26 or rack_id = 27 order by model_id""")
				return self.cursor.fetchall()
		
		def Feb_2021_update(self,sn):
				#print("{}".format(sn))
				self.cursor.execute("""UPDATE assets set warranty_date = '03/31/2022' where serial_number like %s""",(sn,))
				self.conn.commit()
				#print("updated warranty_date to 03/21/2022 where serial_number like {}".format(sn))
		
		def	Feb_2021_confirm(self,sn):
				self.cursor.execute("""SELECT warranty_date from assets where serial_number like %s""",(sn,))
				c = self.cursor.fetchone()
				print("warranty date {} for sn {}".format(c,sn))

		def splitable(self,linein,sep):
				p = re.compile("\t")
				line = p.sub(" ",linein)
				p = re.compile("   ")
				k = p.findall(line)
				i = len(k)
				while i > 0:
						l1 = p.sub("  ",line)
						k = p.findall(l1)
						i = len(k)
						line = l1
				p = re.compile("  ")
				k = p.findall(line)
				i = len(k)
				while i > 0:
						l1 = p.sub(" ",line)
						k = p.findall(l1)
						i = len(k)
						line = l1
				p = re.compile(" ")
				return p.sub(sep,line).strip()
		
		def parsezonefile(self,file):
				fo = []
				f1 = open(file)
				for i in f1:
						if not re.search(";",i):
								a = splitable(i,"?").split("?")
								if len(a) > 2:
										fo.append(a)
				return fo
		
		def parseDNS(self,file):
				fo = []
				f1 = open(file)
				for i in f1:
						if re.match("^@",i):
								fo.append(i)
						elif re.match("^;",i):
								fo.append(i)
						elif re.match("^$",i):
								fo.append(i)
						elif re.search("IN",i):
								a = splitable(i,"?").split("?")
								fo.append(a)
						else:
								fo.append(i)
				return fo
		
		
		def calcnetwork(self,ip,mask):
				i1 = ip.split(".")
				m1 = mask.split(".")
				l = len(i1)
				r = []
				k = 0
				while k < 4:
						o = int(i1[k]) & int(m1[k])
						r.append(o)
						k = k + 1
				n = str(r[0]) + "." + str(r[1]) + "." + str(r[2]) + "." + str(r[3])  
				return n
		
		def calcmask(self,mask):
				sm = {}
				sm['255.255.255.128'] = '/25'
				sm['255.255.255.0'] = '/24'
				sm['255.255.254.0'] = '/23'
				sm['255.255.252.0'] = '/22'
				sm['255.255.248.0'] = '/21'
				sm['255.255.240.0'] = '/20'
				sm['255.255.224.0'] = '/19'
		
				sn = {}
				sn['/25'] = '255.255.255.128'
				sn['/24'] = '255.255.255.0'
				sn['/23'] = '255.255.254.0'
				sn['/22'] = '255.255.252.0'
				sn['/21'] = '255.255.248.0'
				sn['/20'] = '255.255.240.0'
				sn['/19'] = '255.255.224.0'
				if mask in sm:
						return sm[mask]
				elif mask in sn:
						return sn[mask]
				else:
						return False
		
		
		def calcnetworkName(self,ip,mask):
				ip1 = str(ip)
				mask1 = str(mask)
				i1 = ip1.split(".")
				m1 = mask1.split(".")
				l = len(i1)
				r = []
				k = 0
				while k < 4:
						o = int(i1[k]) & int(m1[k])
						r.append(o)
						k = k + 1
				n = str(r[1]) + "-" + str(r[2])  
				return n
		
		

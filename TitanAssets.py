#!/usr/bin/env python
import os,sys
import string
import mysql.connector
import re
import time
from sfrDBobj import *

passed = ""
dbname = "util-3.endofdays-2012.dev","root",passwd,"titan"
#Starting U Asset Tag Model Name Rack Name Serial Number
srec = slcrecord('"3","AT","Model","Rack","SN"')
print (srec.asset_tag)
# db = DBobj(dbname)
# r=db.print_qwest()
# for i in r:
#     print (i)
#r = db.all_rack_names()
#r = db.all_assets()
#for i in r:
#    print (i)
#f = open ("titan_M610_blades.csv")
#line = []
#for l in f:
#    l0 = l.strip()
#    l1 = l0.split(",")
#    db.insert_asset(l1[0],l1[1],l1[2])
# new line
# new line 2
#for i in db.get_au_assets():
#    if i[2]:
#        print "%s,%s,%s,%s,%s" % i
#    else:
#        print "%s,%s,%s,%s,%s,Pre-PMI" % i
#f = open("ML1colinv.csv")

#      0             1        2       3           4          5          6
#Serial Number , Asset tag, FQDN, Starting U, Model Name, Rack Name, Customer

#assets.asset_id,fqdn,serial_number,asset_tag,rack_id,model_id,assets.cust_id,warranty_date,starting_u
#lineout = ["","","","","","",""]
#for line in f:
#    line_values = line.split(',')
#    lineout[0:4] = line_values[0:4]
#    lineout[5] = db.get_rack_id_from_rack_name(line_values[5].strip())
#    lineout[4] = db.get_model_id_from_model_name(line_values[4].strip())
#    lineout[6] = db.get_cust_id_from_customer_name(line_values[6].strip())
#    print lineout
#    db.update_newqwest(lineout)
#    print line_values
#    print ("%s %s %s %s %s %s %s") % (line_values[1],line_values[5],db.get_rack_id_from_rack_name(line_values[5].strip()), \
#                                line_values[4],db.get_model_id_from_model_name(line_values[4].strip()), \
#                                line_values[6],db.get_cust_id_from_customer_name(line_values[6].strip()))


#
# rn = ("BW02","BW03","BW04","BW05","BW06","BW07","BW08","BW09","BW10","BW11","BW12","BW13","BW14","BW17","CC02","CC03","CC04","CC05","CC06","CC07","CC08","Floor",)
# for r in rn:
#     print (r,db.get_rack_id_from_rack_name(r))

# models = db.get_models_from_db()    # get models
# racks = db.all_rack_names()         # get racks
# for i in models:
#     print (i)
# for i in racks:
#     print (i)
#f = open("ML1colinv.csv")
#fr = open("TitanList.csv",'w')
#for i in f:
#    i1 = i.split(',')
#    print i1

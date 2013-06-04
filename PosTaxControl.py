#-------------------------------------------------------------------------------
# Name:        税票批量处理
# Purpose:
#
# Author:      wgyg535@sohu.com
#
# Created:     28/05/2013
# Copyright:   (c) wgyg535@sohu.com 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python
#coding=utf-8
import cx_Oracle
from ctypes import *
import os
import sys
import time,datetime
import re
import logging
from xml.dom import minidom, Node
import codecs

#reload(sys)
#sys.setdefaultencoding('utf-8')


logging.basicConfig(filename=os.getcwd()+'/PosTaxControl.log', \
                     format='%(asctime)s %(levelname)s: %(message)s', \
                     datefmt='%m/%d/%Y %H:%M:%S', level=logging.INFO)
#定义数据库名密码
userid='xxxx'
passwd='x'
tns='xxx.xxx.xx.xx:1521/xxxx'
try:
   CON =cx_Oracle.connect (userid+'/'+passwd+'@'+tns,threaded=True)
   logging.info('Lmgs server connect successful')
except cx_Oracle.DatabaseError,msg:
   logging.error('Lmgs server connect error,please check network!!'+'\n')
   logging.error(str(msg)+'\n')
   sys.exit(-1)
Qrycursor = CON.cursor()
UptCursor = CON.cursor()

def PosTaxtoXml(sale_dy,str_cd,pos_no,trd_no):
    PosHeadSql="select distinct sale_dy,str_cd,pos_no,trd_no,sale_emp_no from sale_prod  where sale_dy='%s' and str_cd='%s' \
   and pos_no='%s' and trd_no='%s' " % (sale_dy,str_cd,pos_no,trd_no)

    Qrycursor.execute(PosHeadSql)
    logging.info(PosHeadSql+'\n')
    row = Qrycursor.fetchone()
    if row==None:
        sys.exit(-2)

    doc = minidom.Document()
    #create inv
    Inv = doc.createElement('Inv')
    doc.appendChild(Inv)
    #create H
    name = doc.createElement('H')
    Inv.appendChild(name)

    BH= doc.createElement('BH')
    BH.appendChild(doc.createTextNode(str(row[2])))
    name.appendChild(BH)

    trdno = doc.createElement('LS')
    name.appendChild(trdno)
    trdno.appendChild(doc.createTextNode(str(row[3])))

    custname = doc.createElement('MC')
    name.appendChild(custname)
    custname.appendChild(doc.createTextNode(""))

    cashno = doc.createElement('SN')
    name.appendChild(cashno)
    cashno.appendChild(doc.createTextNode(str(row[4])))

    #pay list:

    poslist = doc.createElement('C')
    Inv.appendChild(poslist)

    PosListSql="select b.prod_nm,b.prod_std,'EA' unit,decode(b.prod_pat_fg||b.wgcnt_fg,'02',1,a.sale_qty) sale_qty,\
decode(b.prod_pat_fg||b.wgcnt_fg,'02',a.sale_amt,a.curr_sale_prc) curr_sale_prc,\
decode(a.cancel_fg,2,-1,3,-1,1)*a.sale_amt sale_amt,decode(a.cancel_fg,2,-1,3,-1,1)*a.dc_amt dc_amt \
  from sale_prod a,str_prod b where a.str_cd=b.str_cd and a.prod_cd=b.prod_cd  and a.cancel_fg<>1 and a.sel_cancel_fg=0  \
and a.sale_dy='%s' and a.str_cd='%s' and pos_no='%s' and trd_no='%s' \
union all select '商品折扣金额',' ','',1,null,sum(-1*dc_amt),0 from sale_pay where sale_dy='%s' and str_cd='%s' \
and pos_no='%s' and trd_no='%s' having sum(-1*dc_amt)<>0 \
union all select '非现金付款','','',1,null,sum(decode(cancel_fg,2,-1,3,-1,1)*-1*sale_amt),0 from sale_pay where \
sale_dy='%s' and str_cd='%s' and pos_no='%s' and trd_no='%s' and pay_way_fg in ('04','08','22','23','52')\
 having sum(decode(cancel_fg,2,-1,3,-1,1)*-1*sale_amt)<>0" % \
(sale_dy,str_cd,pos_no,trd_no,sale_dy,str_cd,pos_no,trd_no,sale_dy,str_cd,pos_no,trd_no)
    Qrycursor.execute(PosListSql)
    logging.info(PosListSql.decode('utf-8').encode('gbk'))
    for rec in Qrycursor.fetchall():
            #na=rec[0].decode('utf-8')
            #print na
            plist = doc.createElement('MX')
            poslist.appendChild(plist)

            name= doc.createElement('MC')
            name.appendChild(doc.createTextNode(str(rec[0].decode('utf-8').encode('gbk'))[0:40]))
            #name.appendChild(doc.createTextNode(unicode(na,'gbk')))
            plist.appendChild(name)

            guige= doc.createElement('GG')
            guige.appendChild(doc.createTextNode(str(rec[1])))
            plist.appendChild(guige)

            dangwei= doc.createElement('DW')
            dangwei.appendChild(doc.createTextNode(""))
            plist.appendChild(dangwei)

            shuliang = doc.createElement('SL')
            shuliang.appendChild(doc.createTextNode(str(rec[3])))
            plist.appendChild(shuliang)

            dangjia = doc.createElement('DJ')
            dangjia.appendChild(doc.createTextNode(str(rec[4])))
            plist.appendChild(dangjia)

            jinger = doc.createElement('JE')
            jinger.appendChild(doc.createTextNode(str(rec[5])))
            plist.appendChild(jinger)

    result = ('<Cmd>1</Cmd>').strip('\n')+doc.toxml().split('<?xml version="1.0" ?>')[1]
    print result
    #str1 = doc.toxml().split('<?xml version="1.0" ?>')[1]
    logging.info(result +'\n')
    return result



#取税控码
def get_taxno(sInXml):
    dll=cdll.LoadLibrary('./libposapi_x64.so')
    perform_function=dll.PosTaxControlService
    #定义输入参数
    perform_function.argtypes = [c_int, c_char_p,c_int,c_char_p]
    #定义返回参数
    perform_function.restype = c_int
    nInLen = len(sInXml)
    #初始化字符串长度
    sOutXml =create_string_buffer(4096)
    #logging.info(sInXml.decode('utf-8').encode('gbk'))
    logging.info(sInXml)
    logging.info(sOutXml.value)
    result = re.findall('<PH>(.*?)</PH>',sOutXml.value)
    if retval == 0 :
        return result[0]
        logging.info(result[0]+'\n')
    else:
        fatal_error('get_Taxno_error')
        return '000000000000'

def deltaxno(sInXml):
    dll=cdll.LoadLibrary('./libposapi_x64.so')
    perform_function=dll.PosTaxControlService
    #定义输入参数
    perform_function.argtypes = [c_int, c_char_p,c_int,c_char_p]
    #定义返回参数
    perform_function.restype = c_int
    nInLen = len(sInXml)
    #初始化字符串长度
    sOutXml =create_string_buffer(4096)
    #logging.info(sInXml.decode('utf-8').encode('gbk'))
    logging.info(sInXml)
    #print sInXml.decode('utf-8').encode('gbk')
    retval = perform_function(nInLen, sInXml,4096,sOutXml)
    logging.info(sOutXml.value)
    if retval == 0 :
        logging.info('作废发票成功\n'.decode('utf-8').encode('gbk'))
    else:
        fatal_error('作废发票失败\n'.decode('utf-8').encode('gbk'))


def delPosTaxxml(taxno):
    delxml=('<Cmd>3</Cmd><PH>%s</PH>' % taxno)
    print delxml
    return delxml

def qryLastPosTaxxml(posno):
    qrylastxml=('<Cmd>2</Cmd><Inv><BH>%s</BH></Inv>' % posno)
    print qrylastxml
    return qrylastxml

def qrycurrPosTaxxml(taxno):
    qrycurrxml=('<Cmd>4</Cmd><PH>%s</PH>' % taxno)
    print qrycurrxml
    return qrycurrxml

def posdatatoxml(sale_dy,str_cd,pos_no,trd_no):
    pass

def taxno_update(tax_no,sale_dy,str_cd,pos_no,trd_no):
    tax_code=tax_no
    Qrycursor.execute("select sale_dy,str_cd,pos_no,trd_no from xwy_sale_tax_bill where offline_fg=1 and tax_code is null")
    for rec in Qrycursor.fetchall():
        #print rec
        sql = "update xwy_sale_tax_bill set tax_code=%s where sale_dy=%s and str_cd=%s and pos_no=%s and trd_no=%s" % (tax_code, rec[0], rec[1], rec[2],rec[3])
        logging.info(sql)
        try:
            UptCursor.execute(sql)
        except cx_Oracle.DatabaseError,msg:
            logging.error('update error' +str(msg)+ '\n')
    #数据更新和关闭联接
    CON.commit()
    UptCursor.close()

def fatal_error(error):
    logging.error(error + '\n')
    quit(1)

def main():
    #sInXml="<Cmd>2</Cmd><Inv><BH>2025</BH><Inv>"

    #sInXml="<Cmd>3</Cmd><PH>370705059010254000000000000299</PH>"
    sale_dy='20130530'
    pos_no='2025'
    trd_no='0074'
    str_cd='03007'
    #sInXml=PosTaxtoXml(sale_dy,str_cd,pos_no,trd_no)
    #rtn1=get_taxno(sInXml)
    sInXml=delPosTaxxml('370705059010254000000000000253')
    rtn1=deltaxno(sInXml)
    print rtn1

    #taxno_update(rtn1,sale_dy,str_cd,pos_no,trd_no)
    Qrycursor.close()
    CON.close()

if __name__ == '__main__':
    main()

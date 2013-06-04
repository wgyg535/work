import cx_Oracle
import sys,os
import logging
import ConfigParser
import shutil
import time



def set_config(client_id,pos_tax_no):
    conf = ConfigParser.ConfigParser()
    conf.read("tcp.cfg")
    conf.set('charact','client_id',client_id)
    conf.set('charact','client_arg',pos_tax_no)
    conf.write(open("tcp.cfg","w"))

def read_config():
    conf = ConfigParser.ConfigParser()
    conf.read('config.ini')
    db_user=str(conf.get("db",'userid'))
    print db_user
    db_pass=conf.get("db",'passwd')
    print db_pass
    db_tns=conf.get("db",'tns')
    print db_tns
    result =str(db_user+'/'+db_pass+'@'+db_tns).replace("'",'')
    #print result
    return result

def main():
    db_tns=read_config()
    print db_tns
    try:
       CON = cx_Oracle.connect(db_tns,threaded=True)
       logging.info('Lmgs server connect successful')
    except cx_Oracle.DatabaseError,msg:
       logging.error('Lmgs server connect error,please check network!!'+'\n')
       logging.error(str(msg)+'\n')
       sys.exit(-1)

    Qrycursor = CON.cursor()
    Qrycursor1 = CON.cursor()
    UptCursor = CON.cursor()

    Qrycursor.execute("select distinct  sale_dy,str_cd,pos_no,trd_no,cancel_fg from xwy_sale_tax_bill where offline_fg=1 and tax_code is null order by pos_no")
    posrow=Qrycursor.fetchall()
    for rec in posrow:
        print rec[2],rec[1]
        filename='tcp_'+rec[2]+'.cfg'
        print filename
        shutil.copyfile('/store/PosTaxControl/tcp_all/'+filename,'/store/PosTaxControl/tcp.cfg')
        time.sleep(5)
    os.system('python PosTaxControl_upt.py rec[2]')

        #sql1="select str_cd,pos_no,pos_tax_no from wy_sale_tax_cfg where str_cd='%s' and pos_no='%s' " % (rec[1],rec[2])
        #Qrycursor1.execute(sql1)
        #logging.info(sql1)
        #postaxrow= Qrycursor1.fetchall()
        #for pos_tax_no in postaxrow:
            #print pos_tax_no
            #print pos_tax_no[0],pos_tax_no[1],pos_tax_no[2]
            #set_config(pos_tax_no[1],pos_tax_no[2])
            #conf1=ConfigParser.ConfigParser()
            #conf1.read('tcp.cfg')
            #rls=conf1.get('charact','client_arg')
            #print rls
            #os.system('python PosTaxControl_upt.py pos_tax_no[1]')




if __name__=='__main__':
    main()

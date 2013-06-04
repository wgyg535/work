from PosTaxtext import *
def main():
    sInXml='<Cmd>2</Cmd><Inv><BH>2025</BH></Inv>'
    posser=PosTaxDall(sInXml)
    rtn=posser.qry_current_taxno(sInXml)
    print rtn


if __name__=='__main__':
    main()

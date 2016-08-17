# coding: utf-8
import os
import sys
from stash import stash
_stash=stash.StaSh()
def copyandexecute(filename,host="pi@10.0.1.181:~/pythonista/"):
    cmd="scp \"%s\" \"%s\""%(os.path.realpath(os.path.expanduser("~/Documents/%s"%filename)),"%s%s"%(host,filename))
    print cmd
    print _stash.__call__(cmd)
    cmd = "ssh %s \'%s\'"%("pi@10.0.1.181","python %s >> test.txt"%"~/pythonista/%s"%filename)
    print cmd
    print _stash.__call__(cmd)
#	rpc(os.path.realpath(__file__))
#import paramiko
if __name__=="__main__":
	copyandexecute("myrepo/SpiralShell.py")
  
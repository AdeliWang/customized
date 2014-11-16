#!/usr/bin/python

import pexpect
import os, sys, getopt
import time
import subprocess
import json
import re

class Common:
  @staticmethod 
  def run_cmd(cmd):
    p = subprocess.Popen(cmd,
                      shell=True,
                      stdout=subprocess.PIPE,
                      stderr=subprocess.PIPE)
    out, err = p.communicate()
    if err:
      return -1, err
    else:
      return 0, out.strip(" \n") 

  @staticmethod
  def is_ip(parameter):
    reobj = re.compile(r"\b([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\b")
    m = reobj.match(parameter)
    return m != None 

  @staticmethod
  def is_name(parameter):
    reobj = re.compile(r"\w.*")
    m = reobj.match(parameter)
    return m != None 

  @staticmethod
  def is_full_path(parameter):
    reobj = re.compile(r"~{0,1}/.+")
    m = reobj.match(parameter)
    return m != None 
  
  @staticmethod
  def dn2ip(dn):
    cmd="nslookup %s|egrep 'Address[^#]*[:space]*$' |awk '{print $2}'"%dn
    result = Common.run_cmd(cmd)
    if Common.is_ip(result[1]):
      return result
    else:
      return ""
  
  @staticmethod 
  def parser_path(full_path):
    ret = {}    
    #[user@]<[host:]/path> 
    reobj = re.compile(r'(\w.*)@(.+):(.+)')#full
    m = reobj.match(full_path)
    if m:
      ret["usr"] = m.group(1)
      ret["host"] = m.group(2)
      ret["path"] = m.group(3)      
    else:
      reobj = re.compile(r'(.+):(.+)')#half
      m = reobj.match(full_path)     
      if m:
        ret["usr"] = ""
        ret["host"] = m.group(1)
        ret["path"] = m.group(2)
      else:   #local
        ret["usr"] = ""
        ret["host"] = ""
        ret["path"] = full_path        

    if ret["usr"] != "" and (not Common.is_name(ret["usr"])): 
      raise Exception("user name error")

    if ret["host"] != "" and (not Common.is_ip(ret["host"])):
      if Common.dn2ip(ret["host"]) == "":
        raise Exception("host error")

    return ret   
        
class SshLink:
  discont,sshd_down,sshd_up=range(3)
  def __init__(self, host, user, passwd, timeout=15): 
    self.user=user
    self.passwd=passwd
    self.host=host
    self.timeout=timeout
    self.status = SshLink.discont
    #self.f = open('/var/log/sshLink.log','w')
    self.list_expect=[
                 pexpect.EOF,
                 pexpect.TIMEOUT,
                 'continue connecting (yes/no)?',
                 'password: ',
                 '#'
                 ]

  def set_timeout(self, timeout):
    self.timeout=timeout

  def set_user(self, user, passwd):
    self.user=user
    self.passwd=passwd
    
  def __is_open_p22(self, times=3):
    #"nc -w 2 -v -z 10.140.28.2 22"
    tout = 2    
    for i in range(times): 
      cmd="(nc -w %d -v -z %s 22 &>/dev/null)"%(tout, self.host)
      ret = subprocess.call(cmd, shell=True)
      tout += 1
      if ret == 0:
        break
      
    return (ret == 0)

  def get_link_st(self, timeout=2):
    map_reply={
                "No route to host":SshLink.discont,
                "timed out":SshLink.discont,
                "Operation now in progress":SshLink.discont,
                "Connection refused":SshLink.sshd_down,
                "succeeded":SshLink.sshd_up                
                }
    cmd="(nc -w %d -v -z %s 22 2>& 1)"%(timeout, self.host)
    res, reply = Common.run_cmd(cmd)
    if res != 0:
      self.status = SshLink.discont
      return -1, self.status
    for key in map_reply:
      if reply.find(key) != -1:
        self.status = map_reply[key]
        return 0, self.status
    self.status = SshLink.discont    
    return -2, self.status
   
  def __cp(self, src, dst):
    if src[0] == ":" and  dst[0] == ":": 
      raise Exception("parameter error")
      
    if src[0] == ":":
      cmd = "scp %s@%s%s %s"%(self.user, self.host, src, dst)
    elif dst[0] == ":":  
      cmd = "scp %s %s@%s%s"%(src, self.user, self.host, dst)
    else:
      raise Exception("parameter error")

    result = self.__over_ssh(cmd)
    return (result[0] == 0)

  def sync(self, src, dst):
    #Pull: rsync [OPTION...] [USER@]HOST:SRC... [DEST]
    #Push: rsync [OPTION...] SRC... [USER@]HOST:DEST 
    #just use pull
    #cmd="rsync  -avSH "
    if not (src[0] == ":" and dst[0] != ":"):
      raise Exception("parameter error")

    if not os.path.isdir(dst):
      os.makedirs(dst)
      
    cmd = "rsync -avSH %s@%s%s %s"%(self.user, self.host, src, dst)
    result = self.__over_ssh(cmd)
    return (result[0] == 0)

  def mnt(self, host_dir, mp):
    #[user@]host:[dir] mountpoint
    if not (host_dir[0] == ":" and mp[0] != ":"):
      raise Exception("parameter error")
   
    if not os.path.isdir(mp):
      os.makedirs(mp)
       
    cmd = "sshfs %s@%s%s %s"%(self.user, self.host, host_dir, mp)
    result = self.__over_ssh(cmd)
    return (result[0] == 0)

  def __over_ssh(self, cmd):    
    list_expect = self.list_expect             
    child = pexpect.spawn(cmd,timeout=self.timeout)
    child.logfile_read = sys.stdout
    print cmd
    try:
      seen = child.expect(list_expect, timeout=self.timeout)
      if seen == 0:
        cmd_rm = "([ -f /root/.ssh/known_hosts ] && rm -f /root/.ssh/known_hosts)"
        cmd_rm += "; ([ -f ~/.ssh/known_hosts ] && rm -f ~/.ssh/known_hosts)"
        subprocess.call(cmd_rm, shell=True)
        child.close()
        child = pexpect.spawn(cmd,timeout=self.timeout)
        seen = child.expect(list_expect, timeout=self.timeout)      
      if seen == 0 :
        child.close()
        raise Exception("panic: pexpect error1")
      elif seen == 1:
        child.close()
        return (-1, "TIMEOUT")
      elif seen == 2:
        child.sendline('yes\n')
        child.expect('password: ')
        child.sendline(self.passwd)
      elif seen == 3:
        child.sendline(self.passwd)
      
      seen = child.expect(list_expect, timeout=self.timeout)
      if seen == 2:
        child.close()
        raise Exception("panic: pexpect error2") 
      elif seen == 3:
        child.close()
        return (-2, "Error password") 
      elif seen == 0:
        child.close()
        return 0, "OK"
    except pexpect.EOF:
      child.close()
      ret = (-3, "unexpected EOF")
    except pexpect.TIMEOUT:
      child.close()
      ret = (-4, "unexpected TIMEOUT")
    return ret    

  def __exec_cmd(self, cmd, nonblock=False):
    list_expect = self.list_expect
    cmd = '(' + cmd+ ');  echo ret=$?'             
    ssh_cmd='ssh %s@%s "%s"' % (self.user, self.host, cmd)
    child = pexpect.spawn(ssh_cmd, timeout=self.timeout)
    #print ssh_cmd
    #child.logfile_read = sys.stdout
    try:
      seen = child.expect(list_expect, timeout=self.timeout)
      if seen == 0:
        cmd_rm = "([ -f /root/.ssh/known_hosts ] && rm -f /root/.ssh/known_hosts)"
        cmd_rm += "; ([ -f ~/.ssh/known_hosts ] && rm -f ~/.ssh/known_hosts)"
        subprocess.call(cmd_rm, shell=True)
        child.close()
        child = pexpect.spawn(ssh_cmd,timeout=self.timeout)
        seen = child.expect(list_expect, timeout=self.timeout) 
      if seen == 0 :
        child.close()
        raise Exception("panic: pexpect error1")
      elif seen == 1:
        child.close()
        return (-1, "TIMEOUT")
      elif seen == 2:
        child.sendline('yes\n')
        child.expect('password: ')
        child.sendline(self.passwd)
      elif seen == 3:
        child.sendline(self.passwd)
      if not nonblock:     
        cnt = child.read()
        info=cnt.replace("\r", "")
        info=info.replace("\n", "") 
        info=info.split("ret=")[0]      
        if cnt.find("ret=0") != -1:
          ret = (0, info.strip())
        else:  
          ret = (1, info.strip())
      else:
        ret = (0, "need not read")
        time.sleep(0.5)
      child.close()
    except pexpect.EOF:
      child.close()       
      ret = -2, "unexpected EOF"
    except pexpect.TIMEOUT:
      child.close()
      ret = -3, "unexpected TIMEOUT"
    except Exception as err:
      print err
      ret = -4, "panic: pexpect error"
    return ret  

  def push_file(self, f_local, f_remote, times=3, verify=True):
    if not os.path.isfile(f_local):
      return -1, "Not find the local file: %s"%f_local
      
    self.set_timeout(50)            
    fn=os.path.basename(f_local)
    f_chk = "/tmp/%s.chk"%fn
    subprocess.call("rm -f %s"%f_chk, shell=True)
    for i in range(times):
      result = self.__cp(f_local, ":%s"%f_remote)
      if verify:
        self.__cp(":%s%s"%(f_remote, fn), f_chk)
        if subprocess.call("diff %s %s"%(f_chk, f_local), shell=True) == 0:
          subprocess.call("rm -f %s"%f_chk, shell=True)
          return 0, "OK"
      else:
        if result:
          return 0, "OK"

    return -2, "Failed to send: %s"%f_local

  def pull_file(self, f_local, f_remote, times=3):
    ret = False
    self.set_timeout(50)
    fn=os.path.basename(f_remote)
    subprocess.call("rm -f %s"%f_local, shell=True)
    for i in range(times):
      result = self.__cp(":%s"%f_remote, f_local)
      if result and os.path.isfile(f_local):
        return True

    return False
                    
  def push_cmd(self, cmd, nonblock = False, times=3):
    self.set_timeout(50)
    for i in range(times):
      res, info = self.__exec_cmd(cmd, nonblock)
      #print res, info
      if res == 0:
        return (True, info)
      elif res == 1:
        return (False, info)

    return (False, info)

##########################################################

def get_usr_info(host, user):
  path=os.path.split(os.path.realpath(__file__))[0]
  f_cfg = "%s/ssh-login.cfg"%path
  fp = open(f_cfg, 'r')
  cfg_ls = json.load(fp, 'UTF-8')
  fp.close()
  
  for cfg in cfg_ls:
    if cfg["host"] == host:
      user=cfg["usr"][0]
      passwd=cfg["usr"][1]
      return True, user, passwd

  if user == "":
    user = raw_input("input user: ")
    passwd = raw_input("input password: ")
  else:
    passwd = raw_input("input password: ")
      
  return False, user, passwd

#{"host":"10.140.28.12", "usr":["user", "key"]}
def insert_usr_info(usr_info):
  if ("host" not in usr_info) \
     or ("usr" not in usr_info) \
     or (len(usr_info["usr"]) != 2):
    raise Exception("parameter error") 

  path=os.path.split(os.path.realpath(__file__))[0]
  f_cfg = "%s/ssh-login.cfg"%path
  fp = open(f_cfg, 'r')
  cfg_ls = json.load(fp, 'UTF-8')
  fp.close()

  for cfg in cfg_ls:
    if cfg["host"] == usr_info["host"]:
      raise Exception("%s user info has already exist!!"%cfg["host"])
      
  cfg_ls.append(usr_info) 
  str_cfg = json.dumps(cfg_ls,sort_keys=True,
              indent=2, separators=(',', ': '))
  fh = open(f_cfg,'w')
  fh.write(str_cfg)
  fh.close()  
  
def usage_myscp():
  fn = os.path.basename(sys.argv[0])
  txt="""%s  --- auto over ssh tools 
  %s <src> <dst>
  """%(fn, fn)
  print txt

def myscp(argv): 
  try:  
    if len(argv) != 2:      
      raise Exception("parameter error")
      
    src = Common.parser_path(argv[0])   
    dst = Common.parser_path(argv[1])
    if (src["host"] == "" and dst["host"] == "")\
      or (src["host"] != "" and dst["host"] != ""):
      raise Exception("parameter error")

    is_pull = True
    usr = src["usr"]
    host = src["host"]   #src is remote
    if src["host"] == "":
      is_pull = False
      usr = dst["usr"]
      host = dst["host"]  #dst is remote
      
    ## need read confige file
    exist, usr, passwd = get_usr_info(host, usr)
    link = SshLink(host, usr, passwd)

    if (is_pull and (not Common.is_full_path(src["path"]))) \
      or ((not is_pull) and (not Common.is_full_path(dst["path"]))):
      raise Exception("remote path error")       
    
    if is_pull:    
      ret = link.pull_file(dst["path"], src["path"])
    else:
      result = link.push_file(src["path"], dst["path"])
      print result[1]
      ret = (result[0] == 0)

    if not ret:
      print "Failed!!"
      
    if ret and (not exist):
      #{"host":"10.140.28.12", "usr":["user", "key"]}       
      user_info = {"host":host, "usr":[usr, passwd]}
      insert_usr_info(user_info)
    
  except Exception as err: 
    print err
    usage_myscp()                        
    sys.exit(2)     

def usage_mysmnt():
  fn = os.path.basename(sys.argv[0])
  txt="""%s  --- auto mount to remote host by ssh
  %s [user@]host:[dir] mountpoint
  """%(fn, fn)
  print txt

def mysmnt(argv):
  try: 
    #[user@]host:[dir] mountpoint
    if len(argv) != 2:
      raise Exception("parameter error")
      
    src = Common.parser_path(argv[0])   
    dst = Common.parser_path(argv[1])
    if not (src["host"]!= "" and dst["host"] == ""):
      raise Exception("parameter error")

    usr = src["usr"]
    host = src["host"]
    ## need read confige file
    exist, usr, passwd = get_usr_info(host, usr)
    
    link = SshLink(src["host"], usr, passwd)
    if not Common.is_full_path(src["path"]):
      raise Exception("remote path error")  
      
    ret = link.mnt(":%s"%src["path"], dst["path"])
    if not ret:
      print "Failed!!"
      
    if ret and (not exist):    
      user_info = {"host":host, "usr":[usr, passwd]}
      insert_usr_info(user_info)
      
  except Exception as err: 
    print err
    usage_mysmnt()                        
    sys.exit(2)  

def usage_mysync():
  fn = os.path.basename(sys.argv[0])
  txt="""%s  --- auto sync the dir from remote host by ssh
  %s [user@]host:[dir] local_dir
  """%(fn, fn)
  print txt
  
def mysync(argv):
  try: 
    #[user@]host:[dir] local_dir
    if len(argv) != 2:
      raise Exception("parameter error")
      
    src = Common.parser_path(argv[0])   
    dst = Common.parser_path(argv[1])
    if not (src["host"]!= "" and dst["host"] == ""):
      raise Exception("parameter error")

    usr = src["usr"]
    host = src["host"]
    ## need read confige file
    exist, usr, passwd = get_usr_info(host, usr)    
    link = SshLink(src["host"], usr, passwd)    
    if not Common.is_full_path(src["path"]):
      raise Exception("remote path error")
      
    ret = link.sync(":%s"%src["path"], dst["path"])
    if not ret:
      print "Failed!!"
      
    if ret and (not exist):    
      user_info = {"host":host, "usr":[usr, passwd]}
      insert_usr_info(user_info)
    
  except Exception as err: 
    print err
    usage_mysync()                        
    sys.exit(2)

if __name__ == '__main__':
  fn = os.path.basename(sys.argv[0])
  fn = fn.split(".")[0]
  if fn == "myscp":
    myscp(sys.argv[1:])
  elif fn == "mysmnt":  
    mysmnt(sys.argv[1:])
  elif fn == "mysync": 
    mysync(sys.argv[1:])
  else:
    bin_myscp = "/usr/bin/myscp"
    bin_mysmnt = "/usr/bin/mysmnt" 
    bin_mysync = "/usr/bin/mysync"
    self_path = os.path.realpath(__file__)
    bins = [bin_myscp, bin_mysmnt, bin_mysync]
    for bin in bins:
      if not os.path.isfile(bin):
        os.system("rm -f %s ; ln -s %s %s"%(bin,self_path, bin))
    os.system("ls -l /usr/bin/mys*")
   

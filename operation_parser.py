# JY @ 2023-11-26

'''
 For each operation file produced by caldera-server after running a adversary-profile
 ,in the specified directory (e.g. reports), 
 read it in as json file
 and parse to determine whether the ability(ies) were properly exectued (status : 0)
'''

import json
import os
import pprint

if __name__ == "__main__":

    reports_dirpath = "/home/priti/Desktop/caldera/etw/tmp/reports/old_reports_20231109" 

    operation_fnames = os.listdir(reports_dirpath)

    for operation_fname in operation_fnames:

        print("="*30,flush= True)

        operation_fpath = os.path.join(reports_dirpath, operation_fname)

        with open( operation_fpath, 'r' ) as fp:
            operation_dict = json.load( fp )

            adversary_info = operation_dict['adversary']

            adversary_id = adversary_info['adversary_id']
            atomic_ordering = adversary_info['atomic_ordering']

            print(f"adversary_id: {adversary_id}\n\natomic_ordering: {atomic_ordering}", flush=True)

            paw_list = list( operation_dict['steps'].keys() )  # paw is caldera-agent-id
                                                               # if paw_list >= 2 , that means there probably was a dead-agent
                                                               # dead-agent will not result in any actual steps

            is_technique_successful_exec = False

            for paw in paw_list:
                if len( operation_dict['steps'][paw]['steps'] ) == 0:
                    # paw corresponds to a agent that was dead (invalid but was not killed for some reason)
                    continue

                print("-"*30,flush= True)


                for step_dict in operation_dict['steps'][paw]['steps']:
                    
                    if step_dict['status'] == 0:

                        pprint.pprint( step_dict )

                        is_technique_successful_exec = True

                print("-"*30,flush= True)

                if is_technique_successful_exec:
                    print("successfully executed technique", flush=True)
                else:
                    print("failed execution of technique", flush=True)

        print("="*30,flush= True)


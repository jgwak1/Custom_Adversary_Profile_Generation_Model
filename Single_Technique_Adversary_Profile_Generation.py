import os
from pathlib import Path
import shutil


import json
import pickle
import yaml

import random
import types
from datetime import datetime


from stockpile_atomic_plugin_ability_ids import *  # includes all ability-id lists per plugin-tactic
                                                   # e.g. 'stockpile_privilege_escalation__ability_ids'

from Custom_Adversary_Profile_Generation_Model import *




class Single_Adversary_Profile_Generation_Model( Custom_Adversary_Profile_Generation_Model_v1 ):

   # implement "def generate_single_technique_adv_profiles(self)"
   # override "generate_adv_yml_file_text()" function for more straightforward yml file-name

   def generate_single_technique_adv_profiles(self, plugin = "atomic", N = 5):
       
      ''' For a given plugin, for each technique, generate N single-technique adversary profiles '''


      # Following 2 parameters should be already handled in constructor,
      # but just explicitly set here again, as these two are most important parameters for "get_list_of_ability_ids"
      self.plugin = plugin

      # keys are in form of "<technique-id>__<tactic>__<technique-name>__<caldera_ability_id>"
      # e.g. "T1543.003__persistence__Create or Modify System Process: Windows Service__52771610-2322-44cf-816b-a7df42b4c086"
      stockpile_keys = [k for k,v in MitreTechniqueID__caldera_ability_id__map_dict.items() if v['plugin'] == "stockpile"]
      atomic_keys = [k for k,v in MitreTechniqueID__caldera_ability_id__map_dict.items() if v['plugin'] == "atomic"]


      delim = "__"
      stockpile_splitted_keys = [key.split(delim) for key in stockpile_keys]
      atomic_splitted_keys = [key.split(delim) for key in atomic_keys]

      stockpile_caldera_ability_ids = [x[-1] for x in stockpile_splitted_keys]
      atomic_caldera_ability_ids = [x[-1] for x in atomic_splitted_keys]

      # generate a dictionary in form of:
      # e.g {T1003__credential-access__OS Credential Dumping__3c647015-ab0a-496a-8847-6ab173cd2b22" : "3c647015-ab0a-496a-8847-6ab173cd2b22"}
      if self.plugin == "stockpile":
         DetailedAbilityID_AbilityID_map = dict(zip(stockpile_keys, stockpile_caldera_ability_ids))
      elif self.plugin == "atomic":
         DetailedAbilityID_AbilityID_map = dict(zip(atomic_keys, atomic_caldera_ability_ids))
      else: # both
         DetailedAbilityID_AbilityID_map = dict(zip(stockpile_keys + atomic_keys, 
                                                    stockpile_caldera_ability_ids + atomic_caldera_ability_ids))


      # now generate N single-technique adversary-profiles for each technique,
      # the adversary-name will be the 'DetailedAbilityID' and '

      for DetailedAbilityID, AbilityID in DetailedAbilityID_AbilityID_map.items():  # for each technique
                    
          for trial in range(1, N+1):

            self.generate_adv_yml_file_text( technique_id = AbilityID,
                                             adversary_profile_name = DetailedAbilityID,
                                             N = trial )



   def generate_adv_yml_file_text(self, technique_id, adversary_profile_name, N ):

      ''' override "generate_adv_yml_file_text()" function for more straightforward yml file-name '''


      adversary_id = f"{self.plugin.lower()}__{adversary_profile_name.lower()}__trial_{N}"
      adversary_id = adversary_id.replace('/', ',').replace(':','-').replace(' ','_').replace('.','_') # to avoid error (also don't allow space)


      # not having '[' and ']' is very important.
      first = f"""adversary_id: {adversary_id}\nname: Single Technique Custom Adversary Profile\ndescription: {self.plugin} plugin\natomic_ordering:\n"""
      mid = f"- {technique_id} # {caldera_ability_id__MitreTechniqueID__map_dict[technique_id]}\n"
      last  ="""objective: 495a9828-cab1-44dd-a0ca-66e58177d8cc\ntags: []"""

      custom_adversary_yml_file_text = first + mid + last

      with open( os.path.join( self.custom_adversary_profile_yml_dirpath, f'{adversary_id}.yml') ,'w') as f:    # Modified by JY @ 2023-02-27
            f.write( custom_adversary_yml_file_text )




if __name__ == "__main__":


   #############################################################################################################################
   single_techique_adversary_profile_yml_dirpath = \
   "/home/priti/Desktop/caldera/etw/caldera/Single_Technique_Adversary_Profile__yml_files"  

   if not os.path.exists(single_techique_adversary_profile_yml_dirpath):
      raise RuntimeError(f"{single_techique_adversary_profile_yml_dirpath} doesn't exist.\nManually create it\n")

   #############################################################################################################################

   # Utilize "Custom_Adversary_Profile_Generation_Model_v1" 
   # to generate single-technique-adversary-profiles for atomic-plugin

   plugin_choice = "atomic"
   num_trials = 5
   



   gen_mod = Single_Adversary_Profile_Generation_Model(
                                                       custom_adversary_profile_yml_dirpath = \
                                                         single_techique_adversary_profile_yml_dirpath,

                                                      #  plugin = plugin_choice,
                                                      #  profile_length = 1,
                                                      #  list_of_technique_ids = None,
                                                      #  sequence_of_tactics = None, 
                                                       
                                                       
                                                      )

   gen_mod.generate_single_technique_adv_profiles(plugin = plugin_choice, 
                                                  N = num_trials)

import pickle
import os
import yaml
import re


# Change
stockpile_plugin_abilities_dpath = "/data/d1/jgwak1/tabby/tools__Copied_from_home_zshu1_tools__run_on_panther/tools__Copied_from_home_zhsu1_tools/caldera/plugins/stockpile/data/abilities"
atomic_plugin_abilities_dpath = "/data/d1/jgwak1/tabby/tools__Copied_from_home_zshu1_tools__run_on_panther/tools__Copied_from_home_zhsu1_tools/caldera/plugins/atomic/data/abilities"

ab_list_pkl_fname = "ab_list__JY.pkl"
ab_list_pkl_save_dpath = "/data/d1/jgwak1/tabby/tools__Copied_from_home_zshu1_tools__run_on_panther/tools__Copied_from_home_zhsu1_tools/etw"
###

if __name__ == "__main__":

   stockpile_tactic_dirs = os.listdir( stockpile_plugin_abilities_dpath )
   atomic_tactic_dirs = os.listdir( atomic_plugin_abilities_dpath )


   ab_list = []

   # ************************************************************************************************************
   # ************************************************************************************************************
   # ************************************************************************************************************
   # ************************************************************************************************************
   # stockpile --------------------------------------------------------------------------------------------------

   for stockpile_tactic_dir in stockpile_tactic_dirs:

      stockpile_tactic_dpath = os.path.join(stockpile_plugin_abilities_dpath, stockpile_tactic_dir)
      ability_yml_files = [x for x in os.listdir(stockpile_tactic_dpath) if x.endswith(".yml")]

      for ability_yml_file in ability_yml_files:

         yml_content = yaml.safe_load( open( os.path.join(stockpile_tactic_dpath, 
                                                          ability_yml_file) ) )[0]  

         # ability_id -----------------------------------------------------------------------
         if 'id' in yml_content:
            ability_id = yml_content['id']
         else: # if retrieving 'id' cannot be done in structured manner, then continue
            continue
         # ----------------------------------------------------------------------------------

         '''   Only abilities that support 'windows' + 'powershell'  
               -> only 'powershell' b/c corresponding benign-data will be psh 
         '''

         if 'platforms' in yml_content:
            
            # 'unknown' appears also to be windows sometimes
            if 'windows' in yml_content['platforms'] or 'unknown' in yml_content['platforms'] :

               powershell_pattern = r'psh,pwsh|pwsh,psh|psh,cmd|cmd,psh|psh|pwsh'   # 'psh,pwsh' and 'psh,cmd' should precede.

               for key in yml_content['platforms']['windows']:
                  powershell_pattern__match  = re.search(powershell_pattern, key)
                  
               
               ##########################################################################################################
               if powershell_pattern__match: # Add to ab_list only if it reached here.

                  fact = None
                  dependency = None 

                  powershell_pattern__match__key_string = powershell_pattern__match.group()  # retrieve matched text    

                  # fact -------------------------------------------------------------------------

                  if 'parsers' in yml_content['platforms']['windows'][powershell_pattern__match__key_string]:
                     # Regex for all parsers in 'stockpile' plugins
                     # All possible patterns can be seen in : /data/d1/jgwak1/tabby/tools__Copied_from_home_zshu1_tools__run_on_panther/tools__Copied_from_home_zhsu1_tools/caldera/plugins/stockpile/app/parsers
                     parsers_pattern  = r'^plugins\.stockpile\.app\.parsers\..*'

                     for key in yml_content['platforms']['windows'][powershell_pattern__match__key_string]['parsers']:
                        parsers_pattern__match = re.search(parsers_pattern, key) # will return first match
                     if parsers_pattern__match:
                        parsers_pattern__match__key_string = parsers_pattern__match.group()  # retrieve matched text 
                        fact = yml_content['platforms']['windows'][powershell_pattern__match__key_string]['parsers']\
                                          [parsers_pattern__match__key_string][0]['source']
                     else:
                        fact = None
                  else: 
                     fact = None

                  # dependency --------------------------------------------------------------------
                  if 'requirements' in yml_content: 
                     # Regex for all requirements in 'stockpile' plugins
                     # All possible patterns can be seen in : /data/d1/jgwak1/tabby/tools__Copied_from_home_zshu1_tools__run_on_panther/tools__Copied_from_home_zhsu1_tools/caldera/plugins/stockpile/app/requirements
                     requirements_pattern  = r'^plugins\.stockpile\.app\.requirements\..*'

                     for key in yml_content['requirements'][0]:
                        requirements_pattern__match = re.search(requirements_pattern, key) # will return first match
                     if requirements_pattern__match:
                        requirements_pattern__match__key_string = requirements_pattern__match.group()  # retrieve matched text 
                        dependency = yml_content['requirements'][0][requirements_pattern__match__key_string][0]['source']
                     else:
                        dependency = None
                  else:
                     dependency = None
                  # -------------------------------------------------------------------------------

                  # (id, dependency, fact)
                  ab_list.append( (ability_id, dependency, fact, 'stockpile') )
               ##########################################################################################################

               else: # if this technique does not support powershell, continue 
                  continue

            else: # if this technique has no chance to support 'windows', continue
               continue

         else: # if can't even retrieve 'platforms' information in a structured manner, continue
            continue

   # print()
   # ************************************************************************************************************
   # ************************************************************************************************************
   # ************************************************************************************************************
   # ************************************************************************************************************
   # atomic --------------------------------------------------------------------------------------------------
   for atomic_tactic_dir in atomic_tactic_dirs:

      atomic_tactic_dpath = os.path.join(atomic_plugin_abilities_dpath, atomic_tactic_dir)
      ability_yml_files = [x for x in os.listdir(atomic_tactic_dpath) if x.endswith(".yml")]

      for ability_yml_file in ability_yml_files:

         yml_content = yaml.safe_load( open( os.path.join(atomic_tactic_dpath, 
                                                          ability_yml_file) ) )[0]  

         # ability_id -----------------------------------------------------------------------
         if 'id' in yml_content:
            ability_id = yml_content['id']
         else: # if retrieving 'id' cannot be done in structured manner, then continue
            continue
         # ----------------------------------------------------------------------------------
         '''   Only abilities that support 'windows' + 'powershell'  
               -> only 'powershell' b/c corresponding benign-data will be psh 
         '''

         if 'platforms' in yml_content:
            
            # 'unknown' appears also to be windows sometimes
            platform_pattern = r'windows|unknown'
            for key in yml_content['platforms']:
               platform__match  = re.search(platform_pattern, key)
            if platform__match:
               platform__match__key_string = platform__match.group()  # retrieve matched text 


               powershell_pattern = r'psh,pwsh|pwsh,psh|psh,cmd|cmd,psh|psh|pwsh'   # 'psh,pwsh' and 'psh,cmd' should precede.

               for key in yml_content['platforms'][platform__match__key_string]:
                  powershell_pattern__match  = re.search(powershell_pattern, key)
                  
               
               ##########################################################################################################
               if powershell_pattern__match: # Add to ab_list only if it reached here.

                  fact = None
                  dependency = None 

                  powershell_pattern__match__key_string = powershell_pattern__match.group()  # retrieve matched text    

                  # fact -------------------------------------------------------------------------

                  if 'parsers' in yml_content['platforms'][platform__match__key_string][powershell_pattern__match__key_string]:
                     # Regex for all parsers in 'stockpile' plugins
                     # All possible patterns can be seen in : /data/d1/jgwak1/tabby/tools__Copied_from_home_zshu1_tools__run_on_panther/tools__Copied_from_home_zhsu1_tools/caldera/plugins/stockpile/app/parsers
                     parsers_pattern  = r'^plugins\.atomic\.app\.parsers\..*'

                     for key in yml_content['platforms'][platform__match__key_string][powershell_pattern__match__key_string]['parsers']:
                        parsers_pattern__match = re.search(parsers_pattern, key) # will return first match
                     
                     if parsers_pattern__match:
                        parsers_pattern__match__key_string = parsers_pattern__match.group()  # retrieve matched text 
                        fact = yml_content['platforms'][platform__match__key_string][powershell_pattern__match__key_string]['parsers']\
                                          [parsers_pattern__match__key_string][0]['source']
                     else:
                        fact = None
                  else: 
                     fact = None

                  # dependency --------------------------------------------------------------------
                  if 'requirements' in yml_content: 
                     # Regex for all requirements in 'stockpile' plugins
                     # All possible patterns can be seen in : /data/d1/jgwak1/tabby/tools__Copied_from_home_zshu1_tools__run_on_panther/tools__Copied_from_home_zhsu1_tools/caldera/plugins/stockpile/app/requirements
                     requirements_pattern  = r'^plugins\.atomic\.app\.requirements\..*'

                     for key in yml_content['requirements'][0]:
                        requirements_pattern__match = re.search(requirements_pattern, key) # will return first match
                     if requirements_pattern__match:
                        requirements_pattern__match__key_string = requirements_pattern__match.group()  # retrieve matched text 
                        dependency = yml_content['requirements'][0][requirements_pattern__match__key_string][0]['source']
                     else:
                        dependency = None
                  else:
                     dependency = None
                  # -------------------------------------------------------------------------------

                  # (id, dependency, fact)
                  ab_list.append( (ability_id, dependency, fact, 'atomic') )
               ##########################################################################################################

               else: # if this technique does not support powershell, continue 
                  continue

            else: # if this technique has no chance to support 'windows', continue
               continue

         else: # if can't even retrieve 'platforms' information in a structured manner, continue
            continue

   
   
   ab_list_pkl_save_fpath = os.path.join(ab_list_pkl_save_dpath, ab_list_pkl_fname)
   fp = open(ab_list_pkl_save_fpath, 'wb')
   pickle.dump(ab_list,fp)
   
   print()
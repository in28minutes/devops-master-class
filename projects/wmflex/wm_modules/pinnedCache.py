"""
#####################################################################################
#                                                                                   #
#    Copyright 2023-2022 Broadcom.  All Rights Reserved.  Broadcom Confidential.    #
#     The term "Broadcom" refers to Broadcom Inc. and/or its subsidiaries.          #
#                                                                                   #
#####################################################################################

All foreign configuration module will be performed as a part of this class.
Both GUI and backend code will be handled with help of ForeignConfig and Flex_ForeignConfig class.

# 04/05/2023 nr888483   ER DCSG01430860  Add support for Pinned Cache module (Initial Version)
#
"""
import Tkinter as tk
import ttk
from copy import deepcopy
from custom_styles import CustomStyles

class PinnedCache:
    def __init__(self, parent):
        self.parent = parent
        self.reset_module_dict()
        self.config_form()
        self.pc_op_dict_value = None

    def reset_module_dict(self):
        self.pc_dictionary = {
            "type": "pinned_cache"
        }

    def config_form(self):
        lable_style = CustomStyles.label_style()
        self.pc_values_list = ("Validate pinned cache exists","Validate no pinned cache exists", "Discard pinned cache")
        ttk.Label(self.parent, text="Validate pinned cache exists", style='Custom.TLabel').grid(row=0, column=0, sticky="w", padx=(10, 5), pady=(0, 5))
        self.pc_options = tk.StringVar()
        self.pc_type = ttk.Combobox(self.parent, textvariable=self.pc_options, width=30)
        self.pc_type["values"] = self.pc_values_list
        self.pc_type.current(self.pc_values_list.index('Validate pinned cache exists'))
        self.pc_type.grid(row=0, column=1)
        self.pc_type.bind("<<ComboboxSelected>>", lambda event: self.dropdown_callback(event, "pc_options"))

    def step_text(self):
        self.pull_selected_values()
        txt = "Perform '{}' operation.".format(self.pc_type.get())
        return txt

    def dropdown_callback(self, event, key):
        new_val = event.widget.get()
        print("Dropdown selected: {}".format(new_val))
        self.pc_dictionary[key] = new_val
        print("Config Dict : {}".format(self.pc_dictionary))

    def entrybox_callback(self, event, key):
        value = event.widget.get().strip()
        print("Key : {}, Text Box Value : {}".format(key, value))
        self.pc_dictionary[key] = value
        print("Config Dict : {}".format(self.pc_dictionary))

    def set_step(self, step_dict):
        print("DICT RECIEVED : {}".format(step_dict))
        if step_dict["pc_operation"] == "pc_exists":
            self.pc_type.current(self.pc_values_list.index("Validate pinned cache exists"))
        elif step_dict["pc_operation"] == "pc_no_exists":
            self.pc_type.current(self.pc_values_list.index("Validate no pinned cache exists"))  
        elif step_dict["pc_operation"] == "discard_pc":
            self.pc_type.current(self.pc_values_list.index("Discard pinned cache"))  

    def pull_selected_values(self):
        if self.pc_type.get().lower() == "validate pinned cache exists":
            self.pc_op_dict_value = "pc_exists"
        elif self.pc_type.get().lower() == "validate no pinned cache exists":
            self.pc_op_dict_value = "pc_no_exists"  
        elif self.pc_type.get().lower() == "discard pinned cache":
            self.pc_op_dict_value = "discard_pc"            
        self.pc_dictionary = {
            "type": "pinned_cache",
            "subtype": None,
            "pc_operation": self.pc_op_dict_value
        }

    def get_step(self):
        self.pull_selected_values()
        tmp = deepcopy(self.pc_dictionary)
        self.reset_module_dict()
        return tmp

'''
class Flex_PinnedCache:
    def __init__(self,mr_object= None, log_object=None):
        self.mr = mr_object
        self.log = log_object

    def mjolnirFlex_check_pc(self):
        pinnedcache_rtn_value = None
        pinnedCacheList = []
        pinnedCacheList = self.mr.get_pinnedcache_list()
        print "\n pinnedCacheList", pinnedCacheList
        if len(pinnedCacheList) == 0:
            self.log.info("There are no VDs with pinned cache on controller ")
            pinnedcache_rtn_value = "There is no VD with pinned cache on controller "
        else:
            self.log.info("Logical drives with pinned cache : " + str(pinnedCacheList))
            pinnedcache_rtn_value = "Logical drives with pinned cache : " + str(pinnedCacheList)
        return pinnedcache_rtn_value 

    def mjolnirFlex_discard_pinnedcache(self):
        Discard_PinnedCache_all_Lds(int(self.mr.ctrl_id))
        self.log.info("")
        self.log.info("All pinned cache discarded from controller " + str(self.mr.ctrl_id))
        self.log.info("")

    def exec_pc(self,opcode=None):      
        try:
            if opcode.lower() == "pc_exists":
                self.log.info("")
                self.log.info("***** Validating VD Pinnedcache exist on controller ******" )
                self.log.info("") 
                check_pc_rtn_value = self.mjolnirFlex_check_pc()
                if not "Logical drives with pinned cache" in check_pc_rtn_value:
                    self.log.info("")
                    #raise SALError("----- %s ----" % (str(check_pc_rtn_value)))    
            elif opcode.lower() == "pc_no_exists":
                self.log.info("")
                self.log.info("***** Validating no VD Pinnedcache exist on controller ******" )
                self.log.info("") 
                check_pc_rtn_value = self.mjolnirFlex_check_pc()
                if not "There is no VD with pinned cache on controller" in check_pc_rtn_value:
                    self.log.info("")
                    #raise SALError("----- %s ----" % (str(check_pc_rtn_value)))  
            elif opcode.lower() == "discard_pc":
                self.log.info("")
                self.log.info("***** Discarding VD Pinnedcache exist on controller ******" )
                self.log.info("") 
                self.mjolnirFlex_discard_pinnedcache()
        except:
            traceback.print_exc()
            raise SALError("------ Failed to perform requested pinned cache operation ------" )
'''
"""
#####################################################################################
#                                                                                   #
#    Copyright 2023-2022 Broadcom.  All Rights Reserved.  Broadcom Confidential.    #
#     The term "Broadcom" refers to Broadcom Inc. and/or its subsidiaries.          #
#                                                                                   #
#####################################################################################

All foreign configuration module will be performed as a part of this class.
Both GUI and backend code will be handled with help of ForeignConfig and Flex_ForeignConfig class.

# 04/03/2023 nr888483   ER DCSG01430859  Add support for Foreign config module (Initial Version)
#
"""
import Tkinter as tk
import ttk
from copy import deepcopy
from custom_styles import CustomStyles

class ForeignConfig:
    def __init__(self, parent):
        self.parent = parent
        self.reset_module_dict()
        self.config_form()
        self.fc_op_dict_value = None

    def reset_module_dict(self):
        self.fc_dictionary = {
            "type": "foreign_cfg"
        }

    def config_form(self):
        lable_style = CustomStyles.label_style()
        self.fc_values_list = ("Clear all foreign configuration","Import all foreign configuration")
        ttk.Label(self.parent, text="Select foreign configuration operation", style='Custom.TLabel').grid(row=0, column=0, sticky="w", padx=(10, 5), pady=(0, 5))
        self.fc_options = tk.StringVar()
        self.fc_type = ttk.Combobox(self.parent, textvariable=self.fc_options, width=30)
        self.fc_type["values"] = self.fc_values_list
        self.fc_type.current(self.fc_values_list.index('Clear all foreign configuration'))
        self.fc_type.grid(row=0, column=1)
        self.fc_type.bind("<<ComboboxSelected>>", lambda event: self.dropdown_callback(event, "fc_options"))

    def step_text(self):
        self.pull_selected_values()
        txt = "Perform {} .".format(self.fc_type.get())
        return txt

    def dropdown_callback(self, event, key):
        new_val = event.widget.get()
        print("Dropdown selected: {}".format(new_val))
        self.fc_dictionary[key] = new_val
        print("Config Dict : {}".format(self.fc_dictionary))

    def entrybox_callback(self, event, key):
        value = event.widget.get().strip()
        print("Key : {}, Text Box Value : {}".format(key, value))
        self.fc_dictionary[key] = value
        print("Config Dict : {}".format(self.fc_dictionary))

    def set_step(self, step_dict):
        print("DICT RECIEVED : {}".format(step_dict))
        if step_dict["fc_operation"] == "clear_fc":
            self.fc_type.current(self.fc_values_list.index("Clear all foreign configuration"))
        elif step_dict["fc_operation"] == "import_fc":
            self.fc_type.current(self.fc_values_list.index("Import all foreign configuration"))

    def pull_selected_values(self):
        if self.fc_type.get().lower() == "clear all foreign configuration":
            self.fc_op_dict_value = "clear_fc"
        elif self.fc_type.get().lower() == "import all foreign configuration":
            self.fc_op_dict_value = "import_fc"            
        self.fc_dictionary = {
            "type": "foreign_cfg",
            "subtype": None,
            "fc_operation": self.fc_op_dict_value
        }

    def get_step(self):
        self.pull_selected_values()
        tmp = deepcopy(self.fc_dictionary)
        self.reset_module_dict()
        return tmp
'''
class Flex_ForeignConfig:
    def __init__(self,mr_object= None, log_object=None):
        self.mr = mr_object
        self.log = log_object
        
    def exec_fc(self,opcode=None):
        self.log.info("")
        self.log.info("******************* Foreign Configuration Module **************")
        self.log.info("")
        self.mr.cli.continue_on_error_set(0)
        exisitng_foreign_config_on_controller = self.mr.cli.foreign_list_all()
        self.log.info("******************* Listing foreign configuration: %s **************" % (
            exisitng_foreign_config_on_controller))
        self.log.info("")
        exisitng_foreign_config_on_controller = list()
        exisitng_foreign_config_on_controller = self.mr.cli.foreign_preview_list()
        self.log.info("******************* Exisiting Foreign Configuration: foreign_preview_list: **************")
        self.log.info("")
        for index in exisitng_foreign_config_on_controller:
            self.log.info("******************* %s **************" % (str(index)))
        self.log.info("")
        try:
            if opcode.lower() == "import_fc":
                self.log.info("")
                self.log.info("******************* Performing foreign config import operation **************")
                self.log.info("")
                self.mr.cli.foreign_import()
            elif opcode.lower() == "clear_fc":
                self.log.info("")
                self.log.info("******************* Performing foreign config clear operation **************")
                self.log.info("")
                self.mr.cli.foreign_del_all()    
        except:
            traceback.print_exc()
            raise SALError("------ Failed to perform foreign configuration: '%s' operation ------" % str(opcode))
'''
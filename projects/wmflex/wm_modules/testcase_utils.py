#!/usr/bin/env python
"""
#####################################################################################
#                                                                                   #
#    Copyright 2023-2024 Broadcom.  All Rights Reserved.  Broadcom Confidential.    #
#     The term "Broadcom" refers to Broadcom Inc. and/or its subsidiaries.          #
#                                                                                   #
#####################################################################################
"""
__doc__ = '''
Defines utilities module for creating a Test case. Currently added :
1. Snapdump

'''
__author__ = ["Amitabh Suman"]
__copyright__ = "Copyright 2023-24, The Wingman Flex Project"
__version__ = 'snapdump_1.0.0'  # Major.Minor.Patch
__credits__ = ["MRPT"]
__email__ = 'dcsg-pt-bangalore-automation.pdl@broadcom.com'
__status__ = 'Development'
__maintainer__ = "Wingman Automation Team"

# Change to next line in case the ER length is > 80 characters
__enhancements__ = '''
DATE(M/D/Y)  CQID            WHO(CQUser)  DESCRIPTION
===============================================================
04/20/23     DCSG01431530    asuman       WM Flex 3.0 : (GUI) : Add support for Snapdump operation as a test step

'''

import Tkinter as tk
import ttk
from copy import deepcopy
from tooltip import ToolTip
import logging

logger = logging.getLogger("root")

class SnapdumpModule:
    def __init__(self, parent):
        self.parent = parent
        self.reset_module_dict()
        self.module_form()

    def reset_module_dict(self):
        self.module_dictionary = {
            "type": "snapdump",
            "subtype": "",
            "stop_io": ""
        }

    def module_form(self):
        self.snpdmp_list = ["Generate OnDemand", "Verify OnDemand", "Delete OnDemand", "Delete All"]
        ttk.Label(self.parent, text="Select reset type", style='Custom.TLabel').grid(row=0, column=0, sticky="w", padx=(10, 5), pady=(0, 5))
        self.snpdmp_options = tk.StringVar()
        self.cb_snpdmp_ops = ttk.Combobox(self.parent, textvariable=self.snpdmp_options, width=30)
        self.cb_snpdmp_ops["values"] = self.snpdmp_list
        self.cb_snpdmp_ops.current(self.snpdmp_list.index('Generate OnDemand'))
        self.cb_snpdmp_ops.grid(row=0, column=1)
        self.cb_snpdmp_ops.bind("<<ComboboxSelected>>", lambda event: self.dropdown_callback(event, "subtype"))

        self.stopio_list = ["Yes", "No"]
        ttk.Label(self.parent, text="Stop IO before reset", style='Custom.TLabel').grid(row=1, column=0, sticky="w", padx=(10, 5), pady=(0, 5))
        self.stopio_option = tk.StringVar()
        self.cb_stopio = ttk.Combobox(self.parent, textvariable=self.stopio_option, width=30)
        self.cb_stopio["values"] = self.stopio_list
        self.cb_stopio.current(self.stopio_list.index('Yes'))
        self.cb_stopio.grid(row=1, column=1)
        self.cb_stopio.bind("<<ComboboxSelected>>", lambda event: self.dropdown_callback(event, "stop_io"))

    def step_text(self):
        self.pull_selected_values()
        txt = "Snapdump operation to perform : {}".format(self.cb_snpdmp_ops.get().upper())
        return txt

    def dropdown_callback(self, event, key):
        new_val = event.widget.get()
        print("Dropdown selected: {}".format(new_val))
        self.module_dictionary[key] = new_val
        print("Config Dict : {}".format(self.module_dictionary))

    def set_step(self, step_dict):
        print("DICT RECIEVED : {}".format(step_dict))
        _map = {"generate ondemand": "Generate OnDemand", "verify ondemand": "Verify OnDemand", "delete ondemand": "Delete OnDemand", "delete all": "Delete All"}
        self.cb_snpdmp_ops.current(self.snpdmp_list.index(_map[step_dict["subtype"].lower()]))
        self.cb_stopio.current(self.stopio_list.index(step_dict["stop_io"].capitalize()))

    def pull_selected_values(self):         
        self.reset_dictionary = {
            "type": "reset",
            "subtype": self.cb_snpdmp_ops.get().lower(),
            "stop_io": self.cb_stopio.get().lower(),
            # "validate_info"
        }

    def get_step(self):
        self.pull_selected_values()
        tmp = deepcopy(self.module_dictionary)
        self.reset_module_dict()
        return tmp


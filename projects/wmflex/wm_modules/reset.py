#!/usr/bin/env python
"""
#####################################################################################
#                                                                                   #
#    Copyright 2023-2022 Broadcom.  All Rights Reserved.  Broadcom Confidential.    #
#     The term "Broadcom" refers to Broadcom Inc. and/or its subsidiaries.          #
#                                                                                   #
#####################################################################################
"""
__doc__ = '''
Defines reset module with its dictionary
'''
__author__ = ["Amitabh Suman"]
__copyright__ = "Copyright 2023-24, The Wingman Flex Project"
__version__ = 'reset_1.0.0'  # Major.Minor.Patch
__credits__ = ["MRPT"]
__email__ = 'dcsg-pt-bangalore-automation.pdl@broadcom.com'
__status__ = 'Development'
__maintainer__ = "Wingman Automation Team"

# Change to next line in case the ER length is > 80 characters
__enhancements__ = '''
DATE(M/D/Y)  CQID            WHO(CQUser)  DESCRIPTION
===============================================================
04/16/23     DCSG01431536    asuman       WM Flex 3.0 : (GUI) : Implement OCR and System Reboot support

'''

import Tkinter as tk
import ttk
from copy import deepcopy
from tooltip import ToolTip
import logging

logger = logging.getLogger("root")


class ResetModule:
    """
    Reset option contains all options needed for Controller, System and Enclosure power resets.
    """
    def __init__(self, parent):
        self.parent = parent
        self.reset_module_dict()
        self.module_form()

    def reset_module_dict(self):
        """
        Module dict for the reset module
        """
        self.reset_dictionary = {
            "type": "reset",
            "subtype": "",
            "stop_io": ""
        }

    def module_form(self):
        """
        Form contains all the required widgets to form the test case.
        """
        self.reset_list = ["OCR", "Reboot", "System Powercycle", "Enclosure On-Off", "Hibernate"]
        ttk.Label(self.parent, text="Select reset type",
                  style='Custom.TLabel').grid(row=0, column=0, sticky="w", padx=(10, 5), pady=(0, 5))
        self.reset_options = tk.StringVar()
        self.cb_reset_ops = ttk.Combobox(self.parent, textvariable=self.reset_options, width=30)
        self.cb_reset_ops["values"] = self.reset_list
        self.cb_reset_ops.current(self.reset_list.index('OCR'))
        self.cb_reset_ops.grid(row=0, column=1)
        self.cb_reset_ops.bind("<<ComboboxSelected>>", lambda event: self.dropdown_callback(event, "subtype"))

        self.stopio_list = ["Yes", "No"]
        ttk.Label(self.parent, text="Stop IO before reset",
                  style='Custom.TLabel').grid(row=3, column=0, sticky="w", padx=(10, 5), pady=(0, 5))
        self.stopio_option = tk.StringVar()
        self.cb_stopio = ttk.Combobox(self.parent, textvariable=self.stopio_option, width=30)
        self.cb_stopio["values"] = self.stopio_list
        self.cb_stopio.current(self.stopio_list.index('Yes'))
        self.cb_stopio.grid(row=3, column=1)
        self.cb_stopio.bind("<<ComboboxSelected>>", lambda event: self.dropdown_callback(event, "stop_io"))
    
    def enclosure_on_off_ops(self):
        """
        If the selected option is Enclosure On and Off, then this option is displayed.
        """
        self.encl_idx_list = [str(i) for i in range(1, 6)]
        ttk.Label(self.parent, text="Select Enclosure Index to powercycle",
                  style='Custom.TLabel').grid(row=1, column=0, sticky="w", padx=(10, 5), pady=(0, 5))
        self.enclIdx_option = tk.StringVar()
        self.cb_encl_idx = ttk.Combobox(self.parent, textvariable=self.enclIdx_option, width=30)
        self.cb_encl_idx["values"] = self.encl_idx_list
        self.cb_encl_idx.current(self.encl_idx_list.index('1'))
        self.cb_encl_idx.grid(row=1, column=1)
        self.cb_encl_idx.bind("<<ComboboxSelected>>", lambda event: self.dropdown_callback(event, "encl_idx"))

        self.encl_op_list = ["Off", "On"]
        ttk.Label(self.parent, text="Select Enclosure operation",
                  style='Custom.TLabel').grid(row=2, column=0, sticky="w", padx=(10, 5), pady=(0, 5))
        self.enclOp_option = tk.StringVar()
        self.cb_encl_op = ttk.Combobox(self.parent, textvariable=self.enclOp_option, width=30)
        self.cb_encl_op["values"] = self.encl_op_list
        self.cb_encl_op.current(self.encl_op_list.index('Off'))
        self.cb_encl_op.grid(row=2, column=1)
        self.cb_encl_op.bind("<<ComboboxSelected>>", lambda event: self.dropdown_callback(event, "encl_op"))

    def reboot_ops(self):
        """
        If the selected option is Reboot or System Powercycle, then this option is displayed.
        """
        logger.info("self.reset_dictionary : {}".format(self.reset_dictionary))
        self.restart_io_list = ["Yes", "No"]
        ttk.Label(self.parent, text="Restart IOs after reset",
                  style='Custom.TLabel').grid(row=2, column=0, sticky="w", padx=(10, 5), pady=(0, 5))
        self.io_option = tk.StringVar()
        self.cb_restartIO = ttk.Combobox(self.parent, textvariable=self.io_option, width=30)
        self.cb_restartIO["values"] = self.restart_io_list
        self.cb_restartIO.current(self.restart_io_list.index(
            self.reset_dictionary.get("restart_io", "No").capitalize()))
        self.cb_restartIO.grid(row=2, column=1)
        self.cb_restartIO.bind("<<ComboboxSelected>>", lambda event: self.dropdown_callback(event, "restart_io"))

        self.reset_with_io_list = ["Yes", "No"]
        ttk.Label(self.parent, text="Reset with IOs in progress",
                  style='Custom.TLabel').grid(row=2, column=0, sticky="w", padx=(10, 5), pady=(0, 5))
        self.reset_option = tk.StringVar()
        self.cb_reset_with_IO = ttk.Combobox(self.parent, textvariable=self.reset_option, width=30)
        self.cb_reset_with_IO["values"] = self.reset_with_io_list
        self.cb_reset_with_IO.current(self.reset_with_io_list.index(
            self.reset_dictionary.get("reset_with_io", 'Yes').capitalize()))
        self.cb_reset_with_IO.grid(row=2, column=1)
        self.cb_reset_with_IO.bind("<<ComboboxSelected>>", lambda event: self.dropdown_callback(event, "reset_with_io"))

    def toggle_options(self):
        """
        Based on what option is selected, widgets needs to be displayed and irrelevant widgets need to be removed.
        This is controller here by the options here.
        """
        if self.cb_reset_ops.get().lower() == "enclosure on-off":
            self.enclosure_on_off_ops()
        
        elif self.cb_reset_ops.get().lower() in ("reboot", "system powercycle"):
            self.reboot_ops()
        
        else:
            for label in self.parent.grid_slaves():
                if int(label.grid_info()["row"]) in (1, 2):
                    label.grid_forget() 

    def step_text(self):
        """
        Presents the step text for this module.
        """
        self.pull_selected_values()
        txt = "Issue : {}".format(self.cb_reset_ops.get().upper())
        return txt

    def dropdown_callback(self, event, key):
        """
        This function takes in the event and the key and changes the value in the module dictionary
        The key value is set to the widget value chosen
        """
        new_val = event.widget.get()
        logger.info("Dropdown selected: {}".format(new_val))
        self.reset_dictionary[key] = new_val
        logger.info("Config Dict : {}".format(self.reset_dictionary))
        self.toggle_options()

    def set_step(self, step_dict):
        """
        The framework uses this function to send the dictionary needed by the module to set its widget to correct
        vlaues as submitted in a test step
        """
        logger.info("Step dictionary as received : {}".format(step_dict))
        self.reset_dictionary = {
            "type": "reset",
            "subtype": step_dict["subtype"].lower().capitalize(),
            "stop_io": step_dict["stop_io"].lower().capitalize()
        }
        
        if self.reset_dictionary["subtype"].lower() in ("reboot", "system powercycle"):
            logger.info("Inside this reboot and system powercycle")
            self.reset_dictionary["restart_io"] = step_dict["restart_io"]
            self.reset_dictionary["reset_with_io"] = step_dict["reset_with_io"]
        _map = {
            "ocr": "OCR",
            "reboot": "Reboot",
            "system powercycle": "System Powercycle",
            "enclosure on-off": "Enclosure On-Off",
            "hibernate": "Hibernate"
        }
        self.cb_reset_ops.current(self.reset_list.index(_map[step_dict["subtype"].lower()]))
        self.toggle_options()
        self.cb_stopio.current(self.stopio_list.index(step_dict["stop_io"].capitalize()))

    def pull_selected_values(self):
        """
        Gets the values from the widgets selected and forms the step dictionary
        """
        self.reset_dictionary = {
            "type": "reset",
            "subtype": self.cb_reset_ops.get().lower(),
            "stop_io": self.cb_stopio.get().lower()
        }
        
        if self.cb_reset_ops.get().lower() in ("reboot", "system powercycle"):
            logger.info("Got into pull selected")
            self.reset_dictionary["restart_io"] = self.cb_restartIO.get().lower()
            self.reset_dictionary["reset_with_io"] = self.cb_reset_with_IO.get().lower()

    def get_step(self):
        """
        Called by the framework to get the values as seen in the module widget
        """
        self.pull_selected_values()
        tmp = deepcopy(self.reset_dictionary)
        self.reset_module_dict()
        return tmp

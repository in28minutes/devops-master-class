# -*- coding: utf-8 -*-
###############################################################################
#                                                                             #
#  Copyright (C) 2021-2023 Broadcom Limited.  All rights reserved.            #
#                                                                             #
###############################################################################
# Date       Who          Description
# ---------- --------     -------------------------------------------------------------
# 04/04/2023 rvats      DCSG01430867: Wingman 3.0: Add GUI support for COL in Wingman flex.

import Tkinter as tk
import ttk
import os
import json
from copy import deepcopy

colmaster = {'Dip': ['SingleDip', 'DoubleDip', 'MultiDip', 'RestoreInterrupt'],
             'Glitch': ['SingleGlitch', 'DoubleGlitch', 'MultiGlitch', 'IncrementalGlitch', 'RandomGlitch'],
             'OCR with offload': ['OcrOffload'],
             'Learn': ['SingleLearn', 'DoubleLearn', 'MultiLearn', 'RetentionTest', 'PinnedcacheLearn'],
             'OCR with pinnedcache': ['OcrPinned']}


class ColModule:
    def __init__(self, parent):
        self.parent = parent
        self.custom_input_entry = {}
        self.init_module_dict()
        self.col_form()

    def init_module_dict(self):
        self.col_dictionary = {
            "type": "col",
            "multidip": "",
            "ocr": "",
            "reboot": "",
            "off_time": "",
            "run_cc": "",
            "coltype": ""
        }

    def col_form(self):
        """IO form with all the input fields to be filled """
        # Select test type
        ttk.Label(self.parent, text="Select test type", style='Custom.TLabel').grid(row=0, column=0, sticky="w",
                                                                                    padx=(10, 5), pady=(0, 5))
        self.test_type = tk.StringVar()
        self.col_test_type = ttk.Combobox(self.parent, textvariable=self.test_type, width=18)
        self.col_test_type["values"] = list(colmaster.keys())
        self.col_test_type.current(0)
        self.col_test_type.grid(row=0, column=1, sticky="w")
        self.col_test_type.bind("<<ComboboxSelected>>", lambda event: self.update_col_combo(event))

        #Select test sub type
        ttk.Label(self.parent, text="Select test sub type", style='Custom.TLabel').grid(row=1, column=0, sticky="w",
                                                                                        padx=(10, 5), pady=(0, 5))
        self.test_sub_type = tk.StringVar()
        self.col_sub_type = ttk.Combobox(self.parent, textvariable=self.test_sub_type, width=18)
        self.col_sub_type.grid(row=1, column=1, sticky="w")
        self.col_sub_type.bind("<<ComboboxSelected>>", lambda event: self.drop_down_selection(event, "coltype"))

        #Select off time
        ttk.Label(self.parent, text="Select pull push delay", style='Custom.TLabel').grid(row=2, column=0, sticky="w",
                                                                                          padx=(10, 5), pady=(0, 5))
        self.off_time_list = ("iteration1", "iteration2")
        self.off_time = tk.StringVar()
        self.off_time_type = ttk.Combobox(self.parent, textvariable=self.off_time, width=18)
        self.off_time_type["values"] = self.off_time_list
        self.off_time_type.current(0)
        self.off_time_type.grid(row=2, column=1, sticky="w")
        self.off_time_type.bind("<<ComboboxSelected>>", lambda event: self.drop_down_selection(event, "off_time"))

        #Select OCR count
        ttk.Label(self.parent, text="Select OCR count", style='Custom.TLabel').grid(row=3, column=0, sticky="w",
                                                                                    padx=(10, 5), pady=(0, 5))
        self.ocr_list = ("iteration1", "iteration2", "custom")
        self.ocr = tk.StringVar()
        self.ocr_type = ttk.Combobox(self.parent, textvariable=self.ocr, width=18)
        self.ocr_type["values"] = self.ocr_list
        self.ocr_type.current(0)
        self.ocr_type.grid(row=3, column=1, sticky="w")
        self.ocr_type.bind("<<ComboboxSelected>>", lambda event: self.drop_down_selection(event, "ocr"))

        #Select Reboot count
        ttk.Label(self.parent, text="Select reboot count", style='Custom.TLabel').grid(row=4, column=0, sticky="w",
                                                                                       padx=(10, 5), pady=(0, 5))
        self.reboot_list = ("iteration1", "iteration2", "custom")
        self.reboot = tk.StringVar()
        self.reboot_type = ttk.Combobox(self.parent, textvariable=self.reboot, width=18)
        self.reboot_type["values"] = self.reboot_list
        self.reboot_type.current(0)
        self.reboot_type.grid(row=4, column=1, sticky="w")
        self.reboot_type.bind("<<ComboboxSelected>>", lambda event: self.drop_down_selection(event, "reboot"))

        #Select multiple dip count
        ttk.Label(self.parent, text="Select multi dip-glitch count", style='Custom.TLabel').grid(row=5, column=0,
                                                                                                 sticky="w",
                                                                                                 padx=(10, 5),
                                                                                                 pady=(0, 5))
        self.multi_list = ("iteration1", "iteration2", "custom")
        self.multidip = tk.StringVar()
        self.multidip_type = ttk.Combobox(self.parent, textvariable=self.multidip, width=18)
        self.multidip_type["values"] = self.multi_list
        self.multidip_type.current(0)
        self.multidip_type.grid(row=5, column=1, sticky="w")
        self.multidip_type.bind("<<ComboboxSelected>>", lambda event: self.drop_down_selection(event, "multidip"))

        #Select Run CC
        ttk.Label(self.parent, text="Select Run Consistency Check", style='Custom.TLabel').grid(row=6, column=0,
                                                                                                sticky="w",
                                                                                                padx=(10, 5),
                                                                                                pady=(0, 5))
        self.run_cc_list = ("False", "True")
        self.run_cc = tk.StringVar()
        self.run_cc_type = ttk.Combobox(self.parent, textvariable=self.run_cc, width=18)
        self.run_cc_type["values"] = self.run_cc_list
        self.run_cc_type.current(0)
        self.run_cc_type.grid(row=6, column=1, sticky="w")
        self.run_cc_type.bind("<<ComboboxSelected>>", lambda event: self.drop_down_selection(event, "run_cc"))

    def update_col_combo(self, event):
        """Update combobox selection"""
        new_val = event.widget.get()
        print("event value: {}".format(new_val))
        self.col_sub_type['values'] = colmaster[self.test_type.get()]

    def drop_down_selection(self, event, key):
        new_val = event.widget.get()
        print("Dropdown selected: {}".format(new_val))
        if new_val.lower() != "custom":
            self.col_dictionary[key] = new_val
            print ("COL custom input entry : {}".format(self.custom_input_entry))
            try:
                self.custom_input_entry[key].grid_forget()
            except Exception as e:
                print "Exception: %s" % e
        else:
            self.custom_entry(event, key)
        print("COL Dict: {}".format(self.col_dictionary))

    def custom_entry(self, event, key):
        """
        Custom entry in case custom input has to be entered.
        :param event: Combobox selected
        :param key: Custom
        :return: None
        """
        widget = event.widget
        row = widget.grid_info()['row']
        col = widget.grid_info()['column']
        self.create_custom_entry_widget(key, row, col)

    def create_custom_entry_widget(self, key, row, col):
        """
        Renders the custom entry box for iteration / duration based on the key
        :param key: Iteration / Duration
        :param row: Row where this widget needs to sit
        :param col: Column where this widget needs to sit
        :return: None
        """
        self.custom_input_entry[key] = tk.Entry(self.parent, width=20)
        self.custom_input_entry[key].grid(row=int(row), column=int(col) + 1, sticky="w")
        self.custom_input_entry[key].bind("<KeyRelease>",
                                          lambda event: self.entrybox_callback(event, key))

    def entrybox_callback(self, event, key):
        """
        Gets the entrybox value and assigns the value to the keys
        :param event: KeyRelease
        :param key: the key in the module dict
        :return: None
        """
        value = event.widget.get().strip()
        print ("Key : {}, Text Box Value : {}".format(key, value))
        self.col_dictionary[key] = value
        print ("COL Dict : {}".format(self.col_dictionary))

    def destroy_custom_widget(self, opts=None):
        """
        Destroys the custom entry widget that appears when the selection is custom
        :param opts: "iteration" and/or "duration"
        :return: None
        """
        if opts is None:
            opts = ["ocr", "reboot" "multidip"]
        for key in opts:
            try:
                self.custom_input_entry[key].destroy()
                del self.custom_input_entry[key]
            except KeyError:
                pass

    def set_step(self, step_dict):
        print("DICT RECIEVED : {}".format(step_dict))
        self.destroy_custom_widget()
        for key in ["ocr", "reboot", "multidip"]:
            if step_dict[key].lower() not in ("iteration1", "iteration2"):
                if key == "ocr":
                    self.ocr_type.current(2)
                    self.create_custom_entry_widget("ocr", 3, 1)
                elif key == "reboot":
                    self.reboot_type.current(2)
                    self.create_custom_entry_widget("reboot", 4, 1)
                elif key == "multidip":
                    self.multidip_type.current(2)
                    self.create_custom_entry_widget("multidip", 5, 1)
                self.custom_input_entry[key].insert(0, step_dict[key])
            else:
                if key == "ocr":
                    self.ocr_type.current(self.ocr_list.index(step_dict["ocr"]))
                elif key == "reboot":
                    self.reboot_type.current(self.reboot_list.index(step_dict["reboot"]))
                elif key == "multidip":
                    self.multidip_type.current(self.multi_list.index(step_dict["multidip"]))
                self.destroy_custom_widget(opts=[key])

    def pull_selected_values(self):
        self.col_dictionary = {
            "type": "col",
            "multidip": self.multidip.get().lower() if self.multidip.get() != 'custom' else
            self.custom_input_entry["multidip"].get(),
            "ocr": self.ocr.get().lower() if self.ocr.get() != 'custom' else self.custom_input_entry["ocr"].get(),
            "reboot": self.reboot.get().lower() if self.reboot.get() != 'custom' else
            self.custom_input_entry["reboot"].get(),
            "off_time": self.off_time.get().lower(),
            "run_cc": False if self.run_cc.get() == 'False' else True,
            "coltype": self.test_sub_type.get().lower()
        }

    def step_text(self):
        """
        Used by the framework to get the step text that appears in the JSON step text
        :return: String (step text)
        """
        self.pull_selected_values()
        txt = "Run COL test type {} .".format(self.col_dictionary["coltype"])
        return txt

    def get_step(self):
        self.pull_selected_values()
        tmp = deepcopy(self.col_dictionary)
        self.init_module_dict()
        return tmp





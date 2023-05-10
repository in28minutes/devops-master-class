# -*- coding: utf-8 -*-
###############################################################################
#                                                                             #
#  Copyright (C) 2021-2023 Broadcom Limited.  All rights reserved.            #
#                                                                             #
###############################################################################
# Date       Who          Description
# ---------- --------     -------------------------------------------------------------
# 03/14/2023 rvats      DCSG01431462: Wingman 3.0: Add GUI support for Medusa IO tool in Wingman flex.
#03/14/2023  rvats      DCSG01430864: Wingman 3.0: Add GUI support for Chaos IO tool in Wingman flex.

import Tkinter as tk
import ttk
import os
import json
from copy import deepcopy


class IoModule:
    def __init__(self, parent):
        self.parent = parent
        self.init_module_dict()
        self.io_form()

    def init_module_dict(self):
        self.io_dictionary = {
            "type": "io",
            "read": "",
            "random": "",
            "pattern": "",
            "tool": "",
            "qd": "",
            "unaligned": "false",
            "size": "",
            "runtime": "",
            "verify": "",
            "completeio": "",
            "raidlevel": "none",
            "journal": ""
        }

    def io_form(self):
        """IO form with all the input fields to be filled """
        # Read percent
        ttk.Label(self.parent, text="Enter Read percentage", style='Custom.TLabel').grid(row=0, column=0, sticky="w",
                                                                                         padx=(10, 5), pady=(0, 5))
        self.read_percent = ttk.Entry(self.parent, width=20)
        self.read_percent.grid(row=0, column=1, sticky="w")
        self.read_percent.insert(0, 50)

        #Random percent
        ttk.Label(self.parent, text="Enter Random percentage", style='Custom.TLabel').grid(row=1, column=0, sticky="w",
                                                                                           padx=(10, 5), pady=(0, 5))
        self.random_percent = ttk.Entry(self.parent, width=20)
        self.random_percent.grid(row=1, column=1, sticky="w")
        self.random_percent.insert(0, 100)

        # Select IO tool
        ttk.Label(self.parent, text="Select IO tool", style='Custom.TLabel').grid(row=2, column=0, sticky="w",
                                                                                  padx=(10, 5), pady=(0, 5))
        self.io_tool_list = ("Medusa", "Chaos")
        self.io_tool = tk.StringVar()
        self.io_tool_type = ttk.Combobox(self.parent, textvariable=self.io_tool, width=18)
        self.io_tool_type["values"] = self.io_tool_list
        self.io_tool_type.current(0)
        self.io_tool_type.grid(row=2, column=1, sticky="w")
        self.io_tool_type.bind("<<ComboboxSelected>>", lambda event: self.drop_down_selection(event, "tool"))

        # Queue depth
        ttk.Label(self.parent, text="Enter Queue Depth", style='Custom.TLabel').grid(row=3, column=0, sticky="w",
                                                                                     padx=(10, 5), pady=(0, 5))
        self.queue_depth = ttk.Entry(self.parent, width=20)
        self.queue_depth.grid(row=3, column=1, sticky="w")
        self.queue_depth.insert(0, 4096)

        # IO size
        ttk.Label(self.parent, text="Enter IO Size", style='Custom.TLabel').grid(row=4, column=0, sticky="w",
                                                                                 padx=(10, 5), pady=(0, 5))
        self.io_size = ttk.Entry(self.parent, width=20)
        self.io_size.grid(row=4, column=1, sticky="w")
        self.io_size.insert(0, '4k')

        # Pattern
        ttk.Label(self.parent, text="Enter IO Pattern", style='Custom.TLabel').grid(row=5, column=0, sticky="w",
                                                                                    padx=(10, 5), pady=(0, 5))
        self.io_pattern = ttk.Entry(self.parent, width=20)
        self.io_pattern.grid(row=5, column=1, sticky="w")
        self.io_pattern.insert(0, 35)

        #Verify IO
        ttk.Label(self.parent, text="Verify IO ", style='Custom.TLabel').grid(row=6, column=0, sticky="w",
                                                                              padx=(10, 5), pady=(0, 5))
        self.verify_io_list = ("False", "True")
        self.verify_io = tk.StringVar()
        self.verify_type = ttk.Combobox(self.parent, textvariable=self.verify_io, width=18)
        self.verify_type["values"] = self.verify_io_list
        self.verify_type.current(0)
        self.verify_type.grid(row=6, column=1, sticky="w")
        self.verify_type.bind("<<ComboboxSelected>>", lambda event: self.drop_down_selection(event, "verify"))

        #Runtime
        ttk.Label(self.parent, text="Select IO Runtime", style='Custom.TLabel').grid(row=7, column=0, sticky="w",
                                                                                     padx=(10, 5), pady=(0, 5))
        self.runtime_list = ("duration1", "duration2", "end_of_test")
        self.runtime = tk.StringVar()
        self.runtime_type = ttk.Combobox(self.parent, textvariable=self.runtime, width=18)
        self.runtime_type["values"] = self.runtime_list
        self.runtime_type.current(0)
        self.runtime_type.grid(row=7, column=1, sticky="w")
        self.runtime_type.bind("<<ComboboxSelected>>",
                               lambda event: self.drop_down_selection(event, "runtime"))

        #Complete IO before next step
        ttk.Label(self.parent, text="Complete IO Before Next Step", style='Custom.TLabel').grid(row=8, column=0,
                                                                                                sticky="w",
                                                                                                padx=(10, 5),
                                                                                                pady=(0, 5))
        self.complete_list = ("False", "True")
        self.complete_io = tk.StringVar()
        self.complete_io_type = ttk.Combobox(self.parent, textvariable=self.complete_io, width=18)
        self.complete_io_type["values"] = self.complete_list
        self.complete_io_type.current(0)
        self.complete_io_type.grid(row=8, column=1, sticky="w")
        self.complete_io_type.bind("<<ComboboxSelected>>",
                                   lambda event: self.drop_down_selection(event, "completeio"))

        # Unaligned IO
        ttk.Label(self.parent, text="Select Unaligned Type", style='Custom.TLabel').grid(row=9, column=0,
                                                                                         sticky="w", padx=(10, 5),
                                                                                         pady=(0, 5))
        self.unaligned_list = ("False", "True")
        self.unaligned_io = tk.StringVar()
        self.unaligned_type = ttk.Combobox(self.parent, textvariable=self.unaligned_io, width=18)
        self.unaligned_type["values"] = self.unaligned_list
        self.unaligned_type.current(0)
        self.unaligned_type.grid(row=9, column=1, sticky="w")
        self.unaligned_type.bind("<<ComboboxSelected>>",
                                 lambda event: self.drop_down_selection(event, "unaligned"))
        self.unaligned_type.config(state='disabled')

    def drop_down_selection(self, event, key):
        new_val = event.widget.get()
        print("Dropdown selected: {}".format(new_val))
        self.io_dictionary[key] = new_val
        print("IO Dict: {}".format(self.io_dictionary))

    def set_step(self, step_dict):
        print("DICT RECIEVED : {}".format(step_dict))
        self.read_percent.delete(0, tk.END)
        self.read_percent.insert(0, step_dict["read"])
        self.random_percent.delete(0, tk.END)
        self.random_percent.insert(0, step_dict["random"])
        self.io_pattern.delete(0, tk.END)
        self.io_pattern.insert(0, step_dict["pattern"])
        self.io_tool_type.current(self.io_tool_list.index(step_dict["tool"]))
        self.queue_depth.delete(0, tk.END)
        self.queue_depth.insert(0, step_dict["qd"])
        self.io_size.delete(0, tk.END)
        self.io_size.insert(0, step_dict["size"])
        self.runtime_type.current(self.runtime_list.index(step_dict["runtime"]))
        self.verify_type.current(self.verify_io_list.index('True' if step_dict["verify"] else 'False'))
        self.complete_io_type.current(self.complete_list.index('True' if step_dict["completeio"] else 'False'))

    def pull_selected_values(self):
        self.io_dictionary = {
            "type": "io",
            "read": self.read_percent.get(),
            "random": self.random_percent.get(),
            "pattern": self.io_pattern.get(),
            "tool": self.io_tool_type.get(),
            "qd": self.queue_depth.get(),
            "unaligned": "false",
            "size": self.io_size.get(),
            "runtime": self.runtime_type.get() if self.runtime_type.get() != "end_of_test" else "-1",
            "verify": False if self.verify_type.get() == 'False' else True,
            "completeio": False if self.complete_io_type.get() == 'False' else True,
            "raidlevel": "none",
            "journal": ""
        }

    def step_text(self):
        """
        Used by the framework to get the step text that appears in the JSON step text
        :return: String (step text)
        """
        self.pull_selected_values()
        txt = "Run {} IO for a duration of {} .".format(self.io_dictionary["tool"],
                                                        self.io_dictionary["runtime"])
        return txt

    def get_step(self):
        self.pull_selected_values()
        tmp = deepcopy(self.io_dictionary)
        self.init_module_dict()
        return tmp





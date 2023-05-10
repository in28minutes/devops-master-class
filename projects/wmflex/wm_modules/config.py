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
Defines entire static config module with its dictionary
'''
__author__ = ["Amitabh Suman"]
__copyright__ = "Copyright 2023-24, The Wingman Flex Project"
__version__ = 'config_2.0.0'  # Major.Minor.Patch
__credits__ = ["MRPT"]
__email__ = 'dcsg-pt-bangalore-automation.pdl@broadcom.com'
__status__ = 'Development'
__maintainer__ = "Wingman Automation Team"

# Change to next line in case the ER length is > 80 characters
__enhancements__ = '''
DATE(M/D/Y)  CQID            WHO(CQUser)  DESCRIPTION
===============================================================
03/07/23     DCSG01431093    asuman       Ph1: Wingman 3.0: New GUI framework for flex config requirements
03/24/23     DCSG01431093    asuman       Ph2: Wingman 3.0: New GUI framework for flex config requirements
04/14/23     DCSG01431509    asuman       Ph2: WM Flex 3.0 : (GUI) : Implement Add-Delete Config, Add-Delete JBOD \
                                          (non-raid), Stop IO
'''

import Tkinter as tk
import ttk
from copy import deepcopy
from tooltip import ToolTip
import logging

logger = logging.getLogger("root")


class ConfigModule:
    def __init__(self, parent):
        self.parent = parent
        self.reset_module_dict()
        self.config_form()

    def reset_module_dict(self):
        """
        Defines the module dictionary for Static Config step
        :return: None
        """
        self.config_dictionary = {
            "type": "staticconfig",
            "config":
                    [
                        {
                            "raid": "",
                            "stripe": "",
                            "pdcount": "",
                            "dtabcount": "",
                            "size": "",
                            "pf_size": "",
                            "exhaust": "",
                            "repeat": "",
                            "hotspare": "",
                            "readpolicy": "",
                            "spans": "",
                            "writepolicy": ""
                        }
                    ]
                }

    def config_form(self):
        """
        This is the main function that basically renders the form for the Static Config module
        :return: None
        """
        self.raid_values_list = ("R0", "R1", "R5", "R6", "R10", "R50", "R60")
        ttk.Label(self.parent, text="Choose RAID to create", style='Custom.TLabel').grid(row=0, column=0, sticky="w",
                                                                                         padx=(10, 5), pady=(0, 5))
        self.raid_level = tk.StringVar()
        self.cb_raid_type = ttk.Combobox(self.parent, textvariable=self.raid_level, width=30)
        self.cb_raid_type["values"] = self.raid_values_list
        self.cb_raid_type.current(self.raid_values_list.index('R0'))
        self.cb_raid_type.grid(row=0, column=1)
        self.cb_raid_type.bind("<<ComboboxSelected>>", lambda event: self.dropdown_callback(event, "raid"))
        self.cb_raid_type.bind("<Enter>", lambda _: ToolTip().notify(self.cb_raid_type,
                                                                     "Choose RAID",
                                                                     "Choose RAID for Static step"))

        ttk.Label(self.parent, text="Choose Strip size", style='Custom.TLabel').grid(row=1, column=0, sticky="w",
                                                                                     padx=(10, 5), pady=(0, 5))
        self.ss_size_list = ["64", "256", "Random"]
        self.ss_size = tk.StringVar()
        self.cb_ssize = ttk.Combobox(self.parent, textvariable=self.ss_size, width=30)
        self.cb_ssize["values"] = self.ss_size_list
        self.cb_ssize.current(self.ss_size_list.index('Random'))
        self.cb_ssize.grid(row=1, column=1)
        self.cb_ssize.bind("<<ComboboxSelected>>", lambda event: self.dropdown_callback(event, "stripe"))

        ttk.Label(self.parent, text="Choose number of Drives", style='Custom.TLabel').grid(row=2, column=0, sticky="w",
                                                                                           padx=(10, 5), pady=(0, 5))
        self.num_drives_list = [str(x) for x in range(1, 33)]
        self.num_drives = tk.StringVar()
        self.cb_num_drives = ttk.Combobox(self.parent, textvariable=self.num_drives, width=30)
        self.cb_num_drives["values"] = self.num_drives_list
        self.cb_num_drives.current(self.num_drives_list.index('5'))
        self.cb_num_drives.grid(row=2, column=1)
        self.cb_num_drives.bind("<<ComboboxSelected>>", lambda event: self.dropdown_callback(event, "pdcount"))

        ttk.Label(self.parent, text="Choose number of DTABs",
                  style='Custom.TLabel').grid(row=3, column=0, sticky="w", padx=(10, 5), pady=(0, 5))
        self.num_dtabs_list = [str(x) for x in range(0, 33)]
        self.selected_dtabs = tk.StringVar()
        self.cb_num_dtabs = ttk.Combobox(self.parent, textvariable=self.selected_dtabs, width=30)
        self.cb_num_dtabs["values"] = self.num_dtabs_list
        self.cb_num_dtabs.current(self.num_dtabs_list.index('0'))
        self.cb_num_dtabs.grid(row=3, column=1)
        self.cb_num_dtabs.bind("<<ComboboxSelected>>", lambda event: self.dropdown_callback(event, "dtabcount"))

        ttk.Label(self.parent, text="Enter VD size",
                  style='Custom.TLabel').grid(row=4, column=0, sticky="w", padx=(10, 5), pady=(0, 5))
        self.entry_vd_size = ttk.Entry(self.parent, width=23)
        self.entry_vd_size.bind("<KeyRelease>",
                                lambda event: self.entrybox_callback(event, "size"))
        self.entry_vd_size.grid(row=4, column=1, sticky="w")
        self.entry_vd_size.insert(0, "10")

        self.cb_size = ["MB", "GB", "TB"]
        self.selected_size_unit = tk.StringVar()
        self.cb_pf_size = ttk.Combobox(self.parent, textvariable=self.selected_size_unit, width=6)
        self.cb_pf_size["values"] = self.cb_size
        self.cb_pf_size.current(self.cb_size.index('GB'))
        self.cb_pf_size.grid(row=4, column=1, sticky="e")
        self.cb_pf_size.bind("<<ComboboxSelected>>", lambda event: self.dropdown_callback(event, "pf_size"))

        ttk.Label(self.parent, text="Choose number of VDs",
                  style='Custom.TLabel').grid(row=5, column=0, sticky="w", padx=(10, 5), pady=(0, 5))
        self.num_vds_list = [str(x) for x in range(1, 241)]
        self.selected_num_vds = tk.StringVar()
        self.cb_num_vds = ttk.Combobox(self.parent, textvariable=self.selected_num_vds, width=30)
        self.cb_num_vds["values"] = self.num_vds_list
        self.cb_num_vds.current(self.num_vds_list.index('1'))
        self.cb_num_vds.grid(row=5, column=1)
        self.cb_num_vds.bind("<<ComboboxSelected>>", lambda event: self.dropdown_callback(event, "vdcount"))

        ttk.Label(self.parent, text="Choose number of Hotspares (DHS)",
                  style='Custom.TLabel').grid(row=6, column=0, sticky="w", padx=(10, 5), pady=(0, 5))
        self.num_dhs_list = [str(x) for x in range(0, 241)]
        self.selected_num_dhs = tk.StringVar()
        self.cb_num_dhs = ttk.Combobox(self.parent, textvariable=self.selected_num_dhs, width=30)
        self.cb_num_dhs["values"] = self.num_dhs_list
        self.cb_num_dhs.current(self.num_dhs_list.index('0'))
        self.cb_num_dhs.grid(row=6, column=1)
        self.cb_num_dhs.bind("<<ComboboxSelected>>", lambda event: self.dropdown_callback(event, "hotspare"))

        ttk.Label(self.parent, text="Choose VD init",
                  style='Custom.TLabel').grid(row=7, column=0, sticky="w", padx=(10, 5), pady=(0, 5))
        self.vd_init_type_list = ["Fast", "Full", "Auto BGI", "None"]
        self.selected_init = tk.StringVar()
        self.cb_vd_init = ttk.Combobox(self.parent, textvariable=self.selected_init, width=30)
        self.cb_vd_init["values"] = self.vd_init_type_list
        self.cb_vd_init.current(self.vd_init_type_list.index('Fast'))
        self.cb_vd_init.grid(row=7, column=1)
        self.cb_vd_init.bind("<<ComboboxSelected>>", lambda event: self.dropdown_callback(event, "init"))

        ttk.Label(self.parent, text="Choose number of Spans",
                  style='Custom.TLabel').grid(row=8, column=0, sticky="w", padx=(10, 5), pady=(0, 5))
        self.span_list = [x for x in range(1, 9)]
        self.selected_span = tk.StringVar()
        self.cb_spans = ttk.Combobox(self.parent, textvariable=self.selected_span, width=30)
        self.cb_spans["values"] = self.span_list
        self.cb_spans.current(self.span_list.index(1))
        self.cb_spans.grid(row=8, column=1)
        self.cb_spans.bind("<<ComboboxSelected>>", lambda event: self.dropdown_callback(event, "spans"))

        ttk.Label(self.parent, text="Choose Write Policy",
            style='Custom.TLabel').grid(row=9, column=0, sticky="w", padx=(10, 5), pady=(0, 5))
        self.write_list = ["WB", "WT", "AWB"]
        self.selected_write = tk.StringVar()
        self.cb_write = ttk.Combobox(self.parent, textvariable=self.selected_write, width=30)
        self.cb_write["values"] = self.write_list
        self.cb_write.current(self.write_list.index("WB"))
        self.cb_write.grid(row=9, column=1)
        self.cb_write.bind("<<ComboboxSelected>>", lambda event: self.dropdown_callback(event, "spans"))

        ttk.Label(self.parent, text="Choose Read Policy",
            style='Custom.TLabel').grid(row=10, column=0, sticky="w", padx=(10, 5), pady=(0, 5))
        self.read_list = ["RA", "NORA"]
        self.selected_read = tk.StringVar()
        self.cb_read = ttk.Combobox(self.parent, textvariable=self.selected_read, width=30)
        self.cb_read["values"] = self.read_list
        self.cb_read.current(self.read_list.index("RA"))
        self.cb_read.grid(row=10, column=1)
        self.cb_read.bind("<<ComboboxSelected>>", lambda event: self.dropdown_callback(event, "spans"))

        ttk.Label(self.parent, text="Enter repeat count",
                  style='Custom.TLabel').grid(row=11, column=0, sticky="w", padx=(10, 5), pady=(0, 5))
        self.entry_repeat = ttk.Entry(self.parent, width=15)
        self.entry_repeat.bind("<KeyRelease>",
                                lambda event: self.entrybox_callback(event, "repeat"))
        self.entry_repeat.grid(row=11, column=1, sticky="w")
        self.entry_repeat.insert(0, "1")
        self.entry_repeat.bind("<Enter>", lambda _: ToolTip().notify(self.entry_repeat,
                                                                     "Choose Repeat",
                                                                     "Number of DGs to create"))

    def dropdown_callback(self, event, key):
        """
        Gets the dropdown value and modifies the dictionary value
        :param event: ComboboxSelected event
        :param key: Key in the dictionary associated to the dropdown
        :return: None
        """
        new_val = event.widget.get()
        logger.info("Dropdown selected: {}".format(new_val))
        self.config_dictionary[key] = new_val
        logger.info("Config Dict : {}".format(self.config_dictionary))

    def entrybox_callback(self, event, key):
        """
        Gets the entrybox value and assigns the value to the keys
        :param event: KeyRelease
        :param key: the key in the module dict
        :return: None
        """
        value = event.widget.get().strip()
        logger.info("Key : {}, Text Box Value : {}".format(key, value))
        self.config_dictionary[key] = value
        logger.info("Config Dict : {}".format(self.config_dictionary))

    def set_step(self, step_dict):
        """
        This is the function that the framework uses and send the data to the module to set the widget values of the
        module to the values as submitted in the test step
        :param step_dict: The step dict for step selected
        :return: None
        """
        logger.info("DICT RECIEVED : {}".format(step_dict))
        self.cb_raid_type.current(self.raid_values_list.index(step_dict["config"][0]["raid"]))
        self.cb_ssize.current(self.ss_size_list.index(step_dict["config"][0]["stripe"].capitalize()))
        self.cb_num_drives.current(self.num_drives_list.index(step_dict["config"][0]["pdcount"]))
        self.cb_num_dtabs.current(self.num_dtabs_list.index(step_dict["config"][0]["dtabcount"]))
        self.cb_num_vds.current(self.num_vds_list.index(step_dict["config"][0]["vdcount"]))

        init_map = {"fast" : "Fast", "full": "Full", "auto bgi": "Auto BGI", "none": "None"}
        self.cb_vd_init.current(self.vd_init_type_list.index(init_map[step_dict["config"][0]["init"]]))
        self.cb_num_dhs.current(self.num_dhs_list.index(step_dict["config"][0]["hotspare"]))
        self.entry_vd_size.delete(0, tk.END)

        _size = step_dict["config"][0]["size"][:-2]
        _unit = step_dict["config"][0]["size"][-2:]
        self.entry_vd_size.insert(0, _size)
        self.cb_pf_size.current(self.cb_size.index(_unit.upper()))

        self.cb_write.current(self.write_list.index(step_dict["config"][0]["writepolicy"].upper()))
        self.cb_read.current(self.read_list.index(step_dict["config"][0]["readpolicy"].upper()))

    def pull_selected_values(self):
        """
        Get the values of all the widgets when called
        :return: None
        """
        logger.info("Config dict : {}".format(self.config_dictionary))
        self.config_dictionary = {
            "type": "staticconfig",
            "config":
                    [
                        {
                            "raid": self.cb_raid_type.get(),
                            "stripe": self.cb_ssize.get().lower(),
                            "pdcount": self.cb_num_drives.get(),
                            "dtabcount": self.cb_num_dtabs.get(),
                            "vdcount": self.cb_num_vds.get(),
                            "size": self.entry_vd_size.get() + self.cb_pf_size.get().lower(),
                            "init": self.cb_vd_init.get().lower(),
                            "repeat": self.entry_repeat.get(),
                            "hotspare": self.cb_num_dhs.get(),
                            "spans": self.cb_spans.get(),
                            "writepolicy": self.cb_write.get().lower(),
                            "readpolicy": self.cb_read.get().lower(),
                        }
                    ],
            "exhaust": 0
        }
        logger.info("Config dict : {}".format(self.config_dictionary))

    def step_text(self):
        """
        Used by the framework to get the step text that appears in the JSON step text
        :return: String (step text)
        """
        self.pull_selected_values()
        txt = "Create RAID {} ({} VDs) with {} drives.".format(self.config_dictionary["config"][0]["raid"],
                                                               self.config_dictionary["config"][0]["vdcount"],
                                                               self.config_dictionary["config"][0]["pdcount"])
        return txt

    def get_step(self):
        """
        Used by framework and returns the value of the widget in the format as decided.
        :return: Dict (step dictionary)
        """
        self.pull_selected_values()
        tmp = deepcopy(self.config_dictionary)
        self.reset_module_dict()
        return tmp


# Class for Delete Config. Handles the JBOD Conversion as well.
class DeleteConfig:
    def __init__(self, parent):
        self.parent = parent
        self.reset_module_dict()
        self.delete_config_form()

    def reset_module_dict(self):
        """
        Defines the module dictionary for Static Config step
        :return: None
        """
        self.delete_config_dictionary = {
            "type": "delete",
            "raid": "",
            "pattern": "",
            "stop_io": "",
            "clear_config": "",
            "jbod_to_ug": ""
        }

    def delete_config_form(self):
        """
        This is the main function that basically renders the form for the Static Config module
        :return: None
        """
        self.raid_values_list = ("R0", "Mirrored", "Parity", "Spanned", "All")
        ttk.Label(self.parent, text="Choose RAID to delete", style='Custom.TLabel').grid(row=0, column=0, sticky="w",
                                                                                         padx=(10, 5), pady=(0, 5))
        self.raid_level = tk.StringVar()
        self.cb_raid_type = ttk.Combobox(self.parent, textvariable=self.raid_level, width=30)
        self.cb_raid_type["values"] = self.raid_values_list
        self.cb_raid_type.current(self.raid_values_list.index('All'))
        self.cb_raid_type.grid(row=0, column=1)
        self.cb_raid_type.bind("<<ComboboxSelected>>", lambda event: self.dropdown_callback(event, "raid"))
        self.cb_raid_type.bind("<Enter>", lambda _: ToolTip().notify(self.cb_raid_type,
                                                                    "Choose RAID",
                                                                    "Step reference overrides this selection"))
        ttk.Label(self.parent, text="Choose delete/conversion pattern", style='Custom.TLabel').grid(row=1, column=0, sticky="w",
                                                                                     padx=(10, 5), pady=(0, 5))
        self.delete_pattern_list = ["All", "Odd", "Even"]
        self.delete_pattern = tk.StringVar()
        self.cb_del_patrn = ttk.Combobox(self.parent, textvariable=self.delete_pattern, width=30)
        self.cb_del_patrn["values"] = self.delete_pattern_list
        self.cb_del_patrn.current(self.delete_pattern_list.index('All'))
        self.cb_del_patrn.grid(row=1, column=1)
        self.cb_del_patrn.bind("<Enter>", lambda _: ToolTip().notify(self.cb_del_patrn,
                                                                    "Delete Pattern",
                                                                    "Odd Even is decided based on VD/JBOD ID"))
        self.cb_del_patrn.bind("<<ComboboxSelected>>", lambda event: self.dropdown_callback(event, "pattern"))

        ttk.Label(self.parent, text="Stop IO before delete", style='Custom.TLabel').grid(row=2, column=0, sticky="w",
                                                                                           padx=(10, 5), pady=(0, 5))
        self.stop_io_list = ["True", "False"]
        self.stop_io = tk.StringVar()
        self.cb_stop_io = ttk.Combobox(self.parent, textvariable=self.stop_io, width=30)
        self.cb_stop_io["values"] = self.stop_io_list
        self.cb_stop_io.current(self.stop_io_list.index("False"))
        self.cb_stop_io.grid(row=2, column=1)
        self.cb_stop_io.bind("<<ComboboxSelected>>", lambda event: self.dropdown_callback(event, "stop_io"))

        ttk.Label(self.parent, text="Clear all config (JBODs included)",
                  style='Custom.TLabel').grid(row=3, column=0, sticky="w", padx=(10, 5), pady=(0, 5))
        self.del_config_list = ["True", "False"]
        self.del_config = tk.StringVar()
        self.cb_del_cfg = ttk.Combobox(self.parent, textvariable=self.del_config, width=30)
        self.cb_del_cfg["values"] = self.del_config_list
        self.cb_del_cfg.current(self.del_config_list.index("True"))
        self.cb_del_cfg.grid(row=3, column=1)
        self.cb_del_cfg.bind("<<ComboboxSelected>>", lambda event: self.dropdown_callback(event, "clear_config"))

        ttk.Label(self.parent, text="Convert JBODs to UG",
                  style='Custom.TLabel').grid(row=4, column=0, sticky="w", padx=(10, 5), pady=(0, 5))
        self.jbod_ug_list = ["True", "False"]
        self.conv_jbod = tk.StringVar()
        self.cb_jbod_ug = ttk.Combobox(self.parent, textvariable=self.conv_jbod, width=30)
        self.cb_jbod_ug["values"] = self.del_config_list
        self.cb_jbod_ug.current(self.del_config_list.index("True"))
        self.cb_jbod_ug.grid(row=4, column=1)
        self.cb_jbod_ug.bind("<<ComboboxSelected>>", lambda event: self.dropdown_callback(event, "jbod_to_ug"))

    def dropdown_callback(self, event, key):
        """
        Gets the dropdown value and modifies the dictionary value
        :param event: ComboboxSelected event
        :param key: Key in the dictionary associated to the dropdown
        :return: None
        """
        new_val = event.widget.get()
        logger.info("Dropdown selected: {}".format(new_val))
        self.delete_config_dictionary[key] = new_val
        logger.info("Config Dict : {}".format(self.delete_config_dictionary))

    def entrybox_callback(self, event, key):
        """
        Gets the entrybox value and assigns the value to the keys
        :param event: KeyRelease
        :param key: the key in the module dict
        :return: None
        """
        value = event.widget.get().strip()
        logger.info("Key : {}, Text Box Value : {}".format(key, value))
        self.delete_config_dictionary[key] = value
        logger.info("Config Dict : {}".format(self.delete_config_dictionary))

    def set_step(self, step_dict):
        """
        This is the function that the framework uses and send the data to the module to set the widget values of the
        module to the values as submitted in the test step
        :param step_dict: The step dict for step selected
        :return: None
        """
        logger.info("DICT RECIEVED : {}".format(step_dict))
        self.cb_raid_type.current(self.raid_values_list.index(step_dict["raid"].capitalize()))
        self.cb_del_patrn.current(self.delete_pattern_list.index(step_dict["pattern"].capitalize()))
        self.cb_stop_io.current(self.stop_io_list.index(step_dict["stop_io"].capitalize()))
        self.cb_del_cfg.current(self.del_config_list.index(step_dict["clear_config"].capitalize()))
        self.cb_jbod_ug.current(self.jbod_ug_list.index(step_dict["jbod_to_ug"].capitalize()))

    def pull_selected_values(self):
        """
        Get the values of all the widgets when called
        :return: None
        """
        logger.info("Config dict : {}".format(self.delete_config_dictionary))
        self.delete_config_dictionary = {
            "type": "delete",
            "raid": self.cb_raid_type.get().lower(),
            "pattern": self.cb_del_patrn.get().lower(),
            "stop_io": self.cb_stop_io.get().lower(),
            "clear_config": self.cb_del_cfg.get().lower(),
            "jbod_to_ug": self.cb_jbod_ug.get().lower()
        }
        logger.info("Config dict : {}".format(self.delete_config_dictionary))

    def step_text(self):
        """
        Used by the framework to get the step text that appears in the JSON step text
        :return: String (step text)
        """
        self.pull_selected_values()
        txt = "Delete Config details:\n\tRAID : {},\n\tJBOD : {},\n\tPattern : {},\n\tClear Config : {},\n\tStop IOs : {}".format(
            self.delete_config_dictionary["raid"].upper(),
            self.delete_config_dictionary["jbod_to_ug"].upper(),
            self.delete_config_dictionary["pattern"].upper(),
            self.delete_config_dictionary["clear_config"].upper(),
            self.delete_config_dictionary["stop_io"].upper()
            )
        return txt

    def get_step(self):
        """
        Used by framework and returns the value of the widget in the format as decided.
        :return: Dict (step dictionary)
        """
        self.pull_selected_values()
        tmp = deepcopy(self.delete_config_dictionary)
        self.reset_module_dict()
        return tmp

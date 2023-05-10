#!/usr/bin/env python
"""
#####################################################################################
#                                                                                   #
#    Copyright 2023-2022 Broadcom.  All Rights Reserved.  Broadcom Confidential.    #
#     The term "Broadcom" refers to Broadcom Inc. and/or its subsidiaries.          #
#                                                                                   #
#####################################################################################
"""
__doc__ = """
    FWOP module used for Controller FW upgrade/downgrade operations with different methods
                         PD FW upgrade/downgrade operations with different methods
                         Enclosure FW upgrade/downgrade operations with different methods
"""
__author__ = ["Santhosh Prabhu"]
__copyright__ = "Copyright 2023-24, The Wingman Flex Project"
__version__ = 'fwop_1.0.0'
__credits__ = ["MRPT"]
__email__ = 'dcsg-pt-bangalore-automation.pdl@broadcom.com'
__status__ = 'Development'
__maintainer__ = "Wingman Automation Team"


__enhancements__ = '''
DATE(M/D/Y)  CQID            WHO(CQUser)  DESCRIPTION
===============================================================
04/10/23     DCSG01431391    saprabhu       Wingman 3.0: Add support for Firmware update GUI module in Wingman Flex
'''

import Tkinter as tk
from Tkinter import END
from ttk import *
import os
from copy import deepcopy
from custom_styles import CustomStyles
import logging
import tkFileDialog
import tkMessageBox


logger = logging.getLogger('root')


class FwOps:
    def __init__(self, parent):
        self.file_opt = options = {}
        self.parent = parent
        self.create_tab()
        self.ctrl_fwops_form(self.tab_ctrl_fw_update)
        self.device_fwops_form(self.tab_dev_fw_update)

    def create_tab(self):
        logger.info("Inside this")
        self.notebook_fw = Notebook(self.parent)
        self.tab_ctrl_fw_update = Frame(self.notebook_fw)
        self.tab_dev_fw_update = Frame(self.notebook_fw)
        self.notebook_fw.add(self.tab_ctrl_fw_update, text='Ctrl FW')
        self.notebook_fw.add(self.tab_dev_fw_update, text='Device FW')
        self.notebook_fw.pack(expand=1, fill="both")

    def ctrl_fwops_form(self, tab):
        """
                To form a controller fw flash GUI
        """
        self.fw_update_frame = tab
        Label(self.fw_update_frame, text=" Select FW file path : ",style='Custom.TLabel').grid(row=0, column=0, padx=1, sticky="w")
        self.fw_file_path = Entry(self.fw_update_frame, width=40, takefocus=1)
        self.fw_file_path.grid(row=0, column=1, padx=1, pady=5, columnspan=4, sticky="w")
        Button(self.fw_update_frame, text='Browse', command=self.get_file_path, width=13).grid(row=0,
                                                                                               column=5, padx=1)
        Label(self.fw_update_frame, text=" Select FW update type : ",
              style='Custom.TLabel').grid(row=1, column=0, padx=1, sticky="w")
        variable_enable_fp = tk.StringVar()
        choices = ( 'OFU', 'Reboot', 'Power_Cycle', 'FW_Flash_only', 'Abrupt_FW_Flash', 'Verify_Last_FW_Flash' )
        self.w_enable_fp = Combobox(self.fw_update_frame, textvariable=choices[0],
                                        state='readonly', width=20)
        self.w_enable_fp['values'] = choices
        self.w_enable_fp.current(0)
        self.w_enable_fp.grid(row=1, column=1, padx=1, pady=5, sticky="w")
        # self.w_enable_fp.bind("<<ComboboxSelected>>", self.newselection)

        self.verify_ver = Label(self.fw_update_frame, text=" FW version verify : ",style='Custom.TLabel')

        self.verifty_ver_tick_var = tk.IntVar(value=1)
        self.verifty_ver_tick = Checkbutton(self.fw_update_frame, text="Yes", variable=self.verifty_ver_tick_var)
        self.verify_ver.grid(row=3, column=0, padx=2, pady=10, sticky="w")
        self.verifty_ver_tick.grid(row=3, column=1, padx=2, pady=10, columnspan=4, sticky="w")

        self.io_run = Label(self.fw_update_frame, text=" Reboot while IO's are in progress: ",
                               style='Custom.TLabel')
        self.vrble = tk.IntVar()
        self.io_run_vble = Checkbutton(self.fw_update_frame, text="Yes", variable=self.vrble)
        self.fw_update_frame.update_idletasks()

    def device_fwops_form(self, tab):
        """
        To form a device fw flash GUI
        """
        self.enpdfw_update_frame = tab
        Label(self.enpdfw_update_frame, text=" Select Device Type : ",
                 style='Custom.TLabel').grid(row=0, column=0, padx=2, sticky="w")
        self.tmp_var_1 = tk.StringVar()
        self.enpdfw_update_type = Combobox(self.enpdfw_update_frame, textvariable=
        self.tmp_var_1,
                                               state='readonly', width=20)
        self.enpdfw_update_type['values'] = ['Enclosure', 'PD']
        self.enpdfw_update_type.current(0)
        self.enpdfw_update_type.grid(row=0, column=1, padx=2, pady=10, sticky="w")
        self.pd_string =Label(self.enpdfw_update_frame, text=" Type PD string (eg: 50:3) : ",
                                  style='Custom.TLabel')
        self.pd = Entry(self.enpdfw_update_frame, width=20)
        self.enclosure_string = Label(self.enpdfw_update_frame, text=" Select enclosure : ",
                                         style='Custom.TLabel')
        self.fd_unused = tk.StringVar()
        self.enclosure = Combobox(self.enpdfw_update_frame, textvariable=self.fd_unused,
                                      font=("segoe", "9", "bold"), width=20)

        self.enclosure['values'] = ["ENC " + str(i + 1) for i in range(0, 10)]
        self.enpdfw_update_type.bind("<<ComboboxSelected>>", self.typeselection)
        Label(self.enpdfw_update_frame, text=" Select FW file path : ",
                 style='Custom.TLabel').grid(row=2, column=0, padx=1, sticky="w")
        self.fw_file_path_enpd = Entry(self.enpdfw_update_frame, width=40, takefocus=1)
        self.fw_file_path_enpd.grid(row=2, column=1, padx=1, pady=5, columnspan=4, sticky="w")

        Button(self.enpdfw_update_frame, text='Browse', command=self.get_file_path_enpd, width=13).grid(row=2,
                                                                                                            column=5,
                                                                                                            padx=1)
        Label(self.enpdfw_update_frame, text=" Select Mode : ",
                 style='Custom.TLabel').grid(row=3, column=0, padx=1, sticky="w")
        self.tmp_var_2 = tk.StringVar()
        self.enpdfw_update_mode = Combobox(self.enpdfw_update_frame, textvariable=
        self.tmp_var_2, state='readonly', width=20)
        self.enpdfw_update_mode['values'] = ['5', '7', 'E', 'F']
        self.enpdfw_update_mode.current(0)
        self.enpdfw_update_mode.grid(row=3, column=1, padx=2, pady=10, sticky="w")


    def get_step(self):
        data = self.print_data()
        tmp = deepcopy(data)
        return tmp

    def step_text(self):
        dat = self.get_step()
        if dat['subtype'] == "Ctrl FW" :
            txt = "Perform Controller FW update(%s)"%dat['method']
        else:
            txt = "Perform %s FW update"%dat['device_type']
        return txt



    def typeselection(self,event):
        self.value_enpd = self.enpdfw_update_type.get().lower()
        if self.value_enpd == "pd":
            self.enclosure_string.grid_forget()
            self.enclosure.grid_forget()
            self.pd_string.grid(row=1, column=0, padx=2, pady=10, sticky="w")
            self.pd.grid(row=1, column=1, padx=2, pady=10, sticky="w")
        elif self.value_enpd == "enclosure":
            self.pd_string.grid_forget()
            self.pd.grid_forget()
            self.enclosure_string.grid(row=1, column=0, padx=2, pady=10, sticky="w")
            self.enclosure.grid(row=1, column=1, padx=2, pady=10, sticky="w")
        self.enpdfw_update_type.update_idletasks()

    def get_file_path(self):
        self.filenames = tkFileDialog.askopenfilename(**self.file_opt)
        self.fw_file_path.delete(0, END)
        self.fw_file_path.insert(0, self.filenames)

    def get_file_path_enpd(self):
        self.filenames_enpd = tkFileDialog.askopenfilename()
        self.fw_file_path_enpd.delete(0, END)
        self.fw_file_path_enpd.insert(0, self.filenames_enpd)

    def print_data(self):
        """
        To get the user seleted value into the dictionary
        return:Dictionary
        """
        current_tab = self.notebook_fw.tab(self.notebook_fw.select(), "text")
        if current_tab == 'Ctrl FW':
            # if self.filenames == '':
            self.filenames = self.fw_file_path.get()

            if self.fw_file_path.get() == "":
                tkMessageBox.showerror("FW package file path is None",
                                   "Please provide FW package file path ")
                return
            if '.rom' not in self.fw_file_path.get():
                tkMessageBox.showerror("Provide a valid FW file", "%s is not a valid FW image" %
                                       self.fw_file_path.get())
                return
            # elif not os.path.exists(self.fw_file_path.get()):
            #     tkMessageBox.showerror("Provide a valid FW file", "%s file not found" % self.fw_file_path.get())
            #     return

            logger.info("FW update to be done with : %s " % self.w_enable_fp.get())
            fw_dict = {}
            fw_dict['fw_package_path'] = self.filenames

            self.filenames = ''
            fw_dict['method'] = self.w_enable_fp.get().lower()


            fw_dict["ver_verify"] = self.verifty_ver_tick_var.get()

            fw_dict['subtype'] = "Ctrl FW"
            fw_dict['type'] = 'FW Update'

            return fw_dict

        elif current_tab == 'Device FW':
            profile_dict = {}
            profile_dict['subtype'] = "Device FW"
            profile_dict['type'] = 'FW Update'
            profile_dict['fw_package_path'] = self.fw_file_path_enpd.get()
            profile_dict['mode_type'] = self.enpdfw_update_mode.get().lower()
            profile_dict['device_type'] = self.enpdfw_update_type.get().lower()
            if profile_dict['device_type'] == 'pd':
                profile_dict['device_id'] = self.pd.get()
            elif profile_dict['device_type'] == 'enclosure':
                profile_dict['device_id'] = self.enclosure.get()
            if profile_dict['device_id'] =="" :
                tkMessageBox.showerror("Device id is None",
                                       "Please provide Enclosure ID/ PD String ")
                return
            if profile_dict['fw_package_path'] == "":
                tkMessageBox.showerror("FW package file path is None",
                                       "Please provide FW package file path ")
                return
            return profile_dict

    """    
    def newselection(self, event):
        self.value_of_combo = self.w_enable_fp.get()

        if not self.value_of_combo in ['FW_Flash_only','OFU']:
            self.loops.grid_forget()
            self.no_of_loop.grid_forget()
        if not self.value_of_combo == 'OFU':
            self.verify_ver.grid_forget()
            self.verifty_ver_tick.grid_forget()
        if not self.value_of_combo == 'Reboot':
            self.loop.grid_forget()
            self.n_of_loop.grid_forget()
            self.io_run.grid_forget()
            self.io_run_vble.grid_forget()
        self.w_enable_fp.update_idletasks()
        if self.value_of_combo in ['FW_Flash_only', 'OFU']:
            self.loops.grid(row=2, column=0, padx=2, pady=10, sticky="w")
            self.no_of_loop.grid(row=2, column=1, padx=2, pady=10, columnspan=4, sticky="w")
        if self.value_of_combo == 'Reboot':
            self.loop.grid(row=2, column=0, padx=2, pady=10, sticky="w")
            self.n_of_loop.grid(row=2, column=1, padx=2, pady=10, columnspan=4, sticky="w")
            self.io_run.grid(row=3, column=0, padx=2, pady=10, sticky="w")
            self.io_run_vble.grid(row=3, column=1, padx=2, pady=10, columnspan=4, sticky="w")
        if self.value_of_combo == 'OFU':
            self.verify_ver.grid(row=3, column=0, padx=2, pady=10, sticky="w")
            self.verifty_ver_tick.grid(row=3, column=1, padx=2, pady=10, columnspan=4, sticky="w")"""
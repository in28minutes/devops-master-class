#!/usr/bin/env python
"""
#####################################################################################
#                                                                                   #
#    Copyright 2023-2024 Broadcom.  All Rights Reserved.  Broadcom Confidential.    #
#     The term "Broadcom" refers to Broadcom Inc. and/or its subsidiaries.          #
#                                                                                   #
#####################################################################################

Wingman Flex GUI is the GUI developed for creating and supporting the flex requirements for the Product test.

"""
__doc__ = '''
The GUI is for designing test case for WM Flex requirements. This file wingmna.py is where all the modules register
 them selves.

The framework will pad and manage the required details on top of module level defined key_values in order to build
 a test case, browse and edit/delete steps.

>>> CODE allows below provisions for modules
1. Allow module owners to plug in their modules.
2. Allows basic test step submission, entry index / test step number auto management by the framework.
3. Provides common widgets to add values for each test step like
   (step_reference, stepwait, expected_result. More to add in case needed)
4. Allows facility to browse test steps that have been submitted.
5. Edit a step and submit
6. Delete submitted step : All the steps from selected step number till last step will be deleted
7. Save JSON with CQ test case description and ID

>>> EACH module needs to have 3 methods implemented
1. get_step() : The function is called to get the selected values from the module widget
2. set_step(step_dict) : Takes step_dict as input and sets widget values to the values submitted for step number n.
3. step_text() : Returns the text for the step that then sits in the Test case description.

>>> STEPS to plugging-in the modules into the framework
1.	Each module needs to define implementation needed for a module
2.	Module files need to sit under the sub-folder "wm_modules"
    C:\Wingman
        |
        | -> wmflex
                 |
                 | -> wm_modules
                         |
                         | -> <module_name>.py    

3.	Each class to implement 2 functions in below names
    a. get_step : From Module to Framework : Framework pulls all the widget values, that a module has,
                    using this function. submits as test step
    b. set_step : From Framework to Module : When browsing test step, the module accepts step data and sets 
                    its widget values as was summited in the
    c. step_text : From Module to Framework : When a step is submitted, the module also returns the human readable
                    text for the step which is what gets captured in the JSON as well

4.	In the framework, each module needs to follow the below
    a.	Basic import : from wm_modules.<module_file.py> import ModuleClass
    b.	Register the module via function : def notebook_register_module.
        ex.
        self.tab_modules["config"] = ttk.Frame(self.notebook_wm) : self.tab_modules["config"] serves as the module_obj
    c.	Add the module tab to the notebook : self.notebook_wm.add(self.tab_modules["config"], text='Config')

5.  To Register the child tabs, ie. tab inside tab: follow the below.
    a.  In function : self.notebook_register_module, under the child registration section, call function as below.
        If there are tabs inside tabs for a module (referred as "Child tabs"), kindly register them here
          1. Name of parent tab (as provided above for self.notebook_wm)
          2. List of all Tabs to create for module.
          3. The order of definition matter here and tabs are seen in same order as defined here
          4. Also note that the test_type to tab name mapping is mentioned in def module_obj_mapper()
'''
__author__ = ["Amitabh Suman", "Nischal Martis", "Nikhil Rai", "Rakesh Vats", "Santhosh Prabhu"]
__copyright__ = "Copyright 2023-24, The Wingman Flex Project"
__version__ = '2023.02.20'
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
03/24/23     DCSG01431509    asuman       Ph1: WM Flex 3.0 : (GUI) : Implement Add-Delete Config, Add-Delete JBOD \
                                          (non-raid), Stop IO
03/24/23     DCSG01431418    nmartis      Wingman 3.0: Add GUI For Config Creation in Wingman Flex
03/24/23     DCSG01459382    nmartis      Add Support Modify the Default RAID Parameters on RAID Selection
04/03/23     DCSG01430859    nr888483     Add support for Foreign config module (Initial Version)
04/05/23     DCSG01430860    nr888483     Add support for Pinned Cache module (Initial Version)
04/10/23     DCSG01431388    saprabhu     Wingman 3.0: Add support for ATE2 module in Wingman Flex
04/10/23     DCSG01431391    saprabhu     Wingman 3.0: Add support for Firmware update GUI module in Wingman Flex
04/14/23     DCSG01431509    asuman       Ph2: WM Flex 3.0 : (GUI) : Implement Add-Delete Config, Add-Delete JBOD \
                                          (non-raid), Stop IO
04/16/23     DCSG01431536    asuman       WM Flex 3.0 : (GUI) : Implement OCR and System Reboot support
04/16/23     DCSG01431530    asuman       WM Flex 3.0 : (GUI) : Add support for Snapdump operation as a test step
05/08/23     DCSG01488185    asuman       WM_Flex (GUI) : Add View saved JSON button, helper tooltips, window \
                                          resizing and code formatting

'''

import Tkinter as tk
import copy
import tkMessageBox
import ttk
import logging
import os
os.environ['DISPLAY'] = ':0.0'
import json
from functools import partial
from datetime import datetime
import utils
from utils import *
from utils import JSONHandler
from custom_styles import *
from tooltip import ToolTip
from PIL import Image, ImageTk
from collections import OrderedDict
import tkFileDialog
from copy import deepcopy
import webbrowser

# DEFINE ALL WM MODULES IMPORT BELOW
# ====================================
from wm_modules.config import ConfigModule, DeleteConfig
from wm_modules.loop import LoopModule
from wm_modules.flexConfigGui import flexRaid, tcDefaults
from wm_modules.io import IoModule
from wm_modules.col import ColModule
from wm_modules.foreignCfg import ForeignConfig
from wm_modules.pinnedCache import PinnedCache
from wm_modules.fwop import FwOps
from wm_modules.reset import ResetModule
from wm_modules.testcase_utils import SnapdumpModule

app_launch_dir = get_app_launch_dir()
logger = get_logger("root")

# Define blanket root window
# TODO : Make it expand full screen and maintain the frame aspect ratio
root_window = tk.Tk()
root_window.title("WingmanFlex " + __version__)
root_window.config(bg="#F0F0F0")
root_window.geometry('1100x900')
# root_window.maxsize(1200, 1000)
screen_width = root_window.winfo_screenwidth()
screen_height = root_window.winfo_screenheight()
root_window.maxsize(screen_width, screen_height)
ratio = 0.7
initial_width = 0.6 * root_window.winfo_screenwidth()


# Import all styles.
# TODO : Needs more work to finalize and clean unused code
def invoke_all_styles():
    return CustomStyles.nb_style(), \
        CustomStyles.button_style(), \
        CustomStyles.label_style(), \
        CustomStyles.label_style(), \
        CustomStyles.menuButton_style(), \
        CustomStyles.combobox_style(), \
        CustomStyles.delete_button_style(), \
        CustomStyles.labelframe_style(), \
        CustomStyles.save_insert_button_style(), \
        CustomStyles.menu_button_style(), \
        CustomStyles.submit_button_style(), \
        CustomStyles.radio_button_style()


try:
    invoke_all_styles()
except:
    pass


# Create a callback function to handle resizing
def resize_notebooks(event, nb1, nb2):
    global initial_width, ratio
    # Compute the new width based on the mouse position
    new_width = event.x / float(root_window.winfo_width())
    new_width *= root_window.winfo_width()
    # Ensure the width is within the range [0.3, 0.7] times the window width
    new_width = max(0.3 * int(root_window.winfo_width()), min(int(new_width), 0.7 * int(root_window.winfo_width())))
    # Update the widths of the notebooks
    nb1.config(width=int(new_width) * int(ratio))
    nb2.config(width=int(new_width) * int(1 - ratio))
    initial_width = int(new_width)


# Class for root window to render the main application
class RootWindow(tk.Tk):
    def __init__(self, parent):
        self.parent = parent
        self.create_top_parent()
        self.create_bottom_parent()
        self.create_top_canvas()
        self.create_right_canvas()
        self.create_left_canvas()
        self.create_bottom_canvas()

    def create_top_parent(self):
        self.top_parent = tk.Canvas(self.parent, height=root_window.winfo_screenheight() * 0.6)
        self.top_parent.pack(side="top", expand=True, fill="both")

    def create_bottom_parent(self):
        self.bottom_parent = tk.Canvas(self.parent, height=screen_height * 0.2)
        self.bottom_parent.pack(side="bottom", expand=False, fill="x")

    def create_top_canvas(self):
        self.canvas_top = tk.Canvas(self.top_parent, height=60)
        self.canvas_top.pack(side="top", expand=False, fill="x")

    def create_right_canvas(self):
        self.canvas_right = tk.Canvas(self.top_parent,
                                      height=root_window.winfo_screenheight() * 0.60,
                                      width=root_window.winfo_screenwidth() * ratio)
        self.canvas_right.pack(side="left", expand=True, fill="both")

    def create_left_canvas(self):
        self.canvas_left = tk.Canvas(self.top_parent,
                                     height=root_window.winfo_screenheight() * 0.60,
                                     width=root_window.winfo_screenwidth() * (1 - ratio))
        self.canvas_left.pack(side="right", expand=True, fill="both")

    def create_bottom_canvas(self):
        self.canvas_bottom = tk.Canvas(self.bottom_parent, height=40)
        self.canvas_bottom.pack(side="bottom", expand=False, fill="x")


class WMMenu():
    """
    Class that handles all the menus and their functionalities. Most of the calling function are called
    from utils.py.
    """

    help_text = {
        "flex_help": "Wingman Flex is redesigned version of previous generation WM."
                     "\nIt helps to parameterize Test runs for automated test cases,\n"
                     "allowing wider coverage of the test scenarios and cases."
    }

    def __init__(self, parent):
        self.parent = parent
        self.menubar = tk.Menu(self.parent)
        self.parent.config(menu=self.menubar)
        self.file_ops()
        self.ate2_ops()
        self.about()

    def ate2_ops(self):
        """
        Adding ATE2 Menu and commands
        ATE - Automated Test Environment
        Clear All Execution - To clear all test runs including current running
        Stop Current Execution - To clear current running test
        Clear Queued Execution - To clear queued tests but continue with current test
        Restart ATE2 - To restart ate
        return: None
        """
        ate2_obj = utils.ate2()
        ate2_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label='ATE2', menu=ate2_menu)
        ate2_menu.add_command(label="Clear All Execution", command=lambda: ate2_obj.clear_execution(0))
        ate2_menu.add_separator()
        ate2_menu.add_command(label="Stop Current Execution", command=lambda: ate2_obj.clear_execution(1))
        ate2_menu.add_command(label="Clear Queued Execution", command=lambda: ate2_obj.clear_execution(2))
        ate2_menu.add_separator()
        ate2_menu.add_command(label="Restart ATE2", command=lambda: ate2_obj.start_ate2())

    def about(self):
        """
        This is about section for Wingman GUI
        """
        abt = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label='About', menu=abt)
        abt.add_command(label='About Wingman Flex',
                        command=lambda: ToolTip().notify(
                            root_window,
                            "Submitted",
                            "{}".format(WMMenu.help_text["flex_help"]),
                            top=True,
                            self_destroy=False,
                            notification_duration=6000,
                            level="info"
                        )
                        )

    def file_ops(self):
        """
        Adding File Menu and commands. All mentions here are dummy and needs to be changed as needed
        :return: None
        """
        file = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label='File', menu=file)
        file.add_command(label='New File', command=lambda: utils.ask_save_json())
        file.add_command(label='Open...', command=lambda: utils.ask_cq_details(self))
        file.add_command(label='Save', command=None)
        file.add_separator()
        file.add_command(label='Exit', command=self.parent.destroy)


# Class for Wingman Root
class Wingman(RootWindow):
    """
    This is the main class where the GUI logic sits. All module are stitched here as per the information in __doc__.
    """

    def __init__(self):
        """
        Defining initial lists, dictionaries and calling few function to render the layout.
        """
        RootWindow.__init__(self, root_window)
        self.place_left_pane()
        self.place_left_info_sub_pane()
        self.reset_common_dict()
        self.objs_module = {}
        self.tab_modules = {}
        self.tab_utils = {}
        self.child_module_tabs = {}
        self.obj_current_module = None
        self.json_file_path = None
        self.init_tc_dictionary()
        self.place_right_pane()
        self.place_version()
        self.place_logo()
        self.refactored_step_details = []
        self.edit_flag = False
        self.selected_step_no = 0
        self.saved_jsons = []

    def init_tc_dictionary(self):
        """
        This is the master test case that gets stored in the JSON when saved.
        :return: None
        """
        self.master_test_case = OrderedDict()
        self.master_test_case["test_step_definition"] = OrderedDict()
        self.master_test_case["test_step_definition"]["id"] = ""
        self.master_test_case["test_step_definition"]["wm_steps"] = []
        self.master_test_case["test_step_definition"]["cq_steps"] = []
        self.master_test_case["tcsteps"] = []

        self.test_case_text = OrderedDict()
        self.test_case_text["id"] = ""
        self.test_case_text["wm_steps"] = []
        self.test_case_text["cq_steps"] = []
        self.test_step_list = []
        self.current_step_dict = {}

    def reorder_master_tc(self):
        """
        Handling the final submission of the Test case which makes sure that order of the Keys in the JSON
        is as per expected format.
        1. TC description
        2. TC defaults
        3. TC steps
        :return: Ordered Dictionary
        """
        temp = OrderedDict()
        temp["test_step_definition"] = self.master_test_case["test_step_definition"]
        temp["tcdefault"] = self.master_test_case["tcdefault"]
        temp["tcsteps"] = self.master_test_case["tcsteps"]
        return temp

    def place_left_pane(self):
        """
        Master Frame for placing all the frames and widgets seen in Test case creation. Names indicate the placement
        of the pane
        :return: None
        """
        self.frame_nb_top = ttk.LabelFrame(self.canvas_right, text="", height=root_window.winfo_screenheight() * 0.6)
        self.frame_nb_top.pack(fill="both", side="top", expand=True)

        self.frame_mid = tk.LabelFrame(
            self.canvas_right,
            text="Required Inputs",
            font=BTN_FONT,
            height=200
        )
        self.frame_mid.configure(labelanchor="w")
        self.frame_mid.pack(fill="x", side="top", expand=False, ipady=5, padx=(10, 5))

        self.frame_nb_bottom = ttk.LabelFrame(self.canvas_right, text="", height=root_window.winfo_screenheight() * 0.2)
        self.frame_nb_bottom.pack(fill="x", side="bottom", expand=False)

    def place_left_info_sub_pane(self):
        """
        As name suggests, this pane sits inside the parent frame_nb_top
        :return: None
        """
        self.frame_wm_info = tk.Frame(self.frame_nb_top, height=15)
        self.frame_wm_info.pack(fill="x", side="top", expand=False, padx=(0, 5))

        self.label_info = ttk.Label(self.frame_wm_info, text="Create your Test Case")
        self.label_info.configure(font=HEADING_FONT, foreground="#357EC7",
                                  background=COLOR["tkinterDef"])
        self.label_info.grid(row=0, column=0, pady=0, padx=10)

    def place_right_pane(self):
        """
        This pane houses the test case, test step and test step list viewer.
        :return: None
        """
        self.frame_broswer_top = ttk.LabelFrame(self.canvas_left, text="", height=20)
        self.frame_broswer_top.pack(fill="y", side="top", expand=False)

        self.frame_tc_viewer = tk.LabelFrame(
            self.canvas_left,
            text="Information  ",
            height=20,
            width=root_window.winfo_screenwidth() * 0.32,
            font=BTN_FONT,
            borderwidth=0
        )
        self.frame_tc_viewer.configure(labelanchor="ne")
        self.frame_tc_viewer.pack(fill="both", side="right", expand=True)

        # self.nb_left_canvas = ttk.Notebook(self.frame_tc_viewer, width=340)
        self.nb_left_canvas = ttk.Notebook(self.frame_tc_viewer, width=340)
        self.nb_left_canvas.pack(expand=True, fill="both", padx=(0, 5), pady=5)

        self.tab_utils["test_case"] = ttk.Frame(self.nb_left_canvas)
        self.tab_utils["test_step"] = ttk.Frame(self.nb_left_canvas)

        # Add the tab to framework defined notebook_wm notebook widget
        self.nb_left_canvas.add(self.tab_utils["test_case"], text='Test case')
        self.nb_left_canvas.add(self.tab_utils["test_step"], text='Test step')
        self.nb_left_canvas.pack(expand=1, fill="both")

        # self.frame_browser_bottom = tk.Frame(self.canvas_left, height=500)
        # self.frame_browser_bottom.pack(fill="both", side="bottom", expand=False)

        # Place Test Step viewer where we add the details related to the test step
        self.browser_test_steps()
        self.test_step_viewer()

    def test_step_viewer(self):
        """
        This function renders the test step view functionality of the framework
        :return: None
        """
        # Add a Scrollbar(horizontal)
        v = ttk.Scrollbar(self.tab_utils["test_case"], orient='vertical')
        v.pack(side="right", fill='y')

        # Add a text widget
        self.tc_text_widget = tk.Text(
            self.tab_utils["test_case"],
            font=LABEL_FONT_3,
            foreground=COLOR["lightgray"],
            yscrollcommand=v.set,
            width=340
        )

        self.tc_text_widget.insert("end", "\n\n\tTest Case text appears here")
        self.tc_text_widget.configure(selectbackground=self.tc_text_widget.cget('fg'),
                                      inactiveselectbackground=self.tc_text_widget.cget('bg'))
        self.tc_text_widget.configure(state="disabled")

        # Attach the scrollbar with the text widget
        v.config(command=self.tc_text_widget.yview)
        self.tc_text_widget.pack(fill="both", expand=1)

    def place_version(self):
        """
        Used to display the version of the Wingman Release.
        :return: None
        """
        tk.Label(self.canvas_top, text=(__version__ + "\nDCSG | Broadcom"), font=('Berlin Sans FB', 10, "bold"),
                 fg='grey34').pack(side='right', expand=False, padx=(0, 10), pady=(18, 0))

        # Randomize selection (choose few colors and link event of mouse hover)
        # _fg = random.choice(list(COLOR.values()))
        # logger.info("Chose : {}".format(_fg))

        tk.Label(self.canvas_top, text="flex", font=('Segoe Script', 19, "bold"),
                 fg="coral2").pack(side='right', expand=False, padx=(0, 0), pady=(10, 0))

        tk.Label(self.canvas_top, text="Wingman", font=('Segoe UI', 18, "bold italic"),
                 fg="grey34").pack(side='right', expand=False, padx=(0, 0), pady=(10, 0))

    def place_logo(self):
        """
        Renders the Wingman Flex Icon
        :return:
        """
        img = Image.open(os.path.join(os.getcwd(), "icons", "wingman_icon_small_black.png"))
        img = img.resize((60, 60), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(img)
        label = tk.Label(image=img, master=self.canvas_top)
        label.image = img  # keep a reference!

        # label = tk.Label(self.banner_frame, image=img)
        label.pack(side='right', padx=(0, 0), pady=(12, 0), expand=False)

    def main(self):
        """
        The main function that bring to the root window, all the widgets and functions that add to the purpose of the
        GUI. This is the function that is called when the GUI mainloop is called.
        :return: None
        """
        self.notebook_wm = ttk.Notebook(self.frame_nb_top)
        self.notebook_register_module()
        self.notebook_wm.pack(expand=True, fill="both", padx=5, pady=5)
        self.add_cb_step_ref()
        self.add_entry_step_wait()
        self.add_radiobtn_expected_result()
        self.wm_crud_widgets()
        self.create_test_modules()

    def notebook_register_module(self):
        """
        All modules come and register themselves here. Few thinsg that needs to be kept in mind is:
        1. Keep the tab name same as module name.
        2. All module objects are collected in the dictionary with names of the tab
        3. Case for the Tab names can we as user needs. It's converted to lower case for object fetch.
        4. The Notebook select event, monitors the selection and associates to the module object as soon as a
            selection is made.
        :return: None
        """
        # REGISTER PARENT TABS
        # ====================
        #   1. Register modules in the self.tab_modules
        #   2. The order of definition matter here and tabs are seen in same order as defined here
        # ====================
        self.tab_modules["config"] = ttk.Frame(self.notebook_wm)
        self.tab_modules["io"] = ttk.Frame(self.notebook_wm)
        self.tab_modules["col"] = ttk.Frame(self.notebook_wm)
        self.tab_modules["loop"] = ttk.Frame(self.notebook_wm)
        self.tab_modules["bgop"] = ttk.Frame(self.notebook_wm)
        self.tab_modules["ops"] = ttk.Frame(self.notebook_wm)
        self.tab_modules["fwop"] = ttk.Frame(self.notebook_wm)
        self.tab_modules["reset"] = ttk.Frame(self.notebook_wm)
        self.tab_modules["utils"] = ttk.Frame(self.notebook_wm)

        # Add the tab to framework defined notebook_wm notebook widget
        self.notebook_wm.add(self.tab_modules["config"], text='Config')
        self.notebook_wm.add(self.tab_modules["io"], text='IO')
        self.notebook_wm.add(self.tab_modules["col"], text='COL')
        self.notebook_wm.add(self.tab_modules["loop"], text='Loop')
        self.notebook_wm.add(self.tab_modules["fwop"], text='FWop')

        self.notebook_wm.add(self.tab_modules["ops"], text='OPS')
        self.notebook_wm.add(self.tab_modules["reset"], text='Reset')
        self.notebook_wm.add(self.tab_modules["utils"], text='Utils')
        # self.ops_tab_modules = {}
        # self.ops_new_nb = ttk.Notebook(self.tab_modules["ops"])
        # self.ops_tab_modules["foreign config"] = ttk.Frame(self.ops_new_nb)
        # self.ops_new_nb.add(self.ops_tab_modules["foreign config"], text='Foreign Config')
        # self.ops_tab_modules["pinned cache"] = ttk.Frame(self.ops_new_nb)
        # self.ops_new_nb.add(self.ops_tab_modules["pinned cache"], text='Pinned Cache')
        # self.ops_new_nb.pack(expand=True, fill="both", padx=5, pady=5)

        self.notebook_wm.pack(expand=1, fill="both")

        # REGISTER CHILD TABS
        # ====================
        # If there are tabs inside tabs for a module (referred as "Child tabs"), kindly register them here
        #   1. Name of parent tab (as provided above for self.notebook_wm)
        #   2. List of all Tabs to create for module.
        #   3. The order of definition matter here and tabs are seen in same order as defined here
        #   4. Also note that the test_type to tab name mapping is mentioned in def module_obj_mapper()
        # ====================
        self.register_child_tabs("config", ["Flex", "Static", "Delete"])
        self.register_child_tabs("ops", ["Foreign Config", "Pinned Cache"])
        self.register_child_tabs("utils", ["Snapdump"])

        # Bind notebook tab selection event
        self.notebook_wm.bind('<<NotebookTabChanged>>', lambda _: self.refresh_tab_info(_))

    def register_child_tabs(self, parent, child_list):
        """
        Creates child tab for a parent tab. Takes in 2 inputs, Parent and Child List. Adds tab to parent tab and
        appends the information to the parent obj __dict__. Key added is "child_tab_info". And this dictionary
        captures 2 major information
        1. The notebook object where child_tabs are placed
        2. Child tab frame objects that gets created.
        For example.
        Parent Tab : "Config"
        Chlid list : ["Flex", "Static", "Delete"]
        Dictionary:
        "child_tab_info" : {
                            "child_nb" : ttk.Notebook instance,
                            "child_1" : ttk.Frame instance,
                            "child_2" : ttk.Frame instance,
                            }
        """
        parent_obj = self.tab_modules[parent]
        child_nb = ttk.Notebook(parent_obj)
        child_nb.pack(expand=True, fill="both", padx=5, pady=5)
        child_tabs_info = self.add_tab(child_nb, child_list)
        child_tabs_info["child_nb"] = child_nb
        self.child_module_tabs[parent] = child_tabs_info
        parent_obj.__dict__["child_tab_info"] = child_tabs_info

        # Generating a tab selected event to register the active module object once the GUI launches.
        # Flex config is the landing screen for the WM Flex GUI launch
        child_nb.bind('<<NotebookTabChanged>>', lambda _: self.refresh_tab_info(_))
        try:
            child_nb.select(1)
        except:
            pass
        child_nb.after(800, lambda: child_nb.select(0))

        # Certain debug information in case of any issues
        logger.debug("child_tabs_info            : {}".format(child_tabs_info))
        logger.debug("Parent details appended    : {}".format(parent_obj.__dict__))
        logger.debug("self.child_module_tabs     : {}".format(self.child_module_tabs))
        logger.debug("child_tabs_info            : {}".format(child_tabs_info))
        logger.debug("self.objs_module           : {}".format(self.objs_module))
        logger.debug("Child tab selected         : {}".format(
            self.get_selected_tab_details(child_tabs_info["child_nb"])))

    def module_obj_mapper(self, module):
        """
        In case tab names are long and needs to be short, define Test Step Type to Tab Name key:val in the function
        def module_obj_mapper():
        <step_type> : <name_of_tab>
        ex : "staticconfig": "config"
        Here :
        staticconfig : This is the step type as seen in JSON.
        config : This is the tab name as seen in GUI
        :param module:
        :return:
        """
        obj_mapper = {
            # PARENT TAB MAPPER
            # =================
            #   Incase a module type has a different name than the Tab name seen in GUI,
            #   define the mapping here.
            "module_test_type": "name_of_tab",

            # CHILD TAB MAPPER
            # =================
            #   If parent tab (self.notebook_wm) mapping does not find the module, search in child tab dictionary
            #   Search in child tab space
            #   sample return : module_type : [parent tab (self.notebook_wm tab), child_tab_name]
            "staticconfig": ["config", "static"],
            "delete": ["config", "delete"],
            "flexconfig": ["config", "flex"],
            "foreign_cfg": ["ops", "foreign config"],
            "pinned_cache": ["ops", "pinned cache"],
            "snapdump": ["utils", "snapdump"]
        }
        return obj_mapper.get(module.lower(), module)

    def add_tab(self, child_nb, child_list):
        """
        Creates frames for all child tabs and then associates them to notebook tab. Returns the dictionary
        with related tab details.
        """
        child_tabs = {}
        for child in child_list:
            child_tabs[child.lower()] = ttk.Frame(child_nb)
            child_nb.add(child_tabs[child.lower()], text=child.capitalize())
        child_nb.pack(expand=1, fill="both")
        return child_tabs

    def get_selected_tab_details(self, parent_nb=None):
        """
        Takes in the notebook for which the details of Tab selection is needed.
        If no tab is provided, return back the self.notebook_wm tab as default
        """
        if parent_nb is None:
            parent_nb = self.notebook_wm
        selected_tab = dict()
        selected_tab["name"] = parent_nb.tab(parent_nb.select(), "text")
        selected_tab["id"] = parent_nb.index(parent_nb.select())
        logger.info("Selected tab {} => ID {}".format(selected_tab["name"], selected_tab["id"]))
        logger.debug("self.objs_module : {}".format(self.objs_module))
        return selected_tab

    def refresh_tab_info(self, event):
        """
        This function gets invoked on the event of notbook tab selection and activates the object associated to the
        module selected.
        :param event: Notebook tab selection
        :return: None
        """
        # TODO : BELOW CODE IS COMMENTED AND WILL BE REMOVED LATER
        #     selected_tab = dict()
        #     selected_tab["name"] = self.notebook_wm.tab(self.notebook_wm.select(), "text")
        #     selected_tab["id"] = self.notebook_wm.index(self.notebook_wm.select())
        #     logger.info("Selected tab {} => ID {}".format(selected_tab["name"], selected_tab["id"]))
        #     logger.info("Event : {}".format(event))
        #     if selected_tab["name"].lower() in ['ops']:
        #         self.refresh_sub_tab_info(event,sub_nb_tab="ops")
        #     else:
        #         self.obj_current_module = self.objs_module[selected_tab["name"].lower()]

        # TODO : BELOW CODE IS COMMENTED AND WILL BE REMOVED LATER
        # def refresh_sub_tab_info(self,event,sub_nb_tab=None):
        #     """
        #     This functions like for refresh_tab but for sub module.
        #     User need to pass the required event and defined sub_tab from main notebook tab
        #     """
        #     if sub_nb_tab == "ops":
        #         sub_nb_tab = self.ops_new_nb
        #     sub_selected_tab = {}
        #     sub_selected_tab["name"] = sub_nb_tab.tab(sub_nb_tab.select(), "text")
        #     sub_selected_tab["id"] = sub_nb_tab.index(sub_nb_tab.select())
        #     logger.info("Selected tab {} => ID {}".format(sub_selected_tab["name"], sub_selected_tab["id"]))
        #     logger.info("Event : {}".format(event))
        #     self.obj_current_module = self.objs_module[sub_selected_tab["name"].lower()]

        # Get selected widget
        selected_module = event.widget
        selected_module_tab = self.notebook_wm.nametowidget(self.notebook_wm.select())

        # Get selected widget's dict
        logger.info("Selected tab      : {}".format(selected_module_tab))
        logger.info("Selected tab dict : {}".format(selected_module_tab.__dict__))

        # Check for the widget child_tab_info
        if selected_module_tab.__dict__.get("child_tab_info"):
            selected_tab = self.get_selected_tab_details(selected_module_tab.__dict__["child_tab_info"]["child_nb"])
            self.obj_current_module = self.objs_module[selected_tab["name"].lower()]
        else:
            selected_tab = self.get_selected_tab_details()
            self.obj_current_module = self.objs_module[selected_tab["name"].lower()]

        # Certain debug information
        logger.debug("Event generated         : {}".format(event))
        logger.debug("Event widget            : {}".format(event.widget))
        logger.debug("Event widget            : {}".format(event.widget.__dict__))
        logger.debug("self.objs_module        : {}".format(self.objs_module))
        logger.debug("Selected Tab Info       : {}".format(selected_tab))
        logger.debug("self.obj_current_module : {}".format(self.obj_current_module))

    def reset_common_dict(self):
        """
        The function is used to initialize the framework level step dictionary.
        :return: None
        """
        self.common_options_dict = {
            "step_reference": {},
            "step_wait": "",
            "expected_result": ""
        }

    def pull_common_dict_values(self):
        """
        Function that pull the latest values from the common option widgets
        # TODO : Add more widgets in the common selection
        :return: None
        """
        self.common_options_dict = {
            "step_reference": self.reformat_step_selection(),
            "step_wait": self.entry_wm_step_wait.get(),
            "expected_result": self.expct_res.get()
        }
        logger.info("Common dict : {}".format(self.common_options_dict))
        self.reformat_step_selection()

    def reformat_step_selection(self):
        """
        Formats the step selected and removed the mcodule info from the step which is otherwise used
        in Test step browsing and Step reference.
        :return:
        """
        logger.info("Step reference dict is : {}".format(self.common_options_dict["step_reference"]))
        _reformatted_step = [k.split(":")[0].strip() for k, v in
                             self.modify_step_ref_to_dict(self.common_options_dict["step_reference"]).iteritems()
                             if v == '1']
        _reformatted_step = list(set(_reformatted_step))
        logger.info("Reformatted step : {}".format(_reformatted_step))
        return _reformatted_step

    def wm_crud_widgets(self):
        """
        Places the CRUD widgets which takes care of the Step creation, edit, delete and submit.
        CRUD : Create, Read, Update, Delete
        """
        # Define Submit Test Step button.
        _upper_child_frame = tk.Frame(self.frame_nb_bottom)
        _upper_child_frame.pack(side="top", fill="both", expand=True, pady=(5, 10))

        _lower_child_frame = tk.Frame(self.frame_nb_bottom)
        _lower_child_frame.pack(side="bottom", fill="x", expand=True, pady=(0, 5))

        # SAVE TEST STEP BUTTON
        self.btn_save_step = ttk.Button(
            _upper_child_frame,
            text="Submit Step",
            width=18,
            command=lambda: self.invoke_submit_calls()
        )
        self.btn_save_step.configure(style='Wild.TButton')
        self.btn_save_step.pack(side="left", expand=False, padx=(5, 0))

        # DELETE TEST STEP BUTTON
        self.btn_delete_step = ttk.Button(
            _upper_child_frame,
            text="Delete Step",
            width=18,
            command=lambda: self.invoke_delete_calls()
        )
        self.btn_delete_step.config(style='Cancel.TButton')
        self.btn_delete_step.pack(side="right", expand=False, padx=(8, 5))

        # SAVE EDITED TEST CASE BUTTON
        self.btn_edit_step = ttk.Button(
            _upper_child_frame,
            text="Save Edited Step",
            width=18,
            command=lambda: self.invoke_edit_calls()
        )
        self.btn_edit_step.config(style='SaveInsert.TButton')
        self.btn_edit_step.pack(side="right", expand=False)

        # VIEW SAVED JSON BUTTON
        self.btn_view_json = ttk.Button(
            _upper_child_frame,
            text="View Saved JSON",
            width=18,
            command=lambda: webbrowser.open(self.saved_jsons[-1])
        )
        self.btn_view_json.config(style='SaveInsert.TButton')

        # SAVE TEST CASE JSON BUTTON
        self.btn_save_json = ttk.Button(
            _lower_child_frame,
            text="Save TC JSON",
            width=80,
            command=lambda: self.invokeGetTcDefaults()
        )
        self.btn_save_json.config(style='Wild.TButton')
        self.btn_save_json.pack(side="bottom", expand=True, fill="x", padx=5, ipady=5)

    def invokeGetTcDefaults(self):
        """PopUp for gathering TC defaults value is created and once user submit the default values fallsback
        to Wingman TC Text Gathering and JSOn Saving Windows"""
        tcDefaults(self)

    def invoke_submit_calls(self):
        """
        Submit call is expected to do the follow
        1. Get all the Module + Common options values
        2. Display the test case text in the Test Case text textbox
        3. Add to master test case list
        4. Post success message that step has been submitted
        5. Set the edit flag to false (Edit flag will be used to save edited step, may not need it at all)
        6. Reset the common dict as it will have selections from previous step
        :return: None
        """
        self.aggregate_step_info()
        if self.current_step_dict:
            self.display_step_text()
            self.add_to_test_step_list()
            self.add_to_master_tc()
            self.post_success()
            self.entry_wm_step_wait.delete(0, "end")
            self.edit_flag = False
            self.reset_common_dict()
            logger.info("Step Text : {}".format(self.test_case_text))
        else:
            self.current_step_dict = {}
            self.reset_common_dict()

    def aggregate_step_info(self):
        """
        Gets the values from Module and also sets step number for the step being submitted
        Marks the aggregated info as the info of the current step dictionary
        :return: None
        """
        self.current_step_dict = self.obj_current_module.get_step()
        if not self.current_step_dict:
            return
        logger.info("Len {}, Received : {}".format(len(self.current_step_dict), self.current_step_dict))
        self.current_step_dict["step"] = len(self.test_step_list) + 1  # to start step from 1

    def add_to_test_step_list(self):
        """
        Pulls widget values for the common keys and added them to the current step. Then adds them to
        the master test case list.
        Then reset common dict to initial values for new test step
        :return: None
        """
        self.pull_common_dict_values()
        self.current_step_dict.update(self.common_options_dict)
        self.test_step_list.append(self.current_step_dict)
        self.test_case_text["wm_steps"].append(self.step_text)
        logger.info("Master Test Case : {}".format(self.test_step_list))

    def add_to_master_tc(self):
        """
        Adds the submitted test step to the master dictionary
        """
        self.master_test_case["test_step_definition"]["wm_steps"] = self.test_case_text["wm_steps"]
        self.master_test_case["tcsteps"].append(self.current_step_dict)
        logger.info("Master Test Case : {}".format(self.master_test_case))

    def post_success(self):
        """
        Changes label on top of the master notebook where all the modules sit.
        The function also notifies the user that the step has been selected.
        :return: None
        """
        steps = len(self.test_step_list)
        self.label_info["text"] = "Added Test Step {}, add new step {}".format(steps, steps + 1)
        ToolTip().notify(
            self.notebook_wm,
            "Submitted",
            "Step {} submitted successfully, add next ! ".format(len(self.test_step_list)),
            mid=True,
            notification_duration=1800,
            level="success"
        )
        if steps == 1:
            ToolTip().notify(
                self.browser_steps,
                "Read here",
                "Browse your submitted test steps here.".format(len(self.test_step_list)),
                mid=True,
                notification_duration=3000,
                self_destroy=False,
                level="success"
            )

    def invoke_delete_calls(self):
        """
        The function gets called when the step has to be deleted. It takes care of below logic/flow
        1. Checks if there was a step selected else notify
        2. If there are steps submitted, get the index of the step selected and delete it from 2 places
            a. Test case list
            b. Test case text
        3. Delete all the steps from the selected index till end
        4. Notify the user
        5. Display correct data in the Test case browser
        :return:
        """
        logger.info("Info of step to delete : {}".format(self.current_step_dict))
        if not self.current_step_dict or not self.selected_step_no:
            ToolTip().notify(
                self.notebook_wm,
                "Deleted",
                "No active selection. Select a step to delete!",
                mid=True,
                notification_duration=1800,
                level="warning"
            )
            ToolTip().notify(
                self.browser_steps,
                "Select here",
                "Select a step here",
                mid=True,
                notification_duration=1800,
                level="info"
            )
            return

        if self.test_case_text:
            if self.current_step_dict and self.selected_step_no:
                index_to_delete = [self.test_step_list.index(step) for step in self.test_step_list
                                   if str(step["step"]) == str(self.selected_step_no)][0]
                logger.info("Info of step to delete : {}".format(index_to_delete))

                choice = tkMessageBox.askyesnocancel("Delete steps from {} till end?".format(index_to_delete + 1),
                                                     "Deleting Step {} will delete all steps till last step (Step {})."
                                                     "\n\nProcced?".format(index_to_delete + 1,
                                                                           len(self.test_case_text["wm_steps"])))

                if choice:
                    del self.test_step_list[index_to_delete:]
                    del self.test_case_text["wm_steps"][index_to_delete:]
                    self.add_to_master_tc()
                    self.current_step_dict = {}
                    self.browser_steps.set("")
                    self.selected_step_no = 0
                    self.reset_common_dict()
                    ToolTip().notify(self.notebook_wm,
                                     "Deleted",
                                     "Step {} onwards, deleted ! ".format(index_to_delete + 1),
                                     mid=True,
                                     notification_duration=2200,
                                     level="success"
                                     )
                    self.label_info["text"] = "Select a step from TC browser to display data or submit a new step"
                    self.display_step_text()

    def invoke_edit_calls(self):
        """
        All functionality related to test step edits come here.
        :return: None
        """
        if self.edit_flag:
            logger.info("Info of step to modify : {}".format(self.current_step_dict))
            logger.info("Step number selected   : {}".format(self.selected_step_no))
            logger.info("Step list              : {}".format(self.test_step_list))

            # Fetch the value from the module
            self.pull_common_dict_values()
            self.current_step_dict = self.obj_current_module.get_step()
            self.current_step_dict.update(self.common_options_dict)
            self.current_step_dict["step"] = int(self.selected_step_no)

            if not self.check_step_validity(): return

            # Repalce at index in test case and Test case text
            before = self.test_step_list[int(self.selected_step_no) - 1]
            after = self.current_step_dict

            logger.info("Before Step Test    : {}".format(self.test_step_list[int(self.selected_step_no) - 1]))
            logger.info("Before Step Current : {}".format(self.current_step_dict))

            if self.check_for_changes(before, after):
                self.test_step_list[int(self.selected_step_no) - 1] = self.current_step_dict
                self.test_case_text["wm_steps"][int(self.selected_step_no) - 1] = self.obj_current_module.step_text()
                logger.info(
                    "After Step Test : {}".format(self.test_case_text["wm_steps"][int(self.selected_step_no) - 1]))

                # Notify success
                ToolTip().notify(
                    self.notebook_wm,
                    "Edited",
                    "Edited Step {} saved successfully".format(self.selected_step_no),
                    mid=True,
                    notification_duration=1400,
                    level="success"
                )
                # Process current step
                self.current_step_dict = {}

                # Display the changes
                self.display_step_text()
        else:
            ToolTip().notify(
                self.notebook_wm,
                "No steps selected",
                "No Steps selected. Select test step to edit.",
                mid=True,
                notification_duration=1800,
                level="warning"
            )
            ToolTip().notify(
                self.browser_steps,
                "Select here",
                "Select a step here",
                mid=True,
                notification_duration=1800,
                level="info"
            )

    def check_step_validity(self):
        """
        Function to determine if a step exists when a delete step or edit step is called
        :return: True or False based on validity
        """
        try:
            logger.info("Current step         : {}".format(self.current_step_dict))
            logger.info("Current step in dict : {}".format(self.test_step_list[int(self.selected_step_no) - 1]))
        except IndexError:
            ToolTip().notify(
                self.notebook_wm,
                "No steps",
                "No Steps found. Add a test step first. ",
                mid=True,
                notification_duration=1800,
                level="warning"
            )
            return False
        return True

    def check_for_changes(self, dict1, dict2):
        """
        In case edit is called, determine if the step was actually edited. Compares the step dict saved internally
        with the step received from the module.
        Dictionary in any order is fine. But mentioned the mode of current use as below
        :param dict1: Pre-Saved Dict
        :param dict2: New Dict
        :return: Boolean (True or False based on change happened or not)
        """
        edit_flag = False
        logger.info("DICT 1 : {}".format(dict1))
        logger.info("DICT 2 : {}".format(dict2))
        for i in dict1:
            if dict1.get(i) != dict2.get(i):
                logger.info("DIFFERENT : {} : {}".format(dict1.get(i), i))
                edit_flag = True
                break
            else:
                logger.info("SAME      : {} : {}".format(dict1.get(i), i))
        if edit_flag:
            return True

        ToolTip().notify(
            self.notebook_wm,
            "No Edits",
            "No changes detected for Step {}".format(self.selected_step_no),
            mid=True,
            notification_duration=1800,
            level="warning"
        )
        return edit_flag

    def invoke_savejson_calls(self):
        """
        When a JSON Save is done, it will do a series of actions.
        1. Save JSON in file
        2. TODO : Once saved, post the link where Test Case JSON as been saved. uses can view the JSON
        :return: None
        """
        if not self.master_test_case["tcsteps"]:
            ToolTip().notify(
                self.btn_save_json,
                "Not Saved",
                "No Steps to save. Kindly submit a step to save",
                notification_duration=1400,
                level="warning"
            )
            return

        self.json_handler_obj = JSONHandler(self.btn_save_json)
        save_btn = self.json_handler_obj.get_save_btn()
        save_btn.configure(command=lambda: self.ask_save_json())

    @staticmethod
    def check_create_dir(dir_path):
        """
        Create a DIR tc_json inside the wm_flex folder to save all the JSONs created by default
        :param dir_path: path to create the directory in.
        :return:
        """
        logger.info("DIR PATH : {}".format(dir_path))
        if not os.path.exists(dir_path):
            # Create a new directory because it does not exist
            os.makedirs(dir_path)
            logger.info("The new directory is created : {}".format(dir_path))
        return dir_path

    def ask_save_json(self):
        """
        The function does few things in order.
        1. Generates a name for the JSON to be saved
        2. Grabs the CQ ID as entered in the window
        3. Grabs the CQ test case description and adds to the master test case
        4. Notifies user about the saved JSON
        :return: None
        """
        initial_dir = self.check_create_dir(os.path.join(app_launch_dir, "test_jsons"))
        test_case_name = self.json_handler_obj.cq_id_entry.get().replace(" ", "_")
        if test_case_name.strip(" ") == "":
            ToolTip().notify(
                self.json_handler_obj.cq_id_entry,
                "No ID",
                "Kindly enter an ID to save the JSON with",
                notification_duration=1200,
                level="warning"
            )
            return

        self.master_test_case["test_step_definition"]["id"] = test_case_name

        file_obj = tkFileDialog.asksaveasfile(
            mode='w+',
            defaultextension=".json",
            initialfile="FlexTC_{}".format(test_case_name),
            initialdir=initial_dir,
            filetypes=[('WingMan Flex JSON', '.json')]
        )
        logger.info("File Obj is  : {}".format(file_obj))
        logger.info("File Name is : {}".format(file_obj.name))

        if file_obj:
            self.json_file_path = file_obj.name
            self.save_json_as_file(file_obj.name)

    def save_json_as_file(self, file_name):
        """
        Takes the name and saves the TC as JSON file
        """
        # Add the CQ text in the JSON:
        self.master_test_case["test_step_definition"]["cq_steps"] = self.get_cq_steps()
        logger.info("File name    : {}".format(file_name))
        if file_name:
            with open(file_name, 'w+') as fp:
                logger.info("MASTER TEST CASE : {}".format(self.master_test_case))
                json.dump(self.reorder_master_tc(), fp, sort_keys=False, ensure_ascii=False, indent=4)
                self.json_handler_obj.close_window(JSONHandler.window[0])
                logger.info("JSON saved successfully!")
                ToolTip().notify(
                    self.notebook_wm,
                    "Saved",
                    "JSON saved successfully! ",
                    mid=True,
                    notification_duration=2000,
                    level="success"
                )
                logger.info("JSON saved  in location : {}".format(self.json_file_path))
                self.saved_jsons.append(file_name)
                self.enable_saved_json_view()
                return True
        return False

    def get_cq_steps(self):
        """
        Takes the CQ test case text copied in the window and adds to the JSON being saved
        :return: string (Test case CQ details)
        """
        test_case = self.json_handler_obj.tc_text_widget.get(1.0, "end")
        test_case = test_case.splitlines()
        logger.info("Test Case text : {}".format(test_case))
        return test_case

    # def ordered_test_json(self):
    #     _tmp_dict = copy.deepcopy(self.master_test_case)
    #     new_dict = OrderedDict()
    #     new_dict["test_step_definition"] = {}
    #     new_dict["test_step_definition"]["id"] = _tmp_dict["test_step_definition"]["id"]
    #     new_dict["test_step_definition"]["cq_steps"] = _tmp_dict["test_step_definition"]["cq_steps"]
    #     new_dict["test_step_definition"]["wm_steps"] = _tmp_dict["test_step_definition"]["wm_steps"]
    #
    #     new_dict["tcsteps"] = []
    #     new_dict["tcsteps"] = _tmp_dict["tcsteps"]
    #     logger.info("ORDERED DICT : {}".format(new_dict))
    #     self.master_test_case = copy.deepcopy(new_dict)

    def enable_saved_json_view(self):
        """
        Function to enable the "View Saved JSON" button.
        This function also checks if there are the JSONs saved. If no, there won't be any action.
        The button state will be disabled as well.
        :return: None
        """
        self.btn_view_json.pack(side="right", expand=False)
        self.btn_view_json.config(state="normal")
        if not self.saved_jsons:
            self.btn_view_json.config(state="disable")
            return
        self.btn_view_json.pack(side="right", expand=False)

    def create_test_modules(self):
        """
        This is the function where each module gets plugged into the WM Framework.
        Steps to perform:
        1. From the module file import the module class.
        2. IMPORTANT : Keep module name and tab name same. This used to create association of selected step v/s
            module object to call. Sets the selected step module as the selected object

        # >>> EDIT for Point #2, dated March 24, 2023:
        In case tab names are long and needs to be short, define Test Step Type to Tab Name key:val in the function
        def module_obj_mapper():
        "<module_step_type>" : "<name_of_tab"
        ex : "staticconfig": "config"
        Here :
        staticconfig : This is the step type as seen in JSON.
        config : This is the tab name as seen in GUI
        :return: None
        """
        # Child modules under config tab : Static, Flex and Delete
        self.objs_module['static'] = ConfigModule(self.child_module_tabs["config"]["static"])
        self.objs_module['delete'] = DeleteConfig(self.child_module_tabs["config"]["delete"])
        self.objs_module['flex'] = flexRaid(self.child_module_tabs["config"]["flex"], root=root_window)

        self.objs_module["loop"] = LoopModule(self.tab_modules["loop"], self.refresh_test_steps)
        self.objs_module["io"] = IoModule(self.tab_modules["io"])
        self.objs_module['col'] = ColModule(self.tab_modules["col"])

        # Child module under OPS tab : Foreign Config and Pinned cache
        self.objs_module["foreign config"] = ForeignConfig(self.child_module_tabs["ops"]["foreign config"])
        self.objs_module["pinned cache"] = PinnedCache(self.child_module_tabs["ops"]["pinned cache"])

        self.objs_module["fwop"] = FwOps(self.tab_modules["fwop"])
        self.objs_module["reset"] = ResetModule(self.tab_modules["reset"])
        self.objs_module["snapdump"] = SnapdumpModule(self.child_module_tabs["utils"]["snapdump"])

    def refresh_test_steps(self, ret=True):
        """
        This function is called via lambda functions which traverses the test_step_list and scans and gathers
        the step number details in the list and posts them in the widgets as needed.
        :param ret: if function needs to return a value, boolean
        :return: list
        """
        tc_test_steps = ["No Steps Submitted"]
        if self.test_step_list:
            tc_test_steps = ["Step {}: {}".format(str(_s["step"]).ljust(2), _s["type"].capitalize())
                             for _s in self.test_step_list]
        self.browser_steps["values"] = tc_test_steps
        if ret:
            return tc_test_steps

    def browser_test_steps(self):
        """
        GUI code for placing the browse test steps
        :return: None
        """
        test_step = tk.StringVar()
        lbl = tk.Label(self.frame_broswer_top, text="Select Test Step : ")
        self.frame_broswer_top.tkraise()
        lbl.grid(row=1, column=0, pady=(5, 5))
        lbl.configure(font=LABEL_FONT_3, foreground="#357EC7")
        self.browser_steps = ttk.Combobox(self.frame_broswer_top,
                                          textvariable=test_step,
                                          width=30)
        self.browser_steps["values"] = self.refresh_test_steps()
        self.browser_steps.configure(textvariable=test_step)
        self.browser_steps.current(0)
        self.browser_steps.grid(row=1, column=1, pady=(5, 5))
        self.browser_steps.bind('<Button-1>', lambda event: self.refresh_test_steps())
        self.browser_steps.bind("<<ComboboxSelected>>", lambda event: self.invoke_browse_calls(event))

    def invoke_browse_calls(self, event):
        """
        Once the step is selected, this function calls the required functionality to populate the widgets
        as selecetd from the test step
        :param event: Combobox selected event
        :return: None
        """
        step = event.widget.get()
        logger.info("Selected : {}".format(step))
        self.play_selected_step(step)

    def play_selected_step(self, step):
        """
        This function does few important things under one single responsibility
        1. Takes in the step as parameter
        2. Automatically selects the Tab which corresponds to the module of the step
        3. Updates the notebook tab ticker stating so-and-so step detail is being displayed
        4. Retrieves the object for the module
        5. Sends the data to module to set its widget values as per the test step selected
        :param step: step info
        :return: None
        """
        # Resolve module and step
        self.edit_flag = True
        self.selected_module = step.split(":")[-1].strip().lower()
        self.selected_step_no = step.split(":")[0].strip().split(" ")[-1]

        # In case tab names are different than Module names, resolution happens here.
        module = self.module_obj_mapper(self.selected_module)

        # Select the Tab
        logger.info("Module : {} -> Step {}".format(module, self.selected_step_no))
        if module != 'no steps submitted':
            # # COMMENTED CODE
            # if module in ['foreign config','pinned cache']:
            #     self.notebook_wm.select(self.tab_modules["ops"])
            #     self.ops_new_nb.select(self.ops_tab_modules[module])
            # else:
            #     self.notebook_wm.select(self.tab_modules[module.lower()])
            if not isinstance(module, list):
                self.notebook_wm.select(self.tab_modules[module.lower()])
            else:
                # Browser the child tab space and select the child tab
                # child_tab_mapper : child_notebook : module_name
                logger.info("self.child_module_tabs     : {}".format(self.child_module_tabs))
                self.notebook_wm.select(self.tab_modules[module[0]])
                self.child_module_tabs[module[0]]["child_nb"].select(self.child_module_tabs[module[0]][module[1]])
                module = module[1]
                # pass

            # Update Display information
            self.label_info["text"] = "Selected Step {} : {}".format(self.selected_step_no, module.capitalize())

            # Fetch Step details of Selected Step
            self.current_step_dict = [step for step in self.test_step_list
                                      if str(step["step"]) == str(self.selected_step_no)][0]

            # Call the module object with test step values. Let module populate the widgets
            logger.info("Modules : {}".format(self.objs_module))
            self.objs_module[module.lower()].set_step(self.current_step_dict)
            self.populate_common_widgets()
            self.preselect_on_browse()
        logger.info("No module selected")

    def place_common_wdigets(self):
        """
        All the common widgets have been places seperately on the GUI. Will use this function to place the widget
        which shall shorten the code for main test case frame creation.
        :return: None
        """
        # Define Step References MS : Multi Select
        # Define Step Wait : Entry Box
        # Define Expected Result : Radio Button
        pass

    def populate_common_widgets(self):
        """
        When a step is elected, the common framework widgets will also need to get selected and populated.
        This function will do the same.
        :return:
        """
        try:
            self.entry_wm_step_wait.delete(0, "end")
        except:
            pass

        self.entry_wm_step_wait.insert(0, self.current_step_dict["step_wait"])
        self.expct_res.set(self.current_step_dict["expected_result"].lower())
        # Step Reference Radio button selection is being handled by the Radio Button function internally
        # TODO : Some visual aid to the selected value

    def callback_step_ref(self, key, choices_dict):
        """
        This function does 2 small things and merges them to 1 expected value
        1. Takes in the fresh selection and adds it to current common options dictionary
        2. Also checks if the user is playing back the step (meaning, using the browse feature)
        3. It then merges current selection and pre-selection into one dictionary
        4. Same is used by interfuncton add_cb() to display the choices and reflect fresh selection
        :param key: ket from the common option dict. Here : step_reference
        :param choices_dict: The choices from teh step ref is a dictionary of Step number and "0" / "1" value
        :return: None
        """
        logger.info("Choices dict     : {}".format(choices_dict))
        logger.info("Refactored Steps : {}".format(self.refactored_step_details))
        logger.info("Common Opts      : {}".format(self.common_options_dict))
        if self.refactored_step_details:
            self.refactored_step_details = list(set(self.refactored_step_details))
        j = {"step_reference": {}}
        for k, v in choices_dict.iteritems():
            logger.info("KEY : {}  :  VAL : {}".format(k, v.get()))
            if str(k).strip(" ") in ["", "No Steps Submitted"]:
                continue
            j[key][k.split(":")[0].strip()] = v.get()
            self.common_options_dict[key][k] = v.get()
            logger.info("From Step ref callback : {}".format(self.common_options_dict[key]))

        # If edit flag is set, add the items from the edited flag here and set flag off
        if self.edit_flag:
            for step in self.refactored_step_details:
                # See if the key already exists. If no, then only add.
                if self.common_options_dict[key].get(step, False):
                    self.common_options_dict[key][step] = "1"

                # Key may exist but value may be "0". Set value to "1"
                else:
                    self.common_options_dict[key][step] = "1"
            self.edit_flag = False

    def preselect_on_browse(self):
        """
        When a step is selected from the dropdown, this function will preselect the Step References in the multiselect
        automatically.
        # TODO : Visual Aid to say values has been selected in the drop down
        :return: None
        """
        # Read the step dict
        logger.info("Dict recevied : {}".format(self.current_step_dict))
        selected_step_ref = self.current_step_dict["step_reference"]
        logger.info("Selected step ref is : {}".format(selected_step_ref))
        step_type = self.current_step_dict["type"]

        # Extract the Steps with value as 1
        steps = ["{} : {}".format(step, step_type.capitalize()) for step in selected_step_ref]
        logger.info("Steps are : {}".format(steps))
        self.refactored_step_details = steps
        logger.info("Refactored Step details : {}".format(self.refactored_step_details))

    def modify_step_ref_to_dict(self, step_ref):
        """
        Since step reference in the JSON is in list format, this converts it to dictionary
        :param step_ref: the step reference in the selected step
        :return: dict
        """
        logger.info("Step reference dict is : {}".format(step_ref))
        mod_ref = {j: "1" for j in step_ref} if not isinstance(step_ref, dict) else step_ref
        return mod_ref

    def clear_tc_text_widget(self):
        """
        Since there is an indicative text in the text box widget, it gets filled with the text in case there is
        no step or all steps were deleted
        :return:
        """
        if "Test Case text appears here" in self.tc_text_widget.get("1.0", "end"):
            self.tc_text_widget.configure(state="normal")
            self.tc_text_widget.delete("1.0", "end")
            self.tc_text_widget.configure(state="disabled")
            self.tc_text_widget.configure(foreground=COLOR["darkgrey"])

        if not self.current_step_dict and not self.test_case_text["wm_steps"]:
            self.tc_text_widget.configure(state="normal")
            self.tc_text_widget.delete("1.0", "end")
            self.tc_text_widget.insert("end", "\n\n\tUgh...the test step list is so empty!")
            self.tc_text_widget.configure(selectbackground=self.tc_text_widget.cget('fg'),
                                          inactiveselectbackground=self.tc_text_widget.cget('bg'))
            self.tc_text_widget.configure(state="disabled")
            self.tc_text_widget.configure(foreground=COLOR["lightgray"])
            self.browser_steps.set("")
            self.label_info["text"] = "Create your Test Case"
            self.tc_text_widget.configure(foreground=COLOR["darkgrey"])

    def display_step_text(self):
        """
        Displays test case text that we have in the JSON. Each step produces a text at time of submission. The same
        gets dispalyed here
        :return: None
        """
        self.clear_tc_text_widget()
        if self.test_step_list or self.current_step_dict:
            self.step_text = self.obj_current_module.step_text()
            self.tc_text_widget.configure(state="normal")
            self.tc_text_widget.delete("1.0", "end")
            for index, step in enumerate(self.test_case_text["wm_steps"]):
                self.tc_text_widget.insert("end", " Step {} : {}\n".format(index + 1, step))
            if self.current_step_dict:
                self.tc_text_widget.insert("end",
                                           " Step {} : {}\n".format(self.current_step_dict["step"], self.step_text))
            self.tc_text_widget.configure(state="disabled")

    def add_cb_step_ref(self):
        """
        # The function should return the following
        # 1. Get the step list just as the Browser step
        # 2. Resolute it to just Step numbers as actually seen in the Test step JSON
        # 3. Carry on the information of the Step chosen and make values (0, 1) based on availability in the JSON
        """
        x = ttk.Label(self.frame_mid, text="Select step references", style='Custom.TLabel')
        x.grid(row=0, column=0, sticky="w", padx=(10, 5), pady=(5, 5))
        x.config(background=COLOR["tkinterDef"])

        def add_cb():
            for choice in self.refresh_test_steps():
                logger.info("Choice : {}".format(choice))
                if not self.edit_flag:
                    if isinstance(self.common_options_dict["step_reference"], list):
                        self.common_options_dict["step_reference"] = self.modify_step_ref_to_dict(
                            self.common_options_dict["step_reference"])
                    logger.info("Edit check is off : {}".format(self.common_options_dict["step_reference"]))
                    choices_dict[choice] = tk.StringVar(value=self.common_options_dict["step_reference"].get(choice,
                                                                                                             "0"))
                else:
                    logger.info("Edit check is on : {}".format(self.refactored_step_details))
                    choices_dict[choice] = tk.StringVar(value="1" if choice in self.refactored_step_details else "0")
                menu.add_checkbutton(label=choice,
                                     variable=choices_dict[choice],
                                     onvalue="1",
                                     offvalue="0",
                                     command=partial(self.callback_step_ref, "step_reference", choices_dict))

        choices_dict = {}
        self.ms_step_ref = ttk.Menubutton(
            self.frame_mid,
            text=" Choose step(s) as applicable",
            width=30,
            style='TMenubutton'
        )
        menu = tk.Menu(self.ms_step_ref, tearoff=False)
        add_cb()
        self.ms_step_ref.configure(menu=menu)

        def update_menu():
            self.refresh_test_steps()
            menu.delete(0, tk.END)
            add_cb()

        self.ms_step_ref.bind("<Enter>", lambda event: update_menu())
        self.ms_step_ref.grid(row=0, column=1, sticky="w", padx=(10, 5), pady=(5, 5))

    def add_entry_step_wait(self):
        """
        This widget will be a GROUP of widgets as the requirement is to have multiple values combined together
        to give a collective time/iteration value.
        TODO : Add all the values needed to make the entry time
        iterationcount, delay, interval, step
        :return: None
        """
        x = ttk.Label(self.frame_mid, text="Enter step wait", style='Custom.TLabel')
        x.grid(row=1, column=0, sticky="w", padx=(10, 5), pady=(0, 5))
        x.config(background=COLOR["tkinterDef"])

        self.entry_wm_step_wait = ttk.Entry(self.frame_mid, width=35)
        self.entry_wm_step_wait.bind("<Enter>",
                                     lambda _: ToolTip().notify(self.entry_wm_step_wait,
                                                                "Choose Step Wait",
                                                                "Enter step wait:"
                                                                " iteration1: iteration, Dec,timeInterval Step"))
        try:
            self.entry_wm_step_wait.delete(0, "end")
        except:
            pass

        self.entry_wm_step_wait.bind("<KeyRelease>",
                                     lambda event: self.entrybox_callback(event, "step_wait"))
        self.entry_wm_step_wait.grid(row=1, column=1, sticky="w", padx=(10, 5), pady=(0, 5))

    def entrybox_callback(self, event, key):
        """
        Reads values from the step wait step entry box
        :param event: Key Release event
        :param key: Which key is to be modified
        :return: None
        """
        value = event.widget.get().strip()
        logger.info("Key : {}, Text Box Value : {}".format(key, value))
        self.common_options_dict[key] = value
        logger.info("Common options : {}".format(self.common_options_dict))

    def add_radiobtn_expected_result(self):
        """
        Added test step expected value widget in the main GUI
        :return: None
        """
        x = ttk.Label(self.frame_mid, text="Choose expected result", style='Custom.TLabel')
        x.grid(row=2, column=0, sticky="w", padx=(10, 5), pady=(0, 5))
        x.config(background=COLOR["tkinterDef"])

        opts = {
            "Pass": "pass",
            "Fail": "fail",
            "Ignore": "ignore"
        }

        style_map = {
            "Fail": "Fail.TRadiobutton",
            "Pass": "Pass.TRadiobutton",
            "Ignore": "Normal.TRadiobutton",
        }

        self.expct_res = tk.StringVar(None, "pass")
        sticky = ["e", "ns", "w"]
        i = 0
        for key, val in opts.iteritems():
            self.rb_expected_result = ttk.Radiobutton(
                self.frame_mid,
                text=str(key),
                value=str(val),
                variable=self.expct_res,
                command=lambda: self.radiobutton_callback("expected_result")
            )
            self.rb_expected_result.grid(row=2, column=1, columnspan=2, sticky=sticky[i], padx=5)
            self.rb_expected_result.configure(style=style_map[key])
            i += 1

    def radiobutton_callback(self, key):
        """
        Radio button callback takes in input from the EXPECT RESULT in the WM framework.
        We would need changes in case this needs to handle other radio buttons in the framework.
        :param key: Key from the self.common_options_dict to change the value in
        :return: None
        """
        value = self.expct_res.get().strip()
        logger.info("Key : {}, Text Box Value : {}".format(key, value))
        self.common_options_dict[key] = value
        logger.info("Common options : {}".format(self.common_options_dict))


if __name__ == '__main__':
    bazinga = Wingman()
    bazinga.main()
    WMMenu(root_window)
    # Bind the <B1-Motion> event to the callback function
    root_window.bind('<B1-Motion>', lambda _: resize_notebooks(_, bazinga.canvas_left, bazinga.canvas_right))
    root_window.mainloop()

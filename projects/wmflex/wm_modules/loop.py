#!/usr/bin/env python
"""
#####################################################################################
#                                                                                   #
#    Copyright 2023-2022 Broadcom.  All Rights Reserved.  Broadcom Confidential.    #
#     The term "Broadcom" refers to Broadcom Inc. and/or its subsidiaries.          #
#                                                                                   #
#####################################################################################

Wingman Flex GUI is the GUI developed for creating and supporting the flex requirements for the Product test.
"""
__doc__ = '''
Defines custom style on top of ttk CLAM theme
'''
__author__ = ["Amitabh Suman"]
__copyright__ = "Copyright 2023-24, The Wingman Flex Project"
__version__ = 'loop_1.0.0'  # Major.Minor.Patch
__credits__ = ["MRPT"]
__email__ = 'dcsg-pt-bangalore-automation.pdl@broadcom.com'
__status__ = 'Development'
__maintainer__ = "Wingman Automation Team"
__enhancements__ = '''
DATE(M/D/Y)  CQID            WHO(CQUser)  DESCRIPTION
===============================================================
03/07/23     DCSG01431093    asuman       Ph1: Wingman 3.0: New GUI framework for flex config requirements
03/24/23     DCSG01431093    asuman       Ph2: Wingman 3.0: New GUI framework for flex config requirements
03/24/23     DCSG01431509    asuman       Ph1: WM Flex 3.0 : (GUI) : Implement Add-Delete Config, Add-Delete JBOD \
                                          (non-raid), Stop IO
'''
import Tkinter as tk
import ttk
from copy import deepcopy
from custom_styles import COLOR, FONT
import logging
from tooltip import ToolTip
from PIL import Image, ImageTk
import os

logger = logging.getLogger("root")


class LoopModule:
    def __init__(self, parent, step_list):
        self.parent = parent
        self.get_step_list = step_list
        self.steps_list = []
        self.steps_found = False
        self.custom_input_entry = {}
        self.loop_dictionary = {}
        self.reset_module_dict()
        self.loop_form()

    def reset_module_dict(self):
        """
        Defines the module dictionary for Loop Test Steps
        :return: None
        """
        self.loop_dictionary = {
            "type": "loop",
            "steplist": [],
            "duration": "",
            "count": ""
        }

    def loop_form(self):
        """
        This is the main function that basically renders the form for the Loop step
        :return: None
        """
        ttk.Label(self.parent, text="Enter step number(s) to loop",
                  style='Custom.TLabel').grid(row=0, column=0, sticky="nw", padx=(10, 5), pady=(0, 10))

        self.get_scoll_textbox(self.parent, 0, 1)
        self.test_step_list_logo(self.parent, 0, 4)
        self.step_icon.bind("<Enter>", lambda _: self.show_step_list())
        self.cb_loop_iteration(self.parent, 3, 0)
        # self.entry_iteration_count(self.parent, 4, 0)
        self.entry_iteration_duration(self.parent, 5, 0)

    def get_scoll_textbox(self, parent, row, col, **kwargs):
        """
        Since ste numbers can swell us, adding a scrollbar for easy user experience
        """
        f = tk.Frame(parent)
        f.grid(row=row, column=col, columnspan=kwargs.get("columnspan", 3))

        xscrollbar = ttk.Scrollbar(f, orient="horizontal")
        xscrollbar.grid(row=row+1, column=col, sticky="nsew")

        self.step_entry_widget = tk.Text(
            f,
            wrap="none",
            xscrollcommand=xscrollbar.set,
            width=50,
            height=1,
            borderwidth=1)
        self.step_entry_widget.grid(row=row, column=col, sticky="w", pady=(1,0))
        xscrollbar.config(command=self.step_entry_widget.xview)
        self.step_entry_widget.bind("<KeyRelease>", lambda event: self.entrybox_callback(event, "steplist"))
        self.step_entry_widget.bind('<Control-a>', lambda event: self.select_all(event))
        self.step_entry_widget.bind('<Control-A>', lambda event: self.select_all(event))

        self.wrong_step_label = ttk.Label(self.parent, text="")
        self.wrong_step_label.configure(font=FONT['courier_new'])
        self.wrong_step_label.grid(row=2, column=0, sticky="w", padx=(10, 0), pady=(2, 5), columnspan=7)
        self.step_entry_widget.bind("<KeyRelease>", lambda event: self.check_valid_step(event))
        return self.step_entry_widget

    def show_step_list(self):
        """
        In the tooltip icon, show the steps submitted in case use needs help to know what all steps have
        been submitted.
        :return: None
        """
        post_text = '\n\nSteps ex. 1,3,5,6,7,8\n' \
                    'Range ex. 1-7,8,9-12'
        ToolTip().notify(
            self.step_icon,
            "Steps",
            "Steps so far :\n{}{}".format('\n'.join([step for step in self.get_step_list()]), post_text),
            mid=False
        )

    def cb_loop_iteration(self, parent, row, col):
        """
        Combobox for selecting the loop iteration
        :param parent: Frame where this widget sits
        :param row: Row for placing the widget
        :param col: Column for placing the widget
        :return: None
        """
        ttk.Label(
            parent,
            text="Choose Iteration/count",
            style='Custom.TLabel').grid(row=row, column=col, sticky="w", padx=(10, 5), pady=(0, 5))
        self.iteration_list = ["Iteration1", "Iteration2", "Custom"]
        self.selected_iteration = tk.StringVar()
        self.cb_iteration = ttk.Combobox(parent, textvariable=self.selected_iteration, width=30)
        self.cb_iteration["values"] = self.iteration_list
        self.cb_iteration.current(self.iteration_list.index('Iteration1'))
        self.cb_iteration.grid(row=row, column=col+1, sticky="w")
        self.cb_iteration.bind("<<ComboboxSelected>>", lambda event: self.dropdown_callback(event, "count"))

    def entry_iteration_count(self, parent, row, col):
        """
        Entrybox for selecting the loop count
        :param parent: Frame where this widget sits
        :param row: Row for placing the widget
        :param col: Column for placing the widget
        :return: None
        """
        ttk.Label(
            parent,
            text="Enter Loop count",
            style='Custom.TLabel').grid(row=row, column=col, sticky="w", padx=(10, 5), pady=(0, 5))
        self.entry_loop_count = ttk.Entry(parent, width=30)
        self.entry_loop_count.bind("<KeyRelease>",
                                lambda event: self.entrybox_callback(event, "count"))
        self.entry_loop_count.grid(row=row, column=col+1, sticky="w")
        self.entry_loop_count.insert(0, "1")

    def entry_iteration_duration(self, parent, row, col):
        """
        Combobox for selecting the loop iteration
        :param parent: Frame where this widget sits
        :param row: Row for placing the widget
        :param col: Column for placing the widget
        :return: None
        """
        ttk.Label(
            parent,
            text="Enter Loop duration (in seconds)",
            style='Custom.TLabel').grid(row=row, column=col, sticky="w", padx=(10, 5), pady=(0, 5))
        self.duration_list = ["Duration1", "Duration2", "Custom"]
        self.selected_duration = tk.StringVar()
        self.cb_duration = ttk.Combobox(parent, textvariable=self.duration_list, width=30)
        self.cb_duration["values"] = self.duration_list
        self.cb_duration.current(self.duration_list.index('Duration1'))
        self.cb_duration.grid(row=row, column=col + 1, sticky="w")
        self.cb_duration.bind("<<ComboboxSelected>>", lambda event: self.dropdown_callback(event, "duration"))

    def test_step_list_logo(self, parent, row, col):
        """
        Logo for step list display
        :param parent: Frame where this logo sits
        :param row: Row for placing the widget
        :param col: Column for placing the widget
        :return: Label of the step list
        """
        img = Image.open(os.path.join(os.getcwd(), "icons", "list.png"))
        img = img.resize((18, 18), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(img)
        self.step_icon = tk.Label(image=img, master=parent)
        self.step_icon.image = img  # keep a reference!
        self.step_icon.grid(row=row, column=col, sticky="nw", pady=(2, 0))
        return self.step_icon

    def select_all(self, event):
        """
        Bind the ctrl+a feature to select all the steps entered.
        :param event: Ctrl + A / a
        :return: Break selection
        """
        event.widget.tag_add("sel", "1.0", "end")
        event.widget.mark_set("insert", "1.0")
        event.widget.see("insert")
        return 'break'

    def dropdown_callback(self, event, key):
        """
        Gets the dropdown value and modifies the dictionary value
        :param event: ComboboxSelected event
        :param key: Key in the dictionary associated to the dropdown
        :return: None
        """
        new_val = event.widget.get()
        logger.info("Dropdown selected: {}".format(new_val))
        if new_val.lower() != "custom":
            self.loop_dictionary[key] = new_val
            logger.info("self.custom_input_entry : {}".format(self.custom_input_entry))
            try:
                self.custom_input_entry[key].grid_remove()
            except:
                pass
        else:
            self.custom_entry(event, key)
        logger.info("Config Dict : {}".format(self.loop_dictionary))

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
        logger.info("Key : {}, Text Box Value : {}".format(key, value))
        self.loop_dictionary[key] = value
        logger.info("Loop Dict : {}".format(self.loop_dictionary))

    def check_valid_step(self, event):
        """
        Checks the validity of the step entered and informs user as necessary
        :param event: KeyRelease
        :return: Step Validity
        """
        test_steps = self.get_step_list()
        logger.info("Steps formed : {}".format(test_steps))
        steps_entered = event.widget.get("1.0", "end")
        if steps_entered.replace(" ", "").split(",")[-1] in (",", " ", "", None):
            return

        # Get steps from the framework
        if test_steps[0] == 'No Steps Submitted':
            test_steps = []
            self.steps_found = False
        test_steps = [str(step.split(":")[0].strip(" ").split(" ")[-1]) for step in test_steps]

        # Check last step entered
        logger.info("Step entered : {}".format(event.widget.get("1.0", "end")))
        last_step = steps_entered.strip(" ").split(",")[-1].strip('\n')
        logger.info("Test Steps : {}".format(test_steps))
        logger.info("Last Step :  {} type : {}".format(last_step, type(last_step)))

        if '-' in last_step:
            txt = self.resolute_step_range(last_step, test_steps)
            if txt==[]:
                txt = "All steps found in range {}".format(last_step)
                self.wrong_step_label.configure(foreground=COLOR["darkgreen"])
                self.steps_found = True
            else:
                mid_list = [txt[0], txt[-1]] if len(txt) > 1 else txt
                txt = "Steps {} not found in given range".format(" to ".join(mid_list))
                self.wrong_step_label.configure(foreground="red")
                self.steps_found = False
        else:
            txt = self.is_step_present(last_step, test_steps)
            if self.steps_found:
                logger.info("Last step : {}".format(last_step))
                self.steps_list.append(str(last_step.strip('\n')))
                logger.info("self.step_listd : {}".format(self.steps_list))
        self.wrong_step_label.configure(text=txt)

    def is_step_present(self, last_step, test_steps):
        """
        Prints the step validity in the lable
        :param last_step: Most recent step entered
        :param test_steps: List of all test steps submitted so far
        :return: Boolean
        """
        if str(last_step).strip(" ") not in test_steps:
            txt = "Step not found : {}".format(last_step.strip('\n'))
            self.wrong_step_label.configure(foreground="red")
            self.steps_found = False

        else:
            txt = "Valid step : {}".format(last_step.strip('\n'))
            self.wrong_step_label.configure(foreground=COLOR["darkgreen"])
            self.steps_found = True

        if str(last_step).strip(" ").strip("\n") == '':
            txt = ''
        return txt

    def resolute_step_range(self, last_step, test_steps):
        """
        In case the step was entered as a range, it will resolve the steps in actual steps in the JSON
        It also makes sure that all steps are valid in range. If not, inform the user.
        :param last_step: Most recent step entered
        :param test_steps: List of all test steps submitted so far
        :return: Boolean
        """
        step_not_found = []
        try:
            steps = last_step.split("-")
            logger.info("Steps : {}".format(steps))
            step_range = [i for i in range(int(steps[0]), int(steps[1])+1)]
            for step in step_range:
                if str(step) not in test_steps:
                    step_not_found.append(str(step))
                    self.steps_list = []
                else:
                    self.steps_list.append(str(step)) if str(step) not in self.steps_list else 0
        except:
            pass
        return step_not_found

    def step_text(self):
        """
        Used by the framework to get the step text that appears in the JSON step text
        :return: String (step text)
        """
        self.pull_selected_values()
        txt = "Loop steps {} for {} seconds".format(self.loop_dictionary["steplist"], self.loop_dictionary["duration"])
        return txt

    def destroy_custom_widget(self, opts=None):
        """
        Destroys the custom entry widget that appears when the selection is custom
        :param opts: "iteration" and/or "duration"
        :return: None
        """
        if opts is None:
            opts = ["count", "duration"]
        if "count" in opts:
            try:
                self.custom_input_entry["count"].destroy()
                del self.custom_input_entry["count"]
            except KeyError:
                pass

        if "duration" in opts:
            try:
                self.custom_input_entry["duration"].destroy()
                del self.custom_input_entry["duration"]
            except KeyError:
                pass

    def set_step(self, step_dict):
        """
        This is the function that the framework uses and send the data to the module to set the widget values of the
        module to the values as submitted in the test step
        :param step_dict: The step dict for step selected
        :return: None
        """
        self.destroy_custom_widget()
        logger.info("DICT RECIEVED     : {}".format(step_dict))
        logger.info("CUSTOM ENTRY DICT : {}".format(self.custom_input_entry))
        self.step_entry_widget.delete("1.0", "end")
        self.step_entry_widget.insert("1.0", ",".join(step_dict["steplist"]))

        if step_dict["count"].lower() not in ("iteration1", "iteration2"):
            self.cb_iteration.current(self.iteration_list.index("Custom"))
            self.create_custom_entry_widget("count", 3, 1)
            self.custom_input_entry["count"].insert(0, step_dict["count"])
        else:
            self.cb_iteration.current(self.iteration_list.index(step_dict["count"].capitalize()))
            self.destroy_custom_widget(opts=["count"])

        if step_dict["duration"].lower() not in ("duration1", "duration2"):
            self.cb_duration.current(self.duration_list.index("Custom"))
            self.create_custom_entry_widget("duration", 5, 1)
            self.custom_input_entry["duration"].insert(0, step_dict["duration"])
        else:
            self.cb_duration.current(self.duration_list.index(step_dict["duration"].capitalize()))
            self.destroy_custom_widget(opts=["duration"])

    def pull_selected_values(self):
        """
        Get the values of all the widgets when called
        :return: None
        """
        iteration = self.cb_iteration.get()
        logger.info("self.custom_input_entry : {}".format(self.custom_input_entry))
        if iteration.lower() == 'custom':
            iteration = self.custom_input_entry["count"].get()

        duration = self.cb_duration.get()
        if duration.lower() == 'custom':
            duration = self.custom_input_entry["duration"].get()

        if not all((iteration, duration)):
            logger.info("Empty Entries for custom values. Kindly enter value and submit")
            ToolTip().notify(self.parent,
                             "Empty Inputs",
                             "Empty Entries for custom values",
                             mid=True,
                             level="warning",
                             notification_duration=1400)
            return False

        self.loop_dictionary = {
            "type": "loop",
            "steplist": self.steps_list,
            "count": iteration.lower(),
            "duration": duration.lower(),
        }
        logger.info("Pulled values : {}".format(self.loop_dictionary))
        return self.loop_dictionary

    def check_steplist_before_submission(self):
        """
        A final check before submitting the step. Incase the value is not valid, inform user.
        :return: Boolean
        """
        logger.info("Steps found : {}".format(self.steps_found))
        if not self.steps_found:
            ToolTip().notify(self.parent,
                             "Steps not found",
                             "Check entered steps and verify they are valid",
                             mid=True,
                             level="warning",
                             notification_duration=1400)
            return False
        return True

    def get_step(self):
        """
        Used by framework and returns the value of the widget in the format as decided.
        :return: Dict (step dictionary)
        """
        if self.check_steplist_before_submission():
            if self.pull_selected_values():
                tmp = deepcopy(self.loop_dictionary)
                self.reset_module_dict()
                return tmp

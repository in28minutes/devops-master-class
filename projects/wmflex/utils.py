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
    utils.py takes in all the functionality needed to feed the framework with"
    It also houses the JSONHandler class that handles all the operations needed to save a JSON
"""
__author__ = ["Amitabh Suman"]
__copyright__ = "Copyright 2023-24, The Wingman Flex Project"
__version__ = 'utils_1.0.0'  # Major.Minor.Patch
__credits__ = ["MRPT"]
__email__ = 'dcsg-pt-bangalore-automation.pdl@broadcom.com'
__status__ = 'Development'
__maintainer__ = "Wingman Automation Team"

# Change to next line in case the ER length is > 80 characters
__enhancements__ = '''
DATE(M/D/Y)  CQID            WHO(CQUser)  DESCRIPTION
===============================================================
03/24/23     DCSG01431093    asuman       Ph2: Wingman 3.0: New GUI framework for flex config requirements
03/24/23     DCSG01431509    asuman       Ph1: WM Flex 3.0 : (GUI) : Implement Add-Delete Config, Add-Delete JBOD \
                                          (non-raid), Stop IO
03/24/23     DCSG01458079    nmartis       Update Raid Keywords in ConfigFileGUI
04/10/233    DCSG01431388    saprabhu     Wingman 3.0: Add support for ATE2 module in Wingman Flex
'''

import logging
from Tkinter import *
import Tkinter as tk
import ttk
from custom_styles import FONT, COLOR, LABEL_FONT_3
from PIL import Image, ImageTk
import os, sys
import psutil
import subprocess
import time
import tkMessageBox

CONFIGFILEPATH = os.path.join("c:\wingman", 'config_file_flex.json') if sys.platform.startswith(
    'win') else os.path.join("/root/wingman", 'config_file_flex.json')

def get_app_launch_dir():
    """
    Returns the path from where the application has been launched
    :return: Path
    """
    app_launch_dir = os.getcwd()
    return app_launch_dir

def get_logger(name, fileName='newLog'):
    """
    Returns logger to log the execution report. Using the default roo logger, all the modules can use same logger
    to log the details
    :param name: Name of the logger. Here "root"
    :return: root logger
    """
    logFormatter = logging.Formatter('%(asctime)s,%(msecs)03d %(levelname)-8s\
        [%(filename)s:%(funcName)16s():%(lineno)d] %(message)s',
                                     datefmt='%Y-%m-%d:%H:%M:%S')
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    fileHandler = logging.FileHandler("{0}/{1}.log".format(os.getcwd(), fileName))
    fileHandler.setFormatter(logFormatter)
    logger.addHandler(fileHandler)
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    consoleHandler.setLevel(logging.INFO)
    logger.addHandler(consoleHandler)
    return logger


class JSONHandler:

    instance = None
    number = 0
    window = []

    def __init__(self, parent):
        """
        Allow only 1 instance of the window to open and save the Test case as JSON
        :param parent:
        """
        print("Instance created : {}".format(JSONHandler.number))
        if JSONHandler.number == 0:
            self.ask_cq_details(parent)
            JSONHandler.number += 1
        try:
            JSONHandler.window[0].lift()
            JSONHandler.window[0].grab_set()
        except tk.TclError:
            JSONHandler.window = []
            self.ask_cq_details(parent)
            JSONHandler.number += 1

    def __new__(cls, *args, **kwargs):
        """
        Allow only 1 object of the class
        :param args:
        :param kwargs:
        """
        if not isinstance(cls.instance, cls):
            cls.instance = object.__new__(cls)
        return cls.instance

    def ask_cq_details(self, widget):
        """
        Render the window to take the user input for Test case ID and Test Case description
        :param widget: Parent
        :return: None
        """
        cq_id_win = self.get_toplevel_window(widget)
        JSONHandler.window.append(cq_id_win)

        frame_cq_top = tk.Frame(cq_id_win, height=15)
        frame_cq_top.pack(fill="x", side="top", expand=0, padx=5, pady=5)

        frame_cq_top_sub1 = tk.Frame(frame_cq_top, height=5)
        frame_cq_top_sub1.pack(fill="x", side="left", expand=0, padx=5, pady=5)

        frame_cq_top_sub2 = tk.Frame(frame_cq_top, height=10)
        frame_cq_top_sub2.pack(fill="x", expand=0, side="right", padx=5, pady=5)

        frame_cq_mid = tk.Frame(cq_id_win)
        frame_cq_mid.pack(fill="both", expand=1, padx=5, pady=5)

        self.frame_cq_down = tk.Frame(cq_id_win, height=15)
        self.frame_cq_down.pack(fill="x", side="bottom", expand=0, padx=5, pady=5)

        # Add Entrybox for CQ ID
        lbl = ttk.Label(frame_cq_top_sub1,
                        text="Enter CQ ID for the test case : ",
                        style='Custom.TLabel')
        lbl.grid(row=0, column=0, sticky="w")
        lbl.configure(background=COLOR["tkinterDef"])
        self.cq_id_entry = tk.Entry(frame_cq_top_sub1, width=50)
        self.cq_id_entry.grid(row=0, column=1, sticky="w", padx=(5))

        # Add TextBox for Flex test
        self.tc_text_widget = self.get_text_box(frame_cq_mid)

    def close_logo(self, frame, parent):
        """
        NOT USED : Function to place a close logo. Was being used mid of development. Here for future use.
        :param frame: Frame to place the close button
        :param parent: Widget to destroy
        :return: Close button
        """
        img = Image.open(os.path.join(os.getcwd(), "icons", "close.png"))
        img = img.resize((35, 35), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(img)
        close_button = ttk.Button(frame, text='X', image=img, command=self.close_window(parent))
        close_button.image = img  # keep a reference!
        close_button.pack(side='right', padx=(0, 0), pady=(0, 0), expand=False)
        return close_button

    def close_window(self, parent):
        """
        Resetting the class variables when window is closed
        :param parent: Parent to close
        :return: None
        """
        JSONHandler.number = 0
        JSONHandler.window = []
        parent.destroy()

    def get_text_box(self, parent):
        """
        Text box where the CQ test steps entry is taken
        :param parent: Parent to place this box
        :return: Text widget
        """
        # Add a Scrollbar(horizontal)
        v = ttk.Scrollbar(parent, orient='vertical')
        v.pack(side="right", fill='y')

        # Add a text widget
        tc_text_widget = tk.Text(parent,
                                  font=LABEL_FONT_3,
                                  foreground=COLOR["dimgray"],
                                  yscrollcommand=v.set)

        tc_text_widget.insert("end", "\n      Copy Test case description from CQ")
        tc_text_widget.configure(selectbackground=tc_text_widget.cget('fg'),
                                      inactiveselectbackground=tc_text_widget.cget('bg'))
        tc_text_widget.configure(state="disabled")
        tc_text_widget.bind('<Button-1>', lambda event: self.clear_text_widget(event))
        tc_text_widget.bind('<Leave>', lambda event: self.check_text_widget(event))

        # Attach the scrollbar with the text widget
        v.config(command=tc_text_widget.yview)
        tc_text_widget.pack(fill="both", expand=1)
        return tc_text_widget


    def get_toplevel_window(self, widget):
        """
        Create a top level window to place all other widgets needed to achieve this GUI.
        :param widget: Widget where to place this window wrt to.
        # :return: Toplevel window
        """
        cq_id_win = tk.Toplevel()
        pos_x = widget.winfo_rootx()
        pos_y = widget.winfo_rooty()
        widget_width = widget.winfo_width()
        widget_height = widget.winfo_height()
        cq_id_win.geometry("%dx%d+%d+%d" % (widget_width+2,
                                           580,
                                           pos_x-10,
                                           pos_y-615))
        cq_id_win.focus_force()
        cq_id_win.title("Enter CQ details to save JSON")
        cq_id_win.wm_attributes("-topmost", 1)
        cq_id_win.wm_attributes("-topmost", 0)
        return cq_id_win

    def get_save_btn(self):
        """
        Create a save button and pass it on to the calling function
        :return: ttk.Button object
        """
        # SAVE TEST CASE JSON BUTTON
        btn_save_json = ttk.Button(
            self.frame_cq_down,
            text="Save now",
            width=30,
        )
        btn_save_json.config(style='Wild.TButton')
        btn_save_json.pack(side="right", expand=0, fill="x", padx=5, ipady=5)
        return btn_save_json

    def clear_text_widget(self, event):
        """
        Clears the text widget in events like click
        :param event:
        :return: None
        """
        if "Copy Test case description from CQ" in event.widget.get("1.0", "end").strip(" \n"):
            event.widget.configure(state="normal")
            event.widget.delete("1.0", "end")

    def check_text_widget(self, event):
        """
        Poplulates the text widget in events when mouse moves away and no text has been entered
        :param event: Mouse move away / Focus out
        :return: None
        """
        if event.widget.get("1.0", "end").strip(" \n") == "":
            event.widget.configure(state="normal")
            event.widget.delete("1.0", "end")
            event.widget.insert("end", "\n      Copy Test case description from CQ")



class ate2:
    """
    Automated Test Environment
    """
    def __init__(self):
        self.log = get_logger("ate2")

    def clear_execution(self, type=0):
        """
        To clear the ate process
        """
        if self.check_process_running():
            self.stop_ate2_queue(type)
        else:
            self.notification_terminate("ate2server error",
                                        "ate2server process not running!\nRestart ATE2 and try again",
                                        2000)

    def notification_terminate(self, title, message, notification_duration):
        """
        This function is used to pop-up a self terminating window with message as appropriate to the
        event with user defined time as one parameter for calling this function.
        """

        top = Toplevel(height=70, width=500)
        self.root = tk.Tk()
        self.root.withdraw()
        pos_x = self.root.winfo_rootx()
        pos_y = self.root.winfo_rooty()
        top.geometry("%dx%d+%d+%d" % (500, 70, pos_x + 350, pos_y + 300))
        top.overrideredirect(True)
        top.wm_attributes('-alpha', 0.8)
        top.wm_attributes('-topmost', True)
        top.title(title)
        Message(top, text=message, padx=20, pady=20, width=450, borderwidth=4, justify=CENTER,
                   background="black", foreground="white", font=("segoe", "9", "bold")).pack(side=LEFT)
        top.after(notification_duration, top.destroy)

    def execute_cmd(self, cmd=''):
        """
        To execute OS commands
        """

        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        final_out = ""
        while True:
            output = p.stdout.readline()
            if output == '' and p.poll() is not None:
                break
            if output:
                final_out = final_out + '\n' + output
            rc = p.poll()
        return final_out

    def check_process_running(self, name="ate2server"):
        """
        To check any process is running on machine
        """

        if sys.platform.startswith('win'):
            service = None
            try:
                service = psutil.win_service_get(name)
                service = service.as_dict()
            except Exception as ex:
                self.log.error(str(ex))
            if service and service['status'] == 'running':
                return True
            else:
                return False
        else:
            output = subprocess.check_output(['ps', '-eaf'])
            if name in output:
                return True
            else:
                return False

    def restart_ate2(self):
        """
        Stop the ATE2service and then start it again
        """

        if os.name.lower().startswith("nt"):  # Windows
            self.execute_cmd("start /wait cmd /c ate2server.py stop")
            time.sleep(5)
            self.execute_cmd("start /wait cmd /c ate2server.py start")
            time.sleep(5)
            # configure the service as auto starting
            import win32service
            scm = win32service.OpenSCManager(
                None, None, win32service.SC_MANAGER_ALL_ACCESS)
            service = win32service.OpenService(
                scm, 'Ate2Server', win32service.SERVICE_ALL_ACCESS)
            win32service.ChangeServiceConfig(
                service,
                win32service.SERVICE_NO_CHANGE,
                win32service.SERVICE_AUTO_START,
                win32service.SERVICE_NO_CHANGE,
                None, None, False, None, None, None, None)
        else:
            self.execute_cmd("service ate2server stop")
            self.execute_cmd("service ate2server start")


    def stop_ate2_queue(self, stop_all=True):
        """
        To stop current running/queued/all tests
        """

        cmd = "ate2run list"
        out = self.execute_cmd(cmd).strip()
        self.log.info("output of command %s"%out)
        if "Appears as though there are no queued items" in out:
            self.notification_terminate("In Progress!", "No queued test found, ATE Queue is empty\n", 3000)
        else:
            user_notify = "Cancellation is in progress please wait!\nWill notify once done\nWarning: It will not clear the existing configuration"
            self.notification_terminate("In Progress!", user_notify, 6000)
            self.root.config(cursor="wait")
            self.root.update()
            word = 'Script Group PID='
            if sys.platform.startswith('win'):
                file_path = r"C:\test_logs\ate2server.log"
            else:
                file_path = r"/var/test_logs/ate2server.log"
            for line in reversed(open(file_path).readlines()):
                if word in line:
                    pid_list = line.split('=')
                    pid = str(pid_list[1].strip())
                    self.log.info("PID : %s"%pid)
                    break
            if sys.platform.startswith('win'):
                kill_cmd = "Taskkill /PID " + pid + " /T /F"
            else:
                kill_cmd = "kill  -TERM -" + pid

            if stop_all == 0:
                cmd = "ate2run cancelall"
                try:
                    out = self.execute_cmd(cmd)
                    self.log.info("stop_all_queued: ", out.strip())
                except Exception as ex:
                    self.log.error(str(ex))
                try:
                    out = self.execute_cmd(kill_cmd)
                    self.log.info("kill current running: ", out.strip())

                except Exception as ex:
                    self.log.error(str(ex))

                if sys.platform.startswith('win'):
                    cmd = "Taskkill /IM " + "pythonservice.exe" + " /F"
                    out = self.execute_cmd(cmd)
                    self.log.info("Kill python service: %s"%out)
                    time.sleep(2)
                    cmd = "net start ate2server"
                    out = self.execute_cmd(cmd)
                    self.log.info("start python service: %s"%out)
                    time.sleep(5)

                else:
                    self.restart_ate2()
                    time.sleep(1)
                cmd = "ate2run list"
                out = self.execute_cmd(cmd)
                self.log.info("after removing all: %s"%out)
                if "Appears as though there are no queued items" in out:
                    tkMessageBox.showinfo("ATE Queue is empty", "Execution queue cleared")
                else:
                    tkMessageBox.showerror("Please try again!", "Execution queue not cleared")
            elif stop_all == 1:
                try:
                    out = self.execute_cmd(kill_cmd)
                    print
                    "kill current running: ", out.strip()
                    time.sleep(5)
                except Exception as ex:
                    self.log.error(str(ex))
                cmd = "ate2run list"
                out = self.execute_cmd(cmd)
                self.log.info("after removing all: %s"%out)
                tkMessageBox.showinfo("Cleared", "Current Execution cleared\nRunning next tests if queued")
            elif stop_all == 2:
                cmd = "ate2run cancel"
                try:
                    out = self.execute_cmd(cmd)
                    self.log.info("stop_all_queued: %s"%out.strip())
                except Exception as ex:
                    self.log.error(str(ex))
                cmd = "ate2run list"
                out = self.execute_cmd(cmd)
                self.log.info("after removing all: %s"%out)
                tkMessageBox.showinfo("Cleared", "Queued Execution Cleared\nRunning current test")
        self.root.config(cursor="")


    def start_ate2(self):
        """
        This function is to start ate2 process
        """

        self.notification_terminate("In Progress!",
                                    "ATE2 Restart in progress!\nWarning: It will clear all the queued tests\n", 3000)
        self.root.config(cursor="wait")
        self.root.update()
        if sys.platform.startswith('win'):
            self.restart_ate2()
            time.sleep(5)
        else:
            self.restart_ate2()
            time.sleep(1)
        self.root.config(cursor="")


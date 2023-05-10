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
Tooltip class to assign tooltips for any widgets as deemed.
There are 3 levels of ToolTips described.
1. Info
2. Success
3. Warning
TODO : Add Error amd CRITICAL if needed
'''
__author__ = ["Amitabh Suman"]
__copyright__ = "Copyright 2023-24, The Wingman Flex Project"
__version__ = 'tooltip_1.1.0'  # Major.Minor.Patch
__credits__ = ["MRPT"]
__email__ = 'dcsg-pt-bangalore-automation.pdl@broadcom.com'
__status__ = 'Development'
__maintainer__ = "Wingman Automation Team"

__enhancements__ = '''
DATE(M/D/Y)  CQID            WHO(CQUser)  DESCRIPTION
===============================================================
03/11/23     DCSG01431389    saprabhu       Wingman 3.0: Add support for ATE2 GUI module in Wingman Flex

'''

import Tkinter as tk
import logging
from PIL import Image, ImageTk
import os
logger = logging.getLogger("root")


class ToolTip:

    tooltip = []

    def notify(self, widget, title, message, mid=False, notification_duration=0,
               level=None, top=False, self_destroy=True):
        """
        This function is used to pop up a self terminating window with message as appropriate to the
        event with user defined time as one parameter for calling this function.

        TOP take precedence over MID. If top is selected as True, mid is overridden.
        CAUTION:
        1. MID is used for alignment wrt to WIDGETS.
        2. TOP is used wrt to parent window or TOPLEVEL, ROOTWINDOW
        """
        count = 1
        if level is None:
            level = "info"

        if count == 1:
            self.top = tk.Toplevel(height=70, width=500)
            pos_x = widget.winfo_rootx()
            pos_y = widget.winfo_rooty()
            widget_width = widget.winfo_width()
            widget_height = widget.winfo_height()

            # Split the message based on new line character and take the max of it.
            num_new_line = message.count('\n')
            message_split = message.split("\n")
            len_msg = len(max(message_split))

            if len_msg < 20:
                len_msg = 30
            message = message.center(len(message)+2, " ")

            if not mid:
                self.top.geometry("%dx%d+%d+%d" % (len_msg*8,
                                                   40+(num_new_line*15),
                                                   pos_x+widget_width+5,
                                                   pos_y-10))
            else:
                self.top.geometry("%dx%d+%d+%d" % (len_msg*8,
                                                   40+(num_new_line*15),
                                                   pos_x+(widget_width-(len_msg*8)-5),
                                                   pos_y+widget_height-45))

            if top:
                self.top.geometry("%dx%d+%d+%d" % (len_msg*10,
                                                   60,
                                                   pos_x+10,
                                                   pos_y+10))
                
            self.top.overrideredirect(True)
            self.top.wm_attributes('-alpha', 0.8)
            self.top.wm_attributes('-topmost', True)
            self.top.title(title)

            self.frame_left = tk.Frame(self.top, width=10)
            self.frame_left.pack(side="left", expand=0, fill="y", pady=2)

            self.frame_right = tk.Frame(self.top, background='black')
            self.frame_right.pack(side="right", expand=1, fill="both")

            if level == "success":
                self.success_logo()

            if level == "warning":
                self.warning_logo()

            if not level or level == "info":
                self.info_logo()

            self.notification_tip = tk.Label(self.frame_right, text=message, borderwidth=4, justify="center",
                                             background="black", foreground="white", font=("segoe", "9", "bold"))
            self.notification_tip.pack(side="right", expand=1, fill="both")

            ToolTip.tooltip.append(self.top)
            if notification_duration:
                self.top.after(notification_duration, self.top.destroy)
            count -= 1
            if self_destroy:
                widget.bind("<Leave>", lambda _: self.notify_destroy())

    def success_logo(self):
        """
        Logo for success message display
        :return: None
        """
        img = Image.open(os.path.join(os.getcwd(), "icons", "success.png"))
        img = img.resize((35, 35), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(img)
        label = tk.Label(image=img, master=self.frame_left)
        label.image = img  # keep a reference!
        label.pack(side='left', padx=(0, 0), pady=(0, 0), expand=False)

    def warning_logo(self):
        """
        Logo for warning message display
        :return: None
        """
        img = Image.open(os.path.join(os.getcwd(), "icons", "warning.png"))
        img = img.resize((35, 30), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(img)
        label = tk.Label(image=img, master=self.frame_left)
        label.image = img  # keep a reference!
        label.pack(side='left', padx=(0, 0), pady=(0, 0), expand=False)

    def info_logo(self):
        """
        Logo for information message display
        :return: None
        """
        img = Image.open(os.path.join(os.getcwd(), "icons", "info.png"))
        img = img.resize((32, 32), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(img)
        label = tk.Label(image=img, master=self.frame_left)
        label.image = img  # keep a reference!
        label.pack(side='left', padx=(0, 0), pady=(0, 0), expand=False)

    def notify_destroy(self):
        """
        Destroy the tooltip if duration or event is over
        :return: None
        """
        try:
            self.top.destroy()
        except Exception:
            pass

        for tips in ToolTip.tooltip:
            tips.destroy()

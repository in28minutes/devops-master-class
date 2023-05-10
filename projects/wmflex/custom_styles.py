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
__version__ = 'custom_styles_1.0.0'  # Major.Minor.Patch
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


import ttk
import Tkinter as tk

try:
    import psutil
    from PIL import ImageTk
except ImportError:
    import tkMessageBox

mygreen = "#d2ffd2"
myred = "#dd0202"
mysteelblue = 'steelblue'
mylightblue = 'LightSteelBlue4'
mylighsteeltblue2 = 'LightSteelBlue3'
mylighsteeltblue3 = 'seashell3'
mylighsteeltblue4 = 'darkgrey'
lightgray = 'lightgrey'
gainsboro = 'gainsboro'

FONT = {
    # HELVETICA
    "smooth_helvetica_small": ('Helvetica', 8, "bold"),
    "smooth_helvetica_big": ('Helvetica', 10, "bold"),

    # SEGOE
    "smooth_segoe_bold_small": ('Segoe UI',  9, "bold"),
    "smooth_segoe_bold_semi": ('Segoe UI',  10, "bold"),
    "smooth_segoe_bold_big": ('Segoe UI',  12, "bold"),
    "smooth_segoe_bold_big_13": ('Segoe UI',  13, "bold"),
    "smooth_segoe_extra_big": ('Segoe UI',  18, "bold italic"),
    "smooth_segoe_script": ('Segoe Script',  19, "bold"),

    # BOOKMAN
    "smooth_bookman": ('Bookman Old Style',  10),
    "smooth_bookman_bold": ('Bookman Old Style',  14, "bold"),
    "smooth_bookman_bold_semi": ('Bookman Old Style',  14, "bold"),

    # BERLINE
    "smooth_berlin_bold_semi": ('Berlin Sans FB',  10, "bold"),
    "smooth_berlin_bold_big": ('Berlin Sans FB',  12, "bold"),

    # BAHNSCHRIFT
    "bahnschrift_bold_big": ('Bahnschrift', 12, "bold"),

    # ROBOTO
    "roboto_semi": ('Roboto', 10, "bold"),

    # SOFIA
    "sofia_pro_semi": ('sofia-pro', 10, "bold"),

    # CENTURY GOTHIC
    "century_gothic_bold": ('Century Gothic', 10, "bold"),

    # COURIER NEW
    "courier_new": ('Courier New', 9, "bold")
}

COLOR = {
    # GREY SECTION
    "dimgray": "dimgray",
    "lightgray": 'lightgrey',
    "l-lightgray": 'gainsboro',
    "darkgrey": 'grey34',
    "tkinterDef": '#F0F0F0',
    "grey20": "grey20",

    # BLUE SECTION
    "lightblue": 'LightSteelBlue4',
    "steelblue1": 'steelblue',
    "steeltblue2": 'LightSteelBlue3',
    "steeltblue3": 'seashell3',
    "blue": "blue",
    "deepskyblue": "DeepSkyBlue4",
    "windowsBlue": '#357EC7',
    
    # WHITE
    "white": "white",
    "offwhite": "whitesmoke",
    
    # GREEN
    "green": "lime green",
    "success": "spring green",
    "success1": "lawn green",
    "seagreen1": "seagreen1",
    "darkgreen": "forestgreen",

    # RED
    "red": "red",
    "brown3": "brown3",
    "coral3": "coral3"
}

HEADING_FONT = FONT["smooth_segoe_bold_big_13"]
HEADING_COLOR = COLOR["darkgrey"]

# TYPE 1
LABEL_FONT = FONT["smooth_segoe_bold_semi"]
LABEL_COLOR = COLOR["l-lightgray"]

# TYPE 2
LABEL_FONT_2 = FONT["smooth_segoe_bold_big"]
LABEL_COLOR_2 = COLOR["windowsBlue"]

# TYPE 3
LABEL_FONT_3 = FONT["smooth_segoe_bold_semi"]
TAB_FONT = FONT["century_gothic_bold"]
BTN_FONT = FONT["smooth_segoe_bold_semi"]

MENUBUTTON_FONT = FONT["smooth_bookman_bold"]

# Other PARENT option : alt, clam, default, classic

class CustomStyles(object):

    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(CustomStyles, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    # def __init__(self):
    #     self.style = ttk.Style()
    #     # self.style.theme_use("clam")
    #     # style.theme_create("customWM", parent="clam")
    #     # style.theme_use("customWM")
    #     self.nb_style()

    @staticmethod
    def nb_style():
        style = ttk.Style()
        style.theme_create("customWM", parent="clam",
            settings={
                # NOTEBOOK STYLER
                # ====================
                # "TNotebook"     : {"configure": {"tabmargins": [13, 10, 23, 10], "tabposition": "ew"} },
                "TNotebook": {"configure": {"tabmargins": [13, 10, 23, 10],
                                            "tabposition": "n", "sticky":'ns'},
                              "map": {"background": [("selected", COLOR["windowsBlue"])]
                        }
                              },

                "TNotebook.Tab": {
                    # "configure" : {"padding": [5, 1], "background": COLOR["l-lightgray"],
                    "configure": {"padding": [5, 1],
                                  "background": COLOR["tkinterDef"],
                                  "foreground": COLOR["dimgray"],
                                  "font": TAB_FONT,
                                  "focuscolor":style.configure(".")["background"]},
                    "map": {"background": [("selected", COLOR["windowsBlue"])],
                            "foreground": [("selected", COLOR["white"])],
                            "expand": [("selected", [1, 1, 1, 0])] } },

                # BUTTON STYLER
                # ====================
                "TButton": {"font": LABEL_FONT, "foreground":"green"},
                'TLabelframe': {
                    'configure': {
                        'background': COLOR["tkinterDef"]
                    }
                },

                'TLabelframe.Label': {
                    'configure': {
                        'background': COLOR["tkinterDef"]
                    }
                },

                'TMenubutton': {
                    'configure': {
                        'background': "white"
                    }
                },

                'Cancel1.TButton': {
                    "configure": {
                           "background" : COLOR["offwhite"],
                           "foreground" : COLOR["brown3"],
                           "highlightthickness":0,
                           "font": BTN_FONT
                    },
                    "map":
                        {
                            "foreground": [('disabled', 'grey60'),
                                           ('pressed', COLOR["darkgrey"]),
                                           ('active', COLOR["offwhite"])],
                            "background": [('disabled', 'grey'),
                                           ('pressed', '!focus', 'cyan'),
                                           ('active', COLOR["brown3"])],

                        "highlightcolor": [('focus', COLOR["red"])],

                        "anchor": [
                            ('focus', tk.CENTER),
                            ('!focus', tk.CENTER)],

                        "relief": [
                            ('pressed', 'flat'),
                            ('!pressed', 'flat')]
                        }

                }
            }
        )

        style.theme_use("customWM")
        return style

    @staticmethod
    def button_style(type=None):
        if not type:
            style = ttk.Style()
            style.configure("Custom.TButton",
                                         font=BTN_FONT,
                                         foreground=COLOR["dimgray"],
                                         bg=COLOR["offwhite"],
                                         highlightthickness=0)
            style.map("Custom.TButton",
                    anchor=[
                          ('focus', tk.E),
                          ('!focus', tk.E)
                    ],
                    foreground = [
                            ('disabled', 'yellow'),
                            ('pressed', COLOR["seagreen1"]),
                            ('active', COLOR["steelblue1"])
                    ]
                    )
            return style

        if type == "wild":
            style = ttk.Style()
            style.configure('Wild.TButton',
                                    background=COLOR["offwhite"],
                                    # foreground=COLOR["dimgray"],
                                    foreground='#357EC7',
                                    highlightthickness=0,
                                    font=BTN_FONT)
            style.map('Wild.TButton',
                    foreground=[
                                ('disabled', 'yellow'),
                                ('pressed', COLOR["success1"]),
                                ('active', COLOR["white"])
                    ],
                    background=[
                                # ('disabled', 'magenta'),
                                ('disabled', 'grey'),
                                ('pressed', '!focus', 'cyan'),
                                ('active', COLOR["windowsBlue"])
                    ],
                    highlightcolor=[('focus', COLOR["lightblue"])],
                    anchor=[
                            ('focus', tk.CENTER),
                            ('!focus', tk.CENTER)
                    ],
                    relief=[
                            ('pressed', 'flat'),
                            ('!pressed', 'flat')]
            )
            return style

    @staticmethod
    def radio_button_style():
        style = ttk.Style()
        style.configure('Pass.TRadiobutton',
                        background=COLOR["tkinterDef"],
                        foreground=COLOR["darkgreen"],
                        font=BTN_FONT)

        style.configure('Fail.TRadiobutton',
                        background=COLOR["tkinterDef"],
                        foreground=COLOR["red"],
                        font=BTN_FONT)

        style.configure('Normal.TRadiobutton',
                        background=COLOR["tkinterDef"],
                        foreground=COLOR["dimgray"],
                        font=BTN_FONT)

    @staticmethod
    def submit_button_style():
        style = ttk.Style()
        style.configure('Wild.TButton',
                        # background=COLOR["offwhite"],
                        background=COLOR["windowsBlue"],
                        # foreground='#357EC7',
                        foreground=COLOR["offwhite"],
                        # background='#357EC7',
                        highlightthickness=5,
                        font=BTN_FONT)

        style.map('Wild.TButton',
                  foreground=[
                      ('disabled', 'yellow'),
                      ('pressed', COLOR["success1"]),
                      ('active', "black")],
                  background=[
                      ('disabled', 'magenta'),
                      ('pressed', '!focus', 'cyan'),
                      ('active', COLOR["windowsBlue"])],

                  highlightcolor=[('focus', COLOR["lightblue"])],

                  anchor=[
                      ('focus', tk.CENTER),
                      ('!focus', tk.CENTER)],

                  relief=[
                      ('pressed', 'flat'),
                      ('!pressed', 'flat')])
        return style

    @staticmethod
    def delete_button_style():
            style = ttk.Style()
            style.configure('Cancel.TButton',
                            background=COLOR["offwhite"],
                            foreground=COLOR["brown3"],
                            highlightthickness=0,
                            font=BTN_FONT)
            style.map('Cancel.TButton',
                      foreground=[
                          ('disabled', 'grey60'),
                          ('pressed', COLOR["darkgrey"]),
                          ('active', COLOR["offwhite"])],
                      background=[
                          ('disabled', 'grey'),
                          ('pressed', '!focus', 'cyan'),
                          ('active', COLOR["brown3"])],

                      highlightcolor=[('focus', COLOR["red"])],

                      anchor=[
                          ('focus', tk.CENTER),
                          ('!focus', tk.CENTER)],

                      relief=[
                          ('pressed', 'flat'),
                          ('!pressed', 'flat')])
            return style

    @staticmethod
    def save_insert_button_style():
            style = ttk.Style()
            style.configure('SaveInsert.TButton',
                            background=COLOR["offwhite"],
                            foreground=LABEL_COLOR_2,
                            highlightthickness=0,
                            font=BTN_FONT)
            style.map('SaveInsert.TButton',
                      foreground=[
                          ('disabled', 'grey60'),
                          ('pressed', COLOR["darkgrey"]),
                          ('active', COLOR["success1"])],
                      background=[
                          ('disabled', 'grey'),
                          ('pressed', '!focus', 'cyan'),
                          ('active', COLOR["lightblue"])],

                      highlightcolor=[('focus', COLOR["red"])],

                      anchor=[
                          ('focus', tk.CENTER),
                          ('!focus', tk.CENTER)],

                      relief=[
                          ('pressed', 'flat'),
                          ('!pressed', 'flat')])
            return style

    @staticmethod
    def menu_button_style():
        style = ttk.Style()
        style.configure('Menu.TButton',
                        background=COLOR["tkinterDef"],
                        foreground=COLOR["dimgray"],
                        highlightthickness=0,
                        font=BTN_FONT)
        style.map('Menu.TButton',
                  foreground=[
                      ('disabled', 'yellow'),
                      ('pressed', COLOR["l-lightgray"]),
                      ('active', COLOR["coral3"])],
                  background=[
                      ('disabled', 'magenta'),
                      ('pressed', '!focus', 'cyan'),
                      ('active', COLOR["l-lightgray"])],

                  highlightcolor=[('focus', COLOR["red"])],

                  anchor=[
                      ('focus', tk.CENTER),
                      ('!focus', tk.CENTER)],

                  relief=[
                      ('pressed', 'flat'),
                      ('!pressed', 'flat')])
        return style

    @staticmethod
    def combobox_style():
        style = ttk.Style()
        style.configure(
                    'Custom.TCombobox',
                    font=MENUBUTTON_FONT,
                    foreground="tomato")
        return style

    @staticmethod
    def submit_button(parent, text=None, **kwargs):
        style = CustomStyles.button_style("wild")
        if not text:
            text = "Submit"
        submitButton = ttk.Button(parent, text=text, width=12)
        submitButton.config(style="Wild.TButton")
        return submitButton

    @staticmethod
    def label_style():
        style = ttk.Style()
        style.configure(
            'Custom.TLabel',
            font= LABEL_FONT,
            foreground= HEADING_COLOR,
            background= COLOR["l-lightgray"]
        )
        return style

    @staticmethod
    def menuButton_style():
        style = ttk.Style()
        style.configure(
                    'Custom.TMenubutton',
                    font=MENUBUTTON_FONT,
                    foreground="tomato")
        return style

    @staticmethod
    def combobox_style():
        style = ttk.Style()
        style.configure(
            'Custom.TCombobox',
            font=MENUBUTTON_FONT,
            padding=3,
            background="white",
            fieldbackground="white",
            foreground="black"
        )
        return style

    @staticmethod
    def labelframe_style():
        style = ttk.Style()
        style.configure(
            'Custom.TLabelFrame',
            background=COLOR["tkinterDef"]
        )

'''
DATE(M/D/Y)  CQID            WHO(CQUser)  DESCRIPTION
===============================================================
03/24/23     DCSG01431416    nmartis       Wingman 3.0: Add GUI For Config File in Wingman Flex
03/24/23     DCSG01458079    nmartis       Update Raid Keywords in ConfigFileGUI
03/24/23     DCSG01459382    nmartis      Add Support Modify the Default RAID Parameters on RAID Selection
05/04/23    DCSG01451129     nmartis    Add Support for teardown options and test JSON queuer in ConfigGUI
'''

import copy
import json
import os
import re
import sys
import threading
import tkFileDialog
import tkMessageBox
import ttk
from Tkconstants import FLAT, GROOVE, RAISED, RIGHT
from Tkinter import Tk as tk, Label, E, W, N, S, Frame, PhotoImage, Entry, Button, StringVar, Toplevel, LabelFrame, END, \
    Checkbutton, Text, Menubutton, Menu
from subprocess import PIPE, Popen
import ctypes
from utils import CONFIGFILEPATH
from wm_modules.configFileIcon import *

try:
    import queue
except ImportError:
    import Queue as queue
try:
    from queue import Queue, Empty
except ImportError:
    from Queue import Queue, Empty

REFRESHBUTTON = """R0lGODlhHgAeAPABAAAAAAAAACH5BAEUAAAAIf8LSW1hZ2VNYWdpY2sOZ2FtbWE9MC40NTQ1NDUALAAAAAAeAB4AAAJKhI+py+0PIwq02msdlTLw/kVe+IykmaBctahiloaY6pbGuB21yOzQ7rO1SLcJrvihYWSKy6mVYw6JQSpRc21UZcGZF6b5LrPkcgEAOw=="""
ADD = """R0lGODlhGQAZAPQAAAAAAByU8x6V8x+V8yCV8yGW8ySY8zSf9Gy49ZTL95bM98vl+Njq+djr+fr6+v37+v/9+v/++gAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACH5BAEUAAAAIf4gQ3JlYXRlZCB3aXRoIGV6Z2lmLmNvbSBHSUYgbWFrZXIALAAAAAAZABkAAAVnIFCMZGmeo4iubOu+cCy7xmHMpoAwiICTAkVE4fsVgsPiD0mcCZ7PRCQBfdIQimxi8VgksgrEjXVgRM6Rh+OBjjAOLQNWy/WCxa6qQEqtOoVNRkxKOINGRzs9hwU1Y4uPkJFGKosAIQA7"""
REMOVE = """R0lGODlhGQAZAPYAAAAAAPNDNvRDNvNENfRENvRHO/RKPfVQQ/VTR/VVSfRXTPVdUfVjWPVkWfVnXPVoXfVqYPVtY/ZvZfZwZvZzafZ0a/Z2bPZ5cPZ/dvaCefaFffaKgvaLhPaMhPePiPeTi/eWj/eXkPeak/eclveemPehm/ejnfeknfenofeooverpfespveuqPivqvixrPi3svi4s/i6tvi8t/i9ufjIxfjLyPjMyfnV0/nX1PnY1fnb2fnc2vne3Prj4vrm5Pns6/nt7Prz8vr39/r6+gAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACH/C05FVFNDQVBFMi4wAwEAAAAh/iBDcmVhdGVkIHdpdGggZXpnaWYuY29tIEdJRiBtYWtlcgAh+QQBFAAAACwAAAAAGQAZAAAHY4AAAoOEhYaHg4KIi4yNjo+QkZKTlJWHBigQhhAoBpEoQz8RhBE/QyiREKaiAqWhmpGuPxyro5OuQ6G2lBy5QxyWuLqUsrTDqbWtq7CPoKyDrqiQmMyDnJ6W2drb3N3eidwAgQA7"""
BG_BASE = '#76a4ee'  # genericblue
BG_BASE = '#3B7097'  # dark blue
BG_LIGHT = '#0075F2'  # Light BLue
BG_LIGHT = '#495057'
BG_BASE = "#cc0930"  # Broadcom Red
# BG_LABEL = "#fafcff" #offwhite
BG_LABEL = '#e2e3e4'  # Broadcom  Grey
BG_SWITCH = '#FFFFFF'  # Broadcom White
BG_SWITCH = '#f8f9fa'
BG_ENTRY = '#FFFFFF'  # Broadcom White
BG_BUTTON = '#A9D09E'
BG_TEXT = '#F6E2BC'  # Yellow

####
BG_LIGHT = "#FFFFFF"
BRCMRED = "#CC092F"
BRCMBLUE = "#005C8A"
BUILD = 'v1.0'
VERSION_INFO = ("wingman flex config file editor ").title() + BUILD
RELIEF = FLAT

global onFlexImg
global offFlexImg
global onImg
global offImg
global brcmLogo
global brcmLogo2
global addImg
global delImg
global saveButton
global closeButton
global runImg
global settingsImg
onImg = None
offImg = None

_configFileData_ = None
_flex_ = False


class ToolTip(object):
    def __init__(self, widget):
        """

        :param widget:
        :type widget:
        """
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        """

        :param text:
        :type text:
        :return:
        :rtype:
    """
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 57
        y = y + cy + self.widget.winfo_rooty() + 27
        self.tipwindow = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = Label(tw, text=self.text, justify=LEFT, background='light goldenrod yellow', relief=SOLID,
                      borderwidth=1, font=("times", "8"))
        label.pack(ipadx=1)

    def hidetip(self):
        """

        """
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()


def center(win):
    """

    :param win:
    :type win:
    """
    win.update_idletasks()
    width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))


def set_ToolTip(widget, text):
    """

    :param widget:
    :type widget:
    :param text:
    :type text:
    """
    toolTip = ToolTip(widget)

    def enter(event):
        toolTip.showtip(text)

    def leave(event):
        toolTip.hidetip()

    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)


def getFontSize(height, mul=10, font='smooth_segoe_bold_small', bold=False):
    _titleFontSize_ = 40 if mul == 1 else 50 if mul == 2 else 60 if mul == 3 else 70 if mul == 4 else 80 if mul == 5 else 90 if mul == 6 else 100 if mul == 7 else 110 if mul == 8 else 120 if mul == 9 else 130 if mul == 10 else 140
    return (font, int((int(height) * 15) / _titleFontSize_), 'bold') if bold else (
        font, int((int(height) * 15) / _titleFontSize_))


def set_textbox(wdgt, value):
    """
    Clears the existing text in the wdgt and updates with value
    :param wdgt: widget where the value will be displayed
    :type wdgt: tk.Entry
    :param value: Text that will show on the entry (ip,port)
    :type value: String
    :return: None
    :rtype: None
    """
    wdgt.delete(0, 'end')
    wdgt.insert(END, value)


def readConfigFile():
    """
    Reads the config file and returns the content. If no config file is present then a popup will shown to the user
    :return: Contents of the config_file.json
    :rtype: dict or list of dict
    """
    if os.path.isfile(CONFIGFILEPATH):
        with open(CONFIGFILEPATH) as data_file:
            configData = json.load(data_file)
            if 'legacy' in configData:
                return configData
            else:
                return {'legacy': configData, 'flexmode': {'mode': False}}
    else:
        import tkMessageBox
        tkMessageBox.showinfo("New Config File will Be Created", "Previous Config File Not Found")
        return {'legacy': {}, 'flexmode': {'mode': False}}


def buttonToggle(buttonData):
    """Changes the Button Image and Sets the status Variable"""
    if buttonData['on']:
        buttonData['on'] = False
        buttonData['button'].config(image=onImg)
    else:
        buttonData['on'] = True
        buttonData['button'].config(image=offImg)


def setGridConfigure(wdgt, row=-1, column=-1, rwght=1, clwght=1):
    """ Sets Weight for the Row and Column to Any widgets"""
    if row != -1:
        wdgt.grid_rowconfigure(row, weight=rwght)
    if column != -1:
        wdgt.grid_columnconfigure(column, weight=clwght)


def createWindow(parent, width, height, rw, cl, bg=BG_SWITCH, pdx=5, pdy=5, relief=FLAT, rwWght=1, colWght=1,
                 columnspan=1, rowspan=1):
    frm = Frame(parent, bd=1, relief=relief, width=int(parent.winfo_width() * width),
                height=int(parent.winfo_height() * height), bg=bg)
    frm.grid(row=rw, column=cl, columnspan=columnspan, rowspan=rowspan, padx=pdx, pady=pdy, sticky=N + W + E + S)
    frm.grid_propagate(0)
    frm.update()
    setGridConfigure(parent, row=rw, column=cl, rwght=rwWght, clwght=colWght)
    return frm


def loadConfigFile():
    """Reads ConfigFile"""
    _configFileData_ = readConfigFile()


def deleteWidgets(wdgt):
    """Deletes the Widgets childrens """
    for child in wdgt.winfo_children():
        try:
            child.destroy()
        except:
            pass


def makeLabel(parent, text, font, row, column, rowspan=1, columnspan=1, bg=BG_SWITCH, width=23, foreground=BRCMBLUE,
              padx=5, pady=5):
    """
    Creates Label and Sets the grid Configuration to Parent with Color. # to be enchanced with ttk.style Later
    """
    Label(parent, text=text.center(20), bg=bg, font=font, borderwidth=1, foreground=foreground, relief=FLAT,
          width=width).grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan, padx=padx, pady=pady,
                            sticky=N + E + W + S)
    setGridConfigure(parent, row, column)


def makeEntry(parent, var, font, row, column, width=2, borderwidth=2, rowspan=1, columnspan=1, validate="",
              validatecommand="", background='#FFFFFF'):
    """Makes Entry and sets the Grid Configuration to the Parent. # to be enchanced with ttk.style Later"""
    dummyEntry = Entry(parent, textvariable=var, font=font, width=width, borderwidth=borderwidth, background=background)
    dummyEntry.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan, padx=5, pady=5,
                    sticky=N + E + W + S)
    if validate:
        dummyEntry.configure(validate=validate, validatecommand=validatecommand)
    setGridConfigure(parent, row, column)
    return dummyEntry


class legacyInputs(LabelFrame):
    """Frame holds all Widgets that are needed to get the switch related info  """
    _pady = 5
    _RELIEF = GROOVE
    _BG = BG_SWITCH
    _font = ('Consolas', 12)

    def __init__(self, parent, *args, **kwargs):
        """
        Initialize the switch GUI class
        :param parent: Frame handler of the frame where the switch gui needs to be placed
        :type parent: tk.Frame
        :param args: args required for the frame
        :type args: args
        :param kwargs:Keyword args required for the frame
        :type kwargs:Keyword args required for the frame
        """
        _font_ = getFontSize((parent.winfo_height() * .98) * .10, mul=7, bold=False)
        LabelFrame.__init__(self, parent, text="SETUP INFO", font=_font_, bg=BG_SWITCH, relief=legacyInputs._RELIEF,
                            bd=1, labelanchor=N, foreground=BRCMRED, *args, **kwargs)
        self.grid(row=0, column=0, padx=5, pady=5, sticky=N + E + W + S)
        self.grid_propagate(0)
        self.update()
        setGridConfigure(parent, 0, 0)
        self.ctrlIndex = StringVar()
        self.iotMedusa = StringVar()
        self.serverIp = StringVar()
        self.serverPort = StringVar()
        self.quarchIp = StringVar()
        self.autoServerIp = StringVar()
        self.debuggerIp = StringVar()
        self.debuggerPort = StringVar()
        self.encIp = StringVar()
        self.encList = StringVar()
        self.encApcMap = {}
        self.encStringVar = []
        self.width = self.winfo_width()
        self.height = self.winfo_height()
        self.bFrame = self
        self.renderServerInfo()
        self.load(_configFileData_['legacy'])

    def validateIP(self, ip):
        test = re.compile(
            '(^\d{0,3}$|^\d{1,3}\.\d{0,3}$|^\d{1,3}\.\d{1,3}\.\d{0,3}$|^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{0,3}$)')
        if test.match(ip):
            return True
        else:
            return False

    @property
    def _legacy(self):
        """Return Widgets Value to Write to File"""
        apcEnclPort = {}
        for index, encPort in enumerate(self.encStringVar):
            apcEnclPort.update({"ENC " + str(index + 1): encPort.get()})
        return {'apc_encl_port': apcEnclPort, 'apc_ip_server': self.serverIp.get(), 'quarch_ip': self.quarchIp.get(),
                'debug_port': self.debuggerPort.get(), 'apc_server_port': self.serverPort.get(),
                'encl_list': [enc for enc in self.encList.get().split(',') if enc],
                'apc_ip_enclosure': self.encIp.get(), 'auto_server_ip': self.autoServerIp.get(),
                'debug_ip': self.debuggerIp.get(),
                'iot_medusa_override': False if self.iotMedusa.get() == 'False' else True,
                'ctrlindex': int(self.ctrlIndex.get())} if self.ctrlIndex.get() != '' else ''

    def renderServerInfo(self):
        """Widgets to Gather the Server Info will be rendered"""
        vcmdIp = self.register(self.validateIP)
        _hght = int(self.winfo_height() * .98)
        _wdth = int(self.winfo_width() * .98)
        _font_ = getFontSize(height=(_hght / 4) * .45, mul=10)
        _BG = BG_SWITCH
        encPortFrame = createWindow(self, width=.97, height=.40, bg=_BG, rw=9, cl=0, columnspan=2, relief=GROOVE)
        makeLabel(self, text="StorCLI Index".center(20), font=_font_, row=0, column=0)
        makeLabel(self, text="IOT Medusa OverRide".center(20), font=_font_, row=1, column=0)
        makeLabel(self, text="Server APC IP".center(20), font=_font_, row=2, column=0)
        makeLabel(self, text="Server APC Port".center(20), font=_font_, row=3, column=0)
        makeLabel(self, text="Debugger IP".center(20), font=_font_, row=4, column=0)
        makeLabel(self, text="Debugger Port".center(20), font=_font_, row=5, column=0)
        makeLabel(self, text="Quarch IP".center(20), font=_font_, row=6, column=0)
        makeLabel(self, text="Auto Server IP".center(20), font=_font_, row=7, column=0)
        makeLabel(self, text="Enc APC IP".center(20), font=_font_, row=8, column=0)
        makeLabel(encPortFrame, text="Enclosure List".center(20), font=_font_, row=0, column=0)
        makeEntry(self, var=self.ctrlIndex, font=_font_, row=0, column=1, width=23)
        iotMedusa = ttk.Combobox(self, textvariable=self.iotMedusa, font=_font_, state='readonly', width=10,
                                 values=["False", "True"])
        iotMedusa.grid(row=1, column=1, padx=5, pady=5, sticky=N + E + W + S)
        iotMedusa.unbind_class("TCombobox", "<MouseWheel>")
        iotMedusa.current(0)
        setGridConfigure(self, 1, 1)
        makeEntry(self, var=self.serverIp, font=_font_, validatecommand=(vcmdIp, '%P'), row=2, column=1, width=23,
                  validate='key')
        makeEntry(self, var=self.serverPort, font=_font_, row=3, column=1, width=23)
        makeEntry(self, var=self.debuggerIp, font=_font_, validatecommand=(vcmdIp, '%P'), row=4, column=1, width=23,
                  validate='key')
        makeEntry(self, var=self.debuggerPort, font=_font_, row=5, column=1, width=23)
        makeEntry(self, var=self.quarchIp, font=_font_, validatecommand=(vcmdIp, '%P'), row=6, column=1, width=23,
                  validate='key')
        makeEntry(self, var=self.autoServerIp, font=_font_, validatecommand=(vcmdIp, '%P'), row=7, column=1, width=23,
                  validate='key')
        makeEntry(self, var=self.encIp, font=_font_, validatecommand=(vcmdIp, '%P'), row=8, column=1, width=23,
                  validate='key')
        enclist = makeEntry(encPortFrame, var=self.encList, font=_font_, row=1, column=0, width=23)
        enclist.bind('<Return>', self.loadEnclistEvent)
        refreshbutton = PhotoImage(data=REFRESHBUTTON)
        self.encListFrame = createWindow(encPortFrame, width=.98, height=.50, bg=_BG, rw=2, cl=0, columnspan=1)
        self.refresh = Button(encPortFrame, text='Click Me !', image=refreshbutton, bg=BG_SWITCH,
                              command=self.loadEncList, relief=RAISED)
        self.refresh.image = refreshbutton
        self.refresh.grid(row=3, column=0, padx=5, pady=5)
        setGridConfigure(encPortFrame, 3, 0)

    def load(self, _config):
        """Load  Values from config file to the widgets for display
        :param _config: config values read from config file
        :type _config: dict
        """
        if _config:
            self.serverIp.set(_config['apc_ip_server'])
            self.serverPort.set(_config['apc_server_port'])
            self.ctrlIndex.set(_config['ctrlindex'])
            self.quarchIp.set(_config['quarch_ip'])
            self.autoServerIp.set(_config['auto_server_ip'])
            self.encIp.set(_config['apc_ip_enclosure'])
            self.debuggerIp.set(_config['debug_ip'])
            self.debuggerPort.set(_config['debug_port'])
            self.encList.set(','.join(_config['encl_list']))
            for x, eid in enumerate(_config['encl_list']):
                try:
                    self.encApcMap.update({eid: _config['apc_encl_port']['ENC ' + str(x + 1)]})
                except:
                    pass
            self.loadEncList()

    def loadEnclistEvent(self, event):
        """Load the Load APC input when user Press Enter in the ENCLIST Entry"""
        self.loadEncList()

    def loadEncList(self):
        """Clears the Enclist APC input Frame and Renders the With New Values"""
        self.clearFrame(self.encListFrame)
        encList = [enc for enc in self.encList.get().split(',') if enc]
        if encList:
            self.apcEncBox(encList)

    def apcEncBox(self, encList):
        """Renders the APC Port Input Boxs to get the Port No with ENCID Tagged Below the Entry"""
        entryList = []
        _font_ = getFontSize(height=(self.encListFrame.winfo_height()) * .50, mul=10, bold=False)
        makeLabel(self.encListFrame, text="APC Ports".center(20), font=_font_, row=0, column=0, columnspan=len(encList))
        for x, enc in enumerate(encList):
            self.encStringVar.append(StringVar())
            entryList.append(
                makeEntry(self.encListFrame, var=self.encStringVar[x], font=_font_, row=1, column=x, width=3))
            makeLabel(self.encListFrame, text=enc.center(5), font=_font_, row=2, column=x)
            if enc in self.encApcMap.keys():
                self.encStringVar[x].set(self.encApcMap[enc])

    def clearFrame(self, widget):
        for child in widget.winfo_children():
            try:
                child.destroy()

            except:
                pass
        self.encStringVar = []


class flexRaid():
    _RELIEF = FLAT
    _BG = BG_SWITCH

    # _BG = "peach puff"

    def __init__(self, parent):
        """
        Initialize the switch GUI class
        :param parent: Frame handler of the frame where the switch gui needs to be placed
        :type parent: tk.Frame
        :param args: args required for the frame
        :type args: args
        :param kwargs:Keyword args required for the frame
        :type kwargs:Keyword args required for the frame
        """
        self.repeatAll = StringVar()
        self.parent = parent
        self.raidConfigVar = [StringVar() for _ in range(0, 13)]
        raidFrame = createWindow(parent, width=.99, height=.88, bg=flexRaid._BG, rw=0, cl=0)
        self.raidMgmtFrame = createWindow(parent, width=.97, height=.08, bg=flexRaid._BG, rw=1, cl=0)
        self.renderRaidFrame(raidFrame)

    def _load(self, values):
        """Values -> from config under raidlevel.values()"""
        self.repeatAll.set(values['exhaust'])
        for raidInfo in values['config']:
            self.raidTree.insert('', END, values=tuple(
                [(str(raidInfo['raid']).center(7)).upper(), str(raidInfo['pdcount']).center(7), ((
                            str(raidInfo['size']) + (
                        '' if str(raidInfo['size']) == '' or 'GB' in str(raidInfo['size']).upper() else 'GB')).center(
                    7)).upper(), str(raidInfo['stripe']).center(7), (str(raidInfo['writepolicy']).center(7)).upper(),
                 (str(raidInfo['readpolicy']).center(7)).upper(), str(raidInfo['vdcount']).center(7),
                 str(raidInfo['spans']).center(7), str(raidInfo['hotspare']).center(7),
                 str(raidInfo['dtabcount']).center(7), (str(raidInfo['init']).center(7)).upper(),
                 str(raidInfo['repeat']).center(7)]), tag='monospace')

    @property
    def _get(self):
        """Returns User Raid Selection"""
        config = []
        for id in self.raidTree.get_children():
            _raid = {}
            _raid.update({'raid': self.raidTree.item(id)['values'][0].strip().lower()})
            _raid.update({'pdcount': int(self.raidTree.item(id)['values'][1])})
            _raid.update({'size': self.raidTree.item(id)['values'][2].strip().lower()})
            _raid.update({'stripe': self.raidTree.item(id)['values'][3]})
            _raid.update({'writepolicy': self.raidTree.item(id)['values'][4].strip().lower()})
            _raid.update({'readpolicy': self.raidTree.item(id)['values'][5].strip().lower()})
            _raid.update({'vdcount': self.raidTree.item(id)['values'][6]})
            _raid.update({'spans': int(self.raidTree.item(id)['values'][7])})
            _raid.update({'hotspare': int(self.raidTree.item(id)['values'][8])})
            _raid.update({'dtabcount': int(self.raidTree.item(id)['values'][9])})
            _raid.update({'init': self.raidTree.item(id)['values'][10].strip().lower()})
            _raid.update({'repeat': int(self.raidTree.item(id)['values'][11])})

            config.append(_raid)
        try:
            repeat = True if int(self.repeatAll.get()) == 1 else False
        except:
            repeat = False
        return {'exhaust': repeat, 'config': config}

    def renderRaidFrame(self, parent):
        # from tkinter.font import nametofont
        _font_ = getFontSize(int(parent.winfo_height() * .01), mul=10, bold=False)
        # nametofont('TkHeadingFont').configure(family=_font_[0], size=_font_[1])
        columns = ['raid', 'pdcount', 'size', 'stripe', 'writepolicy', 'readpolicy', 'vdcount', 'span', 'hotspare',
                   'dtab', 'init', 'repeat']
        s = ttk.Style()
        s.configure('nmartis.Treeview', rowheight=50)
        self.raidTree = ttk.Treeview(parent, columns=columns, show='headings', style='nmartis.Treeview')
        self.raidTree.heading('raid', text='Raid', anchor='c')
        self.raidTree.heading('pdcount', text='PD\'s', anchor='c')
        self.raidTree.heading('size', text='VD Size', anchor='c')
        self.raidTree.heading('stripe', text='Stripe', anchor='c')
        self.raidTree.heading('writepolicy', text='WP', anchor='c')
        self.raidTree.heading('readpolicy', text='RP', anchor='c')
        self.raidTree.heading('vdcount', text='VD\'s', anchor='c')
        self.raidTree.heading('span', text='Span', anchor='c')
        self.raidTree.heading('hotspare', text='Spare', anchor='c')
        self.raidTree.heading('dtab', text='Dtab', anchor='c')
        self.raidTree.heading('init', text='Init', anchor='c')
        self.raidTree.heading('repeat', text='Repeat', anchor='c')
        self.raidTree.tag_configure('monospace', font=_font_)
        self.raidTree.bind("<Motion>", 'break')
        self.raidTree.grid(row=0, column=0, padx=5, pady=5, sticky=N + E + W + S)
        self.raidTree.grid_propagate(0)
        self.raidTree.update()
        setGridConfigure(parent, 0, 0)
        Checkbutton(self.raidMgmtFrame, text='Repeat Until Exhaust',
                    font=getFontSize(height=self.raidMgmtFrame.winfo_height(), mul=3, bold=True),
                    variable=self.repeatAll, bg=flexRaid._BG, foreground=BRCMRED, justify=RIGHT, state='disabled').grid(
            row=0, column=0, padx=5, pady=5)
        setGridConfigure(self.raidMgmtFrame, 0, 0)
        self.raidAddButton = Button(self.raidMgmtFrame, image=addImg, relief=FLAT, font=_font_, bg=flexRaid._BG,
                                    command=self.raidPopup)
        self.raidAddButton.img = addImg
        self.raidAddButton.grid(row=0, column=1, padx=5, pady=5, sticky=N + E + W + S)
        setGridConfigure(self.raidMgmtFrame, 0, 1)
        remButton = Button(self.raidMgmtFrame, image=delImg, relief=FLAT, font=_font_, bg=flexRaid._BG,
                           command=self.item_selected)
        remButton.img = delImg
        remButton.grid(row=0, column=2, padx=5, pady=5, sticky=N + E + W + S)
        setGridConfigure(self.raidMgmtFrame, 0, 2)

    def raidPopup(self):
        """Popup Add new Raid Popup"""
        self.addRaidPopup = Toplevel(root, height=int(self.parent.winfo_height() / 2),
                                     width=int(self.parent.winfo_width() * .98), bd=1, bg=flexRaid._BG,
                                     highlightbackground=BRCMRED, highlightthickness=2, relief=flexRaid._RELIEF)
        self.addRaidPopup.grab_set()
        center(self.addRaidPopup)
        self.addRaidPopup.overrideredirect(True)
        self.addRaidPopup.grid_propagate(0)
        self.addRaidPopup.update_idletasks()
        _font_ = getFontSize(int(self.addRaidPopup.winfo_height() * .50), mul=6, bold=True)
        makeLabel(self.addRaidPopup, text="Add Configuration", font=_font_, row=0, column=0, foreground=BRCMRED)
        widgetFrame = createWindow(self.addRaidPopup, width=.80, height=.50, bg=flexRaid._BG, rw=1, cl=0,
                                   relief=flexRaid._RELIEF)
        buttonFrame = createWindow(self.addRaidPopup, width=.80, height=.20, bg=flexRaid._BG, rw=2, cl=0)
        svBtn = addImg
        self.save = Button(buttonFrame, image=svBtn, relief=FLAT, font=_font_, bg=flexRaid._BG, command=self.addToTree)
        self.save.image = svBtn
        self.save.grid(row=0, column=0, padx=5, pady=5, sticky=N + E + W + S)
        setGridConfigure(buttonFrame, 0, 0)
        close = Button(buttonFrame, image=delImg, bg=flexRaid._BG, relief=FLAT, font=_font_,
                       command=self.addRaidPopup.destroy)
        close.image = delImg
        close.grid(row=0, column=1, padx=5, pady=5, sticky=N + E + W + S)
        setGridConfigure(buttonFrame, 0, 1)
        self.renderRaid(widgetFrame)

    def addToTree(self):
        """ Add Button functiont to add new Raid Level"""
        raidInfo = []
        for x, wdgt in enumerate(self.raidConfigVar):
            if x == 2:
                size = 'GB' if wdgt.get() != '' else ''
                raidInfo.append((str(wdgt.get()) + size).center(7))
            else:
                raidInfo.append(str(wdgt.get()).center(7))
        self.raidTree.insert('', END, values=tuple(raidInfo), tag=['monospace'])
        self.addRaidPopup.destroy()
        self.raidConfigVar = []
        self.raidAddButton.configure(state='active' if len(self.raidTree.get_children()) < 10 else 'disable')

    def item_selected(self):
        """Treview Selected Item Delete function on delete key press"""
        for selected_item in self.raidTree.selection():
            item = self.raidTree.item(selected_item)
            self.raidTree.delete(selected_item)
        self.raidAddButton.configure(state='active' if len(self.raidTree.get_children()) < 10 else 'disable')

    def renderRaid(self, frm):
        """ Raid Option Frame"""
        relief = FLAT
        _bd = 0
        _hght = int(frm.winfo_height() * .96)
        _wdth = int(frm.winfo_width() / 13)
        _font_ = getFontSize(height=int(_hght * .70), mul=10, bold=False)
        self.raidConfigVar = [StringVar() for _ in range(0, 13)]
        self.raidComBoxWidgets = {}
        inputList = ['RAID', 'PD\'s', 'Size', 'Stripe', 'WP', 'RP', 'VD\'s', 'Span', 'Spare', 'DTAB', 'Init', 'Reps']
        # [self.raidComBoxWidgets.update({inpField: None}) for inpField in
        # ['RAID', 'PD\'s', 'Size', 'Stripe', 'WP', 'RP', 'VD\'s', 'Span', 'Spare', 'DTAB', 'Init', 'Reps']]
        for _, inpField in enumerate(inputList):
            dummyFrame = createWindow(frm, width=.90, height=.99, bg=BG_SWITCH, rw=0, cl=_)
            makeLabel(dummyFrame, text=inpField, font=_font_, row=0, column=0)
            if _ == 0:
                dummyCombList = ttk.Combobox(dummyFrame, textvariable=self.raidConfigVar[_], font=_font_,
                                             state='readonly', width=4)
                dummyCombList['values'] = ['R0', 'R1', 'R5', 'R6', 'R10', 'R50', 'R60', 'JBOD']
                dummyCombList.grid(row=1, column=0, padx=2, pady=2, sticky=N + E + W + S)
                dummyCombList.unbind_class("TCombobox", "<MouseWheel>")
                dummyCombList.current(0)
                dummyCombList.bind('<<ComboboxSelected>>', lambda event: self.raidSelect())
            elif _ == 1:
                dummyCombList = ttk.Combobox(dummyFrame, textvariable=self.raidConfigVar[_], font=_font_,
                                             state='readonly', width=4)
                dummyCombList['values'] = range(1, 32)
                dummyCombList.grid(row=1, column=0, padx=2, pady=2, sticky=N + E + W + S)
                dummyCombList.unbind_class("TCombobox", "<MouseWheel>")
                dummyCombList.current(0)
            elif _ == 2:
                dummyCombList = Entry(dummyFrame, textvariable=self.raidConfigVar[_], font=_font_, width=4)
                dummyCombList.grid(row=1, column=0, padx=2, pady=2, sticky=N + E + W + S)
            elif _ == 3:
                dummyCombList = ttk.Combobox(dummyFrame, textvariable=self.raidConfigVar[_], font=_font_,
                                             state='readonly', width=4)
                dummyCombList['values'] = ['64', '256', 'RANDOM']
                dummyCombList.grid(row=1, column=0, padx=2, pady=2, sticky=N + E + W + S)
                dummyCombList.unbind_class("TCombobox", "<MouseWheel>")
                dummyCombList.current(0)
            elif _ == 4:
                dummyCombList = ttk.Combobox(dummyFrame, textvariable=self.raidConfigVar[_], font=_font_,
                                             state='readonly', width=3)
                dummyCombList['values'] = ['WT', 'WB', 'AWB', 'RANDOM']
                dummyCombList.grid(row=1, column=0, padx=2, pady=2, sticky=N + E + W + S)
                dummyCombList.unbind_class("TCombobox", "<MouseWheel>")
                dummyCombList.current(0)
            elif _ == 5:
                dummyCombList = ttk.Combobox(dummyFrame, textvariable=self.raidConfigVar[_], font=_font_,
                                             state='readonly', width=4)
                dummyCombList['values'] = ['RA', 'NORA', 'RANDOM']
                dummyCombList.grid(row=1, column=0, padx=2, pady=2, sticky=N + E + W + S)
                dummyCombList.unbind_class("TCombobox", "<MouseWheel>")
                dummyCombList.current(0)
            elif _ == 6:
                dummyCombList = ttk.Combobox(dummyFrame, textvariable=self.raidConfigVar[_], font=_font_,
                                             state='readonly', width=2)
                dummyCombList['values'] = range(1, 17)
                dummyCombList.grid(row=1, column=0, padx=2, pady=2, sticky=N + E + W + S)
                dummyCombList.unbind_class("TCombobox", "<MouseWheel>")
                dummyCombList.current(0)
            elif _ == 7:

                dummyCombList = ttk.Combobox(dummyFrame, textvariable=self.raidConfigVar[_], font=_font_,
                                             state='readonly', width=2)
                dummyCombList['values'] = range(1, 9)
                dummyCombList.grid(row=1, column=0, padx=2, pady=2, sticky=N + E + W + S)
                dummyCombList.unbind_class("TCombobox", "<MouseWheel>")
                dummyCombList.current(0)
            elif _ == 8:

                dummyCombList = ttk.Combobox(dummyFrame, textvariable=self.raidConfigVar[_], font=_font_,
                                             state='readonly', width=2)
                dummyCombList['values'] = range(0, 6)
                dummyCombList.grid(row=1, column=0, padx=2, pady=2, sticky=N + E + W + S)
                dummyCombList.unbind_class("TCombobox", "<MouseWheel>")
                dummyCombList.current(0)
            elif _ == 9:
                dummyCombList = ttk.Combobox(dummyFrame, textvariable=self.raidConfigVar[_], font=_font_,
                                             state='readonly', width=2)
                dummyCombList['values'] = range(0, 33)
                dummyCombList.grid(row=1, column=0, padx=2, pady=2, sticky=N + E + W + S)
                dummyCombList.unbind_class("TCombobox", "<MouseWheel>")
                dummyCombList.current(0)
            elif _ == 10:
                dummyCombList = ttk.Combobox(dummyFrame, textvariable=self.raidConfigVar[_], font=_font_,
                                             state='readonly', width=4)
                dummyCombList['values'] = ['NA', 'FULL', 'FAST', 'BGI']
                dummyCombList.grid(row=1, column=0, padx=2, pady=2, sticky=N + E + W + S)
                dummyCombList.unbind_class("TCombobox", "<MouseWheel>")
                dummyCombList.current(0)
            elif _ == 11:
                dummyCombList = ttk.Combobox(dummyFrame, textvariable=self.raidConfigVar[_], font=_font_,
                                             state='readonly', width=2)
                dummyCombList['values'] = range(1, 10)
                dummyCombList.grid(row=1, column=0, padx=2, pady=2, sticky=N + E + W + S)
                dummyCombList.unbind_class("TCombobox", "<MouseWheel>")
                dummyCombList.current(0)
            self.raidComBoxWidgets.update({inpField: dummyCombList})
            setGridConfigure(dummyFrame, 1, 0)

    def raidSelect(self):
        '''Change VD Attributes base on Raid Selection'''
        raidLevel = self.raidConfigVar[0].get()
        for widgets in self.raidComBoxWidgets.values():
            widgets['state'] = 'normal'
        self.raidComBoxWidgets['Spare']['values'] = range(0, 6)
        self.raidComBoxWidgets['Stripe']['values'] = ['64', '256', 'RANDOM']
        self.raidComBoxWidgets['WP']['values'] = ['WT', 'WB', 'AWB', 'RANDOM']
        self.raidComBoxWidgets['RP']['values'] = ['RA', 'NORA', 'RANDOM']
        self.raidComBoxWidgets['VD\'s']['values'] = range(1, 17)
        self.raidComBoxWidgets['Init']['values'] = ['NA', 'FULL', 'FAST', 'BGI']
        if raidLevel == 'R0':
            self.raidComBoxWidgets['PD\'s']['values'] = range(1, 33)
            self.raidComBoxWidgets['Span']['values'] = range(1, 2)
            self.raidComBoxWidgets['Spare']['values'] = range(0, 1)
        elif raidLevel in ['R1', 'R10']:
            self.raidComBoxWidgets['PD\'s']['values'] = range(2, 3) if raidLevel == 'R1' else range(4, 33, 2) + [36, 40,
                                                                                                                 44, 48,
                                                                                                                 52, 56,
                                                                                                                 60, 64,
                                                                                                                 66, 72,
                                                                                                                 78, 84,
                                                                                                                 90, 96,
                                                                                                                 104,
                                                                                                                 112,
                                                                                                                 120,
                                                                                                                 128,
                                                                                                                 130,
                                                                                                                 140,
                                                                                                                 150,
                                                                                                                 160,
                                                                                                                 168,
                                                                                                                 180,
                                                                                                                 192,
                                                                                                                 196,
                                                                                                                 210,
                                                                                                                 224,
                                                                                                                 240]
            self.raidComBoxWidgets['Span']['values'] = range(1, 2)
        elif raidLevel in ['R5', 'R50']:
            self.raidComBoxWidgets['PD\'s']['values'] = range(3, 33)
            self.raidComBoxWidgets['Span']['values'] = range(1, 2) if raidLevel == 'R5' else range(2, 9)
        elif raidLevel in ['R6', 'R60']:
            self.raidComBoxWidgets['PD\'s']['values'] = range(4, 33)
            self.raidComBoxWidgets['Span']['values'] = range(1, 2) if raidLevel == 'R6' else range(2, 9)
        elif raidLevel == 'JBOD':
            self.raidComBoxWidgets['PD\'s']['values'] = range(1, 241)
            for widgets in ['Span', 'Spare', 'Stripe', 'WP', 'RP', 'VD\'s', 'Init']:
                self.raidComBoxWidgets[widgets]['values'] = ['N/A'] if widgets not in ['Span', 'Spare'] else [0]
                if widgets == 'Span':
                    self.raidComBoxWidgets[widgets]['values'] = [1]
                self.raidComBoxWidgets[widgets]['state'] = 'disabled'
            self.raidComBoxWidgets['Size']['state'] = 'disabled'
        for widgets in ['PD\'s', 'Stripe', 'WP', 'RP', 'VD\'s', 'Span', 'Spare', 'DTAB', 'Init', 'Reps']:
            self.raidComBoxWidgets[widgets].current(0)


class adhocInputs(LabelFrame):
    """Frame holds all Widgets that are needed to get the switch related info  """
    _pady = 5
    _RELIEF = GROOVE
    _BG = BG_SWITCH
    _font = ('Consolas', 12)

    def __init__(self, parent, *args, **kwargs):
        """
        Initialize the switch GUI class
        :param parent: Frame handler of the frame where the switch gui needs to be placed
        :type parent: tk.Frame
        :param args: args required for the frame
        :type args: args
        :param kwargs:Keyword args required for the frame
        :type kwargs:Keyword args required for the frame
        """
        _font_ = getFontSize((parent.winfo_height() * .98) * .10, mul=5, bold=True)
        LabelFrame.__init__(self, parent, text="flex mode".title(), font=_font_, bg=adhocInputs._BG,
                            relief=adhocInputs._RELIEF, bd=1, labelanchor=N, foreground=BRCMRED, *args, **kwargs)
        self.grid(row=0, column=1, padx=5, pady=5, sticky=N + E + W + S)
        self.grid_propagate(0)
        self.update()
        setGridConfigure(parent, 0, 1)
        self.width = self.winfo_width()
        self.height = self.winfo_height()
        self.flexRaid = None
        self.plugFw = {'on': False, 'upgrade': StringVar(), 'downgrade': StringVar()}
        self.plugSnapDump = {'on': False, 'delay': StringVar()}
        self.plugMe = {'on': False, 'startLba': StringVar(), 'count': StringVar(), "skip": StringVar(),
                       'delay': StringVar()}
        self.plugOcr = {'on': False, 'delay': StringVar()}
        self.plugPolicyChange = {'on': False, 'delay': StringVar()}
        self.plugDcmd = {'on': False, 'delay': StringVar()}
        self.durations = [StringVar(), StringVar()]
        self.bgOprate = StringVar()
        self.iteration = [StringVar(), StringVar()]
        self.delayType = [StringVar(), StringVar()]
        self.timeInterval = [StringVar(), StringVar()]
        self.intervalStep = [StringVar(), StringVar()]
        self.ioParams = {'queue depth': StringVar(), 'tool': StringVar(), 'pattern': StringVar(), 'read': StringVar(),
                         'unaligned': StringVar(), 'io size': StringVar()}
        self.renderFlex()

    @property
    def _get(self):
        """returns all the flex widget values"""
        return {"raidlevel": self.flexRaid._get,
                "duration": {"duration1": self.durations[0].get(), "duration2": self.durations[1].get(), },
                "iteration": {"iteration1": {'count': self.iteration[0].get(), 'type': self.delayType[0].get(),
                                             'interval': self.timeInterval[0].get(),
                                             'step': self.intervalStep[0].get()},
                    "iteration2": {'count': self.iteration[1].get(), 'type': self.delayType[1].get(),
                                   'interval': self.timeInterval[1].get(), 'step': self.intervalStep[1].get()}},
                "io": {"qd": self.ioParams['queue depth'].get(), "pattern": self.ioParams['pattern'].get(),
                    "tool": self.ioParams['tool'].get(), "read": self.ioParams['read'].get(),
                    "unaligned": self.ioParams['unaligned'].get(), "size": self.ioParams['io size'].get(), },
                "bgops": {"rate": self.bgOprate.get()}, "plugins": {
                "me": {"on": self.plugMe['on'], "startlba": self.plugMe['startLba'].get(),
                    "count": self.plugMe['count'].get(), "skip": self.plugMe['skip'].get(),
                    "delay": self.plugMe['count'].get()},
                "snapdump": {'on': self.plugSnapDump['on'], 'delay': self.plugSnapDump['delay'].get()},
                "fwdownload": {'on': self.plugFw['on'], 'upgrade': self.plugFw['upgrade'].get(),
                               'downgrade': self.plugFw['downgrade'].get()},
                "ocr": {'on': self.plugOcr['on'], 'delay': self.plugOcr['delay'].get()},
                "policychange": {'on': self.plugPolicyChange['on'], 'delay': self.plugPolicyChange['delay'].get()},
                "dcmd": {'on': self.plugDcmd['on'], 'delay': self.plugDcmd['delay'].get()}

            }}

    def _load(self):
        """"""
        if 'raidlevel' in _configFileData_['flexmode']:
            self.flexRaid._load(values=_configFileData_['flexmode']['raidlevel'])
            duration = _configFileData_['flexmode']['duration']
            self.durations[0].set(duration['duration1'])
            self.durations[1].set(duration['duration2'])
            iteration = _configFileData_['flexmode']['iteration']
            for _ in range(0, 2):
                self.iteration[_].set(iteration['iteration' + str(_ + 1)]['count'])
                self.delayType[_].set(iteration['iteration' + str(_ + 1)]['type'])
                self.timeInterval[_].set(iteration['iteration' + str(_ + 1)]['interval'])
                self.intervalStep[_].set(iteration['iteration' + str(_ + 1)]['step'])
            io = _configFileData_['flexmode']['io']
            self.ioParams['queue depth'].set(io['qd'])
            self.ioParams['pattern'].set(io['pattern'])
            self.ioParams['tool'].set(io['tool'])
            self.ioParams['read'].set(io['read'])
            self.ioParams['io size'].set(io['size'])
            self.ioParams['unaligned'].set(io['unaligned'])
            self.bgOprate.set(_configFileData_['flexmode']['bgops']['rate'])
            pluginMe = _configFileData_['flexmode']['plugins']['me']
            self.plugMe['on'] = pluginMe['on']
            buttonToggle(self.plugMe)
            self.plugMe['startLba'].set(pluginMe['startlba'])
            self.plugMe['count'].set(pluginMe['count'])
            self.plugMe['skip'].set(pluginMe['skip'])
            self.plugMe['delay'].set(pluginMe['delay'])
            snapDump = _configFileData_['flexmode']['plugins']['snapdump']
            self.plugSnapDump['on'] = snapDump['on']
            buttonToggle(self.plugSnapDump)
            self.plugSnapDump['delay'].set(snapDump['delay'])
            dcmd = _configFileData_['flexmode']['plugins']['dcmd']
            self.plugDcmd['on'] = dcmd['on']
            buttonToggle(self.plugDcmd)
            self.plugDcmd['delay'].set(dcmd['delay'])
            ocr = _configFileData_['flexmode']['plugins']['ocr']
            self.plugOcr['on'] = ocr['on']
            buttonToggle(self.plugOcr)
            self.plugOcr['delay'].set(ocr['delay'])
            policychange = _configFileData_['flexmode']['plugins']['policychange']
            self.plugPolicyChange['on'] = policychange['on']
            buttonToggle(self.plugPolicyChange)
            self.plugPolicyChange['button'].image = onImg if policychange['on'] else offImg
            self.plugPolicyChange['delay'].set(policychange['delay'])
            fwdownload = _configFileData_['flexmode']['plugins']['fwdownload']
            self.plugFw['on'] = fwdownload['on']
            self.plugFw['upgrade'].set(fwdownload['upgrade'])
            self.plugFw['downgrade'].set(fwdownload['downgrade'])
            buttonToggle(self.plugFw)

    def renderFlex(self):
        relief = FLAT
        _BG = BG_SWITCH
        hght = int(self.winfo_height())
        wdth = int(self.winfo_width())
        flexFrameList = []
        flexFrameList.append(createWindow(self, relief=GROOVE, width=.69, height=.54, bg=_BG, rw=0, cl=0))
        flexFrameList.append(createWindow(self, width=.69, height=.44, bg=_BG, rw=1, cl=0))
        flexFrameList.append(
            LabelFrame(self, text='Plugins'.title(), font=getFontSize(height=int(hght * .15), bold=True), bd=1,
                       relief=GROOVE, width=int(wdth * .34), height=int(hght * .95), bg=BG_SWITCH, labelanchor=N,
                       foreground=BRCMRED))
        flexFrameList[-1].grid(row=0, column=1, rowspan=2, padx=5, pady=5, sticky=N + E + W + S)
        flexFrameList[-1].grid_propagate(0)
        flexFrameList[-1].update()
        setGridConfigure(self, 0, 1)
        self.flexRaid = flexRaid(flexFrameList[0])
        self.renderGeneric(frm=flexFrameList[1])
        self.renderPlugin(frm=flexFrameList[2])
        self._load()

    def renderGeneric(self, frm):
        relief = FLAT
        _bd = 1
        hght = int(frm.winfo_height())
        wdth = int(frm.winfo_width())
        durationFrame = createWindow(frm, relief=GROOVE, width=.45, height=.99, bg=BG_SWITCH, rw=0, cl=0)
        ioFrame = createWindow(frm, relief=GROOVE, width=.53, height=.99, bg=BG_SWITCH, rw=0, cl=1)
        _font_ = getFontSize(hght * .25, 10)
        makeLabel(durationFrame, text="duration 1".title(), font=_font_, row=0, column=0)
        makeLabel(durationFrame, text="duration 2".title(), font=_font_, row=1, column=0)
        makeLabel(durationFrame, text="bgops rate".title(), font=_font_, row=2, column=0)
        makeEntry(durationFrame, var=self.durations[0], font=_font_, row=0, column=1, width=5)
        makeEntry(durationFrame, var=self.durations[1], font=_font_, row=1, column=1, width=5)
        makeEntry(durationFrame, var=self.bgOprate, font=_font_, row=2, column=1, width=5)
        # --------------------------Iteration-----------------------------
        _ihght = hght / 4
        _iwdth = int(durationFrame.winfo_width() * .95)
        _iFont_ = getFontSize(height=hght * .30, mul=10)
        iFrameList = []
        widgtList = []
        for _ in range(3, 5):
            iFrameList.append(
                createWindow(durationFrame, relief=relief, width=.95, height=.25, bg=BG_SWITCH, rw=_, cl=0,
                             columnspan=2))
            _font_ = getFontSize(height=iFrameList[-1].winfo_height() * .75)
            makeLabel(iFrameList[-1], text='Iteration ' + str(_ - 2), font=_iFont_, row=0, column=0, columnspan=4,
                      foreground=BRCMRED, width=15)
            makeLabel(iFrameList[-1], text='Iter', font=_font_, row=1, column=0, width=7)
            makeLabel(iFrameList[-1], text='Delay', font=_font_, row=1, column=1, width=7)
            makeLabel(iFrameList[-1], text='Interval', font=_font_, row=1, column=2, width=7)
            makeLabel(iFrameList[-1], text='Step', font=_font_, row=1, column=3, width=7)
            makeEntry(iFrameList[-1], var=self.iteration[_ - 3], font=_font_, row=2, column=0, width=5)
            widgtList.append(
                ttk.Combobox(iFrameList[-1], textvariable=self.delayType[_ - 3], font=_font_, state='readonly',
                             width=5))
            widgtList[-1]['values'] = ['FIXED', 'INC', 'DEC', 'RAND']
            widgtList[-1].grid(row=2, column=1, padx=5, pady=5, sticky=N + E + W + S)
            setGridConfigure(iFrameList[-1], 2, 1)
            widgtList[-1].unbind_class("TCombobox", "<MouseWheel>")
            makeEntry(iFrameList[-1], var=self.timeInterval[_ - 3], font=_font_, row=2, column=2, width=5)
            makeEntry(iFrameList[-1], var=self.intervalStep[_ - 3], font=_font_, row=2, column=3, width=5)
        # --------------------IO----------------------------------
        makeLabel(ioFrame, text='IO Param ', font=getFontSize(height=int(hght * .30), bold=False), row=0, column=0,
                  columnspan=4, width=15, foreground=BRCMRED)
        _iFont_ = getFontSize(height=(ioFrame.winfo_height() * .25), mul=10, bold=False)
        for index, prm in enumerate(self.ioParams):
            makeLabel(ioFrame, text=prm.title(), font=_iFont_, row=index + 1, column=0, width=10)
            if prm == 'tool':
                cmb = ttk.Combobox(ioFrame, textvariable=self.ioParams[prm], font=_iFont_, state='readonly', width=5,
                                   foreground=BRCMBLUE, values=['CHAOS', 'MEDUSA'])
                cmb.grid(row=index + 1, column=1, padx=5, pady=5, sticky=N + E + W + S)
                setGridConfigure(ioFrame, index + 1, 1)
            else:
                dummy = makeEntry(ioFrame, var=self.ioParams[prm], font=_iFont_, row=index + 1, column=1, width=10)
                if prm == 'unaligned':
                    dummy.configure(state='disabled')
            setGridConfigure(ioFrame, index + 1, 0)

    def renderPlugin(self, frm):
        # -------------------------------------------Plugins----------------
        relief = FLAT
        pluginFrame = frm
        _plHght_ = pluginFrame.winfo_height() / 7
        _plwdth_ = pluginFrame.winfo_width()
        plFrameList = {}
        self.plugin = ['medium error', 'fw download', 'snapdump', 'policy change', 'ocr', 'dcmd']
        _feFont_ = getFontSize(height=int(_plHght_ * .60), bold=False)
        for index, feature in enumerate(['medium error', 'fw download']):
            plFrameList.update({feature: {
                'frm': LabelFrame(pluginFrame, text=feature.upper(), font=_feFont_, bd=1, relief=GROOVE,
                                  width=int(_plwdth_ * .98), height=int(_plHght_ * .72) * 2, foreground=BRCMRED,
                                  bg=BG_SWITCH, labelanchor=N)}})
            plFrameList[feature]['frm'].grid(row=index, column=0, columnspan=2, padx=5, pady=5, sticky=N + E + W + S)
            plFrameList[feature]['frm'].grid_propagate(0)
            plFrameList[feature]['frm'].update()
            setGridConfigure(pluginFrame, index, 0)
        for index in range(2, 6):
            feature = self.plugin[index]
            rw = [2, 2, 3, 3]
            plFrameList.update({feature: {
                'frm': LabelFrame(pluginFrame, text=feature.upper(), font=_feFont_, bd=1, relief=GROOVE,
                                  width=int(_plwdth_ * .47), foreground=BRCMRED, height=int(_plHght_ * .72) * 2,
                                  bg=BG_SWITCH, labelanchor=N)}})
            plFrameList[feature]['frm'].grid(row=rw[index - 2], column=index % 2, padx=5, pady=5, sticky=N + E + W + S)
            plFrameList[feature]['frm'].grid_propagate(0)
            plFrameList[feature]['frm'].update()
            setGridConfigure(pluginFrame, rw[index - 2], index % 2)
        for feature in plFrameList:
            plFrameList[feature].update({'frame1': createWindow(plFrameList[feature]['frm'], relief=relief, width=.98,
                                                                height=.80, bg=BG_SWITCH, rw=0, cl=0)})
        self.renderOnOff(_frame=plFrameList['medium error'], wdgthhandler=self.plugMe, typ=1)
        self.renderOnOff(_frame=plFrameList['fw download'], wdgthhandler=self.plugFw, typ=2)
        self.renderOnOff(_frame=plFrameList['snapdump'], wdgthhandler=self.plugSnapDump)
        self.renderOnOff(_frame=plFrameList['policy change'], wdgthhandler=self.plugPolicyChange)
        self.renderOnOff(_frame=plFrameList['ocr'], wdgthhandler=self.plugOcr)
        self.renderOnOff(_frame=plFrameList['dcmd'], wdgthhandler=self.plugDcmd)

    def renderOnOff(self, _frame, wdgthhandler, typ=3):
        """Renders Plugin widgets"""
        _fwHght = _frame['frame1'].winfo_height() * .98
        _fFont_ = getFontSize(height=int(_fwHght * .50), bold=False)
        if typ == 3:
            wdgthhandler['button'] = Button(_frame['frame1'], image=offImg, bd=0, bg=BG_SWITCH,
                                            command=lambda: buttonToggle(wdgthhandler))
            wdgthhandler['button'].image = offImg
            wdgthhandler['button'].grid(row=2, column=0, padx=5, pady=5, sticky=N + E + W + S)
            setGridConfigure(_frame['frame1'], 2, 0)
            makeLabel(_frame['frame1'], text='Delay', font=_fFont_, row=0, column=0, width=5)
            makeEntry(_frame['frame1'], var=wdgthhandler['delay'], font=_fFont_, row=1, column=0, width=5)
        else:
            wdgthhandler['button'] = Button(_frame['frame1'], image=offImg, bd=0, bg=BG_SWITCH,
                                            command=lambda: buttonToggle(wdgthhandler))
            wdgthhandler['button'].image = offImg
            wdgthhandler['button'].grid(row=(4 if typ == 2 else 2), column=0, columnspan=(1 if typ == 2 else 4), padx=5,
                                        pady=5, sticky=N + E + W + S)
            setGridConfigure(_frame['frame1'], 4, 0)
            _frame['frame2'] = _frame['frame1']
            if typ == 2:
                _fFont_ = getFontSize(height=int(_fwHght * .40), bold=False)
                makeLabel(_frame['frame1'], text='Upgrade File', font=_fFont_, row=0, column=0, width=15)
                makeLabel(_frame['frame1'], text='Downgrade File', font=_fFont_, row=2, column=0, width=15)
                makeEntry(_frame['frame1'], var=wdgthhandler['upgrade'], font=_fFont_, row=1, column=0, width=30)
                makeEntry(_frame['frame1'], var=wdgthhandler['downgrade'], font=_fFont_, row=3, column=0, width=30)
            else:
                makeLabel(_frame['frame1'], text='LBA', font=_fFont_, row=0, column=0, width=10)
                makeLabel(_frame['frame1'], text='Count', font=_fFont_, row=0, column=1, width=10)
                makeLabel(_frame['frame1'], text='Skip', font=_fFont_, row=0, column=2, width=10)
                makeLabel(_frame['frame1'], text='Delay', font=_fFont_, row=0, column=3, width=10)
                makeEntry(_frame['frame1'], var=wdgthhandler['startLba'], font=_fFont_, row=1, column=0, width=4)
                makeEntry(_frame['frame1'], var=wdgthhandler['count'], font=_fFont_, row=1, column=1, width=4)
                makeEntry(_frame['frame1'], var=wdgthhandler['skip'], font=_fFont_, row=1, column=2, width=4)
                makeEntry(_frame['frame1'], var=wdgthhandler['delay'], font=_fFont_, row=1, column=3, width=4)


class mainApplication():

    def __init__(self, parent):
        """

        :param parent:
        :type parent:
        :param args:
        :type args:
        :param kwargs:
        :type kwargs:
        """
        self.pwdir = os.getcwd()
        self.makeConfigFileDir()
        self.flexModeOn = {'on': _configFileData_['flexmode']['mode'], 'button': ''}
        self.legacyInputs = None
        self.adhocInputs = None
        self.loadGui(parent)

    def makeConfigFileDir(self):
        '''
        Creates Config File Dir under os.pwd() if doesnt Exists
        '''
        path = os.path.join(self.pwdir, 'configfilesfolder')
        if not os.path.exists(path):
            os.makedirs(path)

    def loadGui(self, parent):
        """ 
        
        """
        self.flex = True if self.flexModeOn['on'] else False
        _flex_ = self.flex
        self.setup_root(parent)  # sets up the root (Window size of the config file GUI)
        self.root = parent
        width = int(parent.winfo_width())
        height = int(parent.winfo_height())
        self.setFrames()
        self.titleBar(parent)
        self.legacyInputs = legacyInputs(self.inputWindow, width=width * (0.25 if self.flex else .96),
                                         height=height * 0.85)
        if self.flex:
            self.adhocInputs = adhocInputs(self.inputWindow, width=width * 0.73, height=height * 0.85)
        self.actionBar()  # self.openConfigFile()

    def setFrames(self):
        """"""
        _BG = BG_LIGHT
        # _BG = 'ghost white'
        self.titleFrame = createWindow(parent=self.root, width=1, height=0.04, bg=_BG, rw=0, cl=0, pdx=0, pdy=5,
                                       rwWght=0, colWght=1)
        self.inputWindow = createWindow(parent=self.root, width=1, height=0.84, bg=_BG, rw=1, cl=0, pdx=0, pdy=5,
                                        rwWght=0, colWght=1)
        self.actionFrame = createWindow(parent=self.root, width=1, height=0.1, bg=_BG, rw=3, cl=0, pdx=0, pdy=5,
                                        rwWght=0, colWght=1)

    def titleBar(self, parent):
        """Renders Title of the Window"""
        makeLabel(self.titleFrame, text=VERSION_INFO,
                  font=getFontSize(height=self.titleFrame.winfo_height() * .80, mul=1 if self.flex else 2, bold=True),
                  bg=BG_LIGHT, row=0, column=0, width=25, foreground=BRCMRED)

    def actionBar(self):
        """Action Bar to save close and toggle flex Window"""
        _BG = BG_LIGHT
        spacerFrame = createWindow(self.actionFrame, width=(.70 if self.flex else .01), height=.90, bg=_BG, rw=0, cl=0)
        Label(spacerFrame, image=brcmLogo if self.flex else brcmLogo2, bg=BG_LIGHT, relief=FLAT).grid(row=0, column=0,
                                                                                                      padx=5, pady=5)
        setGridConfigure(spacerFrame, 0, 0, 1, 1)
        buttonFrame = createWindow(self.actionFrame, width=.70, height=.90, bg=_BG, rw=0, cl=1)
        _font = getFontSize(height=int(buttonFrame.winfo_height() * .70), mul=9, bold=False)
        """openFile = Button(buttonFrame, image=runImg, bg=BG_LIGHT, relief=FLAT, font=_font, command=self.queueTestCase)
        openFile.img = runImg

        openFile.grid(row=0, column=0, padx=5, pady=2, sticky=N + E + W + S)
        makeLabel(buttonFrame, text='Open', font=_font, bg=BG_LIGHT, row=1, column=0, width=10, padx=5, pady=2,
                  foreground=BRCMBLUE)
        setGridConfigure(buttonFrame, column=0, clwght=1)"""
        self.flexModeOn['button'] = Button(buttonFrame, image=onImg if self.flexModeOn['on'] else offImg, relief=FLAT,
                                           font=_font, bg=BG_LIGHT, command=lambda: self.flexToggle(self.flexModeOn))
        self.flexModeOn['button'].img = onImg if self.flexModeOn['on'] else offImg
        self.flexModeOn['button'].grid(row=0, column=1, padx=5, pady=2, sticky=N + E + W + S)
        makeLabel(buttonFrame, text='Flex Mode', font=_font, bg=BG_LIGHT, row=1, column=1, width=10, padx=5, pady=2,
                  foreground=BRCMBLUE)
        setGridConfigure(buttonFrame, column=1, clwght=1)
        self.save = Button(buttonFrame, image=saveButton, relief=FLAT, font=_font, bg=BG_LIGHT,
                           command=self.save_to_file)
        self.save.img = saveButton
        self.save.grid(row=0, column=2, padx=5, pady=2, sticky=N + E + W + S)
        makeLabel(buttonFrame, text='Save', font=_font, bg=BG_LIGHT, row=1, column=2, width=10, padx=5, pady=2,
                  foreground=BRCMBLUE)
        setGridConfigure(buttonFrame, column=2, clwght=1)
        runTest = Button(buttonFrame, image=runImg, bg=BG_LIGHT, relief=FLAT, font=_font, command=self.queueTestCase)
        runTest.img = runImg

        runTest.grid(row=0, column=3, padx=5, pady=2, sticky=N + E + W + S)
        makeLabel(buttonFrame, text='Run', font=_font, bg=BG_LIGHT, row=1, column=3, width=10, padx=5, pady=2,
                  foreground=BRCMBLUE)
        setGridConfigure(buttonFrame, column=3, clwght=1)
        settings = Menubutton(buttonFrame, image=settingsImg, bg=BG_LIGHT, relief=FLAT, font=_font, wraplength=25,
                              direction='above')
        settings.img = settingsImg
        settings.grid(row=0, column=4, padx=5, pady=2, sticky=N + E + W + S)
        makeLabel(buttonFrame, text='ATE2', font=_font, bg=BG_LIGHT, row=1, column=4, width=10, padx=5, pady=2,
                  foreground=BRCMBLUE)
        setGridConfigure(buttonFrame, column=4, clwght=1)
        close = Button(buttonFrame, image=closeButton, bg=BG_LIGHT, relief=FLAT, font=_font, command=self.root.destroy)
        close.img = closeButton
        close.grid(row=0, column=5, padx=5, pady=2, sticky=N + E + W + S)
        makeLabel(buttonFrame, text='Exit', font=_font, bg=BG_LIGHT, row=1, column=5, width=10, padx=5, pady=2,
                  foreground=BRCMBLUE)
        setGridConfigure(buttonFrame, column=5, clwght=1)
        ate2Option = Menu(settings, tearoff=0, font=_font, relief=FLAT, bg=BG_LIGHT)
        ate2Option.add_command(label='Clear ATE2 Queued List')
        ate2Option.add_command(label='Stop Current Test Run')
        ate2Option.add_command(label='Restart ATE2 Services')
        settings.config(menu=ate2Option)

    def flexToggle(self, wdgt):
        _configFileData_['legacy'] = copy.deepcopy(self.legacyInputs._legacy)
        # print _configFileData_
        buttonToggle(wdgt)
        deleteWidgets(self.root)
        del self.legacyInputs
        self.loadGui(self.root)

    def write_to_file(self, data):
        """
        Writes the widget values from the config file to the config_file.json
        :param data: Dictionary containing all the gui widget values
        :type data: dict
        :return: None
        :rtype: None
        """
        with open(CONFIGFILEPATH, "w+") as data_file:
            data_file.write(json.dumps(data, indent=4))
            data_file.close()

    def save_to_file(self):
        """Write to Config File"""
        if self.flex:
            _configFileData_['flexmode']['mode'] = True
            _configFileData_['flexmode'].update(self.adhocInputs._get)
        else:
            _configFileData_['flexmode']['mode'] = False
        self.write_to_file(
            {'legacy': copy.deepcopy(self.legacyInputs._legacy), 'flexmode': _configFileData_['flexmode']})

    def setup_root(self, parent):
        """

        :param parent:
        :type parent:
        """
        width = int(parent.winfo_screenwidth() * (.95 if self.flex else .25))
        height = int(parent.winfo_screenheight() * (.90 if self.flex else .80))
        parent.configure(bg=BG_LIGHT, width=width, height=height)
        parent.geometry(str(width) + 'x' + str(height))
        parent.title(BUILD)
        # parent.icon(False, brcmLogo2)
        parent.protocol("WM_DELETE_WINDOW", lambda: parent.destroy())
        parent.grab_set()
        parent.grid_propagate(0)
        parent.update()
        parent.resizable(0, 0)
        # parent.overrideredirect(1)
        center(parent)

    def enqueue_output(self, input):
        for line in iter(input['file'].readline, b''):
            input['queue'].put(line)  # input['file'].close()

    def get_line_nowait(self):
        '''Dequeue and return a line output or None if the queue is empty'''
        try:
            line = self.q_stdout.get_nowait()
        except Empty:
            line = None
        return line

    def queueTestCase(self):
        """
        Queues Test Case to Ate2
        """

        '''testCaseJson = tkFileDialog.askopenfilename(initialdir="C://Wingman//wmflex//test_jsons//",
                                                    title="Select Test Case JSON",
                                                    filetypes=(("Text files",
                                                                "*.json*"),
                                                               ("all files",
                                                                "*.*")))'''
        testCaseJson = tkFileDialog.askopenfilenames(initialdir="C://Wingman//wmflex//test_jsons//",
                                                     title="Select Test Case JSON",
                                                     filetypes=(("Text files", "*.json*"), ("all files", "*.*")))
        if not testCaseJson:
            tkMessageBox.showwarning(title='Test Case JSON', message='Test Case JSON Not Selected')
            return
        self.tcRunnerPopUp = Toplevel(self.root, height=int(500), width=int(600), bd=1, bg=BG_LIGHT,
                                      highlightbackground=BRCMRED, highlightthickness=2, relief=FLAT)
        self.tcRunnerPopUp.grab_set()
        center(self.tcRunnerPopUp)
        self.tcRunnerPopUp.grid_propagate(0)
        self.tcRunnerPopUp.update_idletasks()
        self.tcRunnerPopUp.title("Wingman Test Queue Status")
        center(self.tcRunnerPopUp)
        _font = getFontSize(height=int(self.tcRunnerPopUp.winfo_height() * .20), mul=7, bold=False)
        _txtFont = getFontSize(height=int(self.tcRunnerPopUp.winfo_height() * .13), mul=10, bold=False)
        self.status = Text(self.tcRunnerPopUp, font=_txtFont, width=int(self.tcRunnerPopUp.winfo_width() * .193),
                           borderwidth=1, background='black', foreground='green',
                           height=int(self.tcRunnerPopUp.winfo_height() * 0.075))
        self.status.grid(row=0, column=0, rowspan=1, columnspan=1, padx=5, pady=5, sticky=N + E + W + S)
        setGridConfigure(self.tcRunnerPopUp, row=0, rwght=2)
        self.progress = ttk.Progressbar(self.tcRunnerPopUp, length=10, mode='determinate')
        self.progress.grid(row=2, column=0, sticky=N + W + E + S, pady=5, padx=5)
        setGridConfigure(self.tcRunnerPopUp, row=2)
        self.tcRunnerPopUp.update_idletasks()
        queued = {}
        try:
            for jsonFile in root.tk.splitlist(testCaseJson):
                if sys.platform.startswith('win'):
                    cmd = r'python C:\Wingman\tc_start.py C:\Wingman\wmflex\mjolnirFlex.py'
                else:
                    cmd = r'python /root/Wingman/tc_start.py /root/Wingman/mjolnir.py'
                cmd += ' --testCaseJson=' + str(jsonFile) + ' --configFileJson=' + str(CONFIGFILEPATH)
                cmd += '\n'
                self.progress['value'] = 10 / len(root.tk.splitlist(testCaseJson))
                self.status.insert(END, cmd)
                self.status.update()
                self.tcRunnerPopUp.update_idletasks()
                self.q_stdout = Queue()
                tcStartProcess = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
                tstdout = threading.Thread(name="stdout ", target=self.enqueue_output,
                                           args=({'file': tcStartProcess.stdout, 'queue': self.q_stdout},))
                tstdout.daemon = True
                tstdout.start()
                per = 0
                queued.update({jsonFile: {'result': False, 'queueLogs': []}})
                while tcStartProcess.poll() == None:
                    line = self.get_line_nowait()
                    if line:
                        self.status.insert(END, line)
                        self.status.update()
                        per += 3
                        self.progress['value'] = per
                        self.tcRunnerPopUp.update_idletasks()
                        if 'CQTST00123456 successfully queued. Run ate2cli list to obtain log and other' in line:
                            queued[jsonFile].update({'result': True})
                        queued[jsonFile]['queueLogs'].append(line)
            self.progress['value'] = 100
            self.tcRunnerPopUp.destroy()
            queuePass, queueFail = [], []
            [queuePass.append(jsonFile) if values['result'] else queueFail.append(jsonFile) for jsonFile, values in
             queued.iteritems()]
            if queuePass:
                tkMessageBox.showinfo('Test Case Queued', 'Test Case ' + ','.join(
                    queuePass) + ' SuccessFully Check TC Runner Window For Log View')
            else:
                for tc in queueFail:
                    tkMessageBox.showerror('Test Case Queued',
                                           'Unable QueueTest Case Please Check ATE2 .. Error ' + '\n'.join(
                                               queued['tc']['queueLogs']))  # AddRotatinLogger to Queue TC
        except Exception as e:
            tkMessageBox.showinfo('Info', "ERROR: {}".format(e))
        self.tcRunnerPopUp.destroy()

    def openConfigFile(self):
        """
        Creates User Prompt Window for Load existing Config File or Creating a new Config File.

        """
        self.openCfgFileWindow = Toplevel(self.root, height=int(150), width=int(300), bd=1, bg=BG_LIGHT,
                                          highlightthickness=2, relief=FLAT)
        self.openCfgFileWindow.grab_set()
        center(self.openCfgFileWindow)
        self.openCfgFileWindow.grid_propagate(0)
        self.openCfgFileWindow.update_idletasks()
        self.openCfgFileWindow.title("Choose Config File")
        center(self.openCfgFileWindow)
        _font = getFontSize(height=int(self.openCfgFileWindow.winfo_height() * .30), mul=7, bold=True)
        newFile = Button(self.openCfgFileWindow, image=newFileImg, bg=BG_LIGHT, relief=FLAT, font=_font,
                         command=self.root.destroy)
        newFile.img = newFileImg
        newFile.grid(row=0, column=0, padx=5, pady=5, sticky=N + E + W + S)
        makeLabel(self.openCfgFileWindow, text='Create New', font=_font, bg=BG_LIGHT, row=1, column=0, width=10, padx=5,
                  pady=2, foreground=BRCMBLUE)
        setGridConfigure(self.openCfgFileWindow, row=0, column=0, clwght=1)
        openFile = Button(self.openCfgFileWindow, image=openFileImg, bg=BG_LIGHT, relief=FLAT, font=_font,
                          command=self.root.destroy)
        openFile.img = openFileImg
        openFile.grid(row=0, column=1, padx=5, pady=2, sticky=N + E + W + S)
        makeLabel(self.openCfgFileWindow, text='Open File', font=_font, bg=BG_LIGHT, row=1, column=1, width=10, padx=5,
                  pady=2, foreground=BRCMBLUE)
        setGridConfigure(self.openCfgFileWindow, row=1, column=1, clwght=1)


if __name__ == "__main__":
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    root = tk()
    onImg = PhotoImage(data=OnSwitch)
    offImg = PhotoImage(data=OffSwitch)
    brcmLogo = PhotoImage(data=BrdcmLogoMax)
    brcmLogo2 = PhotoImage(data=BrdcmLogoMini)
    addImg = PhotoImage(data=AddButton)
    delImg = PhotoImage(data=TrashButton)
    saveButton = PhotoImage(data=SaveFile)
    closeButton = PhotoImage(data=QuitApp)
    addImg = PhotoImage(data=ADD)
    delImg = PhotoImage(data=REMOVE)
    runImg = PhotoImage(data=RunTest)
    settingsImg = PhotoImage(data=Settings)
    openFileImg = PhotoImage(data=openFile)
    newFileImg = PhotoImage(data=newFile)
    _configFileData_ = readConfigFile()
    mainApplication(root)
    root.mainloop()

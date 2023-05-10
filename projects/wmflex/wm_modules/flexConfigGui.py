'''
DATE(M/D/Y)  CQID            WHO(CQUser)  DESCRIPTION
===============================================================
03/24/23     DCSG01431093    nmartis       Ph2: Wingman 3.0: New GUI framework for flex config requirements
03/24/23     DCSG01459382    nmartis      Add Support Modify the Default RAID Parameters on RAID Selection
'''

import ttk
from Tkconstants import FLAT, GROOVE, RAISED, SUNKEN, CENTER, RIGHT
from Tkinter import Tk as tk, Label, E, W, N, S, Frame, PhotoImage, Entry, Button, StringVar, Toplevel, LabelFrame, END, \
    Checkbutton, Scrollbar, Canvas, Text
from utils import __version__, CONFIGFILEPATH

import copy
import json
import os
import re

ADD = """R0lGODlhGQAZAPQAAAAAAByU8x6V8x+V8yCV8yGW8ySY8zSf9Gy49ZTL95bM98vl+Njq+djr+fr6+v37+v/9+v/++gAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACH5BAEUAAAAIf4gQ3JlYXRlZCB3aXRoIGV6Z2lmLmNvbSBHSUYgbWFrZXIALAAAAAAZABkAAAVnIFCMZGmeo4iubOu+cCy7xmHMpoAwiICTAkVE4fsVgsPiD0mcCZ7PRCQBfdIQimxi8VgksgrEjXVgRM6Rh+OBjjAOLQNWy/WCxa6qQEqtOoVNRkxKOINGRzs9hwU1Y4uPkJFGKosAIQA7"""
REMOVE = """R0lGODlhGQAZAPYAAAAAAPNDNvRDNvNENfRENvRHO/RKPfVQQ/VTR/VVSfRXTPVdUfVjWPVkWfVnXPVoXfVqYPVtY/ZvZfZwZvZzafZ0a/Z2bPZ5cPZ/dvaCefaFffaKgvaLhPaMhPePiPeTi/eWj/eXkPeak/eclveemPehm/ejnfeknfenofeooverpfespveuqPivqvixrPi3svi4s/i6tvi8t/i9ufjIxfjLyPjMyfnV0/nX1PnY1fnb2fnc2vne3Prj4vrm5Pns6/nt7Prz8vr39/r6+gAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACH/C05FVFNDQVBFMi4wAwEAAAAh/iBDcmVhdGVkIHdpdGggZXpnaWYuY29tIEdJRiBtYWtlcgAh+QQBFAAAACwAAAAAGQAZAAAHY4AAAoOEhYaHg4KIi4yNjo+QkZKTlJWHBigQhhAoBpEoQz8RhBE/QyiREKaiAqWhmpGuPxyro5OuQ6G2lBy5QxyWuLqUsrTDqbWtq7CPoKyDrqiQmMyDnJ6W2drb3N3eidwAgQA7"""
SAVE_BUTTON = """R0lGODlhHgAeAPYAAAAAAC59Mi5+Mi9/MzCANDCBNDGBNTGCNTGDNTKDNjWJOTaKOjiNPD2VQT2WQD2WQT2XQT6XQT6XQkKfRkOgR0alSkenS0ioTEqrTkmtT0qsTkqtTkutTkqtT0utT0quT0uuT0uvT0yvT0uuUEuvUEyvUE2vUEywUE2wUE2wUU6wUVGyU1GzU1S0VFW1VFW1VVa1VVq4V1+7WmG8WmfAXWjBXmzDYHvNaI/ZcZHacpfedpjfdqDkeqHkeqHke6Lle6TmfKnqf6zrgLLvg7PvhLbxhbr0h8L5i8P5i8f8jcj8jsn9jsr9j8r+j8v/kMz/kM3/kM3/kc//kc//ktH/kgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACH5BAEUAAAALAAAAAAeAB4AAAfxgACCIiAWhoeIiYkgIoKOJSANAZOUlZaWDSCOgicUBZegoAUUJ48WCqGplgoYJQCEDQWys5+ptLOZIiWQGL2+GLWXBb++ILvHyLsgDKEMxsnQ0RPBlAUT0djJkdQFmdnfyhMMsgwTz+DgIL3n6O3u7/DtJ/Mn8dggOUVFOez2yj9UqPzo5w/EDyhQBvrTdjAhQXsGESpcuMKFRSAIgVh0scLeDSNHjixBuCSkkRv2VuBIgrAllCU5OsYb4ULHyJZLdrgYUTDGDycInfyI8dAdCBlBEAqZURQejSFEaiyEdsKGjanRRvBspwtrshFN/Y0IBAA7"""
CLOSEBUTTON = """R0lGODlhGwAeAPYAAAAAAPRBNPRCNPRCNfRDNfRDNvREN/RFOPRFOfRGOfRHOvRHO/RIO/RIPPRJPPRJPfVLP/VQRPVRRfVRRvVSRvVSR/VXTPVYTfZcUfVcUvZdUvZdU/dsYvdsY/dza/d0bPh6c/h9dviEffmIgfmKhPmLhfmNh/mOh/mOiPmPiPmPifmPivmQi/mTjvqalfqalvqfm/qhnfqinvqin/qjn/qjoPqlofqnpPuwrfy2tPy3tPy3tfy5t/3Fxf3Gxv3P0P7U1f7V1v7b3P7d3/7e4P7f4f7g4f7g4v7h4//j5f/j5v/k5v/l6P/m6P/m6f/n6f/n6v/o6v/o6//p7P/q7f/r7v/r7//s7wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACH5BAEUAAAALAAAAAAbAB4AAAfXgAAABYSFhoeIhIKDiY2OjI6RkpOUlZaEDA2OCQaUDSs4GYkRLB6dkQkkQ1M5ooYRM1A/H6eNCSNGU1CthbBQU1ItCZINJkVTUzyivrozEZ4ruVI5HbG6Nc+Vn7lQQEm6NtmWxavISc6XBZ0XPshTQB3phLBLU1dX066WETW/Sz7HkumbxAzKjAvGgPEiaA1KuALbFA5MlMDFL4PiIk65oWkTCSEYDxUzAiTEsEgMSLgQZ6iBCBAnJSWIichALXk4c+pMBGnnop0FFgkdSrSo0aNIkyo1GggAOw=="""
SWITCHON = """R0lGODlhLQAeAPQAAAAAAHixPXmxPXmxPnuyQHuyQXyzQoq7Voy9WY29WqTKe6fNgKjNgKrOg6rOhKvOha/Ri/H46fL46vL46/X67vX67/X77wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACH5BAEUAAAALAAAAAAtAB4AAAXDICCOZGmeaKqubOu+cCy7hWHfeK7veFGkNZ6uMCgaj8hi7XcSDg8NiHRKrToQNZQzN1BELOCweBxxDAza7W3QsETe8LjcAjmn1YbBwi3vw+l2TXh5e36GgGiCeHp8hnN1iSaDhI2Of5B3aoyWj4GSg5ucl54lk6GiX5iKmoWoqaQkpq2oiJlbp6K1q7ezuaqfi72cusCaba6vkaWgXmPOYmWwI0FqBVBV2FRXWbtbREngRkspBtSTeD4z6uvs7e7v8CUhADs="""
SWITCHOFF = """R0lGODlhLQAeAPUAAAAAAOAlM+EmM+MnNeMoNuUpN+UqOOYrOecsOuYvPegsO+gtO+QxP+A+St5QWt1RXN1SXOFEUOBOWOFOWeFVX+FWYOFlbuFncOBpcuV/huWDi+WEi+qrsO7Ex+/FyPjz9Pj19vn5+fn6+vn7+/n8+/r+/vr//vr//wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACH5BAEUAAAALAAAAAAtAB4AAAbPQIBwSCwaj8ikcMFsOp/QqPQ5nFqv2AWgeSAMvuCweEA4ZK+JiAXDbrvfmMuEcZYiGhyQac/v+00hHhUFdVAHDh8hiouMjYskGQKFTwcQjpeOJhuSk1yWmKAhJhqcnQuVoaCjpZ2oqZerpkyur42xsrS1i7emubqipLKnn7+KvK3ExceTvrrLhc21z3XRr9Nn1anXWdmh21jdqsG4yb+arMyIxYqQ6IV3eX/yfCEdFITCaWtw/GxydMJmeRlD8EuZgFsCyqqicJKShxAjAggCADs="""

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
BUILD = __version__
global addImg
global delImg
global onImg
global offImg
global saveButton
global closeButton

VERSION_INFO = ("wingman avenger config file editor " + __version__).title()
RELIEF = FLAT


def getFontSize(height, mul=10, font='smooth_segoe_bold_small', bold=False):
    _titleFontSize_ = 40 if mul == 1 else 50 if mul == 2 else 60 if mul == 3 else 70 if mul == 4 else 80 if mul == 5 else 90 if mul == 6 else 100 if mul == 7 else 110 if mul == 8 else 120 if mul == 9 else 130 if mul == 10 else 140
    return (font, int((int(height) * 20) / _titleFontSize_), 'bold') if bold else (
        font, int((int(height) * 20) / _titleFontSize_))


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


def buttonToggle(buttonData):
    """Changes the Button Image and Sets the status Variable"""
    offImg = PhotoImage(data=SWITCHOFF)
    onImg = PhotoImage(data=SWITCHON)
    if buttonData['on']:
        buttonData['on'] = False
        buttonData['button'].config(image=offImg)
        buttonData['button'].img = offImg
    else:
        buttonData['on'] = True
        buttonData['button'].config(image=onImg)
        buttonData['button'].img = onImg


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


def makeLabel(parent, text, font, row, column, rowspan=1, columnspan=1, bg=BG_SWITCH, width=23, foreground=BRCMBLUE, pdx=5,pdy=5):
    """
    Creates Label and Sets the grid Configuration to Parent with Color. # to be enchanced with ttk.style Later
    """
    Label(parent, text=text.center(20), bg=bg, font=font, borderwidth=1, foreground=foreground, relief=FLAT,
          width=width).grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan, padx=pdx, pady=pdy,
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


class flexRaid():
    _RELIEF = FLAT
    _BG = BG_SWITCH

    # _BG = "peach puff"

    def __init__(self, parent, root):
        """
        Initialize the switch GUI class
        :param parent: Frame handler of the frame where the switch gui needs to be placed
        :type parent: tk.Frame
        :param args: args required for the frame
        :type args: args
        :param kwargs:Keyword args required for the frame
        :type kwargs:Keyword args required for the frame
        """
        self.root = root
        self.repeatAll = StringVar()
        self.parent = Frame(parent, width=750, height=450)
        self.parent.grid(row=0, column=0, columnspan=1, rowspan=1, padx=1, pady=1, sticky=N + W + E + S)
        self.parent.grid_propagate(0)
        self.parent.update()
        setGridConfigure(self.parent, row=0, column=0, rwght=1, clwght=1)
        self.raidConfigVar = [StringVar() for _ in range(0, 13)]
        raidFrame = createWindow(self.parent, width=.99, height=.88, bg=flexRaid._BG, rw=0, cl=0)
        self.raidMgmtFrame = createWindow(self.parent, width=.97, height=.08, bg=flexRaid._BG, rw=1, cl=0)
        self.renderRaidFrame(raidFrame)

    def set_step(self, values):
        """Values -> from config under raidlevel.values()"""
        for item in self.raidTree.get_children():
            self.raidTree.delete(item)
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

    def get_step(self):
        """Returns User Raid Selection"""
        config = []
        for id in self.raidTree.get_children():
            _raid = {}
            _raid.update({'raid': self.raidTree.item(id)['values'][0].strip().lower()})
            _raid.update({'pdcount': int(self.raidTree.item(id)['values'][1])})
            _raid.update({'size': self.raidTree.item(id)['values'][2].strip().lower()})
            _raid.update({'stripe': int(self.raidTree.item(id)['values'][3])})
            _raid.update({'writepolicy': self.raidTree.item(id)['values'][4].strip().lower()})
            _raid.update({'readpolicy': self.raidTree.item(id)['values'][5].strip().lower()})
            _raid.update({'vdcount': int(self.raidTree.item(id)['values'][6])})
            _raid.update({'spans': int(self.raidTree.item(id)['values'][7])})
            _raid.update({'hotspare': int(self.raidTree.item(id)['values'][8])})
            _raid.update({'dtabcount': int(self.raidTree.item(id)['values'][9])})
            _raid.update({'init': self.raidTree.item(id)['values'][10].strip().lower()})
            _raid.update({'repeat': int(self.raidTree.item(id)['values'][11])})

            config.append(_raid)
        if config == []:
            return False
        try:
            repeat = True if int(self.repeatAll.get()) == 1 else False
        except:
            repeat = False
        return {'type': 'flexconfig', 'exhaust': repeat, 'config': config}

    def step_text(self):
        """"""
        config = self.get_step()
        txt = 'ADD '
        for raid in config['config']:
            if raid['raid'].lower() != 'jbod':
                txt += '%s %s VD\'s With  %s Drives and Repeat %s Times | ' % (
                raid['vdcount'], raid['raid'].upper(), raid['pdcount'] * raid['spans'], raid['repeat'])
            else:
                txt += '%s JBOD Drives and Repeat %s Times | ' % (raid['pdcount'], raid['repeat'])
        txt += ' RepeatUntilExhaust %s' % (config['exhaust'])
        for item in self.raidTree.get_children():
            self.raidTree.delete(item)
        return txt

    def renderRaidFrame(self, parent):
        # from tkinter.font import nametofont
        _font_ = getFontSize(int(parent.winfo_height() * .01), mul=10, bold=False)
        # nametofont('TkHeadingFont').configure(family=_font_[0], size=_font_[1])
        columns = ['raid', 'pdcount', 'size', 'stripe', 'writepolicy', 'readpolicy', 'vdcount', 'span', 'hotspare',
                   'dtab', 'init', 'repeat']
        s = ttk.Style()
        s.configure('nmartis.Treeview', rowheight=25)
        self.raidTree = ttk.Treeview(parent, columns=columns, show='headings', style='nmartis.Treeview')
        self.raidTree.heading('raid', text='Raid', anchor='c')

        self.raidTree.heading('pdcount', text='PD\'s'.upper(), anchor='c')
        self.raidTree.heading('size', text='VD Size'.upper(), anchor='c')
        self.raidTree.heading('stripe', text='Stripe'.upper(), anchor='c')
        self.raidTree.heading('writepolicy', text='WP'.upper(), anchor='c')
        self.raidTree.heading('readpolicy', text='RP'.upper(), anchor='c')
        self.raidTree.heading('vdcount', text='VD\'s'.upper(), anchor='c')
        self.raidTree.heading('span', text='Span'.upper(), anchor='c')
        self.raidTree.heading('hotspare', text='Spare'.upper(), anchor='c')
        self.raidTree.heading('dtab', text='Dtab'.upper(), anchor='c')
        self.raidTree.heading('init', text='Init'.upper(), anchor='c')
        self.raidTree.heading('repeat', text='Repeat'.upper(), anchor='c')
        [self.raidTree.column(col, minwidth=50, width=7) for col in columns]
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
        addImg = PhotoImage(data=ADD)
        delImg = PhotoImage(data=REMOVE)
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
        addImg = PhotoImage(data=ADD)
        delImg = PhotoImage(data=REMOVE)
        self.addRaidPopup = Toplevel(self.root, height=int(self.parent.winfo_height() / 2),
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
                dummyCombList['values'] = range(1, 8)
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
            self.raidComBoxWidgets['Span']['values'] = range(1, 2) if raidLevel == 'R5' else range(2, 8)
        elif raidLevel in ['R6', 'R60']:
            self.raidComBoxWidgets['PD\'s']['values'] = range(4, 33)
            self.raidComBoxWidgets['Span']['values'] = range(1, 2) if raidLevel == 'R6' else range(2, 8)
        elif raidLevel == 'JBOD':
            self.raidComBoxWidgets['PD\'s']['values'] = range(1, 241)
            for widgets in ['Span', 'Spare', 'Stripe', 'WP', 'RP', 'VD\'s', 'Init']:
                self.raidComBoxWidgets[widgets]['values'] = ['N/A'] if widgets not in ['Stripe','VD\'s','Span', 'Spare'] else [0]
                if widgets == 'Span':
                    self.raidComBoxWidgets[widgets]['values']= [1]
                self.raidComBoxWidgets[widgets]['state'] = 'disabled'
            self.raidComBoxWidgets['Size']['state'] = 'disabled'
        for widgets in ['PD\'s', 'Stripe', 'WP', 'RP', 'VD\'s', 'Span', 'Spare', 'DTAB', 'Init', 'Reps']:
            self.raidComBoxWidgets[widgets].current(0)


class tcDefaults(Toplevel):
    """Frame holds all Widgets that are needed to get the switch related info  """
    _pady = 5
    _RELIEF = GROOVE
    _BG = BG_SWITCH
    _font = ('Consolas', 12)

    def __init__(self, wmStack):
        """
        Initialize the switch GUI class
        :param parent: Frame handler of the frame where the switch gui needs to be placed
        :type parent: tk.Frame
        :param args: args required for the frame
        :type args: args
        :param kwargs:Keyword args required for the frame
        :type kwargs:Keyword args required for the frame
        """
        self.wmStack = wmStack
        Toplevel.__init__(self, width=750, height=450, bd=1, bg=tcDefaults._BG, highlightthickness=2,
                          relief=tcDefaults._RELIEF)
        self.grab_set()
        center(self)
        self.overrideredirect(True)
        self.grid_propagate(0)
        self.update_idletasks()
        _font_ = getFontSize(int(self.winfo_height() * .50), mul=6, bold=True)
        _font_ = getFontSize((self.winfo_height() * .98) * .10, mul=5, bold=True)
        self.width = self.winfo_width()
        self.height = self.winfo_height()
        self.plugFw = {'on': False}
        self.plugSnapDump = {'on': False}
        self.plugMe = {'on': False}
        self.plugOcr = {'on': False}
        self.plugPolicyChange = {'on': False}
        self.plugDcmd = {'on': False}
        self.durations = [StringVar(), StringVar()]
        self.bgOprate = StringVar()
        self.iteration = [StringVar(), StringVar()]
        self.delayType = [StringVar(), StringVar()]
        self.timeInterval = [StringVar(), StringVar()]
        self.intervalStep = [StringVar(), StringVar()]
        self.renderFlex()

    @property
    def _get(self):
        """returns all the flex widget values"""
        return {"duration": {"duration1": self.durations[0].get(), "duration2": self.durations[1].get(), },
                "iteration": {"iteration1": {'count': self.iteration[0].get(), 'type': self.delayType[0].get(),
                                             'interval': self.timeInterval[0].get(),
                                             'step': self.intervalStep[0].get()},
                              "iteration2": {'count': self.iteration[1].get(), 'type': self.delayType[1].get(),
                                             'interval': self.timeInterval[1].get(),
                                             'step': self.intervalStep[1].get()}},
                "bgops": {"rate": self.bgOprate.get()},
                "plugins": {"me": self.plugMe['on'], "snapdump": self.plugSnapDump['on'],
                            "fwdownload": self.plugFw['on'], "ocr": self.plugOcr['on'],
                            "policychange": self.plugPolicyChange['on'], "dcmd": self.plugDcmd['on']

                            }}

    def renderFlex(self):
        relief = FLAT
        _BG = BG_SWITCH
        hght = int(self.winfo_height())
        wdth = int(self.winfo_width())
        flexFrameList = []

        frm= createWindow(self, width=.99, height=.10, bg=_BG, rw=0, pdx=1,pdy=1, columnspan=2, cl=0)
        makeLabel(frm, text="Test Case Default Values", font=getFontSize(int(frm.winfo_height() * .99), 2, bold=True), row=0, column=0,columnspan=2,foreground=BRCMRED, pdx=1,pdy=1)
        flexFrameList.append(createWindow(self, width=.48, height=.53, bg=_BG, rw=1, cl=0))
        flexFrameList.append(createWindow(self, width=.48, height=.27, bg=_BG, rw=2, cl=0))
        flexFrameList.append(
            LabelFrame(self, text='Plugins'.title(), font=getFontSize(height=int(hght * .15), bold=True), bd=1,
                       relief=GROOVE, width=int(wdth * .48), height=int(hght * .78), bg=_BG, labelanchor=N,
                       foreground=BRCMRED))
        flexFrameList[2].grid(row=1, column=1, rowspan=2, padx=5, pady=5, sticky=N + E + W + S)
        flexFrameList[2].grid_propagate(0)
        flexFrameList[2].update()
        setGridConfigure(self, 2, 1)
        flexFrameList.append(createWindow(self, width=.99, height=.10, bg=_BG, columnspan=2, rw=3, cl=0))
        saveButton = PhotoImage(data=ADD)
        closeButton = PhotoImage(data=CLOSEBUTTON)
        self.save = Button(flexFrameList[3], image=saveButton, relief=FLAT, bg=_BG, command=self.saveTcDefaults)
        self.save.image = saveButton
        self.save.grid(row=0, column=0, padx=1, pady=1, sticky=N + E + W + S)
        setGridConfigure(flexFrameList[3], 0, 0)
        close = Button(flexFrameList[3], image=closeButton, bg=_BG, relief=FLAT, command=self.destroy)
        close.image = closeButton
        close.grid(row=0, column=1, padx=1, pady=1, sticky=N + E + W + S)
        setGridConfigure(flexFrameList[3], 0, 1)
        self.renderGeneric(frm=flexFrameList)
        self.renderPlugin(frm=flexFrameList)

    def renderGeneric(self, frm):
        relief = FLAT
        _bd = 1
        hght = int(frm[0].winfo_height())
        wdth = int(frm[0].winfo_width())
        durationFrame = createWindow(frm[1], relief=GROOVE, width=.45, height=.99, bg=BG_SWITCH, rw=0, cl=0)
        iTerationFrame = frm[0]
        _font_ = getFontSize(hght * .35, 10)
        makeLabel(durationFrame, text="duration 1".upper(), font=_font_, row=0, column=0, foreground=BRCMRED)
        makeLabel(durationFrame, text="duration 2".upper(), font=_font_, row=1, column=0, foreground=BRCMRED)
        makeLabel(durationFrame, text="bgops rate".upper(), font=_font_, row=2, column=0, foreground=BRCMRED)
        makeEntry(durationFrame, var=self.durations[0], font=_font_, row=0, column=1, width=15)
        makeEntry(durationFrame, var=self.durations[1], font=_font_, row=1, column=1, width=15)
        makeEntry(durationFrame, var=self.bgOprate, font=_font_, row=2, column=1, width=15)
        # --------------------------Iteration-----------------------------
        _ihght = hght / 4
        _iwdth = int(durationFrame.winfo_width() * .95)
        _iFont_ = getFontSize(height=hght * .05, mul=10)
        iFrameList = []
        widgtList = []
        for _ in range(0, 2):
            iFrameList.append(
                createWindow(iTerationFrame, relief=GROOVE, width=.48, height=.48, bg=BG_SWITCH, rw=_, cl=0))
            makeLabel(iFrameList[-1], text='ITERATION ' + str(_ + 1),
                      font=getFontSize(height=iTerationFrame.winfo_height() * .35, mul=10), row=0, column=0,
                      columnspan=4, foreground=BRCMRED, width=15)
            _font_ = getFontSize(height=iTerationFrame.winfo_height() * .30, mul=10)
            makeLabel(iFrameList[-1], text='ITER', font=_font_, row=1, column=0, width=7)
            makeLabel(iFrameList[-1], text='DELAY', font=_font_, row=1, column=1, width=7)
            makeLabel(iFrameList[-1], text='INTERVAL', font=_font_, row=1, column=2, width=7)
            makeLabel(iFrameList[-1], text='STEP', font=_font_, row=1, column=3, width=7)
            makeEntry(iFrameList[-1], var=self.iteration[_], font=_font_, row=2, column=0, width=5)
            widgtList.append(
                ttk.Combobox(iFrameList[-1], textvariable=self.delayType[_], font=_font_, state='readonly', width=5))
            widgtList[-1]['values'] = ['FIXED', 'INC', 'DEC', 'RAND']
            widgtList[-1].grid(row=2, column=1, padx=5, pady=5, sticky=N + E + W + S)
            setGridConfigure(iFrameList[-1], 2, 1)
            widgtList[-1].unbind_class("TCombobox", "<MouseWheel>")
            makeEntry(iFrameList[-1], var=self.timeInterval[_], font=_font_, row=2, column=2, width=5)
            makeEntry(iFrameList[-1], var=self.intervalStep[_], font=_font_, row=2, column=3, width=5)

    def renderPlugin(self, frm):
        # -------------------------------------------Plugins----------------
        relief = FLAT
        pluginFrame = frm[2]
        _plHght_ = pluginFrame.winfo_height()
        _plwdth_ = pluginFrame.winfo_width()
        plFrameList = {}
        self.plugin = ['medium error', 'fw download', 'snapdump', 'policy change', 'ocr', 'dcmd']
        _feFont_ = getFontSize(height=int(_plHght_ * .60), bold=False)

        for index, feature in enumerate(self.plugin):
            plFrameList.update({feature: {
                'frm': Frame(pluginFrame, bd=1, relief=FLAT, width=int(_plwdth_ * .99), height=int(_plHght_ * .99) / 6, bg=BG_SWITCH)}})
            plFrameList[feature]['frm'].grid(row=index, column=0, padx=1, pady=1,
                                             sticky=N + E + W + S)
            plFrameList[feature]['frm'].grid_propagate(0)
            plFrameList[feature]['frm'].update()
            setGridConfigure(pluginFrame, index, 0)
        self.renderOnOff(_frame=plFrameList['medium error'], wdgthhandler=self.plugMe, typ='ME')
        self.renderOnOff(_frame=plFrameList['fw download'], wdgthhandler=self.plugFw, typ='Firmware Up Down')
        self.renderOnOff(_frame=plFrameList['snapdump'], wdgthhandler=self.plugSnapDump, typ='snapdump')
        self.renderOnOff(_frame=plFrameList['policy change'], wdgthhandler=self.plugPolicyChange,typ='Write policy')
        self.renderOnOff(_frame=plFrameList['ocr'], wdgthhandler=self.plugOcr, typ='ocr')
        self.renderOnOff(_frame=plFrameList['dcmd'], wdgthhandler=self.plugDcmd,typ='dcmd')

    def renderOnOff(self, _frame, wdgthhandler, typ=''):
        """Renders Plugin widgets"""
        onImg = PhotoImage(data=SWITCHON)
        offImg = PhotoImage(data=SWITCHOFF)
        _fwHght = _frame['frm'].winfo_height() * .98
        _fFont_ = getFontSize(height=int(_fwHght * .75), mul=5,bold=False)
        makeLabel(_frame['frm'], text=typ.upper(), font=_fFont_, row=0, column=0,width=7)
        wdgthhandler['button'] = Button(_frame['frm'], image=offImg, bd=0, bg=BG_SWITCH,
                                        command=lambda: buttonToggle(wdgthhandler))
        wdgthhandler['button'].image = offImg
        wdgthhandler['button'].grid(row=0, column=1, padx=5, pady=5)
        setGridConfigure(_frame['frm'], 0, 1)

    def saveTcDefaults(self):
        self.wmStack.master_test_case['tcdefault'] = self._get
        self.destroy()
        self.wmStack.invoke_savejson_calls()


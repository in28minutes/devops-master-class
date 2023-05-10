# -*- coding: utf-8 -*-
###############################################################################
#                                                                             #
#  Copyright (C) 2021-2023 Broadcom Limited.  All rights reserved.            #
#                                                                             #
###############################################################################

'''
DATE(M/D/Y)  CQID            WHO(CQUser)   DESCRIPTION
===============================================================
03/16/2023   DCSG01431413    nmartis       Wingman 3.0: Add Init module in Wingman Flex
03/24/2023   DCSG01431420    nmartis       Wingman 3.0: Add Config Creation Logic  in Wingman Flex
03/24/2023   DCSG01459382    nmartis       Add Support Modify the Default RAID Parameters on RAID Selection
04/03/2023   DCSG01430859    nr888483      Add support for Foreign config module (Initial Version)
05/03/2023   DCSG01430860    nr888483      Add support for Pinned cache module (Initial Version)
04/06/2023   DCSG01430866    rvats         Wingman 3.0: Add backend support for Medusa IO tool in Wingman flex.
04/06/2023   DCSG01431481    rvats         Wingman 3.0: Add backend support for IO monitoring (Chaos/Medusa) in Wingman
                                           flex.
04/06/2023   DCSG01430869    rvats         Wingman 3.0: Add backend support for COL dip (single/double/multiple)
                                           modules in flex.
04/20/2023   DCSG01431392    saprabhu      Wingman 3.0: Add support for Firmware update module in Wingman Flex
04/24/2023   DCSG01431537    asuman        WM Flex 3.0 : (Backend) : Implement OCR and System Reboot test step support
                                           and controller status check
04/27/2023   DCSG01431655    saprabhu      Wingman 3.0: Add support for controller level BGOP module and handle wait
                                           till all type of bgop completes in Wingman Flex
04/30/2023   DCSG01431531    asuman        WM Flex 3.0 : (Backend) : Implement Snapdump test step processing

05/04/23    DCSG01451129     nmartis       Add Support for teardown options and test JSON queuer in ConfigGUI
05/04/23    DCSG01431504     nmartis       WM Flex 3.0 : (Backend) : Add and Delete Config , Initialization During Creation and other generic updates

'''

import ast
import copy
import json
import ntpath
import os
import random
import zipfile
import re

import sal
import shutil
import subprocess
import sys
import threading
import time
from pprint import pformat
from sal import *
from sal import mr_events8
from sal.apc import APC
from sal.automation_server import AutomationSend
from sal.common import Size
from sal.io_tools.medusa import Maim
from sal.mr_events import *
from sal.mr_names import DCP_WB, DCP_WT, DCP_RA, DCP_NRA, DCP_ARA
from sal.mradapter import MRAdapter
from sal.sl8 import getMR8ColInfo
from sal.storelib import Discard_PinnedCache_all_Lds
from sal.testscript import *
from sal.apc import APC
from zipfile import ZipFile
from sal.avengersalevents import MR_EVT_CFG_CLEARED, MR8_EVT_LD_DELETED, MR8_EVT_PD_STATE_CHANGE_UPDATED, \
    MR_EVT_LD_CC_DONE, MR_EVT_LD_CC_DONE_INCON

BANNER_WIDTH = 80
BUILD = 'Wingman Flex 3.0 Automation '
LOOPDEBUG = True
IODEBUG = True
MORPHDEBUG = True
COLDEBUG = False
PDALLOCDEBUG = True
ADDCONFIGDEBUG = True


def get_snapdump_dir():
    """
    Gets snapdump directory for the snapdump extraction and validation
    """
    snapdump_dir = os.path.join(os.path.join(os.getcwd()), 'snapdump_wingman_dir')
    if not os.path.exists(snapdump_dir):
        os.mkdir(snapdump_dir)
    return snapdump_dir

class Reset:
    """
    This class handles all the resets possible for achieving a Test case.
    Initializes itself with the backend instance and handles the required execution.
    Currently, the class handles OCR and Reboot

    1. issue_ocr
    2. issue_reboot

    TODO
    3. issue_system_powercycle
    4. issue_enclsoure_powercycle
    """
    def __init__(self, wm):
        """
        Taking the main class instance to activate this class
        """
        self.wm = wm
        self.mr = wm.mr
        self.log = wm.log
        self.def_ocr_val = self.mr.cli.ocr_get()

    def get_vd_details(self):
        """
        Get the VD details of all VDs created
        """
        vd_details = self.mr.get_all_vds()
        return vd_details

    def get_pd_details(self):
        """
        Get the PD details of all pds present
        """
        pd_details = self.mr.get_all_pds()
        return pd_details

    def get_ctrl_details(self):
        """
        Get all controller details to take before and after the operation status.
        """
        ctrl_details = self.mr.get_ctrl_property()
        return ctrl_details

    def check_for_changes(self, pre_reset_val, post_reset_val):
        """
        Compares the below and after values on controller. Report values that are safe to changes and also which
        are not. Raises SALError when certain changes that happened are not OK.
        """
        self.log.info("Total properties to compare : {}".format(len(pre_reset_val)))
        matched = {}
        changed = {
            "b4": {},
            "after": {}
        }
        change_ok = ['temperatureROC', 'temperatureCtrl']
        change_not_ok = []

        for k, v in pre_reset_val.iteritems():
            if post_reset_val.get(k) == v:
               matched[k] = v
            else:
                changed["b4"][k] = v
                changed["after"][k] = post_reset_val.get(k)

        self.log.debug("Changed : {}".format(changed))

        if changed:
            self.log.info(" >>> Below Values (if any) changed but are safe to proceed")
            for k, v in changed["b4"].iteritems():
                if k in change_ok:
                    # Few values are okay to ignore:
                    self.log.info(" >>> KEY {} : BEFORE : {}\tAFTER : {}".format(str(k).upper(),
                                                                                str(v).ljust(20),
                                                                                str(changed["after"].get(k)).ljust(20)))
                else:
                    change_not_ok.append(k)

        if change_not_ok:
            raise SALError(">>> FEW VALUES CHANGED that were not expected to change : {}".format(change_not_ok))
        else:
            self.log.info(">>> All Values expected to remain same, remained same. Proceeding")
            return True

    def issue_ocr(self):
        """
        This is an aggregate function that calls various functions to execute an OCR with complete context.
        1. Register AEN
        2. Take pre-OCR value
        3. Issue OCR
        4. Check for OCR AEN and report accordingly
        5. If #4, take post-OCR value
        6. Compare and evaluate the changes and report
        """
        self.log.info("Issuing RESET : Type OCR")

        # Register OCR AEN
        ocr_evt = self.mr.wait_for_event(event_id=avengersalevents.MR_EVT_CTRL_HOST_DRIVER_LOADED,
                                         time_out='600',
                                         background=True)
        self.log.info("Issuing RESET : Registered AEN")

        # Get before value for CTRl, PD, VD
        b4_val = self.get_ctrl_details()
        self.log.info("Issuing RESET : Got pre OCR values")

        # Issue OCR
        self.log.info("Issuing RESET : Issuing OCR")
        self.mr.ocr_start()
        self.log.info("Issuing RESET : OCR done")

        # Check if OCR done evt is found
        if self.check_ocr_event(ocr_evt):
            # Get after value for CTRl, PD, VD
            after_val = self.get_ctrl_details()
            self.log.info("Issuing RESET : Got post OCR values")

            # Compare
            self.log.info("Issuing RESET : Checking changes")
            if self.check_for_changes(b4_val, after_val):
                self.log.info("Issuing RESET : OCR complete, proceeding")

    def check_ocr_event(self, evt):
        """
        Check for OCR event and notify as per event availability
        """
        retry = 0
        while retry < 20:
            if self.mr.all_events_found(evt):
                self.log.info("OCR event found proceeding, waiting for some time for processes to restore")
                time.sleep(200-(retry*10))
                retry = 0
                return True
            else:
                retry += 1
                if retry % 4 == 0:
                    self.log.info("Waiting for Driver load event.")
                time.sleep(10)
        if not retry:
            raise SALError(">>> Driver load event was not found post OCR. (MR_EVT_CTRL_HOST_DRIVER_LOADED)")

    def issue_reboot(self, dict):
        """
        Same as issue_ocr, this is an aggregated step for REBOOT functionality.
        """
        # Get before value for CTRl, PD, VD
        self.log.info("Issuing RESET : Type REBOOT")
        if not self.wm.sysResume:
            self.log.info("Issuing RESET : Getting pre Reboot values")
            self.wm.pre_reset_val = self.get_ctrl_details()

        # Issue reboot
        self.log.info("Issuing RESET : Issuing Reboot")
        self.wm.sysReboot(dict)

        self.log.info("Issuing RESET : Getting post Reboot values")
        post_reset_val = self.get_ctrl_details()

        # Compare
        self.log.info("Issuing RESET : Checking changes")
        if self.check_for_changes(self.wm.pre_reset_val, post_reset_val):
            self.log.info("Issuing RESET : Reboot complete, proceeding")


class wingmanFlex(TestScript):
    ''' Flex (backend) Code which interacts with user generated JSON Interpreter'''

    REQ_ARGS = [arg('--configFileJson', dest='configFileJson', type='str', help='configfile path that needs'
                                                                                ' to be used for the json')
        , arg('--testCaseJson', dest='tcJson', type='str', help='test case json path')]

    def advance_step(self, step=None, desc='', logit=False):
        '''

        Overriding testscript class function to stop testscript from print step banner and doc string in to logs.
        This way the Flex Logs will be only print the step number from JSON instead of SAL Level
        Updates the current step number and prints it in the log as well.
        If step is not provided, the value is incremented by one.
        If step is provided, it must be an integer.
        If desc is provided it will be logged.
        '''
        if step is None:
            if self.step is None:
                self.step = 1
            else:
                self.step += 1
        else:
            self.step = step
        if logit:
            lines = desc.split('\n')
            self.log.info('=== Starting step %2d: %s %s', self.step, desc,
                          '=' * ((119 if len(lines) > 1 else 75) - len(lines[-1])))

    def init(self):
        ''' Reads Config File and Creates Controller Instance '''
        configFileName = os.path.join(os.getcwd(), os.path.basename(self.args.configFileJson))
        self.waitForFileInPath(filePath=configFileName)
        configFile = self.readJsonFile(path=configFileName)
        self.setupInfo = configFile['legacy']
        self.flexInfo = configFile['flexmode']
        self.ctrl = self.setupInfo['ctrlindex']
        self.isWindows = True if sys.platform.startswith('win') else False
        self.setCtrlIndex()
        self.mr = sal.mradapter.create_mradapter(self.ctrl, test_script=self, rate_change=False, fail_on_ocr=False)
        self.init_child_classes()

    def init_child_classes(self):
        """
        If there are modules that use class for implementing and handling the functionalities withing the class
        itself, the object can be created here.

        If module needs to reboot / powercycle the machine, kindly add the object in get_wm_state() local list
        supporting_class_obj so that the class object can be removed.
        """
        self.reset_obj = Reset(self)
        self.sd_obj = Snapdump(self)

    def teardown(self):
        '''

        '''
        self.log.debug('cq_testcase_id---->%s' % self.tcId)
        resultStr = ('Wingman 3.0 Test Case %s :: %s' % (self.tcId, 'PASSED' if self._passed else 'FAILED')).center(
            BANNER_WIDTH)
        # self.log.debug(resultStr)
        self.debuggerText(text=resultStr)
        self.bgop_cleanup()
        self.io_cleanup()
        if not self._passed:
            self.dumpCtrlInfo()
            # code enable teardown
            # code snapdump
            # morphedJSon
            # powersequence all ports including quarch
        self.mr.restore_pretest(pretest=self.pretest_info)

    def get_wm_state(self):
        """
        The method should have been handled in __reduce__ or __getstate__ as well. But
        that over-rides the super class methods and leads to missing attributes. Hence, wrote
        method that needs to be called before all save_state() call.
        If a new class has been written, the object name must be mentioned in the list as below.
        supporting_class_obj
        This class instance is not pickleable. So the class objects are deleted before pickle.
        """
        supporting_class_obj = ["reset_obj", "sd_obj"]
        for obj in supporting_class_obj:
            if hasattr(self, obj):
                del self.__dict__[obj]

    def waitForFileInPath(self, filePath, retry=10):
        '''
        Waits for File to be found in filepath and retires with 1 sec delay

        Added to wait until TC_start Copies the File to Log Folder after Queuing the JSON.
        Since Queuing JSON with customized configFile fileName needs to supported we need to read config from
        the test directory in case user edits the configfile in org path to queue a different JSON.
        Same Check will added in confiFileGUI which will stop user from editing until file is copied to test log folder.
        '''
        while retry > 0:
            if os.path.exists(filePath):
                break
            self.log.debug('Wait for TC_Start.py File %s To Copied To Folder %s ' % (
                os.path.basename(filePath), os.path.dirname(filePath)))
            time.sleep(1)
            retry -= 1
        else:
            raise SALError(
                'Unable to Find File %s in Folder %s ' % (os.path.basename(filePath), os.path.dirname(filePath)))

    def debuggerText(self, text):
        try:
            from sal.mpt.errors import IoctlError, IoctlTimeoutError
            cmd_string = 'iop uart echo \'\n\n%s\n%s\n%s\n\'' % ('.' * BANNER_WIDTH, text, '.' * BANNER_WIDTH)
            for retry in range(10):
                self.log.debug("Attempt %d: Passing '%s' to MegaMon" % (retry + 1, cmd_string))
                try:
                    return self.mr.hba.cli_command(cmd_string, bufsize=4096, timeout=10)
                except IoctlTimeoutError:
                    pass
                continue
            else:
                self.log.debug("megamon_cmd failed")
                raise ("megamon_cmd failed")
        except Exception as e:
            self.log.info('Unable to send String to UART : %s' % e)

    def readJsonFile(self, path, copyToLogFolder=False):
        '''
            Reads the config file and returns the content. If no config file is present then a popup will shown to the user
            :return: Contents of the config_file.json
            :rtype: dict or list of dict
        '''
        if os.path.isfile(path):
            if copyToLogFolder:
                try:
                    shutil.copyfile(path, os.path.join(os.getcwd(), ntpath.basename(path)))
                except:
                    pass
            with open(path) as data_file:
                self.log.debug('*' * BANNER_WIDTH)
                self.log.debug(('JSON File : %s ' % path).center(BANNER_WIDTH))
                self.log.debug('*' * BANNER_WIDTH)
                fileContents = json.load(data_file)
                self.log.debug((pformat(fileContents)).center(BANNER_WIDTH))
                self.log.debug('-' * BANNER_WIDTH)
                return fileContents
        else:
            raise SALError(' File : %s doesnt Exist' % path)

    def printBanner(self):
        '''
          Prints the Banner with the Suite Version set in Util.py in the test logs
        '''
        self.log.info('')
        self.log.info('*' * BANNER_WIDTH)
        self.log.info(('Welcome to the %s. ' % BUILD).center(BANNER_WIDTH))
        self.log.info('Copyright 2023-2025 Broadcom Inc.  All rights reserved.'.center(BANNER_WIDTH))
        self.log.info('*' * BANNER_WIDTH)
        self.log.info('')

    def setCtrlIndex(self):
        '''
            Sync CTRL index from Storcli to Storelib
        '''
        debug = False
        if self.ctrl == "":
            raise SALError('Ctrl Index Not Set in the Config File')
        if self.isWindows:
            # Avenger_Change -- updating storecli2
            storcli_data = ast.literal_eval(
                subprocess.check_output('c:\windows\storcli2 /c' + str(self.ctrl) + ' show  j', shell=True))
        else:
            storcli_data = ast.literal_eval(
                subprocess.check_output('/usr/local/bin/storcli2  /c' + str(self.ctrl) + ' show  j', shell=True))
        if 'Controller 0 not found' in storcli_data:
            if self.isWindows:
                storcli_data = ast.literal_eval(
                    subprocess.check_output('c:\windows\perccli2 /c' + str(cont_id) + ' show  j', shell=True))
            else:
                storcli_data = ast.literal_eval(
                    subprocess.check_output('/usr/local/bin/perccli2  /c' + str(cont_id) + ' show  j', shell=True))
        if debug:
            self.log.debug(' CLI Data  %s ' % pformat(storcli_data, indent=4))
            self.log.debug(' CLI PCI  %s ' % str(
                int(storcli_data['Controllers'][-1]['Response Data']['PCI Address'].split(':')[1], 16)))
            self.log.debug(
                ' -------- system adapter list : %s ----------' % pformat(sal.system.Adapter.list(), indent=4))
            [self.log.debug(' PCE - %s' % str(ctrl).split(',')[0].split('(')[-1]) for ctrl in
             sal.system.Adapter.list(filter=lambda x: isinstance(x, MRAdapter))]
        for ctrl in sal.system.Adapter.list(filter=lambda x: isinstance(x, MRAdapter)):
            self.log.debug(' --index-- : %s  ' % ctrl.ctrl_id)
            self.log.debug(' --ctrl-- : %s  ' % ctrl)
            if int(str(ctrl).split(',')[0].split('(')[-1]) == int(
                    storcli_data['Controllers'][-1]['Response Data']['PCI Address'].split(':')[1], 16):
                self.log.debug('------- matched Index : %s --------' % ctrl.ctrl_id)
                self.ctrl = ctrl.ctrl_id
                break

    def dumpCtrlInfo(self, j=False):
        '''Dumps Storclli Cx show all j to the logs before start of the test and End of the if the test fails'''
        ctrlInfo = self.mr.cli.storcli_cmd('show all' + (' j' if j else ''))
        if j:
            try:
                ctrlInfo = json.loads(ctrlInfo.lower())
                if ctrlInfo['controllers'][0]['command status']['status'] != 'success':
                    raise SALError('Unable to Fetch Controller Info : %s' % ctrlInfo)
            except:
                raise SALError('Unable to Fetch Controller Info : %s' % ctrlInfo)
            return ctrlInfo['controllers'][0]['response data']
        else:
            self.log.debug(' ')
            self.log.debug('.' * BANNER_WIDTH)
            self.log.debug(ctrlInfo)
            self.log.debug('.' * BANNER_WIDTH)
            self.log.debug(' ')

    def setupController(self):
        '''
             Gathers Controller Information and Stores it in self.ctrlInfo for Further Processing.
             self.ctrlInfo will have controller info before the start of the test.
        '''
        if not self.sysResume:
            if not self.mr.is_avenger():
                raise SALError('wingman flex is supported only avenger1 controller'.title())
            self.dumpCtrlInfo()
            ctrlInfo = self.dumpCtrlInfo(j=True)
            _ctrlSupport_ = ctrlInfo['max. supported config']
            self.ctrlInfo = {}
            self.ctrlPdMap = {}
            self.ctrlDtabPdMap = {}
            self.ctrlVdMap = {}
            self.ctrlInfo.update(
                {'maxVds': _ctrlSupport_['max number of vds'], 'maxPds': _ctrlSupport_['max number of physical drives'],
                 'maxSasPds': _ctrlSupport_['max sas/sata drives'], 'maxNvmePds': _ctrlSupport_['max nvme drives'],
                 'maxSlices': _ctrlSupport_['max vds per array'], 'maxSpans': _ctrlSupport_['max spans per vd'],
                 'maxJbod': _ctrlSupport_['max jbods'], 'maxPdPerArray': _ctrlSupport_['max pd per array'],
                 'maxQd': _ctrlSupport_['max parallel commands'], 'currentVds': len(self.mr.get_vds())})
            _capabilities_ = ctrlInfo['capabilities']
            self.ctrlInfo.update({'interfaceSupport': _capabilities_['supported drive interfaces'].split(' '),
                                  'raidLevelSupport': [_.strip()[4:] for _ in
                                                       _capabilities_['supported raid levels'].split(',')],
                                  'mixSasSata': True if _capabilities_[
                                                            'mix of sas-hdd/sata-hdd in vd'] == 'allowed' else False,
                                  'mixSsdHdd': True if _capabilities_['mix of ssd/hdd in vd'] == 'allowed' else False,
                                  'mixPrpSgl': True if _capabilities_['mix of nvme sgl and prp in a vd'] else False})
            cliEncl = self.mr.cli.enclosure_list() + [252]
            self.enclosure_list = [int(enc) for enc in
                                   (cliEncl if self.setupInfo['encl_list'] == [] else self.setupInfo['encl_list'])]
            self.log.info('.' * BANNER_WIDTH)
            self.log.info(
                (('enclosure ids to be used for this test :: %s' % self.enclosure_list).title()).center(BANNER_WIDTH))
            self.log.info('.' * BANNER_WIDTH)
            if [encl for encl in self.enclosure_list if encl not in cliEncl]:
                self.log.info((" ***** Enclosure connected to the controller  %s***** " % cliEncl).center(BANNER_WIDTH))
                raise SALError(
                    "Enclosure %s not connected to the controller. Please Update the Config file and Rerun" % [encl for
                                                                                                               encl in
                                                                                                               self.enclosure_list
                                                                                                               if
                                                                                                               encl not in cliEncl])
            if self.setupInfo['quarch_ip']:
                self.mr.dtab_setup(self.setupInfo['quarch_ip'])
                self.all_dtab_list = copy.deepcopy(self.mr.all_dtab_list)
                self.all_dtab_pds = [pd.cli for pd in self.mr.all_dtab_pds]
            else:
                self.mr.all_dtab_list = []
                self.mr.all_dtab_pds = []
                self.all_dtab_list = []
                self.all_dtab_pds = []
        else:
            self.mr.all_dtab_list = self.all_dtab_list
            self.mr.all_dtab_pds = [pd for pd in self.mr.get_all_pds() if pd.cli in self.all_dtab_pds]
            ctrlInfo = self.dumpCtrlInfo(j=True)
        _epack_ = ctrlInfo['energy pack info'][0] if not self.mr.is_evp() else None
        self.ctrlInfo.update(
            {'bbutype': _epack_['type'] if _epack_ else None, 'status': _epack_['status'] if _epack_ else None})
        [self.ctrlDtabPdMap.update({pd.cli: {'pdId': pd.id, 'pdObj': pd, 'dtabPort': self.mr.all_dtab_list[_]}}) for
         _, pd in enumerate(self.mr.all_dtab_pds)]
        [self.ctrlPdMap.update({pd.cli: {'pdId': pd.id, 'pdObj': pd, 'dtabPort': None}}) for pd in self.mr.get_all_pds()
         if pd not in self.mr.all_dtab_pds]
        self.log.debug(' ')
        self.log.debug('.' * BANNER_WIDTH)
        self.log.debug('Controller Setup'.center(BANNER_WIDTH))
        self.log.debug('.' * BANNER_WIDTH)
        self.log.debug(' ')
        self.log.debug('Controller Capabilities'.center(BANNER_WIDTH))
        self.log.debug('%s' % pformat(self.ctrlInfo, indent=4))
        self.log.debug(' ')
        self.log.debug('Controller PD Map'.center(BANNER_WIDTH))
        self.log.debug('%s' % pformat(self.ctrlPdMap, indent=4))
        self.log.debug(' ')
        self.log.debug('Controller Dtab PD Map'.center(BANNER_WIDTH))
        self.log.debug('%s' % pformat(self.ctrlDtabPdMap, indent=4))
        self.log.debug(' ')
        self.log.debug('.' * BANNER_WIDTH)
        self.log.debug(' ')

    def morphJson(self):
        ''' Merge JSON with Config File'''
        self.morphedSteps = []
        self.graspStepList = []  # Store Steps in this format [[<Config Steps Pre Delete>] , delete_step,[<config_step Post Delete>], ....]
        tempStepDict = {}
        self.log.debug('.' * BANNER_WIDTH)
        self.log.debug('MORPH JSON'.center(BANNER_WIDTH))
        self.log.debug('.' * BANNER_WIDTH)
        morpValues = {'duration1': self.tcDefaults['duration']['duration1'],
                      'duration2': self.tcDefaults['duration']['duration2'],
                      'iteration1': self.tcDefaults['iteration']['iteration1'],
                      'iteration2': self.tcDefaults['iteration']['iteration2'], 'flexraid': {}, 'ioparam': {}}
        if self.flexInfo['mode']:
            if self.flexInfo['duration']['duration1'] != '':
                morpValues.update({'duration1': self.flexInfo['duration']['duration1']})
            if self.flexInfo['duration']['duration2'] != '':
                morpValues.update({'duration2': self.flexInfo['duration']['duration2']})
            if self.flexInfo['iteration']['iteration1'] != {}:
                morpValues.update({'iteration1': self.flexInfo['iteration']['iteration1']})
            if self.flexInfo['iteration']['iteration2'] != {}:
                morpValues.update({'iteration2': self.flexInfo['iteration']['iteration2']})
            if self.flexInfo['io'] != {}:
                morpValues.update({"ioparam": self.flexInfo['io']})
            if self.flexInfo['raidlevel']['config'] != []:
                morpValues.update({'flexraid': self.flexInfo['raidlevel']})
        self.log.debug('Morp With Below Values '.center(BANNER_WIDTH))
        self.log.debug('%s' % pformat(morpValues, indent=4))
        self.log.debug('.' * BANNER_WIDTH)
        for st in self.tcSteps:
            step = copy.deepcopy(st)
            if MORPHDEBUG:
                self.log.debug(' ')
                self.log.debug('_' * BANNER_WIDTH)
                self.log.debug('STEP'.center(BANNER_WIDTH))
                self.log.debug('_' * BANNER_WIDTH)
                self.log.debug('%s' % pformat(step, indent=4))
                self.log.debug('_' * BANNER_WIDTH)
            step['processed'] = False
            if step['type'] == 'flexconfig':
                if morpValues['flexraid']:
                    step.update({'config': morpValues['flexraid']['config']})
                    step.update({'exhaust': morpValues['flexraid']['exhaust']})
            if morpValues['ioparam'] and step['type'] == 'io':
                [step.update({ioKey: ioValue}) for ioKey, ioValue in morpValues['ioparam'].iteritems() if ioValue != '']
            dummy = copy.deepcopy(step)
            [step.update({key: morpValues[item]}) for key, item in dummy.iteritems() if item in morpValues.keys()]
            if MORPHDEBUG:
                self.log.debug(' ')
                self.log.debug('_' * BANNER_WIDTH)
                self.log.debug('MORPHED STEP'.center(BANNER_WIDTH))
                self.log.debug('_' * BANNER_WIDTH)
                self.log.debug('%s' % pformat(step, indent=4))
                self.log.debug('_' * BANNER_WIDTH)
                if step['type'] == 'delete':
                    if tempStepDict:
                        self.graspStepList.append([copy.deepcopy(tempStepDict)])
                        self.graspStepList.append({step['step']: step})
                        tempStepDict = {}
                else:
                    tempStepDict.update({step['step']: step})
            self.morphedSteps.append(step)
        if tempStepDict:
            self.graspStepList.append([copy.deepcopy(tempStepDict)])
        self.log.debug((' morphedsteps : %s ' % pformat(self.morphedSteps, indent=4)).center(BANNER_WIDTH))
        self.log.debug('*' * BANNER_WIDTH)
        self.log.debug('LearnStep'.center(BANNER_WIDTH))
        self.log.debug('*' * BANNER_WIDTH)
        self.log.debug(pformat(self.graspStepList))
        self.log.debug('*' * BANNER_WIDTH)
        self.createDecodePdMap()
        self.pdAllocator()

    def createDecodePdMap(self):
        # PDSorting
        dtabDrive = []
        nDtabDrive = []
        [(dtabDrive.append(pd) if pd in self.mr.all_dtab_pds else nDtabDrive.append(pd)) for pd in self.mr.get_all_pds()
         if int(pd.cli.split(":")[
                    0]) in self.enclosure_list and not pd.is_foreign and pd.state.lower() == 'unconfigured_good']
        if PDALLOCDEBUG:
            self.log.debug('nonDtabDrives : %s' % pformat(nDtabDrive, indent=4))
            self.log.debug('DtabDrives : %s' % pformat(dtabDrive, indent=4))
        self.decodePdMap = {'ssd': {'sas': {512: {'dtab': [], 'ndtab': [], 'useddtab': [], 'usedndtab': []},
                                            4096: {'dtab': [], 'ndtab': [], 'useddtab': [], 'usedndtab': []}},
                                    'sata': {512: {'dtab': [], 'ndtab': [], 'useddtab': [], 'usedndtab': []},
                                             4096: {'dtab': [], 'ndtab': [], 'useddtab': [], 'usedndtab': []}},
                                    'nvme': {512: {'dtab': [], 'ndtab': [], 'useddtab': [], 'usedndtab': []},
                                             4096: {'dtab': [], 'ndtab': [], 'useddtab': [], 'usedndtab': []}}},
                            'hdd': {'sas': {512: {'dtab': [], 'ndtab': [], 'useddtab': [], 'usedndtab': []},
                                            4096: {'dtab': [], 'ndtab': [], 'useddtab': [], 'usedndtab': []}},
                                    'sata': {512: {'dtab': [], 'ndtab': [], 'useddtab': [], 'usedndtab': []},
                                             4096: {'dtab': [], 'ndtab': [], 'useddtab': [], 'usedndtab': []}}}}
        [self.decodePdMap[pd.media_type][pd.get_interface_type()][pd.physical_block_size]['dtab'].append(pd.cli) for pd
         in dtabDrive]
        [self.decodePdMap[pd.media_type][pd.get_interface_type()][pd.physical_block_size]['ndtab'].append(pd.cli) for pd
         in nDtabDrive]
        self.log.debug(pformat(self.decodePdMap, indent=4))

    def updateDecodePdMap(self, pdList, remove=True):
        """"""
        if PDALLOCDEBUG:
            self.log.debug('updateDecodePdMap'.center(BANNER_WIDTH))
            self.log.debug(pformat(pdList, indent=4))
        for mediaType, attrib in self.decodePdMap.iteritems():
            for interfaceType, attrib1 in attrib.iteritems():
                for sectorSize, attrib2 in attrib1.iteritems():
                    _tmp = copy.deepcopy(pdList)
                    dtabKey1 = 'dtab' if remove else 'useddtab'
                    ndtabKey1 = 'ndtab' if remove else 'usedndtab'
                    dtabkey2 = 'useddtab' if remove else 'dtab'
                    ndtabkey2 = 'usedndtab' if remove else 'ndtab'
                    for pd in _tmp:
                        if pd in attrib2[dtabKey1]:
                            self.decodePdMap[mediaType][interfaceType][sectorSize][dtabKey1].remove(pd)
                            self.decodePdMap[mediaType][interfaceType][sectorSize][dtabkey2].append(pd)
                            pdList.remove(pd)
                        elif pd in attrib2[ndtabKey1]:
                            self.decodePdMap[mediaType][interfaceType][sectorSize][ndtabKey1].remove(pd)
                            self.decodePdMap[mediaType][interfaceType][sectorSize][ndtabkey2].append(pd)
                            pdList.remove(pd)
                        if pd in attrib2[dtabKey1] + attrib2[ndtabKey1]:
                            if PDALLOCDEBUG:
                                self.log.debug('-' * BANNER_WIDTH)
                                self.log.debug('Found the Pd MAP to Update'.center(BANNER_WIDTH))
                                self.log.debug(('MediaType %s' % mediaType).center(BANNER_WIDTH))
                                self.log.debug(('InterFaceType %s' % interfaceType).center(BANNER_WIDTH))
                                self.log.debug(('Sector Size %s' % sectorSize).center(BANNER_WIDTH))
                                self.log.debug('Updated PD List'.center(BANNER_WIDTH))
                                self.log.debug(pformat(attrib2, indent=4))
                                self.log.debug('-' * BANNER_WIDTH)
        if pdList:
            self.log.debug(pformat(pdList, indent=4))
            raise SALError('Update Decode PD Map Failed')

    def pdAllocator(self):
        '''Allocates PDS to the Config Steps'''
        self.stepPDdist = {}
        staticStepList = []
        flexStepList = []
        for seqList in self.graspStepList:
            if isinstance(seqList, list):
                [(staticStepList.append(step) if step['type'] == 'staticconfig' else flexStepList.append(step)) for step
                 in seqList[0].values() if step['type'] in ['staticconfig', 'flexconfig']]
                if PDALLOCDEBUG:
                    self.log.debug('-' * BANNER_WIDTH)
                    self.log.debug('Static Step List'.center(BANNER_WIDTH))
                    self.log.debug('-' * BANNER_WIDTH)
                    self.log.debug('%s' % pformat(staticStepList, indent=4))
                    self.log.debug('-' * BANNER_WIDTH)
                    self.log.debug('Flex Step List'.center(BANNER_WIDTH))
                    self.log.debug('-' * BANNER_WIDTH)
                    self.log.debug('%s' % pformat(flexStepList, indent=4))
                    self.log.debug('-' * BANNER_WIDTH)
                staticStepList = self.sortPdRequest(staticStepList, seqList)
                flexStepList = self.sortPdRequest(flexStepList, seqList)
                [self.stepPDdist.update({step['step']: self.getStepPdList(step)}) for step in staticStepList]
                # ADD Code to Repeat untilExhaust
                [self.stepPDdist.update({step['step']: self.getStepPdList(step)}) for step in flexStepList]
                self.log.debug('-' * BANNER_WIDTH)
                self.log.debug('PD\'s Distrubited to Step'.center(BANNER_WIDTH))
                self.log.debug('-' * BANNER_WIDTH)
                self.log.debug(pformat(self.stepPDdist, indent=4))
                self.log.debug('-' * BANNER_WIDTH)
            else:
                # DeleteCase Add Code Add the PD Back to Pool from reservation for Delete VD's
                # TwoCase ClearConfig or JBOD to UG and Ignore if 'pattern' !=all
                pass

    def sortPdRequest(self, configStepList, seqList):
        '''Sorts the Requirement List to Highest 1st Order
        configsteplist : Config Steps from the Seq
        seqList : Entire Sequence of steps until delete step
        addcode to check  to reservedPD in Seqlist and Include Same in the request,
        Since SeqList is used Check How to Handle Post delete Step if Any reservedPd is required post delete step or not.'''
        '''sortedList = []
        pdCountMap = {}
        if len(configStepList)==1:
            return configStepList
        for index , cfg in enumerate(configStepList):
            pdCount = (int(cfg[0]['pdcount']) * ((int(cfg[0]['spans']) + int(cfg[0]['hotspare'])) if cfg[0]['raid'] != 'jbod' else 1)) - int(cfg[0]['dtabcount'])
            pdCountMap.update({pdCount:index})
        self.log.info('`'*BANNER_WIDTH)
        self.log.info('%s' % pformat(pdCountMap, indent=4))
        self.log.info('`' * BANNER_WIDTH)
        for pdCount in (pdCountMap.keys()).sort(reverse=True):
            sortedList.append(configStepList[pdCountMap[pdCount]])
        self.log.info('SortedPdRequed %s ' % pformat(sortedList, indent=4))'''
        return configStepList

    def getStepPdList(self, step):
        """ """
        if PDALLOCDEBUG:
            self.log.debug('-' * BANNER_WIDTH)
            self.log.debug((' Get Step %s  PD List' % step['step']).center(BANNER_WIDTH))
            self.log.debug('-' * BANNER_WIDTH)
        _config = step['config']
        _pdList = []
        # static = False if step['type'] == 'flexconfig' else True
        for index, cfg in enumerate(_config):
            _pdList.append([])
            static = True if (index == 0 and step['type'] == 'flexconfig') or step[
                'type'] == 'staticconfig' else False  # static variable is used to determine if we need to fail when pdallocation fails.
            for repeat in range(0, int(cfg['repeat'])):
                _dtab = int(cfg['dtabcount'])
                _ndtab = (int(cfg['pdcount']) * (
                    (int(cfg['spans']) + int(cfg['hotspare'])) if cfg['raid'] != 'jbod' else 1)) - _dtab
                _reserved = 0  # addLogic to reserve based during the BGops Implemenation for now set Zero
                # Also Enchance Logic to Request for the MAXPD Request First to Get a better Match of PD's
                self.log.debug("-" * BANNER_WIDTH)
                self.log.debug('Get PD From Decode PDMAP'.center(BANNER_WIDTH))
                self.log.debug(cfg['raid'].center(BANNER_WIDTH))
                self.log.debug('-' * BANNER_WIDTH)
                self.log.debug(('_dtab :%s' % _dtab).center(BANNER_WIDTH))
                self.log.debug(('_ndtab :%s' % _ndtab).center(BANNER_WIDTH))
                self.log.debug(('_reserved :%s' % _reserved).center(BANNER_WIDTH))
                self.log.debug('-' * BANNER_WIDTH)
                _pdList[index].append(self.getPdFromDecodePdMap(ndtabCount=_ndtab, dtabCount=_dtab, reserved=_reserved))
                if static and _pdList[index][-1] == {}:
                    raise SALError('Unable Allocate PD for Config STEP : %s' % step['step'])
        if _pdList == [[]]:
            raise SALError('Unable Allocate PD for Config STEP : %s' % step['step'])
        if PDALLOCDEBUG:
            self.log.debug('+' * BANNER_WIDTH)
            self.log.debug('Returning PDList to Step'.center(BANNER_WIDTH))
            self.log.debug(pformat(_pdList, indent=4))
            self.log.debug('+' * BANNER_WIDTH)
        return _pdList

    def getPdFromDecodePdMap(self, ndtabCount, dtabCount, reserved):
        """ """
        _match = []
        _rtn = {}
        for mediaType, attrib in self.decodePdMap.iteritems():
            for interfaceType, attrib1 in attrib.iteritems():
                for sectorSize, attrib2 in attrib1.iteritems():
                    if len(attrib2['dtab']) >= dtabCount and len(attrib2['ndtab']) > ndtabCount + reserved:
                        if PDALLOCDEBUG:
                            self.log.debug('-' * BANNER_WIDTH)
                            self.log.debug(
                                'Found Possible Match for the Request With Below PD Types'.center(BANNER_WIDTH))
                            self.log.debug(('MediaType %s' % mediaType).center(BANNER_WIDTH))
                            self.log.debug(('InterFaceType %s' % interfaceType).center(BANNER_WIDTH))
                            self.log.debug(('Sector Size %s' % sectorSize).center(BANNER_WIDTH))
                            self.log.debug('Available Pd List'.center(BANNER_WIDTH))
                            self.log.debug(pformat(attrib2, indent=4))
                            self.log.debug('-' * BANNER_WIDTH)
                        _match.append({len(attrib2['ndtab']): attrib2})
        self.log.debug('-' * BANNER_WIDTH)
        self.log.debug('Match Pd'.center(BANNER_WIDTH))
        self.log.debug('-' * BANNER_WIDTH)
        self.log.debug(pformat(_match, indent=4))
        self.log.debug('-' * BANNER_WIDTH)
        if _match:
            _match = sorted(_match)[0].values()[-1]
            _rtn = {'dtab': _match['dtab'][:dtabCount], 'ndtab': _match['ndtab'][:ndtabCount + reserved]}
            self.log.debug('-' * BANNER_WIDTH)
            self.log.debug('Return Get PD From Decode Pd Map'.center(BANNER_WIDTH))
            self.log.debug(pformat(_rtn, indent=4))
            self.log.debug('-' * BANNER_WIDTH)
            self.updateDecodePdMap(pdList=(_rtn['dtab'] + _rtn['ndtab']))
        return _rtn

    def getPdObjects(self, pdList):
        _rtn = {}
        self.checkObjects(vdMap=False)
        for pd in pdList:
            _rtn.update(
                {pd: (self.ctrlPdMap[pd]['pdObj'] if pd in self.ctrlPdMap else self.ctrlDtabPdMap[pd]['pdObj'])})
        if PDALLOCDEBUG:
            self.log.debug('-' * BANNER_WIDTH)
            self.log.debug('Return PD Objects for PDs : %s ' % pdList)
            self.log.debug('-' * BANNER_WIDTH)
            self.log.debug(pformat(_rtn, indent=4))
            self.log.debug('-' * BANNER_WIDTH)
        if len(pdList) != len(_rtn.keys()):
            raise SALError('Unable To Get PD Objects')
        return _rtn

    def decodePd(self, step, cli=False):
        _rtn = []
        self.log.debug('-' * BANNER_WIDTH)
        self.log.debug(('DECODE PD STEP : %s' % step['step']).center(BANNER_WIDTH))
        self.log.debug('-' * BANNER_WIDTH)
        self.log.debug(pformat(step, indent=4))
        self.log.debug('-' * BANNER_WIDTH)
        pdDist = self.stepPDdist[step['step']]
        self.log.debug(('STEP PD DIST : %s ' % pformat(pdDist, indent=4)).center(BANNER_WIDTH))
        for index, raidLevel in enumerate(pdDist):
            if PDALLOCDEBUG:
                self.log.debug('-' * BANNER_WIDTH)
                self.log.debug(pformat(raidLevel, indent=4))
                self.log.debug(pformat(step['config'][index], indent=4))
                self.log.debug('-' * BANNER_WIDTH)
            _rtn.append([])
            for raidRepeat in raidLevel:
                raidPdList = []
                dtabPerSpan = int(step['config'][index]['dtabcount']) / int(step['config'][index]['spans'])
                ndtabPerSpan = int(step['config'][index]['pdcount']) - dtabPerSpan
                if PDALLOCDEBUG:
                    self.log.debug('-' * BANNER_WIDTH)
                    self.log.debug(('dtabPerSpan : %s ' % dtabPerSpan).center(BANNER_WIDTH))
                    self.log.debug(('ndtabPerSpan : %s ' % ndtabPerSpan).center(BANNER_WIDTH))
                    self.log.debug(('raidPdlist : %s ' % raidPdList).center(BANNER_WIDTH))
                    self.log.debug(('raidRepeat : %s ' % pformat(raidRepeat, indent=4)).center(BANNER_WIDTH))
                    self.log.debug('-' * BANNER_WIDTH)
                pdList = self.getPdObjects(pdList=(raidRepeat['dtab'] + raidRepeat['ndtab']))
                _rtn[index].append({'dtab': [pdList[pdCli] for pdCli in raidRepeat['dtab']]})
                for span in range(0, int(step['config'][index]['spans'])):
                    for _ in range(0, dtabPerSpan):
                        raidPdList.append(pdList[raidRepeat['dtab'].pop()])
                    for _ in range(0, ndtabPerSpan):
                        raidPdList.append(pdList[raidRepeat['ndtab'].pop()])
                if PDALLOCDEBUG:
                    self.log.debug(raidPdList)
                    self.log.debug(pformat(raidRepeat, indent=4))
                hotsparePd = []
                for hotspare in range(0, int(step['config'][index]['hotspare'])):
                    hotsparePd.append(pdList[raidRepeat['ndtab'].pop()])
                _rtn[index][-1].update({'pdlist': raidPdList, 'hotspare': hotsparePd, 'reserved': raidRepeat['ndtab']})
        self.log.debug('-' * BANNER_WIDTH)
        self.log.debug('Returning Drives to ADD Config')
        self.log.debug(pformat(_rtn, indent=4))
        self.log.debug('-' * BANNER_WIDTH)
        if _rtn == [[]]:
            raise SALError('Unable Get PDObjects')
        return _rtn

    def readTcJson(self):
        '''Reads TC JSON and Stores the Data for Execution'''
        tcJson = os.path.join(os.getcwd(), os.path.basename(self.args.tcJson))
        self.tcJson = self.readJsonFile(path=tcJson)
        self.tcSteps = self.tcJson['tcsteps']
        self.tcDefaults = self.tcJson['tcdefault']
        self.tcId = self.tcJson['test_step_definition']['id']
        self.log.debug(' TC Steps : %s ' % pformat(self.tcSteps, indent=4))

    def generateLoop(self, step):
        '''

        '''
        self.log.info('*' * BANNER_WIDTH)
        self.log.info(('LOOP STEP -> %s' % step['steplist']).center(BANNER_WIDTH))
        self.log.info('*' * BANNER_WIDTH)
        stepList = []
        for stepNo in step['steplist']:
            for sp in self.morphedSteps:
                if sp['step'] == int(stepNo):
                    if sp['type'] == 'loop':
                        stepList.extend(self.generateLoop(sp))
                    else:
                        sp['processed'] = False
                        stepList.append(sp)
                        break
        self.log.debug(' Generated loop Steps : %s  ' % pformat(stepList, indent=4))
        return stepList

    def getStepOutput(self, step):
        '''
         Function returns the previously stored step output self.step_output_map
        :param step: step number in format 'step #'
        :type step:  string
        :return: step output
        :rtype:
        '''
        return self.stepMap[int(step)]

    def checkObjects(self, vdMap=True, pdMap=True):
        """Check if the Objects are corrupted"""
        vdCorrupt = False
        if vdMap:

            if not self.ctrlVdMap:
                vdCorrupt = True
            else:
                for vd in self.ctrlVdMap:
                    try:
                        if vd.id == 0:
                            vdCorrupt = True
                            break
                    except:
                        vdCorrupt = True
                        break
            if vdCorrupt:
                [self.ctrlVdMap.update({vd.id: vd}) for vd in self.mr.get_vds()]
        pdCorrupt = False
        if pdMap:
            for pd in [_['pdObj'] for pdCli, _ in self.ctrlPdMap.iteritems()] + [_['pdObj'] for pdCli, _ in
                                                                                 self.ctrlDtabPdMap.iteritems()]:
                try:
                    if pd.id == 0:
                        pdCorrupt = True
                        break
                except:
                    pdCorrupt = True
                    break
            if pdCorrupt:
                [(self.ctrlPdMap[pd.cli].update({'pdObj': pd}) if pd.cli in self.ctrlPdMap else self.ctrlDtabPdMap[
                    pd.cli].update({'pdObj': pd})) for pd in self.mr.get_all_pds()]
        if pdCorrupt or vdCorrupt:
            self.log.debug('')
            self.log.debug('`' * BANNER_WIDTH)
            self.log.debug('checkObjects'.center(BANNER_WIDTH))
            self.log.debug('`' * BANNER_WIDTH)
            if vdCorrupt:
                self.log.debug('CTRL VD MAP'.center(BANNER_WIDTH))
                self.log.debug(pformat(self.ctrlVdMap, indent=4))
                self.log.debug('')
            else:
                self.log.debug('CTRL PD MAP'.center(BANNER_WIDTH))
                self.log.debug(pformat(self.ctrlPdMap, indent=4))
                self.log.debug('')
                self.log.debug('')
                self.log.debug('CTRL DTAB PD MAP'.center(BANNER_WIDTH))
                self.log.debug(pformat(self.ctrlDtabPdMap, indent=4))
                self.log.debug('')

    def getDevObjects(self, stepList, raidLevel=None, vdList=True):
        '''
        Returns the DeviceObjects Based on the Step Number passed
        RaidLevel = None, ALl VD Objects From the Step be returned irrespective of the RAIDlevel in Step
        vdList=True VD list based on RaidLevel will be returned else Entire DriveGroup Info will be returned in form
            {   '0': {   'dtabPd': [],
                 'pdList': [Pd:862 890:15],
                 'reservedPd': [],
                 'vdList': [Vd:1]},
        '1': {   'dtabPd': [],
                 'pdList': [   Pd:856 890:9,
                               Pd:855 890:8,
                               Pd:854 890:7,
                               Pd:853 890:6],
                 'reservedPd': [],
                 'vdList': [Vd:2]},
        '2': {   'dtabPd': [],
                 'pdList': [   Pd:979 934:0,
                               Pd:870 890:23,
                               Pd:869 890:22,
                               Pd:868 890:21,
                               Pd:867 890:20],
                 'reservedPd': [],
                 'vdList': [Vd:3]}}
        '''
        rtn = {}
        self.log.debug('.' * BANNER_WIDTH)
        self.log.debug(('Device Objects Requested For %s Steps' % stepList).center(BANNER_WIDTH))
        self.log.debug('.' * BANNER_WIDTH)
        if stepList == 'all':
            stepList = ['step ' + str(step['step']) for step in self.morphedSteps if
                        step['type'] in ['staticconfig', 'flexconfig']]
            self.log.debug(('Updated StepList : %s' % stepList).center(BANNER_WIDTH))
        raidLevel = None if raidLevel == 'all' else raidLevel
        for step in [_.split(' ')[-1] for _ in stepList]:
            output = self.getStepOutput(step)
            self.log.debug('`' * BANNER_WIDTH)
            self.log.debug(('OUTPUT FROM STEP : %s ' % step).center(BANNER_WIDTH))
            self.log.debug(pformat(output, indent=4))
            self.log.debug('`' * BANNER_WIDTH)
            if raidLevel:
                output = output[raidLevel]
            else:
                temp = {}
                [temp.update(values) for rdLvl, values in output.iteritems()]
                output = temp
                self.log.debug(pformat(output, indent=4))
            self.checkObjects()
            temp = {}
            for dg, attr in output.iteritems():
                temp.update({dg: {'vdList': [], 'pdList': [], 'reservedPd': [], 'dtabPd': []}})
                for pd in attr['pdList']:
                    temp[dg]['pdList'].append(self.ctrlPdMap[pd]['pdObj'])
                for pd in attr['reservedPd']:
                    temp[dg]['reservedPd'].append(self.ctrlPdMap[pd]['pdObj'])
                for pd in attr['dtabPd']:
                    temp[dg]['dtabPd'].append(self.ctrlDtabPdMap[pd]['pdObj'])
                for vd in attr['vdList']:
                    temp[dg]['vdList'].append(self.ctrlVdMap[vd])
                temp[dg].update({'raidType': temp[dg]['vdList'][0].raid_level if attr['vdList'] else 'jbod'})
            rtn.update(temp)
            self.log.debug('.' * BANNER_WIDTH)
            self.log.debug(('Requested Dev Info For StepList : %s' % step).center(BANNER_WIDTH))
            self.log.debug('.' * BANNER_WIDTH)
            self.log.debug(pformat(rtn, indent=4))
            self.log.debug('.' * BANNER_WIDTH)
        if vdList:
            _rtnVdList = []
            for dg, values in rtn.iteritems():
                _rtnVdList.extend(values['pdList'] if dg == 'jbod' else values['vdList'])
            self.log.debug('Return Dev Object List : %s ' % pformat(_rtnVdList, indent=4))
            return _rtnVdList
        else:
            self.log.debug('Return Dev Info List : %s ' % pformat(rtn, indent=4))
            return rtn

    def addConfigToStepMap(self, vdList, pdDict, step, raidType):
        if ADDCONFIGDEBUG:
            self.log.debug('.' * BANNER_WIDTH)
            self.log.debug('vdList'.center(BANNER_WIDTH))
            self.log.debug('%s' % pformat(vdList, indent=4))
            self.log.debug('PDDICT '.center(BANNER_WIDTH))
            self.log.debug('%s' % pformat(pdDict, indent=4))
            self.log.debug('Step '.center(BANNER_WIDTH))
            self.log.debug('%s' % pformat(step, indent=4))
            self.log.debug('RAID Type'.center(BANNER_WIDTH))
            self.log.debug('%s' % pformat(raidType, indent=4))
            self.log.debug('.' * BANNER_WIDTH)
        if raidType != 'jbod':
            self.log.debug('VDLIST : %s ' % vdList)
            dgVd = self.mr.cli.vd_get_info(vd_id=vdList[-1].id)
            if ADDCONFIGDEBUG:
                self.log.debug('VDINFO : %s ' % pformat(dgVd, indent=4))
            dgVd = dgVd['dg/vd'].split('/')[0]
        else:
            vdList = []
            dgVd = 'jbod'
        [self.ctrlVdMap.update({vd.id: vd}) for vd in vdList]
        if step not in self.stepMap.keys():
            self.stepMap.update({step: {}})
        if raidType not in self.stepMap[step].keys():
            self.stepMap[step].update({raidType: {}})
        self.stepMap[step][raidType].update({
            dgVd: {'vdList': [vd.id for vd in vdList], 'pdList': [pd.cli for pd in pdDict['pdlist']],
                   'reservedPd': pdDict['reserved'], 'hotspare': [pd.cli for pd in pdDict['hotspare']],
                   'dtabPd': [pd.cli for pd in pdDict['dtab']]}})
        self.log.debug('-' * BANNER_WIDTH)
        self.log.debug('STEPMAP'.center(BANNER_WIDTH))
        self.log.debug('-' * BANNER_WIDTH)
        self.log.debug(pformat(self.stepMap, indent=4))
        self.log.debug('-' * BANNER_WIDTH)

    def updateVDMap(self):
        pass

    def removeFromStepMap(self, devInfo, clearConfig=False):
        if clearConfig:
            self.stepMap = {}
        else:
            self.log.debug('-' * BANNER_WIDTH)
            self.log.debug('DEVINFO TO REMOVE'.center(BANNER_WIDTH))
            self.log.debug('%s' % pformat(devInfo))
            self.log.debug('-' * BANNER_WIDTH)
            for dg, attrib in devInfo.iteritems():
                # self.log.info('dg : %s  Attrib : %s' % ( dg,attrib))
                for step, raidAtrib in self.stepMap.iteritems():
                    # self.log.info('step : %s : raidAtrib : %s' % (step, raidAtrib))
                    for raid, attrib in raidAtrib.iteritems():
                        # self.log.info('step : %s : raidAtrib : %s' % (step, raidAtrib))
                        if dg in attrib.keys():
                            del self.stepMap[step][raid][dg]
                            break
            self.log.debug('-' * BANNER_WIDTH)
            self.log.debug('STEP MAP'.center(BANNER_WIDTH))
            self.log.debug('-' * BANNER_WIDTH)
            self.log.debug(pformat(self.stepMap, indent=4))
            self.log.debug('-' * BANNER_WIDTH)

    def waitStep(self, wait):
        '''Performs Step Wait'''
        if isinstance(wait, dict):
            self.log.debug('Step Wait is Dict : %s' % pformat(wait, indent=4))
            if '-' in wait['interval']:
                _rnge = wait['interval'].split('-')
                wait = random.choice(range(int(_rnge[0]), int(_rnge[1])))
            else:
                wait = int(wait['interval'])
        elif wait != '':
            wait = int(wait)
        else:
            return
        break_time = time.time() + wait
        self.log.info('`' * BANNER_WIDTH)
        self.log.info(("Remaining Step Delay : %s  Seconds" % str(int(break_time - time.time()))).center(BANNER_WIDTH))
        self.log.info('`' * BANNER_WIDTH)
        while (time.time() <= break_time):
            if self.iofailure:
                self.log.info('!' * BANNER_WIDTH)
                self.log.info("IO Failure Detected".center(BANNER_WIDTH))
                self.log.info('!' * BANNER_WIDTH)
                break
            if int(time.time() % 60) == 0:
                self.log.info('`' * BANNER_WIDTH)
                self.log.info(
                    ("Remaining Step Delay : %s  Seconds" % str(int(break_time - time.time()))).center(BANNER_WIDTH))
                self.log.info('`' * BANNER_WIDTH)
                time.sleep(10)
        self.log.info('`' * BANNER_WIDTH)
        self.log.info('.' * BANNER_WIDTH)
        self.log.info(("Step Delay Of %s sec Completed" % wait).center(BANNER_WIDTH))
        self.log.info('.' * BANNER_WIDTH)

    def step1(self):
        '''Wingman FLEX Initialization'''
        self.tcId = 'N/A'
        self.stepList = []
        self.loopFlag = False
        self.loopCount = -1
        self.duration = -1
        self.startTime = -1
        self.sysResume = False
        self.coljson = False
        self.iobatchmode = False
        self.iomonitormap = {}
        self.iomonitordict = {}
        self.iomonitorthread = None
        self.iofailure = False
        self.iotracker = {'cleanexit': [], 'expectedfail': [], 'unexpectedfail': []}
        self.exitiomonitor = False
        self.ioexpectedfailure = []
        self.iocompletelist = []
        self.col_off_time = []
        self.col_cmd = None
        self.colverify = False
        self.colindex = -1
        self.currentStep = -1
        self.stepMap = {}
        self.stepPDdist = {}
        self.decodePdMap = {}
        self.raidKeywordMap = {0: 'stripe', 1: 'mirror', 5: 'parity', 6: 'dparity', 10: 'smirror', 50: 'sparity',
                               60: 'sdparity', 'jbod': 'jbod'}
        self.printBanner()
        self.readTcJson()
        self.setupController()
        self.morphJson()
        self.end_of_test = False
        self.fc_obj = None
        self.target_fw_file = ""
        self.pre_reset_val = {}
        self.current_pr_state = ""
        self.bgop_all_thread = []
        self.stop_pr_flag = 0
        self.thread_exceptions = {}
        self.init_crash_monitor()

    def step2(self):
        '''
                                    Wingman FLEX Execution Logic. If any changes needed please discuss prior to modifying

                                    #pending Add Iteration Count from iteration dict conversion and stepwait based interaval defined
        '''
        if self.sysResume:
            self.check_crash_events()
            self.setupController()
            self.exceute_bgop_all_thread_after_reboot()
        if LOOPDEBUG:
            self.log.debug('`' * BANNER_WIDTH)
            self.log.debug((' steplist : %s ' % self.stepList).center(BANNER_WIDTH))
            self.log.debug((' starttime : %s ' % self.startTime).center(BANNER_WIDTH))
            self.log.debug((' morphedsteps : %s ' % pformat(self.morphedSteps, indent=4)).center(BANNER_WIDTH))
            self.log.debug('`' * BANNER_WIDTH)
        for seq in self.morphedSteps:
            if LOOPDEBUG:
                self.log.debug('~' * BANNER_WIDTH)
                self.log.debug((' Execute Seq : %s ' % seq).center(BANNER_WIDTH))
                self.log.debug((' CurrentStep Marker : %s ' % self.currentStep).center(BANNER_WIDTH))
                self.log.debug('~' * BANNER_WIDTH)
            if not self.sysResume:
                self.currentStep = seq['step']
            elif seq['step'] != self.currentStep:
                continue
            if not self.stepList:
                if LOOPDEBUG:
                    self.log.debug('Step Empty Generating Step List '.center(BANNER_WIDTH))
                if seq['type'] == 'loop':
                    self.stepList = self.generateLoop(copy.deepcopy(seq))
                    self.loopCount = int(seq['count']['count'] if isinstance(seq['count'], dict) else seq['count'])
                    self.duration = int(seq['duration']) if seq['duration'] else 0
                    self.loopFlag = True
                else:
                    self.stepList = [copy.deepcopy(seq)]
                    self.loopCount = 1
                    self.duration = 0
                    self.loopFlag = False
                if LOOPDEBUG:
                    self.log.debug((' SET Duration : %s ' % self.duration).center(BANNER_WIDTH))
                    self.log.debug((' SET Loop Count : %s ' % self.loopCount).center(BANNER_WIDTH))
                    self.log.debug((' SET Loop FLAG: %s ' % self.loopFlag).center(BANNER_WIDTH))
            if self.startTime == -1:
                self.startTime = time.time()
                if LOOPDEBUG:
                    self.log.debug((' Reset Start Time : %s ' % self.startTime).center(BANNER_WIDTH))
            if LOOPDEBUG:
                self.log.debug((' Self.Start Time already set to : %s ' % self.startTime).center(BANNER_WIDTH))
                self.log.debug((' self.duration : %s :  %s  ' % ((time.time() - self.startTime), self.duration)).center(
                    BANNER_WIDTH))
                self.log.debug((' sysResume ? : %s ' % self.sysResume).center(BANNER_WIDTH))
            while (((
                    time.time() - self.startTime < self.duration) if self.duration else self.loopCount > 0) or self.sysResume):
                if LOOPDEBUG:
                    self.log.debug((' Inside Loop Execution : Loop Flag : %s ' % self.loopFlag).center(BANNER_WIDTH))
                if not self.sysResume:
                    if self.loopFlag:
                        text = ','.join([str('step ' + str(no)) for no in seq['steplist']])
                        self.log.info('')
                        self.log.info('')
                        self.log.info('#' * BANNER_WIDTH)
                        if self.duration:
                            self.log.info((('loop steps : %s for   %s seconds  ' % (
                                text, str(self.duration - (time.time() - self.startTime)))).title()).center(
                                BANNER_WIDTH))
                        else:
                            self.log.info((('loop steps : %s  loop# %s' % (text, int(
                                seq['count']['count'] if isinstance(seq['count'], dict) else seq[
                                    'count']) - self.loopCount)).title()).center(BANNER_WIDTH))
                        self.loopCount -= 1
                        self.log.info('#' * BANNER_WIDTH)
                        self.log.info('')
                    else:
                        self.loopCount -= 1
                self.runStep()
                if LOOPDEBUG:
                    self.log.debug(' Run step Completed '.center(BANNER_WIDTH))
                if ((time.time() - self.startTime < self.duration) if self.duration else self.loopCount > 0):
                    if LOOPDEBUG:
                        self.log.debug(' Reset Step list for False '.center(BANNER_WIDTH))
                    for step in self.stepList:
                        step['processed'] = False
            if self.loopFlag:
                txt = ','.join([str('step ' + str(no)) for no in seq['steplist']])
                txt1 = str(self.duration) if self.duration else str(
                    seq['count']['count'] if isinstance(seq['count'], dict) else seq['count'])
                txt2 = 'Seconds' if self.duration else 'Iterations'
                self.log.info(' Loop Steps %s Completed for : %s  %s' % (txt, txt1, txt2))
            self.stepList = []
            self.startTime = -1
            if LOOPDEBUG:
                self.log.debug(('Loop Complete : Reset Steplist and start time ').center(BANNER_WIDTH))
                self.log.debug(('self.steplist : %s ' % self.stepList).center(BANNER_WIDTH))
                self.log.debug(('Self.starttime : %s ' % self.startTime).center(BANNER_WIDTH))
                self.log.debug(('seq : %s ' % seq['processed']).center(BANNER_WIDTH))
        self.end_of_test = True
        self.eot_bgop()
        self.check_bgop_exception()
        self.wait_for_threads()
        self.checkioexit()

    def runStep(self):
        ''' Each Step Generated in Step2 will be Executed Here'''
        banner_text = "Test Step"
        for step in self.stepList:
            if not step['processed']:
                if not self.sysResume:
                    self.log.info('')
                    self.log.info('-' * BANNER_WIDTH)
                    self.log.info(('TEST STEP : %s ' % step['step']).center(BANNER_WIDTH))
                    self.log.info('-' * BANNER_WIDTH)
                    stepbanner = ('WINGMAN 3.0 TEST STEP : %s --> TEST TYPE : %s' % (
                        step['step'], step['type'].upper())).center(BANNER_WIDTH)
                    self.debuggerText(text=stepbanner)
                    '''self.mr.megamon_cmd(cmd_string='iop uart echo \'\n\n%s\n%s\n%s\n\'' % (
                    '.' * BANNER_WIDTH, stepbanner, '.' * BANNER_WIDTH), usr_str=True)'''
                    self.log.debug(('%s ' % pformat(step, indent=4)).center(BANNER_WIDTH))
                    self.log.info('')
                if step['type'] in ['flexconfig', 'staticconfig']:
                    self.addConfig(step)
                elif step['type'] == 'delete':
                    self.deleteConfig(step)
                elif step['type'] == 'reboot':
                    self.sysReboot(step)
                    pass
                elif step['type'] == 'io':
                    self.startIo(step)
                elif step['type'] == 'foreign_cfg':
                    self.exec_fc(opcode=step["fc_operation"])
                elif step['type'] == 'pinned_cache':
                    self.exec_pc(opcode=step["pc_operation"])
                elif step['type'] == 'col':
                    self.startCol(step)
                elif step['type'] == 'FW Update':
                    self.exec_fwupdate(step)
                elif step['type'].lower() == 'reset':
                    self.exec_reset(step)
                elif step['type'] == "bgop":
                    self.exec_bgop(step)
                elif step['type'].lower() == 'snapdump':
                    self.exec_snapdump(step)
                else:
                    self.log.info('%s' % pformat(step))
                step['processed'] = True
                self.check_crash_events()
                self.sd_obj.verify_sd_type()
            self.waitStep(wait=step['step_wait'])
            self.check_bgop_exception()
            self.checkioexit()


    def addConfig(self, step):
        '''Create Flex Config As Per the Config File or TC Default'''
        pdDict = self.decodePd(step)
        initVds = {'fast': [], 'full': []}
        for _cIndex, _config in enumerate(step['config']):
            for repeatIndex in range(0, int(_config['repeat'])):
                if repeatIndex > 0:
                    self.log.info('.' * BANNER_WIDTH)
                    self.log.info(('RAID LEVEL %s REPEAT Count %s ' % (_config['raid'].upper(), repeatIndex)).center(
                        BANNER_WIDTH))
                    self.log.info('.' * BANNER_WIDTH)
                if _config['raid'] == 'jbod':
                    self.log.info(
                        'Make JBOD on Drives -> %s ' % [pd.cli for pd in pdDict[_cIndex][repeatIndex]['pdlist']])
                    self.mr.quick_adv(pd_list=pdDict[_cIndex][repeatIndex]['pdlist'])
                    self.addConfigToStepMap(vdList=[], pdDict=pdDict[_cIndex][repeatIndex], step=step['step'],
                                            raidType=self.raidKeywordMap[_config['raid']])
                else:
                    raidLevel = int(_config['raid'].lower()[1::])
                    stripe = random.choice([7, 9]) if _config['stripe'] == 'random' else 7 if int(
                        _config['stripe']) == 64 else 9
                    DCP = random.choice([DCP_WB, DCP_WT]) if _config['writepolicy'] == 'random' else DCP_WB if _config[
                                                                                                                   'writepolicy'] == 'wb' else DCP_WT
                    span = int(_config['spans'])
                    size = None if _config['size'] == '' else _config['size']
                    count = int(_config['vdcount'])
                    autobgi = 'enable' if _config['init'] == 'bgi' else 'disable'
                    vdList = self.mr.add_vd(raid=raidLevel, vd_count=count,
                                            pd_list=pdDict[_cIndex][repeatIndex]['pdlist'], default_cache_policy=DCP,
                                            span_count=span, strip_size=stripe, vd_size=size, bgi=autobgi)
                    vdList = vdList if isinstance(vdList, list) else [vdList]
                    if _config['init'] == 'fast':
                        initVds['fast'].extend(vdList)
                    elif _config['init'] == 'full':
                        initVds['full'].extend(vdList)
                    [vdList[0].make_dedicated_hotspare(pd=pd) for pd in pdDict[_cIndex][repeatIndex]['hotspare']]
                    self.addConfigToStepMap(vdList=vdList, pdDict=pdDict[_cIndex][repeatIndex], step=step['step'],
                                            raidType=self.raidKeywordMap[raidLevel])
                self.log.info(" ")
        if initVds['fast']:
            self.mr.run_init(vds=initVds['fast'], full=False)
        if initVds['full']:
            self.mr.run_init(vds=initVds['full'], full=True)
        self.log.debug(' ')
        self.log.debug('*' * BANNER_WIDTH)
        self.log.debug(pformat(self.ctrlVdMap, indent=4))
        self.log.debug(pformat(self.stepMap, indent=4))
        self.log.debug('*' * BANNER_WIDTH)
        self.log.debug(' ')

    def deleteConfig(self, step):
        ''''Deletes Config
         {
            "clear_config": "false",
            "expected_result": "pass",
            "jbod_to_ug": "false",
            "pattern": "all",
            "raid": "r0",
            "step": 3,
            "step_reference": [
                "Step 1",
                "Step 2"
            ],
            "step_wait": "",
            "stop_io": "false",
            "type": "delete"
        }
        '''
        stepList = 'all' if step['clear_config'] == 'true' else step['step_reference']
        raidLevel = 'all' if step['clear_config'] == 'true' else step['raid']
        devInfo = self.getDevObjects(stepList=stepList, raidLevel=raidLevel, vdList=False)
        deleteDevObjects = []
        jbods = []
        vds = []
        for dg, values in devInfo.iteritems():
            deleteDevObjects.extend(values['pdList'] if dg == 'jbod' else values['vdList'])
        self.removeFromStepMap(devInfo=devInfo, clearConfig=True if step['clear_config'] == 'true' else False)
        if step['stop_io'] == 'true':
            self.stopIo(vdIdList=[_.id for _ in deleteDevObjects])
        else:
            [vds.append(dev) if dev.is_vd else jbods.append(dev) for dev in deleteDevObjects]
            if step['pattern'] != 'even':
                vds = [vd for vd in vds if vd.id % 2 == 0]
                jbods = [jbod for jbod in jbods if jbod.id % 2 == 0]
            elif step['pattern'] != 'odd':
                vds = [vd for vd in vds if vd.id % 2 != 0]
                jbods = [jbod for jbod in jbods if jbod.id % 2 != 0]
        if step['clear_config'] == 'true':
            self.ioexpectedfailure.extend([_.id for _ in deleteDevObjects])
            lookBack = time.time()
            self.log.info('.' * BANNER_WIDTH)
            self.log.info('Clearing Config'.center(BANNER_WIDTH))
            self.log.info('.' * BANNER_WIDTH)
            self.mr.clear_config(force=True)
            self.mr.wait_for_event(event_id=MR_EVT_CFG_CLEARED, lookback=time.time() - lookBack, time_out=30)
            self.removeFromStepMap(clearConfig=False)
        else:
            self.ioexpectedfailure.extend([_.id for _ in vds + jbods])
            lookBack = time.time()
            time.sleep(1)
            if vds:
                self.log.info('.' * BANNER_WIDTH)
                self.log.info(('Deleting VD\'s : %s ' % vds).center(BANNER_WIDTH))
                self.log.info('.' * BANNER_WIDTH)
                self.mr.delete_vds(vds=vds)
                self.mr.wait_for_event(event_id=MR8_EVT_LD_DELETED, lookback=time.time() - lookBack, vd=vds,
                                       time_out=30)
            if jbods:
                self.log.info('.' * BANNER_WIDTH)
                self.log.info(('Deleting JBOD\'s : %s ' % jbods).center(BANNER_WIDTH))
                for pd in jbods:
                    pd.state = 'unconfigured_good'
                    self.mr.wait_for_event(event_id=MR8_EVT_PD_STATE_CHANGE_UPDATED, lookback=time.time() - lookBack,
                                           pd=pd, time_out=30)
            self.log.info('.' * BANNER_WIDTH)
        self.log.info('.' * BANNER_WIDTH)

    def sysReboot(self, step):
        '''
        System Reboot Function JSON Format
            {
              'comparedriverversion': false,
              'stepwait': 0,
              'resumeio': false,
              'enclosureoperation': '',
              'step': 3.0,
              'type': 'reboot',
              'iteration': '1',
              'reboot_while_io': false,
              'result': 'pass'
            }
        '''
        if not self.sysResume:
            self.sysResume = True
            self.execute_bgop_all_thread_update_b4_reboot()
            self.get_wm_state()
            self.save_state(advance=False)
            sal.util.reboot_system()
            self.log.info(' ********** Rebooting the system **********')
            self.wait_for_restart()
        else:
            self.log.info('!' * BANNER_WIDTH)
            self.log.info('System Resumed After Reboot'.center(BANNER_WIDTH))
            self.log.info('!' * BANNER_WIDTH)
            self.sysResume = False

    def startIo(self, step):
        self.log.debug(' ')
        self.log.debug('.' * BANNER_WIDTH)
        self.log.debug('Starting %s IO'.center(BANNER_WIDTH) % step['tool'])
        self.log.debug(' ')
        vd_step_reference = self.getDevObjects(step['step_reference'])
        self.io_determine_mode()
        if self.iobatchmode:
            self.init_io_tool(step, vd_object=[vd_step_reference])
        else:
            self.init_io_tool(step, vd_object=vd_step_reference)
        time.sleep(30)
        if self.iomonitorthread is None:
            self.log.debug("Spawning a IO monitor thread")
            self.iomonitorthread = threading.Thread(name="IO monitor thread", target=self.io_monitor)
            self.iomonitorthread.start()

    def stopIo(self, vdIdList):
        '''vdIdList to stop the IO'''
        self.log.debug('stopping io on vdIdList')
        for vdId in vdIdList:
            if vdId in self.iomonitormap.keys():
                try:
                    self.iomonitormap[vdId]['io_handle'].stop()
                except Exception as e:
                    self.log.info('Unable to Stop IO on VD : %s Error : %s' % (vdId, e))
            else:
                self.log.debug('IO not Initiated on VD : %s' % vdId)

    def io_determine_mode(self):
        """Set the value of iobatch mode based on the JSON"""
        for st in self.morphedSteps:
            steplocal = copy.deepcopy(st)
            if steplocal['type'] in ['col']:
                self.coljson = True
                self.iobatchmode = True
        self.log.debug(('IO Batch Mode Set to True : %s' % self.iobatchmode))

    def io_monitor(self):
        """Monitor IO and raise appropriate exception"""
        try:
            while True:
                tempVdList = self.iomonitormap.keys()
                if len(self.iomonitormap) == 0:
                    self.iomonitorthread = None
                    break
                curTime = time.time()
                delList = []
                #self.log.debug('tempVdList : %s' % tempVdList)
                if int(time.time() % 60) == 0:
                    self.log.debug('tempVdList : %s' % tempVdList)
                for vd in tempVdList:
                    if IODEBUG:
                        if int(time.time() % 60) == 0:
                            self.log.debug(' IO Expected Failure List : %s' % self.ioexpectedfailure)
                            self.log.debug('IO runtime for Dev ID: %s : %s secs (Total time : %s)' % (
                                str(vd), (curTime - int(self.iomonitormap[vd]['start_time'])),
                                self.iomonitormap[vd]['runtime']))
                    if self.iomonitormap[vd]['io_handle'].running():
                        if int(self.iomonitormap[vd]['runtime']) != -1 and (
                                curTime - int(self.iomonitormap[vd]['start_time'])) > int(
                            self.iomonitormap[vd]['runtime']):
                            self.iomonitormap[vd]['io_handle'].stop()
                            self.log.info(('IO runtime for Dev ID: %s : %s secs (Total time : %s) Completed' % (
                                str(vd), (curTime - int(self.iomonitormap[vd]['start_time'])),
                                int(self.iomonitormap[vd]['runtime']))).center(BANNER_WIDTH))
                            self.log.debug(('Stopping IO On Dev ID: %s' % str(vd)).center(BANNER_WIDTH))
                            self.iotracker['cleanexit'].append(vd)
                            delList.append(vd)
                        elif self.end_of_test:
                            if int(time.time() % 60) == 0:
                                self.log.debug('End of Test Flag : %s ' % self.end_of_test)
                            self.exitiomonitor = True
                            for vd, attrib in self.iomonitormap.iteritems():
                                #self.log.debug('%s :: %s' %(vd, attrib))
                                if int(attrib['runtime']) != -1:
                                    self.exitiomonitor = False
                                    break
                            else:
                                delList = self.iomonitormap.keys()
                            if not self.exitiomonitor:
                                continue
                        else:
                            continue

                    self.log.debug('IO on VD %s Has Stopped Checking For Errors' % str(vd))
                    delList.append(vd)
                    try:
                        self.iomonitormap[vd]['io_handle'].check()
                    except SALIOError:
                        self.log.info('*' * BANNER_WIDTH)
                        self.log.info(('SALIOError ON VD %s' % str(vd)).center(BANNER_WIDTH))
                        self.log.info('*' * BANNER_WIDTH)
                        self.log.info('.' * BANNER_WIDTH)
                        vdExpected = vd if isinstance(vd, tuple) else [vd]
                        self.log.info(vdExpected)
                        for vdId in vdExpected:
                            if vdId in self.ioexpectedfailure:
                                self.log.info(('IO Error On Dev ID %s  is Expected' % vdId).center(BANNER_WIDTH))
                                self.iotracker['expectedfail'].append(vdId)
                            else:
                                self.log.info(('IO Error On Dev ID %s  is Not Expected' % vdId).center(BANNER_WIDTH))
                                self.iotracker['unexpectedfail'].append(vdId)
                                self.iofailure = True
                                self.exitiomonitor = True  # self.log.info(delList)
                    except SALDataCorruption:
                        self.log.info('*' * BANNER_WIDTH)
                        self.log.info(('DATA CORRUPTION ON Dev ID %s' % vd).center(BANNER_WIDTH))
                        self.log.info('*' * BANNER_WIDTH)
                        self.iotracker['unexpectedfail'].append(vd)
                        self.exitiomonitor = True
                        self.iofailure = True
                if delList:
                    self.log.debug(set(delList))
                    for vd in set(delList):
                        try:
                            self.iomonitormap[vd]['io_handle'].stop()
                        except:
                            pass
                        del self.iomonitormap[vd]
                    if not self.iomonitormap.keys():
                        self.exitiomonitor = True
                if self.iofailure or self.exitiomonitor:
                    self.log.info('.' * BANNER_WIDTH)
                    self.log.info('Exiting  IO Monitor'.center(BANNER_WIDTH))
                    self.log.info(
                        'self.ioFailure : %s :: self.exitiomonitor :: %s' % (self.iofailure, self.exitiomonitor))
                    self.log.info('.' * BANNER_WIDTH)
                    break
                time.sleep(1)
            if IODEBUG:
                self.log.debug("IO tracker values: %s" % pformat(self.iotracker, indent=4))
        except Exception as e:
            self.log.debug("Exception occurred: %s" % e)
            self.iofailure = True

    def io_num_threads(self, step):
        """Determine the no of threads to be issued"""
        expected_vd_count = 0
        multiply_factor = 1
        threads = 1
        for st in self.morphedSteps:
            steplocal = copy.deepcopy(st)
            if steplocal['type'] in ['flexconfig', 'staticconfig']:
                for configkey in steplocal['config']:
                    if 'vdcount' in configkey.keys():
                        try:
                            expected_vd_count += int(configkey['vdcount']) * int(configkey['repeat'])
                        except:
                            expected_vd_count += 1 * int(configkey['repeat'])  # JBOD VDcount='N/A'
        if IODEBUG:
            self.log.debug("Expected vd count formed is: %s" % expected_vd_count)
        if step['tool'].lower() == 'medusa':
            size = Size(step['size'])
            if size <= Size('1M'):
                multiply_factor = 1
            elif Size('1M') < size <= Size('2M'):
                multiply_factor = 2
            elif Size('2M') < size <= Size('3M'):
                multiply_factor = 3
            elif Size('3M') < size <= Size('4M'):
                multiply_factor = 4
            elif Size('4M') < size <= Size('5M'):
                multiply_factor = 5
            threads = int(round(int(step['qd']) / (expected_vd_count * multiply_factor)))
        if IODEBUG:
            self.log.debug("Number of threads formed is: %s" % threads)
        return threads

    def init_io_tool(self, step, vd_object):
        """Initialize and creates IO tool handles for the given vd object references"""
        if IODEBUG:
            self.log.debug('VD object reference in init IO tool: %s' % pformat(vd_object, indent=4))
        # calculate no of threads
        if self.iomonitorthread is None:
            self.threads = self.io_num_threads(step)
        if step['tool'].lower() == 'medusa':
            read_percent = int(step['read'])
            write_percent = (100 - read_percent)
            size = Size(step['size'])
            pattern = int(step['pattern'])
            random_percent = int(step['random'])
            flags = '--full-device -t%s --journal' % self.threads
            timeout = 400
            journal_path = ''
            if self.coljson:
                write_percent = 100
                read_percent = 0
                timeout = 400
                flags = "--full-device -m17 -t%s --journal=%s" % (self.threads, journal_path)
                if pattern != 35:
                    pattern = 35
            for vd in vd_object:
                if not self.iobatchmode:
                    journal_path = os.path.join(os.getcwd(), ("VD%s" % vd.id))
                    if IODEBUG:
                        self.log.debug("Journal path formed is: %s" % journal_path)
                    if not os.path.exists(journal_path):
                        if IODEBUG:
                            self.log.debug("Creating Journal Path : %s" % journal_path)
                        os.mkdir(journal_path)
                    flags = '--full-device -t%s --journal=%s' % (self.threads, journal_path)
                    if IODEBUG:
                        self.log.debug("Extra flags command formed is: %s" % flags)
                medusa_handle = Maim(devs=vd)
                medusa_handle.configure(buf_size=size, rand_pct=random_percent, workload="stress", data_pattern=pattern,
                                        extra_flags=flags, read_pct=read_percent, write_pct=write_percent,
                                        timeout=timeout)
                medusa_handle.start()
                if isinstance(vd, list):
                    vd_id_list = []
                    for item in vd:
                        vd_id_list.append(item.id)
                    self.iomonitormap[tuple(vd_id_list)] = {'io_handle': medusa_handle, 'runtime': step['runtime'],
                                                            'start_time': time.time(), 'journal_path': journal_path}
                    self.iomonitordict[tuple(vd_id_list)] = medusa_handle
                else:
                    self.iomonitormap[vd.id] = {'io_handle': medusa_handle, 'runtime': step['runtime'],
                                                'start_time': time.time(), 'journal_path': journal_path}
                    self.iomonitordict[vd.id] = medusa_handle
            if IODEBUG:
                self.log.debug("io monitor map formed is: %s" % self.iomonitormap)
                self.log.debug("io monitor sub map: %s" % self.iomonitordict)

    def checkioexit(self):
        """Check for IO exit status"""
        if self.iofailure:
            self.wait_for_threads()
        self.log.debug(' checkIOExit  %s ' % self.iofailure)
        if len(self.iotracker) != 0:
            if len(self.iotracker['cleanexit']) != 0:
                self.log.info("VD Id's exited cleanly from io monitor: %s" % self.iotracker[
                    'cleanexit'])  # for vd in self.iotracker['cleanexit']:  # self.iomonitordict[vd].check()
            if len(self.iotracker['expectedfail']) != 0:
                self.log.info("IO's failed as expected on VD ID's: %s" % self.iotracker['expectedfail'])
            if len(self.iotracker['unexpectedfail']) != 0:
                self.log.info("IO's failed unexpectedly on VD ID's: %s" % self.iotracker['unexpectedfail'])
                try:
                    for item in self.iomonitordict:
                        self.iomonitordict[item].stop()
                except Exception as e:
                    self.log.debug("Exception occurred in checkioexit function: %s" % e)
                    pass
                if self.iofailure:
                    raise SALError("IO failure is not expected on VD IDs: %s" % self.iotracker['unexpectedfail'])
        if self.iofailure:
            raise SALError('Unhandled IO Error Seen Please Report to Wingman Team')

    def io_cleanup(self):
        """Stop all IO instances during cleanup"""
        for item in self.iomonitordict:
            try:
                self.iomonitordict[item].stop()
            except Exception as e:
                pass

    def startCol(self, step):
        """Function to gather and start respective COL module"""
        if COLDEBUG:
            self.log.debug("COL morphed dictionary recevied is: %s" % step)
        # Init params
        self.init_col_params(step)
        # Check battery status
        self.colbattery_check()
        if not self.sysResume:
            self.col_initial_values()
            self.col_gen_offtime(step)
            if self.coltesttype in ['singledip', 'singleglitch', 'ocroffload', 'singlelearn']:
                self.col_cmd = self.col_singledip(step)
            elif self.coltesttype in ['doubledip', 'doubleglitch', 'multidip', 'multiglitch', 'restoreinterrupt']:
                self.col_cmd = self.col_doubledip(step)
            if COLDEBUG:
                self.log.debug("Command sent to automation server: %s" % self.col_cmd)
            self.col_auto_obj.send_cmd(self.col_cmd)
            self.sysResume = True
            self.iomonitorthread = None
            self.execute_bgop_all_thread_update_b4_reboot()
            self.get_wm_state()
            self.save_state(advance=False)
            self.wait_for_restart()
            if self.coltesttype in ['ocroffload']:
                self.mr.cli.restart_controller()
        else:
            # verify col happened
            self.sysResume = False
            self.colverify_offload()
            self.col_verify_maim(step)
            if step['run_cc']:
                self.col_cc(step)

    def init_col_params(self, step):
        """Initialize all required values"""
        self.coltesttype = step['coltype']
        self.col_autoserverip = self.setupInfo['auto_server_ip']
        self.col_debugger = self.setupInfo['debug_ip']
        self.col_debugport = self.setupInfo['debug_port']
        self.col_auto_obj = AutomationSend(self.col_autoserverip)
        self.col_apcip = self.setupInfo['apc_ip_server']
        self.col_apcport = self.setupInfo['apc_server_port']
        if isinstance(step['multidip'], dict):
            self.col_multidipcount = int(step['multidip']['count'])
        else:
            self.col_multidipcount = int(step['multidip'])
        self.col_wait_time = 600
        try:
            self.mr.megamon_cmd(cmd_string='colFlushDbg 1 1')
        except Exception as e:
            self.log.info("Exception while setting colflushdbg flag: %s" % e)
        if COLDEBUG:
            self.log.debug(' ')
            self.log.debug('.' * BANNER_WIDTH)
            self.log.debug('COL INIT parameters'.center(BANNER_WIDTH))
            self.log.debug('.' * BANNER_WIDTH)
            self.log.debug(' ')
            self.log.debug("Test type: %s" % self.coltesttype)
            self.log.debug("Automation server: %s" % self.col_autoserverip)
            self.log.debug("Debugger: %s" % self.col_debugger)
            self.log.debug("Debugger port: %s" % self.col_debugport)
            self.log.debug("APC: %s" % self.col_apcip)
            self.log.debug("APC port: %s" % self.col_apcport)
            self.log.debug("Multidip count: %s" % self.col_multidipcount)

    def colbattery_check(self):
        """Check for the status of controller Supercap before proceeding with COL"""
        if self.mr.cli.is_supercap_attached():
            self.log.info("SuperCap was found")
        elif self.mr.cli.is_battery_attached():
            self.log.info("iBBU was found")
        elif self.mr.cli.is_EnergyPack_attached():
            self.log.info("Energy Pack Found")
        else:
            raise SALError("No power source was found for the memory board!")

    def col_gen_offtime(self, step):
        """Generate off time values based on the selection by user"""
        if step['off_time']['type'].lower() in ['rand', 'inc', 'dec']:
            if step['off_time']['type'].lower() == 'rand':
                if self.coltesttype in ['singledip', 'doubledip', 'multidip', 'ocroffload', 'restoreinterrupt',
                                        'singlelearn']:
                    self.col_off_time = random.sample(range(10, 40), 3)
                elif self.coltesttype in ['singleglitch', 'doubleglitch', 'multiglitch']:
                    self.col_off_time = random.sample(range(1, 5), 3)
            elif step['off_time']['type'].lower() in ['inc', 'dec']:
                if self.coltesttype in ['singledip', 'doubledip', 'multidip', 'ocroffload', 'restoreinterrupt',
                                        'singlelearn']:
                    off_time = (random.sample(range(10, 40), 30))
                elif self.coltesttype in ['singleglitch', 'doubleglitch', 'multiglitch']:
                    off_time = (random.sample(range(1, 10), 9))
                if step['off_time']['type'].lower() == 'inc':
                    off_time.sort(reverse=False)
                elif step['off_time']['type'].lower() == 'dec':
                    off_time.sort(reverse=True)
                self.log.debug("Off time formed is: %s" % off_time)
                self.colindex += 1
                try:
                    if self.coltesttype not in ['doubledip', 'doubleglitch', 'multidip', 'multiglitch',
                                                'restoreinterrupt']:
                        self.col_off_time = [off_time[self.colindex]]
                    else:
                        if not self.colindex > len(off_time):
                            self.col_off_time = [item for item in off_time[self.colindex: self.colindex + 3]]
                            if len(self.col_off_time) != 0:
                                if len(self.col_off_time) != 3:
                                    self.col_off_time = [self.col_off_time[0], self.col_off_time[0],
                                                         self.col_off_time[0]]
                            else:
                                self.colindex = 0
                                self.col_off_time = [item for item in off_time[self.colindex: self.colindex + 3]]
                        else:
                            self.colindex = 0
                            self.col_off_time = [item for item in off_time[self.colindex: self.colindex + 3]]
                except IndexError:
                    self.colindex = 0
                    self.col_off_time = [off_time[self.colindex]]
        else:
            if self.coltesttype in ['singledip', 'doubledip', 'multidip', 'ocroffload', 'restoreinterrupt',
                                    'singlelearn']:
                self.col_off_time = [30, 30, 30]
            elif self.coltesttype in ['singleglitch', 'doubleglitch', 'multiglitch']:
                self.col_off_time = [5, 5, 5]
        self.log.debug("COL OFF Time: %s" % self.col_off_time)

    def col_singledip(self, step):
        """Perform dip related operations in this function"""
        self.col_auto_obj.log_megamon(self.col_debugger, self.col_debugport)
        if self.coltesttype in ['singledip', 'singleglitch', 'ocroffload', 'singlelearn']:
            wait_time = 10
            if self.coltesttype in ['ocroffload']:
                wait_time = 20
            if self.coltesttype in ['singlelearn']:
                self.col_start_learn_cycle()
            cmd = ' wait %s apc pull %s %s' % (wait_time, self.col_apcip, self.col_apcport)
            cmd += ' wait %s apc push %s %s ' % (self.col_off_time[0], self.col_apcip, self.col_apcport)
            if self.coltesttype in ['ocroffload']:
                cmd += ' find %s %s %s "%s"' % (self.col_debugger, self.col_debugport, self.col_wait_time,
                                                "Offload was started and completed successfully")

        self.log.info("Send to Automation Server:\n" + cmd)
        return cmd

    def col_doubledip(self, step):
        """Perform double dip/glitch operations in this function"""
        self.col_auto_obj.log_megamon(self.col_debugger, self.col_debugport)
        if self.coltesttype in ['doubleglitch', 'multiglitch']:
            cmd = 'loop %s 5 (' % self.col_multidipcount

            cmd += ' wait 10 apc pull %s %s' % (self.col_apcip, self.col_apcport)

            cmd += ' wait %s apc push %s %s ' % (self.col_off_time[0], self.col_apcip, self.col_apcport)

            cmd += ' wait %s apc pull %s %s ' % (self.col_off_time[1], self.col_apcip, self.col_apcport)

            cmd += ' wait %s apc push %s %s )' % (self.col_off_time[2], self.col_apcip, self.col_apcport)
        else:
            cmd = 'loop %s 20 (' % self.col_multidipcount
            cmd += ' wait 10 apc pull %s %s' % (self.col_apcip, self.col_apcport)
            cmd += ' wait %s apc push %s %s ' % (self.col_off_time[0], self.col_apcip, self.col_apcport)
            if self.coltesttype in ['restoreinterrupt']:
                cmd += 'find %s %s %s "%s" ' % (
                    self.col_debugger, self.col_debugport, self.col_wait_time, "Offload was started and completed")
                cmd += ' wait 2 apc pull %s %s ' % (self.col_apcip, self.col_apcport)
            else:
                cmd += 'find_any %s %s %s "%s" "%s" ' % (
                    self.col_debugger, self.col_debugport, self.col_wait_time, "Cache Flush is Active",
                    "FW Idle Flush Started")
            cmd += ' apc pull %s %s ' % (self.col_apcip, self.col_apcport)
            cmd += ' wait %s apc push %s %s )' % (self.col_off_time[1], self.col_apcip, self.col_apcport)
        return cmd

    def col_initial_values(self):
        """Gather current offload/restore/flush count before system powercycle"""
        col = getMR8ColInfo(self.ctrl)
        self.unsuccessful_offload_count = col[0].unsuccessfulOffloadCount
        self.successful_offload_count = col[0].successfulOffloadCount
        self.successful_restore_count = col[0].successfulRestoreCount
        self.unsuccesful_restore_count = col[0].unsuccessfulRestoreCount
        self.cache_flush_count = col[0].cacheFlushCount

    def colverify_offload(self):
        """Verify offload/restore/flush happened successfully"""
        col = getMR8ColInfo(self.ctrl)
        unsuccessful_offload_count = col[0].unsuccessfulOffloadCount
        successful_offload_count = col[0].successfulOffloadCount
        successful_restore_count = col[0].successfulRestoreCount
        unsuccesful_restore_count = col[0].unsuccessfulRestoreCount
        cache_flush_count = col[0].cacheFlushCount
        if COLDEBUG:
            self.log.debug("unsuccessful_offload_count in verify offload: %s" % unsuccessful_offload_count)
            self.log.debug("successful_offload_count in verify offload: %s" % successful_offload_count)
            self.log.debug("successful_restore_count in verify offload: %s" % successful_restore_count)
            self.log.debug("unsuccessful_restore_count in verify offload: %s" % unsuccesful_restore_count)
            self.log.debug("cache_flush_count offload count in verify offload: %s" % cache_flush_count)
        self.log.info(' ')
        self.log.info('.' * BANNER_WIDTH)
        self.log.info('COL RESULTS'.center(BANNER_WIDTH))
        self.log.info('.' * BANNER_WIDTH)
        self.log.info(' ')
        # Check for offload/restore/flush
        if unsuccessful_offload_count > self.unsuccessful_offload_count or unsuccesful_restore_count > self.unsuccesful_restore_count:
            raise SALError("Unsuccessful OFFLOAD/RESTORE DETECTED, HALTING EXECUTION")
        else:
            if successful_offload_count > self.successful_offload_count:
                no_of_offloads = successful_offload_count - self.successful_offload_count
                self.log.info("No of successful offloads are: %d" % no_of_offloads)
            else:
                raise SALError("No offload detected!!")
            if successful_restore_count > self.successful_restore_count:
                no_of_restore = successful_restore_count - self.successful_restore_count
                self.log.info("No of successful restores are: %d" % no_of_restore)
            else:
                raise SALError("No restore detected!!")
            if cache_flush_count > self.cache_flush_count:
                flush_count = cache_flush_count - self.cache_flush_count
                self.log.info("No of times flush happened: %d" % flush_count)
                if self.coltesttype in ['doubledip']:
                    if not flush_count >= 2:
                        raise SALError("Expecting flush to happen twice for this test, found %d times" % flush_count)
                    else:
                        self.log.info("Double dip successful")
                if self.coltesttype in ["multidip"]:
                    if not flush_count >= self.col_multidipcount + 1:
                        raise SALError("Expecting flush to happen %d times, found %d times" % (
                            self.col_multidipcount + 1, flush_count))
                    else:
                        self.log.info("Multi dip successful")

    def col_verify_maim(self, step):
        """Verify Medusa IO's for col cases"""
        self.setupController()
        vd_reference = self.getDevObjects(step['step_reference'])
        medusa_handle = Maim(devs=vd_reference)
        medusa_handle.configure(workload="stress", timeout=400, rand_pct=100,
                                extra_flags="-V --jv-compat -m17  --journal")
        medusa_handle.start()
        while True:
            if not medusa_handle.running():
                self.log.info("Maim process finished, stopping IO's")
                break
        medusa_handle.stop()
        str1 = "FAILED (confirmed or queued/confirmed-error with partial writes with data corruption)"
        with open("script.log", "r") as movinf:
            listp = movinf.readlines()
        for i in range(0, len(listp)):
            if "DEBUG" in listp[i] and str1 in listp[i]:
                seclist = listp[i + 1].split()[-1]
                if int(seclist) != 0:
                    raise SALError("Possible data corruption detected ,refer medusa logs")

    def col_cc(self, step):
        """Run CC on the VD's as part of COL"""
        vd_reference = [vd for vd in self.getDevObjects(step['step_reference']) if vd.raid_level != '0']
        for vd in vd_reference:
            while vd.cc_running:
                time.sleep(20)
        if COLDEBUG:
            self.log.info("VD list formed for CC is: %s" % vd_reference)
        vdccStart = {}
        for vd in vd_reference:
            vdccStart.update({vd.id: time.time()})
            time.sleep(0.1)
            vd.start_cc()
        completedList = []
        while True:
            for vd in vd_reference:
                if vd.id not in completedList:
                    prg = vd.get_progress_cc()
                    if prg != -1:
                        self.log.info('CC Progress on VD : %s : %s ' % (vd.id, str(prg) + ' %'))
                    else:
                        completedList.append(vd.id)
                        try:
                            self.mr.wait_for_event(event_id=MR_EVT_LD_CC_DONE, lookback=time.time() - vdccStart[vd.id],
                                                   vd=vd.id, time_out=30)
                            self.log.info('CC On VD : %s Completed, No Inconsistencies Found' % vd.id)
                        except SALError:
                            try:
                                self.mr.wait_for_event(event_id=MR_EVT_LD_CC_DONE_INCON,
                                                       lookback=time.time() - vdccStart[vd.id], vd=vd.id, time_out=30)
                                self.log.info('CC On VD : %s Completed with Inconsistencies' % vd.id)
                                raise SALError('CC On VD : %s Completed with Inconsistencies' % vd.id)
                            except SALError:
                                raise SALError("Consistency Check completion event not found on vd: %s" % vd.id)

            time.sleep(random.choice(range(30, 60)))
            if len(vd_reference) == len(completedList):
                break

    def col_start_learn_cycle(self):
        """Start learn cycle and look for event"""
        learn_start_seq = self.mr.get_event_seq_info()['newestSeqNum']
        # Start Learn cycle
        from sal.sl8 import epackLearnStart
        try:
            epackLearnStart(self.ctrl)
        except Exception as e:
            self.log.info("Exception occured while starting Learn Cycle: %s" % e)
            raise SALError("Learn cycle start failed with exception: %s" % e)
        evt_logger = mr_events8.EventLogCache(self.mr, start_seq=int(learn_start_seq))
        awatcher = mr_events8.Watcher(evt_logger, code=avengersalevents.MR_EVT_BEM_RELEARN_IN_PROGRESS)
        for retry in range(1, 6):
            learn_result = awatcher.found(force_update=True)
            if learn_result:
                break
            else:
                time.sleep(10)
        if not learn_result:
            try:
                self.mr.wait_for_event(event_id=avengersalevents.MR_EVT_BEM_RELEARN_IN_PROGRESS, background=False,
                                       lookback=600, time_out=900)
            except SALError:
                raise SALError("Learn cycle is in progress event not found")
        else:
            self.log.info("Learn cycle is in progress event found!")

    def wait_for_threads(self):
        """Placeholder function to add all common operations before and after reboot/powercycle"""
        try:
            if self.iomonitorthread.is_alive():
                self.iomonitorthread.join()
        except AttributeError:
            pass

    def exec_fc(self, opcode=None):
        self.log.info("")
        self.log.info("******************* Foreign Configuration Module **************")
        self.log.info("")
        self.mr.cli.continue_on_error_set(0)
        exisitng_foreign_config_on_controller = self.mr.cli.foreign_list_all()
        self.log.info("******************* Listing foreign configuration: %s **************" % (
            exisitng_foreign_config_on_controller))
        self.log.info("")
        exisitng_foreign_config_on_controller = list()
        exisitng_foreign_config_on_controller = self.mr.cli.foreign_preview_list()
        self.log.info("******************* Exisiting Foreign Configuration: foreign_preview_list: **************")
        self.log.info("")
        for index in exisitng_foreign_config_on_controller:
            self.log.info("******************* %s **************" % (str(index)))
        self.log.info("")
        try:
            if opcode.lower() == "import_fc":
                self.log.info("")
                self.log.info("******************* Performing foreign config import operation **************")
                self.log.info("")
                self.mr.cli.foreign_import()
            elif opcode.lower() == "clear_fc":
                self.log.info("")
                self.log.info("******************* Performing foreign config clear operation **************")
                self.log.info("")
                self.mr.cli.foreign_del_all()
        except:
            traceback.print_exc()
            raise SALError("------ Failed to perform foreign configuration: '%s' operation ------" % str(opcode))

    def mjolnirFlex_check_pc(self):
        pinnedcache_rtn_value = None
        pinnedCacheList = []
        pinnedCacheList = self.mr.get_pinnedcache_list()
        self.log.debug("\n pinnedCacheList:  %s" % pinnedCacheList)
        if len(pinnedCacheList) == 0:
            self.log.info("There are no VDs with pinned cache on controller ")
            pinnedcache_rtn_value = "There is no VD with pinned cache on controller "
        else:
            self.log.info("Logical drives with pinned cache : " + str(pinnedCacheList))
            pinnedcache_rtn_value = "Logical drives with pinned cache : " + str(pinnedCacheList)
        return pinnedcache_rtn_value

    def mjolnirFlex_discard_pinnedcache(self):
        Discard_PinnedCache_all_Lds(int(self.mr.ctrl_id))
        self.log.info("")
        self.log.info("All pinned cache discarded from controller " + str(self.mr.ctrl_id))
        self.log.info("")

    def exec_pc(self, opcode=None):
        try:
            if opcode.lower() == "pc_exists":
                self.log.info("")
                self.log.info("***** Validating VD Pinnedcache exist on controller ******")
                self.log.info("")
                check_pc_rtn_value = self.mjolnirFlex_check_pc()
                if not "Logical drives with pinned cache" in check_pc_rtn_value:
                    self.log.info("")
                    raise SALError("----- %s ----" % (str(check_pc_rtn_value)))
            elif opcode.lower() == "pc_no_exists":
                self.log.info("")
                self.log.info("***** Validating no VD Pinnedcache exist on controller ******")
                self.log.info("")
                check_pc_rtn_value = self.mjolnirFlex_check_pc()
                if not "There is no VD with pinned cache on controller" in check_pc_rtn_value:
                    self.log.info("")
                    raise SALError("----- %s ----" % (str(check_pc_rtn_value)))
            elif opcode.lower() == "discard_pc":
                self.log.info("")
                self.log.info("***** Discarding VD Pinnedcache exist on controller ******")
                self.log.info("")
                self.mjolnirFlex_discard_pinnedcache()
        except:
            traceback.print_exc()
            raise SALError("------ Failed to perform requested pinned cache operation ------")

    def exec_fwupdate(self,step):
        """
        This function is to flash controller/PD/Enclosure Firmware
        Also it will verify the version after flash depending on the user request
        """
        self.log.info("")
        self.log.info(" ********** FW Upgrade/Downgrade module **********")
        self.log.info("")
        if step["subtype"].lower() == "ctrl fw":
            version_verify = step["ver_verify"]
            method = step["method"]
            if 'state' not in step:
                step['state'] = 2
            if version_verify:
                if not method == "verify_last_fw_flash":
                    self.fw_version_get_verify(step, "before_fwflash")
            if step['state'] == 2:
                step = self.flash_ctrl(step)
            if step['state'] == 1:
                if not self.sysResume:
                    self.sysResume = True
                    self.execute_bgop_all_thread_update_b4_reboot()
                    self.get_wm_state()
                    self.save_state(advance=False)
                    if method == "reboot":
                        sal.util.reboot_system()
                        self.wait_for_restart()
                    elif method in ["power_cycle","abrupt_fw_flash"]:
                        fw_apcip = self.setupInfo['apc_ip_server']
                        fw_apcport = self.setupInfo['apc_server_port']
                        apc = APC(str(fw_apcip))
                        apc.login("apc", "apc")
                        apc.reboot_apc(int(fw_apcport))
                        self.wait_for_restart()
                else:
                    self.log.info("")
                    self.log.info('System Resumed After Reboot')
                    self.log.info("")
                    self.sysResume = False
                    step['state'] = 0
            if step['state'] == 0:
                if version_verify or method == "verify_last_fw_flash":
                    self.fw_version_get_verify(step, "after_fwflash")
                    self.fw_version_get_verify(step, "version_verify")
                    self.log.info("")
                    self.log.info(
                        "FW version before upgrade/downgrade: " + str(self.before_fw_version))
                    self.log.info("FW version after upgrade/downgrade: " + str(self.after_fw_version))
                    self.log.info("")

        elif step["subtype"].lower() == "device fw":
            step = self.flash_device(step)

    def flash_ctrl(self, step):
        """
        This function is to flash controller FW
        """
        method = step["method"]
        if not method == "verify_last_fw_flash":
            try:
                file_name = step["fw_package_path"]
            except:
                raise SALError("User not selected target firmware file")

            if not os.path.isfile(file_name):
                self.log.error("----- Fail to find firmware package %s -----"%file_name)
                raise SALError("-------- Fail to find firmware package %s--------"%file_name)
            self.target_fw_file = file_name
            self.log.info("")
            self.log.info("Controller FW Flash is in progress")
            self.log.info("")
            if method == "fw_flash_only":
                status, output = self.run_command_raw(
                                                      "download file=" + file_name + " activationtype=offline noverchk")
                self.log.info(output)
                if not status:
                    self.log.info("")
                    self.log.error("FW Flash Failed")
                    raise SALError("Fail to update FW")
                else:
                    self.log.info("")
                    self.log.info("FW flash success")
                    step['state'] = 0
                    time.sleep(150)
            elif method == "ofu":
                ocr_val = self.mr.cli.ocr_get()
                if ocr_val[0] == 'AUTO-->OFF':
                    self.log.error("Controller current OCR state is OFF, Try to set OCR state=ON and retry the test")
                    raise SALError("Controller current OCR state is OFF, Try to set OCR state=ON and retry the test")
                if ocr_val[1] == 'ALL-->OFF':
                    self.log.error("Controller current OCR state is OFF, Try to set OCR state=ON and retry the test")
                    raise SALError("Controller current OCR state is OFF, Try to set OCR state=ON and retry the test")

                status, output = self.run_command_raw("download file=" + file_name + " noverchk")

                if not status:
                    self.log.info("")
                    self.log.error("FW Flash Failed")
                    raise SALError("Fail to update FW")
                else:
                    self.log.info("")
                    self.log.info("FW flash success")
                    self.log.info("Waiting 180sec for OCR to complete")
                    time.sleep(180)
                step['state'] = 0

            elif method == "reboot":
                status, output = self.run_command_raw(
                                                      "download file=" + file_name + " activationtype=offline noverchk")
                self.log.info(output)
                if not status:
                    self.log.info("")
                    self.log.error("FW Flash Failed")
                    step['state'] = 0
                    raise SALError("FW flash failed")
                else:
                    self.log.info("")
                    self.log.info("Sytem reboot required to effect firmware changes")
                    step['state'] = 1

            elif method == "power_cycle":
                status, output = self.run_command_raw(
                                                      "download file=" + file_name + " activationtype=offline noverchk")
                self.log.info(output)
                if not status:
                    self.log.info("")
                    self.log.error("FW Flash Failed")
                    step['state'] = 0
                    raise SALError("FW flash failed")
                else:
                    self.log.info("")
                    self.log.info("Sytem Power cycle required to effect firmware changes")
                    step['state'] = 1

            elif method == "abrupt_fw_flash":
                self.log.info("Starting FW Flash followed by system power Cycle")
                fwdowloadthread = threading.Thread(name="FW download", target=self.download_fw, args=(file_name))
                fwdowloadthread.start()
                time.sleep(8)
                step['state'] = 1


        elif method == "verify_last_fw_flash":
            step['state'] = 0

        return step

    def download_fw(self, file_name=None):
        """
        To download FW
        """
        status, output = self.run_command_raw(
                                              "download file=" + file_name + " noverchk")


    def get_version_rom(self, file_path):
        """
        To get version info of fw rom file
        """
        output = self.mr.cli._cmd_run_local("show file=" + file_path + " J")
        output = json.loads(output)
        ver_details = {}
        try:
            d = output["Controllers"][0]["Response Data"]["Firmware Package Version"]
            ver_details["Firmware Package Version"] = d['Version']
        except:
            pass
        try:
            for x in output["Controllers"][0]["Response Data"]["Image Overview"]:
                if x['Component'] == 'PnP ID':
                    continue
                ver_details[x['Component']] = x['Version']
        except:
            raise SALError("No version details present in the fw file %s using storcli" % file_path)
        self.log.info("Version information from the firmware file is :%s" % ver_details)
        return ver_details

    def fw_version_get_verify(self, dict_item, state=''):
        """
        To Verify FW version
        Before FW flash
        After FW flash
        Compare Current Controller  FW version with .rom FW version
        """
        fw_dict = dict_item
        flash_type = fw_dict["method"]
        file_path = fw_dict["fw_package_path"]
        if state == "before_fwflash":
            try:
                self.before_fw_version = self.mr.cli.get_all()['firmware_version']
            except:
                self.log.error("Not able to fetch FW version before FW flash")
                raise SALError("Not able to fetch FW version")
        elif state == "after_fwflash":
            try:
                self.after_fw_version = self.mr.cli.get_all()['firmware_version']
            except:
                self.log.error("Not able to fetch FW version after FW flash")
                raise SALError("Not able to fetch FW version")
        elif state == "version_verify":
            if flash_type not in ["fw_flash_only", "abrupt_fw_flash"]:
                self.log.info("")
                self.log.info("FW version before upgrade/downgrade: " + str(self.before_fw_version))
                self.log.info("FW version after upgrade/downgrade: " + str(self.after_fw_version))
                self.log.info("")
                ver_list = ["sbr", "package", "bios", "nvdt", "app", "hiim", "btbl", "cbb"]
                self.log.info("-----Gathering version information from FW rom file-----")
                version_info = self.get_version_rom(self.target_fw_file)
                self.log.info("")
                self.log.info("-----Gathering version information from controller-----")
                all_fw_info = self.mr.cli.get_all()
                self.log.info("")
                self.log.info("-----Comparing Version between Controller and FW .rom file-----")
                for key, value in version_info.items():
                    if "sbr" in key.lower():
                        if str(value).lower() == str(all_fw_info["sbr_version"]).lower():
                            self.log.info(
                                "SBR version updated to %s after FW flash" % all_fw_info["sbr_version"])
                        else:
                            raise SALError(
                                "SBR version expected %s actual %s" % (value, all_fw_info["sbr_version"]))
                    if "package" in key.lower():
                        if str(value).lower() == str(all_fw_info["firmware_package_build"]).lower():
                            self.log.info(
                                "firmware_package_build version updated to %s after FW flash" % all_fw_info[
                                    "firmware_package_build"])
                        else:
                            raise SALError("firmware_package_build version expected %s actual %s" % (
                                value, all_fw_info["firmware_package_build"]))
                    if "bios" in key.lower():
                        if str(value).lower() == str(all_fw_info["bios_version"]).lower():
                            self.log.info(
                                "BIOS version updated to %s after FW flash" % all_fw_info["bios_version"])
                        else:
                            raise SALError(
                                "BIOS version expected %s actual %s" % (value, all_fw_info["bios_version"]))
                    if "nvdt" in key.lower():
                        if str(value).lower() == str(all_fw_info["nvdata_version"]).lower():
                            self.log.info(
                                "NVDATA version updated to %s after FW flash" % all_fw_info["nvdata_version"])
                        else:
                            raise SALError(
                                "NVDATA version expected %s actual %s" % (value, all_fw_info["nvdata_version"]))
                    if "app" in key.lower():
                        if str(value).lower().replace("0", "") == str(
                                all_fw_info["firmware_version"]).lower().replace("0", ""):
                            self.log.info(
                                "Firmware version updated to %s after FW flash" % all_fw_info["firmware_version"])
                        else:
                            raise SALError(
                                "Firmware version expected %s actual %s" % (value, all_fw_info["firmware_version"]))
                    if "fmc" in key.lower():
                        if str(value).lower().replace("0", "") == str(
                                all_fw_info["fmc_version"]).lower().replace("0", ""):
                            self.log.info(
                                "FMC version updated to %s after FW flash" % all_fw_info["fmc_version"])
                        else:
                            raise SALError(
                                "FMC version expected %s actual %s" % (value, all_fw_info["fmc_version"]))
                    if "bsp" in key.lower():
                        if str(value).lower().replace("0", "") == str(
                                all_fw_info["bsp_version"]).lower().replace("0", ""):
                            self.log.info(
                                "BSP version updated to %s after FW flash" % all_fw_info["bsp_version"])
                        else:
                            raise SALError(
                                "BSP version expected %s actual %s" % (value, all_fw_info["bsp_version"]))
                    if "hiim" in key.lower():
                        if "hiim_version" in all_fw_info.keys():
                            if str(value).lower() == str(all_fw_info["hiim_version"]).lower():
                                self.log.info(
                                    "HIIM version updated to %s after FW flash" % all_fw_info["hiim_version"])
                            else:
                                raise SALError(
                                    "HIIM version expected %s actual %s"(value, all_fw_info["hiim_version"]))
                        else:
                            self.log.warning("HIIM version information not available on controller")
                    if "btbl" in key.lower():
                        if str(value).lower() == str(all_fw_info["boot_block_version"]).lower():
                            self.log.info(
                                "BTBL version updated to %s after FW flash" % all_fw_info["boot_block_version"])
                        else:
                            raise SALError(
                                "BTBL version expected %s actual %s" % (value, all_fw_info["boot_block_version"]))
                    if "cbb" in key.lower():
                        if "cbb" in all_fw_info.keys():
                            if str(all_fw_info["cbb_version"]).lower() in str(value).lower():
                                self.log.info(
                                    "CBB version updated to %s after FW flash" % all_fw_info["cbb_version"])
                            else:
                                raise SALError(
                                    "CBB version expected %s actual %s" % (value, all_fw_info["cbb_version"]))
                        else:
                            self.log.warning("CBB version information not available on controller")

                self.log.info("")
                self.log.info("-----Firmware upgrade/downgrade passed-----")
            else:
                if self.before_fw_version == self.after_fw_version:
                    self.log.info("")
                    self.log.info("FW version before upgrade/downgrade: " + str(self.before_fw_version))
                    self.log.info("FW version after upgrade/downgrade: " + str(self.after_fw_version))
                    self.log.info("-----Firmware upgrade/downgrade passed-----")
                else:
                    self.log.info("")
                    self.log.info("FW version before upgrade/downgrade: " + str(self.before_fw_version))
                    self.log.info("FW version after upgrade/downgrade: " + str(self.after_fw_version))
                    self.log.error("Firmware upgrade/downgrade failed")
                    raise SALError("Firmware upgrade/downgrade failed")

    def run_command_raw(self, command=''):
        """To run raw command"""
        command = "/C" + str(self.ctrl) + " " + command
        self.log.debug("Command is : %s" % command)
        self.mr.cli.continue_on_error_set(1)
        try:
            raw_output = self.mr.cli.storcli_run_cmd_raw(command, log_cmd=False)
        except:
            raw_output = self.mr.cli.storcli_run_cmd_raw(command)
        self.mr.cli.continue_on_error_set(0)
        if (raw_output.upper().find("SUCCESS") >= 0 or raw_output.upper().find("IS CLEARED") >= 0):
            return True, raw_output
        else:
            return False, raw_output

    def flash_device(self, enc_pd_fw_dict):
        """
        To flash enclosure FW and PD FW
        """

        file_path = enc_pd_fw_dict["fw_package_path"]
        if not os.path.isfile(file_path):
            self.log.error("Failed to find firmware package")
            raise SALError("Error with target firmware package path")

        if enc_pd_fw_dict["device_type"] == "pd":
            self.log.info("*******  PD FW Flash is in progress  *******")
            device_id = enc_pd_fw_dict["device_id"].split(":")
            command_1 = "/E" + device_id[0] + "/S" + device_id[1] + " show all j"
            status_1, output_1 = self.run_command_raw(command_1)
            output_2 = json.loads(output_1)
            output_3 = output_2["Controllers"][0]["Response Data"]["Drives List"][0]["Drive Detailed Information"][
                "Firmware Revision Level"]
            self.log.info("PD FW Revision before FW Flash: %s" % output_3)
            command = "/E" + device_id[0] + "/S" + device_id[1] + " download file=" + file_path + " mode=" + \
                      enc_pd_fw_dict["mode_type"]
            self.log.info("Command: %s" % command)
            for x in range(1, 3):
                status, output = self.run_command_raw(command)
                self.log.info(output)
                if status:
                    break
                self.log.error("FW Download command failed %s times" % x)
            if not status:
                self.log.error("PD FW Flash Failed")
                raise SALError("PD Fail to update FW")
            else:
                status_1, output_1 = self.run_command_raw(command_1)
                output_2 = json.loads(output_1)
                output_4 = output_2["Controllers"][0]["Response Data"]["Drives List"][0]["Drive Detailed Information"][
                    "Firmware Revision Level"]
                self.log.info("")
                self.log.info("PD FW Revision after FW Flash: %s" % output_4)
                if output_3 == output_4:
                    self.log.error("PD FW after flash (%s) and before flash (%s) are same" % (output_4, output_3))
                    raise SALError("PD FW Flash Failed")
                else:
                    self.log.info("")
                    self.log.info("PD FW Revision after flash (%s) and before flash (%s) " % (output_4, output_3))
                    self.log.info("PD FW flash success")

        elif enc_pd_fw_dict["device_type"] == "enclosure":
            self.log.info("*******  Enclosure FW Flash is in progress  *******")
            device_id = enc_pd_fw_dict["device_id"].split(" ")
            self.log.info("enclosure_list %s" % self.enclosure_list)
            device_id[0] = str(self.enclosure_list[int(device_id[1]) - 1])
            command_1 = "/E" + device_id[0] + " show all j"
            status_1, output_1 = self.run_command_raw(command_1)
            output_2 = json.loads(output_1)
            output_3 = output_2["Controllers"][0]["Response Data"]["Enclosures"][0][
                "Drive /c" + str(self.ctrl) + "/e" + device_id[0] + " Properties"]["Inquiry Data"][
                "Product Revision Level"]
            self.log.info("")
            self.log.info("Enclosure FW Revision before FW Flash: %s" % output_3)
            command = "/E" + device_id[0] + " download file=" + file_path + " mode=" + \
                      enc_pd_fw_dict["mode_type"]
            self.log.info("Command: %s" % command)

            for x in range(1, 3):
                status, output = self.run_command_raw(command)
                self.log.info(output)
                if status:
                    break
                self.log.error("FW Download command failed %s times" % x)

            if not status:
                self.log.error("Enclosure FW Flash Failed")
                raise SALError("Enclosure Fail to update FW")
            else:
                status_1, output_1 = self.run_command_raw(command_1)
                output_2 = json.loads(output_1)
                output_4 = output_2["Controllers"][0]["Response Data"]["Enclosures"][0][
                    "Drive /c" + str(self.ctrl) + "/e" + device_id[0] + " Properties"]["Inquiry Data"][
                    "Product Revision Level"]
                self.log.info("")
                self.log.info("Enclosure FW Revision after FW Flash: %s" % output_4)

                if output_3 == output_4:
                    self.log.info("")
                    self.log.error(
                        "Enclosure FW after flash (%s) and before flash (%s) are same" % (output_4, output_3))
                    raise SALError("Enclosure FW Flash Failed")
                else:
                    self.log.info("")
                    self.log.info(
                        "Enclosure FW Revision after flash (%s) and before flash (%s) " % (output_4, output_3))
                    self.log.info("Enclosure FW flash success")

    def exec_reset(self, dict):
        """
        This function block handles the flex reset (Ctrl, System and Enclosures)
        Currently it handles the OCR and System Reboot.
        TODO :
        1. Add system powercycle
        2. Add enclosure powercycle
        """
        if dict["subtype"].lower() == "ocr":
            self.reset_obj.issue_ocr()

        elif dict["subtype"].lower() == "reboot":
            self.reset_obj.issue_reboot(dict)

    def exec_bgop(self, step):
        """
        This module is to process BackGround Operations
        Which includes:
        Controller Level : Patrol Read
        VD Level : Background Initialization, Consistency Check, Online Capacity Expansion, VD Erase
        PD Level: Manual Rebuild, Automatic Rebuild, Manual Copy Back, Automatic Copy Back
        """
        op_type = step['bg_op_type']
        self.log.debug("TEST TYPE  : %s" % op_type)
        bg_op_start_stop_pause_resume = step['op_state']
        if not op_type.lower() == "wait_till_bgop_complete":
            wait_till_percentage_of_progress = step['wait_till_percentage_of_progress']
            bgop_monitor = step["bgop_monitor"]
        if op_type.lower() == "patrol_read":
            bg_op_rate = step['bg_op_rate']
            try:
                exclude_vd = step['exclude_vd']
            except KeyError:
                exclude_vd = {}
            try:
                concurrent_pd = step['concurrent_pd_count']
            except:
                concurrent_pd = ''

            self.pr_process_states(op_type, bg_op_rate, bg_op_start_stop_pause_resume, wait_till_percentage_of_progress,
                                   bgop_monitor, exclude_vd, concurrent_pd)
        elif op_type.lower() == "wait_till_bgop_complete":
            wait_type = step['op_state']
            self.wait_till_bgop_complete(wait_type)

    def patrolread_state(self, retry_time=2, retry_count=10):
        """
        To get state of patrol read from sl8
        """
        from sal.sl8 import prStatusGet
        for x in range(retry_count):
            try:
                out = prStatusGet(int(self.ctrl)).state
                break
            except Exception as e:
                if x == (retry_count - 1):
                    self.log.info("Retry exhausted to get PR state")
                    raise SALError("Exception is \n %s" % e)
                self.log.debug("Retry %s to get PR state" % (str(x + 1)))
                time.sleep(retry_time)
        map = {0: "stopped", 2: "active", 3: "paused"}
        return map[out]

    def pr_process_states(self, op_type, bg_op_rate, bg_op_start_stop_pause_resume, wait_till_percentage_of_progress,
                          bgop_monitor, exclude_vd, concurrent_pd):
        """
        This function is to process the patrol read states and move the process to foreground/background
        states will be start, stop, pause, resume
        """

        if len(self.bgop_all_thread) > 0:
            for threads in self.bgop_all_thread:
                if threads[2] == "patrol_read":
                    if threads[0].is_alive():
                        self.log.info(
                            "Again BG OP PR request on the controller stopping the BG OP monitoring on the same")
                        self.stop_pr_flag = 1
                        time.sleep(1)
                        threads[0].join()
                        self.stop_pr_flag = 0
        if self.mr.cli.patrolread_get_mode() == 'OFF':
            self.mr.logging.info("")
            self.mr.logging.info("  PR mode is OFF. Turning PR mode ON")
            self.mr.logging.info("")
            from datetime import timedelta, date
            new_date = date.today() + timedelta(days=10)
            pr_start_time = str(new_date.year) + "/" + str(new_date.month) + "/" + str(new_date.day) + " 12"
            cmd = "ON starttime=" + pr_start_time + " execfrequency hours=168"
            self.mr.cli.patrolread_set(options=cmd)
        if not self.mr.cli.patrolread_get_ssd().lower() == "on":
            self.mr.cli.patrolread_set(options='includeSSDs=on')
        if bg_op_rate:
            current_pr_rate = self.mr.cli.prrate_get()
            if current_pr_rate == int(bg_op_rate):
                self.log.info("PR rate is already set to %s" % bg_op_rate)
            else:
                self.log.info("PR rate is %s. Setting it to %s" % (current_pr_rate, bg_op_rate))
                self.mr.cli.prrate_set(int(bg_op_rate))
                current_pr_rate = self.mr.cli.prrate_get()
                if not current_pr_rate == int(bg_op_rate):
                    raise SALError(
                        "Fail to set patrol read rate to %s current rate is %s" % (bg_op_rate, current_pr_rate))
                else:
                    self.log.info("Patrol read rate set to %s" % str(current_pr_rate))
        if concurrent_pd:
            concurrent_pd = int(concurrent_pd)
            concurrent_pd_count_current = self.mr.get_patrolread_properties()['max_pd']
            self.log.info(
                "Current concurrent pd count is %s requested is %s" % (concurrent_pd_count_current, concurrent_pd))
            if concurrent_pd == concurrent_pd_count_current:
                self.log.info("Current concurrent pd count and requested concurrent pd count are the same")
            try:
                self.mr.set_patrolread_properties(max_pd=concurrent_pd)
            except Exception as e:
                pass
            concurrent_pd_count_updated = self.mr.get_patrolread_properties()['max_pd']
            if concurrent_pd == concurrent_pd_count_updated:
                self.log.info("Concurrent pd count set to %s" % concurrent_pd)
            else:
                self.log.error("Fail to set concurrent pd count to %s current concurrent pd count is %s" % (
                    concurrent_pd, concurrent_pd_count_updated))
                self.log.error("Error message %s" % e)
                raise SALError("Fail to set concurrent pd count to %s" % concurrent_pd)
        self.pr_evt_start_seq = int(self.mr.get_event_seq_info()['newestSeqNum'])
        if bg_op_start_stop_pause_resume.lower() == 'start':
            self.log.info("Request found for start Patrol read")
            self.current_pr_state = self.patrolread_state()
            if self.current_pr_state in ["active", "paused"]:
                self.log.info("Patrol read is active, stopping Patrol read and starting again ")
                pr_stop_event = self.mr.wait_for_event(event_id=avengersalevents.MR_EVT_PD_PR_ABORTED, background=True)
                time.sleep(2)
                self.mr.cli.patrolread_stop()
                time.sleep(5)
                if not self.mr.all_events_found(pr_stop_event):
                    if not self.patrolread_state() == "stopped":
                        self.log.error("Failed to get  MR_EVT_PD_PR_ABORTED event after 5 second from ctrl")
                        raise SALError
                    else:
                        self.log.info("Patrol read stopped on controller")
                else:
                    self.log.info("EVENT found : MR_EVT_PD_PR_ABORTED")
                self.current_pr_state = 'stopped'
            # if len(exclude_vd) != 0:
            #     self.log.info("Request found to exclude VD's, processing now")
            #     exclude_vd_id = []
            #     for key, value in exclude_vd.items():
            #         for id in value:
            #             for id_1 in self.wingman_dg_vd_id_map:
            #                 if str(key) == str(id_1[0]) and str(id) == str(id_1[1]):
            #                     exclude_vd_id.append(int(id_1[2]))
            #                     self.log.info(
            #                         "Wingman dg%s vd%s : actual system vd id to exclude %s" % (
            #                             str(key), str(id), str(id_1[2])))
            #     self.log.info(" Vd List to be excluded from PR is %s" % exclude_vd_id)
            #     exclude_arg1 = [str(i) for i in exclude_vd_id]
            #     exclude_arg = ','.join(map(str, exclude_arg1))
            #     self.mr.cli.patrolread_set(options=('excludevd=%s' % exclude_arg))
            pr_start_event = self.mr.wait_for_event(event_id=avengersalevents.MR_EVT_CTRL_PR_START, background=True)
            pr_done_event = self.mr.wait_for_event(event_id=avengersalevents.MR_EVT_CTRL_PR_DONE, background=True)
            time.sleep(3)
            self.mr.start_patrolread()
            time.sleep(5)
            if not self.mr.all_events_found(pr_start_event):
                if not self.patrolread_state() == "active":
                    self.log.error("Failed to get  MR_EVT_CTRL_PR_START event after 5 second from ctrl")
                    raise SALError
                else:
                    self.log.info("******* Patrol read started on controller ********")
            else:
                self.log.info("EVENT found : MR_EVT_CTRL_PR_START")
                self.log.info("******* Patrol read started on controller ********")
            if wait_till_percentage_of_progress:
                self.get_pr_progress(wait_till_percentage_of_progress)
            if bgop_monitor:
                self.current_pr_state = self.patrolread_state()
                if self.current_pr_state == "active":
                    t1_pr = threading.Thread(name="Patrol Read Monitor", target=self.monitor_pr,
                                             args=(self.current_pr_state,))
                    self.t1_pr_state = [t1_pr, self.current_pr_state, op_type.lower()]
                    self.bgop_all_thread.append([t1_pr, self.current_pr_state, op_type.lower()])
                    t1_pr.start()
                    time.sleep(5)
                else:
                    self.log.info("PR state is not active")
                    if not self.mr.all_events_found(pr_done_event):
                        self.log.error("Failed to get  MR_EVT_CTRL_PR_DONE event from ctrl")
                        raise SALError
        elif bg_op_start_stop_pause_resume.lower() == 'stop':
            self.log.info("Request found for stop Patrol read")
            if wait_till_percentage_of_progress:
                if self.patrolread_state() == "active":
                    self.get_pr_progress(wait_till_percentage_of_progress)
            if self.patrolread_state() in ["active", "paused"]:
                pr_stop_event = self.mr.wait_for_event(event_id=avengersalevents.MR_EVT_PD_PR_ABORTED, background=True)
                time.sleep(3)
                self.mr.cli.patrolread_stop()
                time.sleep(5)
                if not self.mr.all_events_found(pr_stop_event):
                    if not self.patrolread_state() == "stopped":
                        self.log.info("Failed to get  MR_EVT_CTRL_PR_STOP event from ctrl")
                        raise SALError
                    else:
                        self.log.info("Patrol read stopped on controller")
                else:
                    self.log.info("EVENT found : MR_EVT_CTRL_PR_STOP")
                self.log.info("Patrol read stopped on controller")
                if bgop_monitor:
                    self.current_pr_state = self.patrolread_state()
                    if self.current_pr_state == "stopped":
                        t1_pr = threading.Thread(name="Patrol Read Monitor", target=self.monitor_pr,
                                                 args=(self.current_pr_state,))
                        self.t1_pr_state = [t1_pr, self.current_pr_state, op_type.lower()]
                        self.bgop_all_thread.append([t1_pr, self.current_pr_state, op_type.lower()])
                        t1_pr.start()
                    else:
                        self.log.info("PR state is not in stopped state")
            else:
                self.log.info("Patrol read not active or paused to stop on controller")
                self.current_pr_state = self.patrolread_state()
        elif bg_op_start_stop_pause_resume.lower() == 'pause':
            self.log.info("Request found for pause Patrol read")
            if wait_till_percentage_of_progress:
                if self.patrolread_state() == "active":
                    self.get_pr_progress(wait_till_percentage_of_progress)
            if self.patrolread_state() == "active":
                pr_pause_event = self.mr.wait_for_event(event_id=avengersalevents.MR_EVT_CTRL_PR_PAUSE, background=True)
                time.sleep(3)
                self.mr.cli.patrolread_pause()
                time.sleep(5)
                if not self.mr.all_events_found(pr_pause_event):
                    if not self.patrolread_state() == "paused":
                        self.log.info("Failed to get  MR_EVT_CTRL_PR_PAUSE event from ctrl")
                        raise SALError
                    else:
                        self.log.info("Patrol read paused on the controller")
                else:
                    self.log.info("EVENT found : MR_EVT_CTRL_PR_PAUSE")
                self.log.info("Patrol read paused on controller")
                if bgop_monitor:
                    self.current_pr_state = self.patrolread_state()
                    if self.current_pr_state == "paused":
                        t1_pr = threading.Thread(name="Patrol Read Monitor", target=self.monitor_pr,
                                                 args=(self.current_pr_state,))
                        self.t1_pr_state = [t1_pr, self.current_pr_state, op_type.lower()]
                        self.bgop_all_thread.append([t1_pr, self.current_pr_state, op_type.lower()])
                        t1_pr.start()
                    else:
                        self.log.info("PR state is not in paused state")
            else:
                self.log.info("Patrol read not active to pause on controller")
                self.current_pr_state = self.patrolread_state()
        elif bg_op_start_stop_pause_resume.lower() == 'resume':
            self.log.info("Request found for resume Patrol read")
            if self.patrolread_state() in ["paused", "suspended"]:
                pr_resume_event = self.mr.wait_for_event(event_id=avengersalevents.MR_EVT_CTRL_PR_RESUME,
                                                         background=True)
                time.sleep(3)
                self.mr.cli.patrolread_resume()
                time.sleep(5)
                if not self.mr.all_events_found(pr_resume_event):
                    if not self.patrolread_state() == "active":
                        self.log.info("Failed to get  MR_EVT_CTRL_PR_RESUME event from ctrl")
                        raise SALError
                    else:
                        self.log.info("Patrol read resumed on the controller")
                else:
                    self.log.info("EVENT found : MR_EVT_CTRL_PR_RESUME")
                self.log.info("Patrol read resumed on controller")
                if wait_till_percentage_of_progress:
                    self.get_pr_progress(wait_till_percentage_of_progress)
                if bgop_monitor:
                    self.current_pr_state = self.patrolread_state()
                    if self.current_pr_state == "active":
                        t1_pr = threading.Thread(name="Patrol Read Monitor", target=self.monitor_pr,
                                                 args=(self.current_pr_state,))
                        self.t1_pr_state = [t1_pr, self.current_pr_state, op_type.lower()]
                        self.bgop_all_thread.append([t1_pr, self.current_pr_state, op_type.lower()])
                        t1_pr.start()
                    else:
                        self.log.info("PR state is not active")
            else:
                self.log.error("Patrol read not paused to resume on controller")
                self.current_pr_state = self.patrolread_state()
                raise SALError

    def get_pr_progress(self, percent=0):
        """
                This function is to process the patrol read in the foreground
                Till 100% Pr completion or partial PR completion
                """
        self.log.info("Waiting BGOP progress to reach %s" % percent)
        online_pd = self.mr.cli.list_all_drives(state='Onln')
        status, out = self.run_command_raw('/eall/sall show j')
        output = json.loads(out)
        pd_info = output["Controllers"][0]["Response Data"]["Drive Information"]
        self.log.info("online pds %s" % online_pd)
        for pd_id in pd_info:
            if pd_id['State'].lower() in ['advhgood', 'hgood', 'jbod']:
                self.log.debug("PD %s is hgood or advhgood" % pd_id['EID:Slt'])
                if pd_id['EID:Slt'] in online_pd:
                    online_pd.remove(pd_id['EID:Slt'])
                    self.log.info("Removed %s jbod/advhgood from online pd list" % pd_id['EID:Slt'])
        dhs = self.mr.cli.list_all_drives(state='DHS')
        ghs = self.mr.cli.list_all_drives(state='GHS')
        online_pds = online_pd + dhs + ghs
        status, out = self.run_command_raw('show pr j')
        output = json.loads(out)
        pr_info = output["Controllers"][0]["Response Data"]["Patrol Read Properties"]
        exclude_info = "None"
        for info in pr_info:
            if info['PR Property'] == "Excluded VDs":
                exclude_info = info["Value"]
                break
        if exclude_info != "None":
            exclude_info = [int(vd) for vd in exclude_info.split(",")]
            self.log.info("%s VD list excluded for the Patrol read" % exclude_info)
            for vd in exclude_info:
                pd_in_vd = self.mr.cli.list_pds_in_vd(vd)
                for pd in pd_in_vd:
                    if pd in online_pds:
                        online_pds.remove(pd)
                        self.log.info("Removing pd %s info from online pd's" % pd)
        break_flag = 0
        progress_flag = 10
        started_pds = []
        pr_evt_start_seq = self.pr_evt_start_seq
        while 1:
            time.sleep(5)
            if len(online_pds) == 0:
                break
            for pd in online_pds:
                time.sleep(1)
                if not pd in started_pds:
                    state = self.get_pr_status(self.ctrl, pd)
                    if state == "active":
                        started_pds.append(pd)
                        self.log.info("PR running on Pd :%s" % pd)
                progress = self.pr_progress(pd)
                if progress_flag == int(progress):
                    self.log.info("PR Progress reached %s percent on pd %s" % (progress_flag, pd))
                    for pds in online_pds:
                        if pds != pd:
                            progress = self.pr_progress(pds)
                            self.log.info("PR Progress reached %s percent on pd %s" % (progress, pds))
                    progress_flag = progress_flag + 10
                if percent == 100:
                    if not self.patrolread_state() == "active":
                        self.log.info("PR state is not alive on controller")
                        evt_logger = mr_events8.EventLogCache(self.mr, start_seq=pr_evt_start_seq)
                        awatcher = mr_events8.Watcher(evt_logger, code=avengersalevents.MR_EVT_CTRL_PR_DONE)
                        awatcher.set_start_point(val=0)
                        for retry in range(1, 6):
                            pr_done_result = awatcher.found(force_update=True)
                            if pr_done_result:
                                break
                            else:
                                time.sleep(10)
                        if not pr_done_result:
                            raise SALError("PR completion not found")
                        else:
                            self.log.info("PR completion found")
                            if not len(online_pds) == len(started_pds):
                                raise SALError(
                                    "PR not started on all online pds %s is the online pd and %s is the list of PR "
                                    "started pds" % (
                                        online_pds, started_pds))
                            break_flag = 1
                            break
                else:
                    if int(progress) >= percent:
                        break_flag = 1
                        break
                    if not self.patrolread_state() == "active":
                        self.log.info("PR state is not alive on controller")
                        evt_logger = mr_events8.EventLogCache(self.mr, start_seq=pr_evt_start_seq)
                        awatcher = mr_events8.Watcher(evt_logger, code=avengersalevents.MR_EVT_CTRL_PR_DONE)
                        awatcher.set_start_point(val=0)
                        for retry in range(1, 6):
                            pr_done_result = awatcher.found(force_update=True)
                            if pr_done_result:
                                break
                            else:
                                time.sleep(10)
                        if not pr_done_result:
                            raise SALError("PR completion not found")
                        else:
                            self.log.info("PR completion found")
                            if not len(online_pds) == len(started_pds):
                                raise SALError(
                                    "PR not started on all online pds %s is the online pd and %s is the list of PR "
                                    "started pds" % (online_pds, started_pds))
                            break_flag = 1
                            break
            if break_flag == 1:
                self.log.info("PR progress percent reached >= %s" % percent)
                break

    def monitor_pr(self, state="active"):
        """
        Monitor patrol read in background
        It will monitor PR active/stopped/paused states
        """
        try:
            self.log.info("Monitoring BGOP PR progress/status")
            counter_ = 0
            t1_pr_state = self.t1_pr_state
            self.t1_pr_state = []
            pr_evt_start_seq = self.pr_evt_start_seq
            if state == "active":
                self.log.info("BG OPS PR under monitor starts")
                pr_complete_event = self.mr.wait_for_event(event_id=avengersalevents.MR_EVT_CTRL_PR_DONE,
                                                           background=True)
                time.sleep(1)
                while 1:
                    if self.stop_pr_flag == 1:
                        self.log.info("Stopping Monitoring of Patrol read")
                        break
                    if not self.patrolread_state(retry_time=10, retry_count=30) == "active":
                        self.log.info("pr state is not alive")
                        try:
                            evt_logger = mr_events8.EventLogCache(self.mr, start_seq=pr_evt_start_seq)
                        except:
                            evt_logger = mr_events8.EventLogCache(self.mr, start_seq="bootSeqNum")
                        awatcher = mr_events8.Watcher(evt_logger, code=avengersalevents.MR_EVT_CTRL_PR_DONE)
                        awatcher.set_start_point(val=0)
                        for retry in range(1, 6):
                            pr_done_result = awatcher.found(force_update=True)
                            if pr_done_result:
                                break
                            else:
                                time.sleep(10)
                        if not pr_done_result:
                            if self.mr.all_events_found(pr_complete_event):
                                self.log.info("PR completion event found")
                            else:
                                self.log.error("PR completion event not found and PR state is not active")
                                self.thread_exceptions[
                                    "BGOP_Patrol read"] = "PR completion event not found and PR state is not active"
                        else:
                            self.log.info("Patrol read completed")
                        break
                    if time.time() > counter_ + 120:
                        self.log.info("BG OP PatrolRead is active, it will take time to complete")
                        counter_ = time.time()
                    time.sleep(10)

            elif state == "paused":
                while 1:
                    if self.stop_pr_flag == 1:
                        self.log.info("Stopping Monitoring of Patrol read")
                        break
                    if not self.patrolread_state() == "paused":
                        self.log.error("PR State changed from paused to %s" % (self.patrolread_state()))
                        self.thread_exceptions["BGOP_Patrol read"] = "PR State changed from paused to " + str(
                            self.patrolread_state())
                        break
                    else:
                        if time.time() > counter_ + 120:
                            self.log.info("BG OPS PR under monitor, it will take time to complete")
                            counter_ = time.time()
                    time.sleep(10)
            elif state == "stopped":
                while 1:
                    if self.stop_pr_flag == 1:
                        self.log.info("Stopping Monitoring of Patrol read")
                        break
                    if not self.patrolread_state() == "stopped":
                        self.log.error("PR State changed from stopped to %s" % (self.patrolread_state()))
                        self.thread_exceptions["BGOP_Patrol read"] = "PR State changed from stopped to " + str(
                            self.patrolread_state())
                        break
                    else:
                        if time.time() > counter_ + 120:
                            self.log.info("BG OPS PR under monitor, it will take time to complete")
                            counter_ = time.time()
                    time.sleep(10)
            self.bgop_all_thread.remove(t1_pr_state)
        except Exception as e:
            self.thread_exceptions["BGOP_Patrol read"] = "Script Exception in the threading : %s" % e
        self.log.info("***************** Exit from PR thread ********************")

    def get_pr_status(self, ctrl_index, pd):
        """
        To Get the Patrol Read status
        Return will be active/paused/stopped
        """
        for x in range(1, 10):
            try:
                esid = pd.split(':')
                command = "/E" + esid[0] + "/S" + esid[1] + " SHOW PR"
                status, raw_output = self.run_command_raw(command)
                if status:
                    output = raw_output.upper().split('\n')
                    for line in range(len(output)):
                        if output[line].find('PROGRESS%') >= 0:  # Header of the PD table
                            line += 2
                            break
                    if line > len(output):
                        line
                        return -1
                    line_list = output[line].split()
                    status = line_list[3].lower()
                    if status == "in":
                        status = "active"
                    elif status == "not":
                        status = "stopped"
                    elif status == "paused" or status == "suspended":
                        status = "paused"
                    else:
                        status = -1
                else:
                    status = -1
            except:
                status = -1
            if not status == -1:
                break
            else:
                time.sleep(45)
        return status

    def pr_progress(self, pd):
        """
        To get the PR progress percent of the PD
        """
        esid = pd.split(':')
        command = "/E" + esid[0] + "/S" + esid[1] + " SHOW PR"
        status, raw_output = self.run_command_raw(command)
        if status:
            output = raw_output.upper().split('\n')
            for line in range(len(output)):
                if output[line].find('PROGRESS%') >= 0:  # Header of the PD table
                    line += 2
                    break
            if line > len(output):
                line
                return -1
            line_list = output[line].split()
            percent = line_list[1]
            try:
                float(percent)
            except ValueError:
                return -1
            return percent
        else:
            return -1

    def execute_bgop_all_thread_update_b4_reboot(self):
        """
        To stop the bgop threads before system go for the reboot/power cycle
        This function is neccessary when system go for the reboot/power cycle
        """
        self.evt_start_seq_b4_reboot = int(self.mr.get_event_seq_info()['newestSeqNum'])
        self.log.debug("evt_start_seq_b4_reboot %s" % self.evt_start_seq_b4_reboot)

        bgop_all_thread_copy = list(self.bgop_all_thread)
        for threads1 in bgop_all_thread_copy:
            if isinstance(threads1[0], threading.Thread):
                if threads1[0].is_alive():
                    if threads1[2] == "patrol_read":
                        self.stop_pr_flag = 1
                        time.sleep(1)
                        threads1[0].join()
                        self.stop_pr_flag = 0

                del threads1[0]
        self.bgop_all_thread = list(bgop_all_thread_copy)
        for threads1 in bgop_all_thread_copy:
            if threads1[1] in ["vd_erase", "fast_init", "full_init"]:
                self.bgop_all_thread.remove(threads1)

        self.t1_pr_state = []

        self.log.info("Exiting all the BGOP threads before reboot")

    def exceute_bgop_all_thread_after_reboot(self):
        """
        This function is to start BGOP threads after system resuming from reboot/power cycle
        """
        temp_remove_entry = []
        if len(self.bgop_all_thread) > 0:
            try:
                evt_logger = mr_events8.EventLogCache(self.mr, start_seq=self.evt_start_seq_b4_reboot)
            except:
                evt_logger = mr_events8.EventLogCache(self.mr, start_seq="bootSeqNum")
        for threads in self.bgop_all_thread:
            if threads[1] == "patrol_read":
                if threads[0] == "active":
                    self.current_pr_state = self.patrolread_state()
                    if self.current_pr_state == threads[0]:
                        awatcher = mr_events8.Watcher(evt_logger, code=avengersalevents.MR_EVT_CTRL_PR_RESUME)
                        awatcher.set_start_point(val=0)
                        temp_search = awatcher.found(force_update=True)
                        if not temp_search:
                            raise SALError("Patrol read is not resumed after reboot")
                        else:
                            self.log.info("Patrol read successfully resumed after reboot")
                        if self.patrolread_state() == threads[0]:
                            t1_pr = threading.Thread(name="Patrol Read Monitor", target=self.monitor_pr,
                                                     args=(self.current_pr_state,))
                            self.t1_pr_state = [t1_pr, self.current_pr_state, threads[1]]
                            threads.insert(0, t1_pr)
                            t1_pr.start()
                        else:
                            self.log.info("Patrol read completed")
                            temp_remove_entry.append(threads)
                    else:
                        awatcher = mr_events8.Watcher(evt_logger, code=avengersalevents.MR_EVT_CTRL_PR_DONE)
                        awatcher.set_start_point(val=0)
                        temp_search1 = awatcher.found(force_update=True)
                        if not temp_search1:
                            raise SALError("Patrol read is not active after reboot and PR completion not found")
                        else:
                            self.log.info("Patrol read is not active after reboot")
                            self.log.info("Patrol read completion event found")
                            temp_remove_entry.append(threads)
                elif threads[0] == "stopped":
                    self.current_pr_state = self.patrolread_state()
                    if self.current_pr_state == threads[0]:
                        t1_pr = threading.Thread(name="Patrol Read Monitor", target=self.monitor_pr,
                                                 args=(self.current_pr_state,))
                        self.t1_pr_state = [t1_pr, self.current_pr_state, threads[1]]
                        threads.insert(0, t1_pr)
                        t1_pr.start()
                    else:
                        self.log.info("PR state is not in stopped state after reboot")
                        raise SALError
                elif threads[0] == "paused":
                    self.current_pr_state = self.patrolread_state()
                    if self.current_pr_state == threads[0]:
                        t1_pr = threading.Thread(name="Patrol Read Monitor", target=self.monitor_pr,
                                                 args=(self.current_pr_state,))
                        self.t1_pr_state = [t1_pr, self.current_pr_state, threads[1]]
                        threads.insert(0, t1_pr)
                        t1_pr.start()
                    else:
                        self.log.info("PR state is not in paused state after reboot")
                        raise SALError

            time.sleep(1)
        for entry in temp_remove_entry:
            if entry in self.bgop_all_thread:
                self.bgop_all_thread.remove(entry)

        time.sleep(5)

    def eot_bgop(self):
        """
        To stop bgop during the end of test
        """
        while self.bgop_all_thread:
            try:
                if self.bgop_all_thread[0][0].is_alive() and self.bgop_all_thread[0][1] == "active":
                    self.bgop_all_thread[0][0].join()
                elif (self.bgop_all_thread[0][0].is_alive()) and (
                        self.bgop_all_thread[0][1] in ["paused", "stopped"]):
                    temp_thread = self.bgop_all_thread[0][0]
                    if self.bgop_all_thread[0][2] == "patrol_read":
                        self.stop_pr_flag = 1
                        time.sleep(2)
                        temp_thread.join()
                        self.stop_pr_flag = 0
            except AttributeError:
                pass

    def check_bgop_exception(self):
        """
        To check BGOP exceptions during threaded operation
        """
        self.log.info("BGOP Exceptions : %s" % self.thread_exceptions)
        if len(self.thread_exceptions) > 0:
            for key, value in self.thread_exceptions.items():
                self.log.error("Error in BGOP %s : error is %s" % (key, value))
            raise SALError

    def bgop_cleanup(self):
        """
        To cleanup bgop functions during teardown
        """
        try:
            self.log.debug("BG OP Teardown Block!")
            bgop_all_thread_copy = list(self.bgop_all_thread)
            self.log.debug("bgop_all_thread details %s" % bgop_all_thread_copy)
            for threads1 in bgop_all_thread_copy:
                if type(threads1[0]) == threading.Thread:
                    if threads1[0].is_alive():
                        if threads1[2] == "patrol_read":
                            self.stop_pr_flag = 1
                            time.sleep(1)
                            threads1[0].join()
                            self.stop_pr_flag = 0
        except Exception as e:
            self.log.debug("BG OP Teardown Block, needs a Look -> %s" % e)
        self.bgop_all_thread = []

    def wait_till_bgop_complete(self, wait_type):
        """
        To complete BGOP threaded operations which is running in background
        This function will run in foreground
        """
        self.log.info("Request find for wait till completion of back ground BGOP : %s" % wait_type)
        temp_bgop_all_thread = list(self.bgop_all_thread)
        if not len(temp_bgop_all_thread) > 0:
            self.log.warning("No back ground BGOP found to wait till completion")
        else:
            for thread in temp_bgop_all_thread:
                if type(thread[0]) == threading.Thread and thread[0].is_alive:
                    if thread[2] == "patrol_read" and wait_type == "patrol_read":
                        self.log.info("Patrol read running in background waiting till it complete")
                        thread[0].join()
                        self.log.info("Patrol read completed moving further")
                    elif wait_type == "all_running_bgop":
                        self.log.info("%s running in background waiting till it complete" % thread[2])
                        thread[0].join()
                        self.log.info("%s completed moving further" % thread[2])
        self.log.info("All requested background thread completion found")


    def exec_snapdump(self, dict):
        """
        Takes the snapdump dictionary and acts accordingly.
                {
            "expected_result": "pass",
            "step": 1,
            "step_reference": [],
            "step_wait": "",
            "stop_io": "",
            "subtype": "Delete OnDemand",
            "type": "snapdump"
        },
        {
            "expected_result": "pass",
            "step": 2,
            "step_reference": [],
            "step_wait": "",
            "stop_io": "",
            "subtype": "Verify OnDemand",
            "type": "snapdump"
        },
        {
            "expected_result": "pass",
            "step": 3,
            "step_reference": [],
            "step_wait": "",
            "stop_io": "",
            "subtype": "Generate OnDemand",
            "type": "snapdump"
        },
        {
            "expected_result": "pass",
            "step": 4,
            "step_reference": [],
            "step_wait": "",
            "stop_io": "",
            "subtype": "Delete All",
            "type": "snapdump"
        }
        """
        prof = Profile()
        if dict["subtype"].lower() == "generate ondemand":
            self.sd_obj.generate_sd_ondemand()
            self.sd_obj.get_snapdump()
            self.sd_obj.verify_sd_type()
            self.sd_obj.move_sd_zip()
            self.sd_obj.unzip_last_snapdump()
            self.sd_obj.check_empty_files()

        if dict["subtype"].lower() == "delete all":
            self.sd_obj.delete_snapdump()

        if dict["subtype"].lower() == "verify ondemand":
            # other possible values will need to be tested.
            self.sd_obj.verify_sd_type()

    def init_crash_monitor(self):
        """
        Using the check_events, we can now check for registered events across reboots as well.
        # 2 things needs to go here
        # 1. AEN based Check
        # 2. TODO : Snapdump based check
        # Register for crash events
        """
        self.crash_evt = []
        self.crash_evt.append(self.mr.check_event(event_id=MR_EVT_CTRL_CRASH, background=True))
        self.log.info("")
        self.log.info(">>> Controller crash monitor initialized")
        self.log.info("")

    def check_crash_events(self):
        """
        Check for registered crash events.
        """
        self.log.info(">>> Checking for crash event presence")
        if self.mr.all_events_found(self.crash_evt):
            self.log.info("")
            self.log.info(">>> MR_EVT_CTRL_CRASH event was found during current step execution.")
            self.log.info("")


class Snapdump:
    """
    Class to handle all operations pertaining to snapdump requirements of the test cases + step end check.
    """
    meta = {
        "last_snapdump": [],
        "all_snapdump": [],
        "code_not_ok": [
            'faultcode 0x86cf',
            'faultcode 0x893e',
            'faultcode 0xa00893e',
            'faultcode 0x4008600'
        ],
        "str_validate": [],
        "files_to_check": ["crashdump.txt"],
        "empty_files": ["writejrnl.txt"],
        "count": 0
    }

    def __init__(self, wm):
        self.wm = wm
        self.log = wm.log

    def generate_sd_ondemand(self):
        """
        This function does a few things for the test case.
        1. Generates Snapdump
        2. Get's the snapdump (created in cli path)
        3. Moves the snapdump to Test log folder.
        4. In last_snapdump key of the Snapdump class dictionary, enters required details as needed.
        5. Increments the count of all snapdumps created
        5. Once done, return the snapdump information in dictionary
        """
        self.log.info(">>> Generating Snapdump ONDEMAND")
        snpdmp = self.wm.mr.generate_snapdump_ondemand()
        Snapdump.meta["last_snapdump"] = snpdmp
        Snapdump.meta["last_snapdump"]["timestamp"] = ""
        self.log.debug("Snapdump Properties : {}".format(self.wm.mr.get_snapdump_properties()))
        self.log.debug("Snapdump all        : {}".format(Snapdump.meta["all_snapdump"]))
        self.log.debug("Snapdump last       : {}".format(Snapdump.meta["last_snapdump"]))
        Snapdump.meta["count"] += 1
        return snpdmp

    def get_snapdump(self):
        self.wm.mr.get_snapdump()

    def delete_snapdump(self):
        """
        This will delete all the snapdump on the controller and reset few values of Snapdump class dictionary to
        initial values like last_snapdump. All values don't need to be reset as the count of the snapdump will be
        maintained across the entire run as we may have multiple SD generation and delete request and we will end
        of extracting them in a folder (created in the test log folder) with the ID of the SD, tracked by the
        WM framework.
        """
        self.wm.mr.delete_snapdump()
        self.log.info(">>> All Snapdumps on the controller has been deleted")
        Snapdump.meta["last_snapdump"] = {}

    def verify_sd_type(self, sd_type="ondemand", safe=["ondemand"]):
        # Check if this Snapdump has been tracked already
        # Verify the time stamps of SL based and CLI based outputs

        try:
            snpdmp_op = self.wm.mr.cli.snapdump_show()
        except ValueError:
            snpdmp_op = {}

        if not snpdmp_op:
            get_logger().info(">>> No snapdumps reported on controller")
            return

        timestamp = snpdmp_op[-1]["TIMESTAMP(LOCALTIME YYYY/MM/DD HH:MM:SEC)"]

        if not self.check_processed_sd(snpdmp_op, timestamp):
            self.log.info(">>> Verifying if last snapdump was of type    : {}".format(sd_type.upper()))
            self.log.info(">>> Total number of SDs generated till now    : {}".format(Snapdump.meta["count"]))
            self.log.info(">>> Total number of SDs present on Controller : {}".format(len(snpdmp_op)))
            self.log.info(">>> Last SD Timestamp reported in CLI         : {}".format(timestamp))
            self.log.info(">>> Last SD details as tracked by WM          : {}".format(
                Snapdump.meta["last_snapdump"]["timestamp"]))
            get_logger().info("")
            self.log.info(">>> New Snapdump seen, analyzing type")
            if str(snpdmp_op[-1]['TRIGGER TYPE'].upper()) == sd_type.upper() and\
                    str(snpdmp_op[-1]['TRIGGER TYPE'].lower()) in safe:
                get_logger().info(">>> Last Snapdump ID {} was {} and safe".format(
                    snpdmp_op[-1]['ID'], snpdmp_op[-1]["TRIGGER TYPE"]))
            else:
                raise SALError(">>> Last snapdump ID {} is of type : {} and not expected.".format(
                    snpdmp_op[-1]['ID'], snpdmp_op[-1]["TRIGGER TYPE"]))
            get_logger().info("")

    def check_processed_sd(self, snpdmp_op, timestamp):
        """
        If a snapdump has been already checked and marked safe, we will skip the check
        Snapdump.meta["last_snapdump"] contains last processed / generated snapdump. Hence using the same
        to check the processed information.
        """
        last_snapdump = Snapdump.meta["last_snapdump"]
        last_timestamp = last_snapdump.get("timestamp")
        last_id = last_snapdump.get("snapdump_id")

        if last_timestamp and last_timestamp == timestamp:
            # Also check the IDs
            if int(last_id) == int(snpdmp_op[-1]["ID"]):
                self.log.info(">>> Last snapdump was ID {}, Size {} generated at {}, type {} and has been marked safe."
                              .format(last_id, last_snapdump["size"], timestamp, snpdmp_op[-1]["TRIGGER TYPE"]))
            return True
        elif last_id and int(last_id) == int(snpdmp_op[-1]["ID"]):
            # Is a snapdump get is not done, tag_sd_zip will return a None.
            # So if the last snapdump timestamp is none, populate its timestamp
            last_snapdump["timestamp"] = timestamp
            return False

    def tag_sd_zip(self):
        """
        This function tags the snapdump in the Snapdump's all SD entries. Then sends the file path
        to tag it with last_snapdump dictionary. This then returns the file path of the last SD which
        is tagged to the last_snapdump information.
        """
        for file in os.listdir(os.getcwd()):
            if zipfile.is_zipfile(file) and file.startswith("snapdump"):
                file = os.path.abspath(file)
                if file not in Snapdump.meta['all_snapdump']:
                    Snapdump.meta["all_snapdump"].append(file)
                    return file

    def move_sd_zip(self):
        """
        From storcli location to test log folder
        TODO :
        Scan for already existing sds at start of test
        As of now, will be working with SAL's ability to handle this.
        """
        # Once the snapdump get command is executed, the timestamp is populated
        Snapdump.meta["last_snapdump"]["file"] = self.tag_sd_zip()
        last_snpdmp_info = os.path.basename(Snapdump.meta["last_snapdump"].get("file", "")).split("_")
        Snapdump.meta["last_snapdump"]["timestamp"] = last_snpdmp_info[-1].split(".")[0]
        cli_path = os.path.dirname(self.wm.mr.cli.full_cli_path)
        for file in os.listdir(cli_path):
            if zipfile.is_zipfile(file) and file.startswith("snapdump"):
                self.log.info("Moving snapdump file : {}".format(file))
                shutil.move(file, self.get_unzip_dir(Snapdump.meta["count"]))
                break

    def check_empty_files(self):
        """
        When a SD is generated, it needs to be unzipped and all the files in the zip needs to be checked if empty.
        This is a PT requirement and hence, implemented here. Now, since each newly generated snapdump is tagged
        as last_snapdump, so this checked the last generated snapdump files.
        """
        unexpected_empty_files = []
        self.log.info("Last unzipped file : {}".format(Snapdump.meta['last_snapdump']['unzipped']))
        for file_name in os.listdir(Snapdump.meta['last_snapdump']['unzipped']):
            file_path = os.path.join(Snapdump.meta['last_snapdump']['unzipped'], file_name)
            file_size = os.stat(file_path).st_size
            if file_size == 0:
                file_name = os.path.basename(file_name).lower()
                if file_name in Snapdump.meta['empty_files']:
                    self.log.info(" >> {} is okay to be empty, ignoring".format(file_name.upper()))
                else:
                    unexpected_empty_files.append(file_name)
            else:
                size_str = "{}KB".format(int(file_size / 1024)) if file_size >= 1024 else "{} bytes".format(file_size)
                self.log.info(" >> VALID file: {} (size: {})".format(file_name.upper(), size_str))

        if unexpected_empty_files:
            file_names_str = "\n".join(map(str.upper, unexpected_empty_files))
            self.log.info("Below files are empty and not expected:\n{}".format(file_names_str))
            raise SALError("Above files were empty and not expected.")

    def unzip_last_snapdump(self):
        """
        Extracts the last snapdump.zip file in the directory and saves it in a new directory
         named after the ID of the snapdump.
        """
        snapdump = Snapdump.meta['last_snapdump']
        snapdump_id = snapdump['snapdump_id']
        file_path = snapdump['file']

        snapdump_dir = get_snapdump_dir()
        self.log.info(">>> Snapdump Dir is   : {}".format(snapdump_dir))
        self.log.info(">>> Last Snapdump is  : {}".format(snapdump))

        new_dir = self.get_unzip_dir(snapdump_id)
        snapdump['unzipped'] = new_dir

        with ZipFile(file_path, 'r') as z_object:
            z_object.extractall(path=new_dir)

        self.log.info("Unzipped Snapdump ID {} in location: {}".format(snapdump_id, new_dir))

    def get_unzip_dir(self, id):
        """
        Create a directory in the test log folder tagged to the ID and returns the path
        """
        new_dir = os.path.join(get_snapdump_dir(), ('USER_snapdump_file_id_{}'.format(str(id))))
        self.log.info("New SD dir is   : {}".format(new_dir))
        if os.path.isdir(new_dir):
            return new_dir
        os.mkdir(new_dir)
        return new_dir

    def check_snapdump_code(self):
        """
        This checks the fault code of the Snapdump generated takes the analysis from analyze_fault_code() Code + Result
        which is then dealt with, accordingly.
        """
        fault_codes = {}
        self.log.info("Last unzipped file : {}".format(Snapdump.meta["last_snapdump"]["unzipped"]))
        for file in os.listdir(Snapdump.meta["last_snapdump"]["unzipped"]):
            if file.lower() in Snapdump.meta["files_to_check"]:
                with open(os.path.join(Snapdump.meta["last_snapdump"]["unzipped"], file), "r") as fp:
                    line = fp.readline()
                    if 'FaultCode' in line:
                        fault_codes[file] = line.replace("\n", "")
                        break
        self.log.debug("All data is : {}".format(fault_codes))
        for key, val in fault_codes.iteritems():
            self.log.info("Check val : {}".format(val))
            fault_code, res = self.analyze_fault_code(val)
            if not res:
                raise SALError(">>> File {} has fault code {}, which is not acceptable!".format(key.upper(),
                                                                                                fault_code.upper()))
            get_logger().info(">>> Fault Code seen in file {} is OK to proceed : {}".format(key.upper(),
                                                                                            fault_code.upper()))

    def analyze_fault_code(self, line):
        """
        Based on what fault code is seen, code and result (True / False) is returned to the calling function
        """
        j = line.split()
        fault_codes = [' '.join(j[i:i + 2]) for i in range(len(j) - 1) if j[i].lower() == 'faultcode']
        fault_code = fault_codes[0]
        get_logger().info(">>> Fault code returned is: {}".format(fault_code.upper()))

        if fault_code.lower() not in (Snapdump.meta["code_not_ok"]) and not any(
            re.findall(r'f00[0-6]', fault_code.lower(), re.IGNORECASE)):
            return fault_code, False
        else:
            return fault_code, True

if __name__ == '__main__':
    sys.argv.append('--nocq')  # unComment later
    wingmanFlex().run()

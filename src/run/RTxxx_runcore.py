#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import RTxxx_rundef
import boot
sys.path.append(os.path.abspath(".."))
from gen import RTxxx_gencore
from ui import RTxxx_uidef
from ui import uidef
from ui import uivar
from ui import uilang
from boot import bltest
from boot import target
from utils import misc

def RTxxx_createTarget(device, exeBinRoot):
    # Build path to target directory and config file.
    cpu = "MIMXRT685"
    if device == RTxxx_uidef.kMcuDevice_iMXRT500:
        cpu = "MIMXRT595"
    elif device == RTxxx_uidef.kMcuDevice_iMXRT600:
        cpu = "MIMXRT685"
    else:
        pass
    targetBaseDir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'targets', cpu)

    # Check for existing target directory.
    if not os.path.isdir(targetBaseDir):
        targetBaseDir = os.path.join(os.path.dirname(exeBinRoot), 'src', 'targets', cpu)
        if not os.path.isdir(targetBaseDir):
            raise ValueError("Missing target directory at path %s" % targetBaseDir)

    targetConfigFile = os.path.join(targetBaseDir, 'bltargetconfig.py')

    # Check for config file existence.
    if not os.path.isfile(targetConfigFile):
        raise RuntimeError("Missing target config file at path %s" % targetConfigFile)

    # Build locals dict by copying our locals and adjusting file path and name.
    targetConfig = locals().copy()
    targetConfig['__file__'] = targetConfigFile
    targetConfig['__name__'] = 'bltargetconfig'

    # Execute the target config script.
    execfile(targetConfigFile, globals(), targetConfig)

    # Create the target object.
    tgt = target.Target(**targetConfig)

    return tgt, targetBaseDir

class secBootRTxxxRun(RTxxx_gencore.secBootRTxxxGen):

    def __init__(self, parent):
        RTxxx_gencore.secBootRTxxxGen.__init__(self, parent)
        if self.mcuSeries == uidef.kMcuSeries_iMXRTxxx:
            self.RTxxx_initRun()

    def RTxxx_initRun( self ):
        self.blhost = None
        self.tgt = None
        self.cpuDir = None
        self.blhostVectorsDir = os.path.join(self.exeTopRoot, 'tools', 'blhost2_3', 'win', 'vectors')

        self.RTxxx_isDeviceEnabledToOperate = True

        self.RTxxx_createMcuTarget()

    def RTxxx_createMcuTarget( self ):
        self.tgt, self.cpuDir = RTxxx_createTarget(self.mcuDevice, self.exeBinRoot)

    def RTxxx_getUsbid( self ):
        self.RTxxx_createMcuTarget()
        return [self.tgt.romUsbVid, self.tgt.romUsbPid]

    def RTxxx_connectToDevice( self , connectStage):
        if connectStage == uidef.kConnectStage_Rom:
            # Create the target object.
            self.RTxxx_createMcuTarget()
            if self.isUartPortSelected:
                blPeripheral = 'uart'
                uartComPort = self.uartComPort
                uartBaudrate = int(self.uartBaudrate)
                usbVid = ''
                usbPid = ''
            elif self.isUsbhidPortSelected:
                blPeripheral = 'usb'
                uartComPort = ''
                uartBaudrate = ''
                usbVid = self.tgt.romUsbVid
                usbPid = self.tgt.romUsbPid
            else:
                pass
            self.blhost = bltest.createBootloader(self.tgt,
                                                  self.blhostVectorsDir,
                                                  blPeripheral,
                                                  uartBaudrate, uartComPort,
                                                  usbVid, usbPid,
                                                  True)
        elif connectStage == uidef.kConnectStage_Reset:
            self.tgt = None
        else:
            pass

    def RTxxx_pingRom( self ):
        status, results, cmdStr = self.blhost.getProperty(boot.properties.kPropertyTag_CurrentVersion)
        self.printLog(cmdStr)
        return (status == boot.status.kStatus_Success)

    def RTxxx_getMcuDeviceInfoViaRom( self ):
        self.printDeviceStatus("--------MCU device Register----------")

    def RTxxx_getBootDeviceInfoViaRom ( self ):
        if self.bootDevice == RTxxx_uidef.kBootDevice_FlexspiNor:
            self.printDeviceStatus("--------FlexSPI NOR memory--------")
            pass
        elif self.bootDevice == RTxxx_uidef.kBootDevice_QuadspiNor:
            self.printDeviceStatus("--------QuadSPI NOR memory--------")
            pass
        elif self.bootDevice == RTxxx_uidef.kBootDevice_FlexcommSpiNor:
            self.printDeviceStatus("--Flexcomm SPI NOR/EEPROM memory--")
            pass
        elif self.bootDevice == RTxxx_uidef.kBootDevice_UsdhcSd:
            self.printDeviceStatus("--------uSDHC SD Card info--------")
            pass
        elif self.bootDevice == RTxxx_uidef.kBootDevice_UsdhcMmc:
            self.printDeviceStatus("--------uSDHC MMC Card info-------")
            pass
        else:
            pass

    def RTxxx_configureBootDevice ( self ):
        return True

    def RTxxx_resetMcuDevice( self ):
        status, results, cmdStr = self.blhost.reset()
        self.printLog(cmdStr)
        return (status == boot.status.kStatus_Success)
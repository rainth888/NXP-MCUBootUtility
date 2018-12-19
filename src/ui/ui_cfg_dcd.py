#! /usr/bin/env python
import wx
import sys
import os
import shutil
import uidef
import uivar
sys.path.append(os.path.abspath(".."))
from win import bootDeviceWin_DCD
from gen import gendef
from run import rundef

class secBootUiCfgDcd(bootDeviceWin_DCD.bootDeviceWin_DCD):

    def __init__(self, parent):
        bootDeviceWin_DCD.bootDeviceWin_DCD.__init__(self, parent)
        dcdCtrlDict, dcdSettingsDict = uivar.getBootDeviceConfiguration(uidef.kBootDevice_Dcd)
        self.dcdCtrlDict = dcdCtrlDict
        self.dcdSettingsDict = dcdSettingsDict
        self.destBinFilename = None
        self.destCfgFilename = None
        self.dcdModelFolder = None
        self._recoverLastSettings()

    def setNecessaryInfo( self, binFilename, cfgFilename, dcdModelFolder ):
        self.destBinFilename = binFilename
        self.destCfgFilename = cfgFilename
        self.dcdModelFolder = dcdModelFolder


    def _recoverLastSettings ( self ):
        self.m_choice_dcdSource.SetSelection(self.m_choice_dcdSource.FindString(self.dcdSettingsDict['dcdSource']))
        self._getDcdSource()
        self.m_filePicker_dcdBinFile.SetPath(self.dcdSettingsDict['userBinFile'])
        self.m_filePicker_dcdCfgFile.SetPath(self.dcdSettingsDict['userCfgFile'])
        self.m_choice_dcdPurpose.SetSelection(self.m_choice_dcdPurpose.FindString(self.dcdSettingsDict['dcdPurpose']))
        self._getDcdPurpose()
        if self.dcdSettingsDict['sdramBase'] != None:
            self.m_textCtrl_sdramBase.Clear()
            self.m_textCtrl_sdramBase.write(self.dcdSettingsDict['sdramBase'])
        self.m_choice_dcdModel.SetSelection(self.m_choice_dcdModel.FindString(self.dcdSettingsDict['deviceModel']))
        self._getDeviceModel()
        if self.dcdSettingsDict['dcdDesc'] != None:
            self.m_textCtrl_dcdDesc.Clear()
            self.m_textCtrl_dcdDesc.write(self.dcdSettingsDict['dcdDesc'])

    def _getDcdSource( self ):
        txt = self.m_choice_dcdSource.GetString(self.m_choice_dcdSource.GetSelection())
        self.dcdSettingsDict['dcdSource'] = txt
        if txt == 'Disable DCD':
            self.dcdCtrlDict['isDcdEnabled'] = False
            self.m_filePicker_dcdBinFile.Enable( False )
            self.m_filePicker_dcdCfgFile.Enable( False )
            self.m_choice_dcdPurpose.Enable( False )
            self.m_textCtrl_sdramBase.Enable( False )
            self.m_panel_dcdDesc.Enable( False )
        elif txt == 'Use DCD bin file':
            self.dcdCtrlDict['isDcdEnabled'] = True
            self.m_filePicker_dcdBinFile.Enable( True )
            self.m_filePicker_dcdCfgFile.Enable( False )
            self.m_choice_dcdPurpose.Enable( True )
            self.m_panel_dcdDesc.Enable( False )
            self._getDcdPurpose()
        elif txt == 'Use DCD cfg file':
            self.dcdCtrlDict['isDcdEnabled'] = True
            self.m_filePicker_dcdBinFile.Enable( False )
            self.m_filePicker_dcdCfgFile.Enable( True )
            self.m_choice_dcdPurpose.Enable( True )
            self.m_panel_dcdDesc.Enable( False )
            self._getDcdPurpose()
        elif txt == 'Use DCD descriptor':
            self.dcdCtrlDict['isDcdEnabled'] = True
            self.m_filePicker_dcdBinFile.Enable( False )
            self.m_filePicker_dcdCfgFile.Enable( False )
            self.m_choice_dcdPurpose.Enable( True )
            self.m_panel_dcdDesc.Enable( True )
            self._getDcdPurpose()
        else:
            pass

    def popupMsgBox( self, msgStr ):
        messageText = (msgStr)
        wx.MessageBox(messageText, "Error", wx.OK | wx.ICON_INFORMATION)

    def _getDcdBinFile( self ):
        status = True
        if self.dcdSettingsDict['dcdSource'] == 'Use DCD bin file':
            self.dcdSettingsDict['userBinFile'] = self.m_filePicker_dcdBinFile.GetPath().encode('utf-8').encode("gbk")
            if os.path.isfile(self.dcdSettingsDict['userBinFile']):
                shutil.copy(self.dcdSettingsDict['userBinFile'], self.destBinFilename)
                self.dcdCtrlDict['dcdFileType'] = gendef.kUserDcdFileType_Bin
            else:
                status = False
                self.dcdSettingsDict['userBinFile'] = 'N/A'
                self.popupMsgBox('You should specify a dcd bin file')
        return status

    def _getDcdCfgFile( self ):
        status = True
        if self.dcdSettingsDict['dcdSource'] == 'Use DCD cfg file':
            self.dcdSettingsDict['userCfgFile'] = self.m_filePicker_dcdCfgFile.GetPath().encode('utf-8').encode("gbk")
            if os.path.isfile(self.dcdSettingsDict['userCfgFile']):
                shutil.copy(self.dcdSettingsDict['userCfgFile'], self.destCfgFilename)
                self.dcdCtrlDict['dcdFileType'] = gendef.kUserDcdFileType_Cfg
            else:
                status = False
                self.dcdSettingsDict['userCfgFile'] = 'N/A'
                self.popupMsgBox('You should specify a dcd cfg file')
        return status

    def _getDcdPurpose( self ):
        if self.dcdSettingsDict['dcdSource'] != 'Disable DCD':
            txt = self.m_choice_dcdPurpose.GetString(self.m_choice_dcdPurpose.GetSelection())
            if txt == 'Misc':
                self.m_textCtrl_sdramBase.Enable( False )
                self.dcdSettingsDict['sdramBase'] = None
            elif txt == 'SDRAM':
                self.m_textCtrl_sdramBase.Enable( True )
                pass
            else:
                pass
            self.dcdSettingsDict['dcdPurpose'] = txt

    def _getSdramBase( self ):
        status = True
        if self.dcdSettingsDict['dcdSource'] != 'Disable DCD' and \
           self.dcdSettingsDict['dcdPurpose'] == 'SDRAM':
            hexText = self.m_textCtrl_sdramBase.GetLineText(0)
            status = False
            val32 = None
            if len(hexText) > 2 and hexText[0:2] == '0x':
                try:
                    val32 = int(hexText[2:len(hexText)], 16)
                    if val32 >= rundef.kBootDeviceMemBase_SemcSdram and val32 < rundef.kBootDeviceMemBase_SemcSdram + rundef.kBootDeviceMemMaxSize_SemcSdram:
                        status = True
                        self.dcdSettingsDict['sdramBase'] = hexText
                    else:
                        self.popupMsgBox('SDRAM base should be in the range of 0x%x - 0x%x' %(rundef.kBootDeviceMemBase_SemcSdram, (rundef.kBootDeviceMemBase_SemcSdram + rundef.kBootDeviceMemMaxSize_SemcSdram - 1)))
                except:
                    self.popupMsgBox('Illegal input detected! You should input like this format: 0x80000000')
            else:
                self.popupMsgBox('Illegal input detected! You should input like this format: 0x80000000')
        return status

    def _getDeviceModel( self ):
        if self.dcdSettingsDict['dcdSource'] == 'Use DCD descriptor':
            txt = self.m_choice_dcdModel.GetString(self.m_choice_dcdModel.GetSelection())
            if txt == 'No':
                self.m_textCtrl_dcdDesc.Clear()
                self.m_textCtrl_dcdDesc.LoadFile(os.path.join(self.dcdModelFolder, 'template', gendef.kStdDcdFilename_Cfg))
            elif txt == 'Micron_MT48LC16M16A2' or txt == 'ISSI_IS42S16160J':
                self.m_textCtrl_dcdDesc.Clear()
                self.m_textCtrl_dcdDesc.LoadFile(os.path.join(self.dcdModelFolder, txt, gendef.kStdDcdFilename_Cfg))
            else:
                pass
            self.dcdSettingsDict['deviceModel'] = txt

    def _getDcdDesc( self ):
        status = True
        if self.dcdSettingsDict['dcdSource'] == 'Use DCD descriptor':
            if self.m_textCtrl_dcdDesc.GetLineLength(0):
                self.m_textCtrl_dcdDesc.SaveFile(self.destCfgFilename)
                self.dcdCtrlDict['dcdFileType'] = gendef.kUserDcdFileType_Cfg
                fileLen = os.path.getsize(self.destCfgFilename)
                with open(self.destCfgFilename, 'rb') as fileObj:
                    self.dcdSettingsDict['dcdDesc'] = fileObj.read(fileLen)
                    fileObj.close()
            else:
                status = False
                self.popupMsgBox('You need to enter the descriptor code!')
        return status

    def callbackSetDcdSource( self, event ):
        self._getDcdSource()

    def callbackSetDcdPurpose( self, event ):
        self._getDcdPurpose()

    def callbackSetDeviceModel( self, event ):
        self._getDeviceModel()

    def callbackOk( self, event ):
        self._getDcdSource()
        if not self._getDcdBinFile():
            return
        if not self._getDcdCfgFile():
            return
        if not self._getSdramBase():
            return
        if not self._getDcdDesc():
            return
        uivar.setBootDeviceConfiguration(uidef.kBootDevice_Dcd, self.dcdCtrlDict, self.dcdSettingsDict)
        self.Show(False)

    def callbackCancel( self, event ):
        self.Show(False)

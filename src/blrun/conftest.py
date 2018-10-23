#! /usr/bin/env python

# Copyright (c) 2013 Freescale Semiconductor, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# o Redistributions of source code must retain the above copyright notice, this list
#   of conditions and the following disclaimer.
#
# o Redistributions in binary form must reproduce the above copyright notice, this
#   list of conditions and the following disclaimer in the documentation and/or
#   other materials provided with the distribution.
#
# o Neither the name of Freescale Semiconductor, Inc. nor the names of its
#   contributors may be used to endorse or promote products derived from this
#   software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import sys
import os

sys.path.append(os.path.abspath("../bin"))

import pytest
from fsl.bootloader import bltest
from fsl.bootloader import target

import bltestconfig

##
# @brief
@pytest.fixture(scope="module")
def tgt(request):
    # Build path to target directory and config file.
    cpu = bltestconfig.target[0].lower()
    if cpu == 'sim':
        targetBaseDir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'validation', 'blsim')
    else:
        targetBaseDir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'targets', cpu)
    targetConfigFile = os.path.join(targetBaseDir, 'bltargetconfig.py')

    # Check for existing target directory.
    if not os.path.isdir(targetBaseDir):
        raise ValueError("Missing target directory at path %s" % targetBaseDir) 

    # Check for config file existence.
    if not os.path.isfile(targetConfigFile):
        raise RuntimeError("Missing target config file at path %s" % targetConfigFile)

    # Build locals dict by copying our locals and adjusting file path and name.
    targetConfig = locals().copy()
    targetConfig['__file__'] = targetConfigFile
    targetConfig['__name__'] = 'bltargetconfig'

    # Execute the target config script.
    execfile(targetConfigFile, globals(), targetConfig)
    
    # Create targetRegs dict and merge it into targetConfig dict
    targetRegsFile = os.path.join(targetBaseDir, 'bltargetregs.py')
    if os.path.isfile(targetRegsFile):
        targetRegs = locals().copy()
        targetRegs['__file__'] = targetRegsFile
        targetRegs['__name__'] = 'bltargetregs'
        execfile(targetRegsFile, globals(), targetRegs)
        
        targetConfig.update(targetRegs)

    # Create the target object.
    return target.Target(**targetConfig)

##
# @brief
@pytest.fixture(scope="function")
def bl(request, tgt):
    bl = bltest.createBootloader(tgt, bltestconfig.vectorsDir, bltestconfig.peripheral, bltestconfig.speed, bltestconfig.port,
                                bltestconfig.loadTarget, bltestconfig.resetTarget, bltestconfig.usePing)
    def closeBootloader():
        bl.close()
    request.addfinalizer(closeBootloader)
    return bl

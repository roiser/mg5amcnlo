################################################################################
#
# Copyright (c) 2009 The MadGraph Development team and Contributors
#
# This file is a part of the MadGraph 5 project, an application which 
# automatically generates Feynman diagrams and matrix elements for arbitrary
# high-energy processes in the Standard Model and beyond.
#
# It is subject to the MadGraph license which should accompany this 
# distribution.
#
# For more information, please visit: http://madgraph.phys.ucl.ac.be
#
################################################################################
from __future__ import division
import subprocess
import unittest
import os
import re
import shutil
import sys
import logging
import time

logger = logging.getLogger('test_cmd')

import tests.unit_tests.iolibs.test_file_writers as test_file_writers

import madgraph.interface.master_interface as MGCmd
import madgraph.interface.amcatnlo_run_interface as NLOCmd
import madgraph.interface.launch_ext_program as launch_ext
import madgraph.various.misc as misc

_file_path = os.path.split(os.path.dirname(os.path.realpath(__file__)))[0]
_pickle_path =os.path.join(_file_path, 'input_files')

from madgraph import MG4DIR, MG5DIR, MadGraph5Error, InvalidCmd

pjoin = os.path.join

    
    


#===============================================================================
# TestCmd
#===============================================================================
class TestMECmdShell(unittest.TestCase):
    """this treats all the command not related to MG_ME"""
    
    def generate(self, process, model):
        """Create a process"""

        try:
            shutil.rmtree('/tmp/MGPROCESS/')
        except Exception, error:
            pass

        interface = MGCmd.MasterCmd()
        interface.onecmd('import model %s' % model)
        if isinstance(process, str):
            interface.onecmd('generate %s' % process)
        else:
            for p in process:
                interface.onecmd('add process %s' % p)
        interface.onecmd('output /tmp/MGPROCESS/ -f')
        if not os.path.exists(pjoin(_file_path, os.path.pardir, 'MCatNLO-utilities')):
            interface.onecmd('install MCatNLO-utilities')
        
        self.cmd_line = NLOCmd.aMCatNLOCmdShell(me_dir= '/tmp/MGPROCESS')
        self.cmd_line.exec_cmd('set automatic_html_opening False')

    @staticmethod
    def join_path(*path):
        """join path and treat spaces"""     
        combine = os.path.join(*path)
        return combine.replace(' ','\ ')        
    
    def do(self, line):
        """ exec a line in the cmd under test """        
        self.cmd_line.exec_cmd(line)


    def test_generate_events_lo_hw6_stdhep(self):
        """test the param_card created is correct"""
        
        cmd = os.getcwd()
        self.generate(['p p > e+ ve [QCD]'], 'loop_sm')
        self.assertEqual(cmd, os.getcwd())
        self.do('generate_events LO -f')        
        
        # test the lhe event file exists
        self.assertTrue(os.path.exists('/tmp/MGPROCESS/Events/run_01/events.lhe.gz'))
        # test the hep event file exists
        self.assertTrue(os.path.exists('/tmp/MGPROCESS/Events/run_01/events_HERWIG6.hep.gz'))
        
        text = open('/tmp/MGPROCESS/Events/run_01/res_1_tot.txt').read()
        # check for the correct total cross-section
        self.assertTrue("5.51648351e+03 +- 3.1224e+01" in text)


    def test_generate_events_lo_py6_stdhep(self):
        """test the param_card created is correct"""
        
        cmd = os.getcwd()
        self.generate(['p p > e+ ve [QCD]'], 'loop_sm')
        self.assertEqual(cmd, os.getcwd())
        #change to py6
        card = open('/tmp/MGPROCESS/Cards/run_card.dat').read()
        open('/tmp/MGPROCESS/Cards/run_card.dat', 'w').write(card.replace('HERWIG6', 'PYTHIA6Q'))
        
        self.do('generate_events LO -f')        
        
        # test the lhe event file exists
        self.assertTrue(os.path.exists('/tmp/MGPROCESS/Events/run_01/events.lhe.gz'))
        # test the hep event file exists
        self.assertTrue(os.path.exists('/tmp/MGPROCESS/Events/run_01/events_PYTHIA6Q.hep.gz'))
        
        text = open('/tmp/MGPROCESS/Events/run_01/res_1_tot.txt').read()
        # check for the correct total cross-section
        self.assertTrue("5.51648351e+03 +- 3.1224e+01" in text)

        
    def test_generate_events_nlo_hw6_stdhep(self):
        """test the param_card created is correct"""
        
        cmd = os.getcwd()
        self.generate(['p p > e+ ve [QCD]'], 'loop_sm')
        self.assertEqual(cmd, os.getcwd())
        self.do('generate_events NLO -f')        
        
        # test the lhe event file exists
        self.assertTrue(os.path.exists('/tmp/MGPROCESS/Events/run_01/events.lhe.gz'))
        # test the hep event file exists
        self.assertTrue(os.path.exists('/tmp/MGPROCESS/Events/run_01/events_HERWIG6.hep.gz'))
        
        text = open('/tmp/MGPROCESS/Events/run_01/res_1_tot.txt').read()
        # check for the correct total cross-section
        self.assertTrue("6.64659781e+03 +- 3.7758e+01" in text)

    def test_generate_events_nlo_py6_stdhep(self):
        """test the param_card created is correct"""
        
        cmd = os.getcwd()
        self.generate(['p p > e+ ve [QCD]'], 'loop_sm')
        self.assertEqual(cmd, os.getcwd())
        #change to py6
        card = open('/tmp/MGPROCESS/Cards/run_card.dat').read()
        open('/tmp/MGPROCESS/Cards/run_card.dat', 'w').write(card.replace('HERWIG6', 'PYTHIA6Q'))
        
        self.do('generate_events NLO -f')        
        
        # test the lhe event file exists
        self.assertTrue(os.path.exists('/tmp/MGPROCESS/Events/run_01/events.lhe.gz'))
        # test the hep event file exists
        self.assertTrue(os.path.exists('/tmp/MGPROCESS/Events/run_01/events_PYTHIA6Q.hep.gz'))
        
        text = open('/tmp/MGPROCESS/Events/run_01/res_1_tot.txt').read()
        # check for the correct total cross-section
        self.assertTrue("6.68336708e+03 +- 3.6889e+01" in text)
        

    def test_calculate_xsect_nlo(self):
        """test the param_card created is correct"""
        
        cmd = os.getcwd()
        self.generate(['p p > e+ ve [QCD]'], 'loop_sm')
        self.assertEqual(cmd, os.getcwd())
        
        self.do('calculate_xsect  NLO -f')        
        
        # test the plot file exists
        self.assertTrue(os.path.exists('/tmp/MGPROCESS/Events/run_01/MADatNLO.top'))
        text = open('/tmp/MGPROCESS/Events/run_01/res.txt').read()
        # check for the correct total cross-section
        self.assertTrue("6.62125958e+03 +- 2.7262e+01" in text)


    def test_calculate_xsect_lo(self):
        """test the param_card created is correct"""
        
        cmd = os.getcwd()
        self.generate(['p p > e+ ve [QCD]'], 'loop_sm')
        self.assertEqual(cmd, os.getcwd())
        
        self.do('calculate_xsect  NLO -f')        
        
        # test the plot file exists
        self.assertTrue(os.path.exists('/tmp/MGPROCESS/Events/run_01/MADatNLO.top'))
        text = open('/tmp/MGPROCESS/Events/run_01/res.txt').read()
        # check for the correct total cross-section
        self.assertTrue("6.62125958e+03 +- 2.7262e+01" in text)
        

    def load_result(self, run_name):
        
        import madgraph.iolibs.save_load_object as save_load_object
        import madgraph.various.gen_crossxhtml as gen_crossxhtml
        
        result = save_load_object.load_from_file('/tmp/MGPROCESS/HTML/results.pkl')
        return result[run_name]

#! /usr/bin/env python3

##############################################################
# Guillaume W. Bres, 2016         <guillaume.bres@noisext.com>
##############################################################
# make new tbench.py
# creates a generic test bench to run advanced simulations run
# Simulations run generally uses an external .vhd file
# describing input data and other stimuli
##############################################################

import sys

from IPCore import *

def import_libraries(fd, **args):
	included_libs = ["ieee"]
	fd.write("library ieee;\n")
	fd.write("use ieee.std_logic_1164.all;\n")

	for lib, packages in args.items():
		for package in packages:
				if (not((lib in included_libs)or(lib.upper() in included_libs)or(lib.lower() in included_libs))):
					fd.write("\nlibrary {:s};\n".format(lib))
					included_libs.append(lib)
				fd.write("use {:s}.{:s}.all;\n".format(lib.lower(), package))

def declare_tbench_entity(fp, fd):
	extension = fp.split(".")[-1]
	entity = fp.strip("."+extension)
	fd.write("\nentity {:s} is\n".format(entity)) 
	fd.write("end entity {:s};\n".format(entity))

def make_clock_sim(fd, freq):
	half_per = 1/freq/2
	half_per_ns = half_per/1e-9
	fd.write("\n\tclk <= not(clk) after {:f} ns; -- clock sim\n".format(half_per_ns))

def make_axi4s_fi_sim(fd, tlastSim=None):
	fd.write("\n\t-- This process generates a TVALID (AXI4S) signal\n")
	fd.write("\t-- TVALID can be prescaled using PRESCALER constant value\n")
	fd.write("\t-- It also generates an AXI4 packet using TLAST defined by FRAME_SIZE value\n")
	fd.write("\tfi_sim: process(clk)\n")
	fd.write("\tbegin\n")
	fd.write("\tif rising_edge(clk) then\n")
	fd.write("\t\tif (resetn = '0') then\n")
	fd.write("\t\t\ts_axis_tvalid <= '0';\n")
	fd.write("\t\t\tprescaler_cnt <= 0;\n")
	if (tlastSim):
		fd.write("\t\t\ttlast_cnt <= 0;\n")
		fd.write("\t\t\ts_axis_tlast <= '0';\n")

	fd.write("\t\telse\n")
	fd.write("\t\t\ts_axis_tvalid <= '0';\n")
	if (tlastSim):
		fd.write("\t\t\ts_axis_tlast <= '0';\n")
	fd.write("\t\t\tif (prescaler_cnt < PRESCALER-1) then\n")
	fd.write("\t\t\t\tprescaler_cnt <= prescaler_cnt+1;\n")
	fd.write("\t\t\telse\n")
	fd.write("\t\t\t\tprescaler_cnt <= 0;\n")
	fd.write("\t\t\t\ts_axis_tvalid <= '1';\n")
	fd.write("\t\t\t\tif (tlast_cnt < FRAME_SIZE-1) then\n")
	fd.write("\t\t\t\t\ttlast_cnt <= tlast_cnt+1;\n")
	fd.write("\t\t\t\telse\n")
	fd.write("\t\t\t\t\ttlast_cnt <= 0;\n")
	fd.write("\t\t\t\t\ts_axis_tlast <= '1';\n")
	fd.write("\t\t\t\tend if;\n")
	fd.write("\t\t\tend if;\n")
	fd.write("\t\tend if;\n")
	fd.write("\tend if;\n")
	fd.write("\tend process fi_sim;\n\n")

def make_axi4s_data_sim(fd):
	fd.write("\n\t-- This process simulates an AXI4 stream\n")
	fd.write("\tdata_sim: process(clk)\n")
	fd.write("\tbegin\n")
	fd.write("\tif rising_edge(clk) then\n")
	fd.write("\t\tif (resetn = '0') then\n")
	fd.write("\t\t\tpointer <= 0;\n")
	fd.write("\t\telse\n")
	fd.write("\t\t\tpointer <= pointer;\n")
	fd.write("\t\t\tif (s_axis_tvalid = '1') then\n")
	fd.write("\t\t\t\tif (pointer < LUT_DEPTH-1) then\n")
	fd.write("\t\t\t\t\tpointer <= pointer+1;\n")
	fd.write("\t\t\t\telse\n")
	fd.write("\t\t\t\t\tpointer <= 0;\n")
	fd.write("\t\t\t\tend if;\n")
	fd.write("\t\t\tend if;\n")
	fd.write("\t\tend if;\n")
	fd.write("\tend if;\n")
	fd.write("\tend process data_sim;\n")

def make_stimuli_process(fd):
	fd.write("\n\t-- XSIM stimuli process\n")
	fd.write("\txsim: process\n")
	fd.write("\tbegin\n")
	fd.write("\t\tresetn <= '0';\n")
	fd.write("\t\twait until rising_edge(clk);\n")
	fd.write("\t\twait until rising_edge(clk);\n")
	fd.write("\t\tresetn <= '1';\n")
	fd.write("\t\twait until rising_edge(clk);\n")
	fd.write("\t\twait until rising_edge(clk);\n")
	fd.write("\t\twait until rising_edge(eos);\n")
	fd.write('\t\treport "End of simulation" severity failure;\n')
	fd.write("\tend process xsim;\n")

def make_output_file_writer(fd, fname, eos=None):
	fd.write("\n\t-- This process writes simulation results into a file\n")
	fd.write("\ttxt_file: process(clk)\n")
	fd.write('\tfile outfile: text is out "{:s}";\n'.format(fname))
	fd.write("\tvariable outline: line;\n")
	fd.write("\tbegin\n")
	fd.write("\tif rising_edge(clk) then\n")
	fd.write("\t\t if (resetn = '0') then\n")
	fd.write("\tend if;\n")
	fd.write("\tend process txt_file;\n")

def make_tbench_arch(fp, fd, DUTs=None):
	extension = fp.split(".")[-1]
	entity = fp.strip("."+extension)
	
	fd.write("\narchitecture rtl of {:s} is\n".format(entity))

	TBSignals = []
	TBSignals.append(Signal('clk','in'))
	TBSignals.append(Signal('resetn','in'))
	TBSignals.append(Signal('eos','in'))

	initZeroState = ['clk','resetn','eos']

	tlastToBeSimulated = False
	tuserToBeSimulated = False

	# create a variable for all DUT signals 
	if (DUTs is not None):
		for DUT in DUTs:
			ports = DUT.getPorts()
			for port in ports:
				name = port.getName()
				if ('clk' in name):
					continue
				
				if ('reset' in name):
					continue

				if ('last' in name.lower()):
					if (not(tlastToBeSimulated)):
						tlastToBeSimulated = True
						TBSignals.append(Signal("tlast_counter",'in',_type="natural",_range=1024))	

				if ('tuser' in name.lower()):
					if (not(tuserToBeSimulated)):
						tuserToBeSimulated = True
						sig = Signal("tuser_counter",'in',_type="natural",_range=8)

				if (port.getDir() == 'in'):
					sig = Signal(name+'_i','in',size=port.getSize())
				else:
					sig = Signal(name+'_o','out',size=port.getSize())
				
				if (not(sig in TBSignals)):
					TBSignals.append(sig)

	# declare all required signals
	fd.write('\n\t ------ XSIM ------- \n')
	for sig in TBSignals:
		if (sig.getName() in initZeroState):
			sig.declare(fd, default="'0'")
		else:
			sig.declare(fd)
	fd.write('\t ------------------- \n')

	fd.write("begin\n")
		
	make_clock_sim(fd, 100e6)
	make_axi4s_fi_sim(fd, tlastSim=tlastToBeSimulated)
	make_axi4s_data_sim(fd)
	
	# if (tuserToBeSimulated):
	# make_axi4s_tuser_sim(fd)

	make_stimuli_process(fd)

	# map DUTs if needed
	if (DUTs is not None):
		for DUT in DUTs:
			DUT.map(fd, DUTs.index(DUT), DUT.getPorts())

	fd.write("\nend rtl;")

def create_tbench(fp, DUTs=None):
	fd = open(fp, "w")
	
	fd.write("-- ######################################################\n")
	fd.write("-- Guillaume W. Bres, 2018   <guillaume.bres@noisext.com>\n")
	fd.write("-- This test bench was automatically generated\n")
	fd.write("-- ######################################################\n\n")

	import_libraries(fd, 
		ieee=["numeric_std", "std_logic_textio"], 
		std=["textio"],
		ieee_proposed=["fixed_pkg","float_pkg"], 
		work=["package_tb.vhd"]
	)

	declare_tbench_entity(fp, fd)
	make_tbench_arch(fp, fd, DUTs=DUTs)
	fd.close()

def main(argv):
	argv = argv[1:]

	if (len(argv) == 0):
		print("Usage:")
		print("./make_new_tbench.py fp=/output/file/path.vhd") 
		print("./make_new_tbench.py fp=/output/file/path.vhd dut=dut1.vhd") 
		print("./make_new_tbench.py fp=/output/file/path.vhd dut=dut1.vhd dut=dut2.vhd") 
		return -1

	fp = None 
	DUTs = [] 
	for arg in argv:
		key = arg.split("=")[0]
		value = arg.split("=")[-1]
		if key == "--fp":
			fp = value
		elif key == "--dut":
			DUTs.append(IPCore(value))
		else:
			print("Unknown flag {:s}".format(key))

	if (fp is None):
		print("output file path must be defined")
		return -1
	
	create_tbench(fp, DUTs=DUTs)	

	print("Test bench {:s} has been created".format(fp))
	return 0

main(sys.argv)

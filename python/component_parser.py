#! /usr/bin/env python3

import sys

def component_vendor(component):
	component = open(component,"r")
	for line in component:
		if "<spirit:vendor" in line:
			parsed = line.split(">")[1].split("</")
			component.close()
			return parsed[0]

def component_version(component):
	component = open(component,"r")
	for line in component:
		if "<spirit:version" in line:
			parsed = line.split(">")[1].split("</")
			component.close()
			return parsed[0]

def component_subcore_refs(component):
	subcores = []
	versions = []
	names = []
	component = open(component,"r")
	for line in component:
		if "<xilinx:componentRef" in line:
			
			parsed = line.split("xilinx:vendor")[1].split(" ")
			parsed = parsed[0].strip("=")
			vendor = parsed.strip('"')
			
			parsed = line.split("xilinx:library")[1].split(" ")
			parsed = parsed[0].strip("=")
			library = parsed.strip('"')
			
			parsed = line.split("xilinx:name")[1].split(" ")
			parsed = parsed[0].strip("=")
			name = parsed.strip('"')
			
			parsed = line.split("xilinx:version")[1].split(">")
			parsed = parsed[0].strip("=")
			version = parsed.strip('"')
			
			if not( name in names ):
				subcores.append( "--subcore={:s}:{:s}:{:s}:{:s}".format(vendor,library,name,version))
				names.append( name )

	component.close()
	return subcores

def documentation(fp):
	f=open(fp,"r")
	for line in f:
		if ("xilinx_productguide" in line):
			f.close()
			return True
	f.close()
	return False

def versionning(fp):
	f=open(fp,"r")
	for line in f:
		if ("xilinx_versioninformation" in line):
			f.close()
			return True
	f.close()
	return False

def component_xci_refs(component):
	xcis = []
	names = []
	component = open( component, "r" )
	for line in component:
		if ".xci" in line:
			parsed = line.split(">")[1]
			parsed = parsed.split("<")[0]
			name = parsed.split("<")[0]
			if not( name in names ):
				xcis.append( "--xci={:s}".format( name ))
				names.append( name )
	return xcis

def main(argv):
	
	argv = argv[1:] # rm script name
	if (len(argv) < 2):
		print(">> usage:")
		print("./vivado_component_parser [path] [flag]")
		print("path: component.xml location")
		print("flag: --vendor, --version, --documentation, --versionning, --subcores, --xci")
		return -1
	
	path = argv[0]
	flag = argv[1]

	if flag == "--vendor":
		print(component_vendor(path))
	elif flag == "--version":
		print( component_version(path))
	elif flag == "--subcores":
		print( " ".join(tuple(component_subcore_refs(path))))
	elif flag == "--xci":
		print( " ".join(tuple(component_xci_refs(path))))
	elif flag == "--versionning":
		print(versionning(path))
	elif flag == "--documentation":
		print(documentation(path))
	else:
		print("flag --{:s} is not known".format(flag))
		return -1

	return 0

main(sys.argv)

#! /usr/bin/env python3

#########################################################
# Guillaume W. Bres, 2016    <guillaume.bres@noisext.com>
#########################################################
# product-guide.py
# creats an ip documentation using latex toolsuite
#########################################################

import os 
import sys 
import datetime 

from latex import *

def build_specifications_section_template( product_guide ):
	latex_section( product_guide, "IP specifications", "ip_specifications")
	_paragraph = "You should explain IP architecture, describe available architectures,"
	_paragraph += " and give expected performances in this section\n\n"
	product_guide.write( _paragraph ) 

	latex_subsection( product_guide, "Timing performances" )
	_paragraph = "Timing performances of the current released version:\n\n"
	product_guide.write( _paragraph ) 

	latex_command( product_guide, "begin", [["center",UNICODE_ACCOLADE],])
	latex_tabular_begin( product_guide, "|c|c|", "0.15cm" )
	product_guide.write( "\\hline\n" )
	product_guide.write( "Highest frequency achieved & 400 MHz \\\\\n" )
	product_guide.write( "\\hline\n" )
	product_guide.write( "Highest frequency implemented & 333 MHz \\\\\n" )
	product_guide.write( "\\hline\n" )
	latex_tabular_end( product_guide, "0.15cm" )
	latex_command( product_guide, "end", [["center",UNICODE_ACCOLADE],])

	latex_command( product_guide, "noindent", [])
	_paragraph = "\\underline{0:s}Highest frequency achieved{1:s}: performance achieved in an out-of-context\n".format(UNICODE_ACCOLADE[0],UNICODE_ACCOLADE[1])
	_paragraph += "analysis using the related constraint file. The core\n"
	_paragraph += "is expected to work at this frequency.\n\n"
	product_guide.write( _paragraph ) 

	latex_command( product_guide, "vspace", [["0.25cm",UNICODE_ACCOLADE],])
	latex_command( product_guide, "noindent", [])
	_paragraph = "\\underline{0:s}Highest frequency implemented{1:s}: the IP core has been\n".format(UNICODE_ACCOLADE[0],UNICODE_ACCOLADE[1])
	_paragraph += "intensively used at this frequency.\n"
	product_guide.write( _paragraph ) 

	latex_subsection( product_guide, "I/O bus interfaces" )
	_paragraph = "Description of the available bus interfaces.\n\n"
	product_guide.write( _paragraph ) 

	latex_command( product_guide, "begin", [["center",UNICODE_ACCOLADE],])
	latex_tabular_begin( product_guide, "|c|c|c|", "0.15cm" )
	product_guide.write( "\\hline\n" )
	product_guide.write( "Name     & Data bus format  & Expected data format\\\\\n" )
	product_guide.write( "\\hline\n" )
	product_guide.write( "DataIn1  & AXI4S slave   & Any signed fixed point representation \\\\\n" )
	product_guide.write( "\\hline\n" )
	product_guide.write( "DataIn1  & AXI4S slave   & Any signed fixed point representation \\\\\n" )
	product_guide.write( "\\hline\n" )
	product_guide.write( "DataOut2 & AXI4S master & DataIn1 size \\\\\n" )
	product_guide.write( "\\hline\n" )
	product_guide.write( "DataOut2 & AXI4S master & DataIn2 size \\\\\n" )
	product_guide.write( "\\hline\n" )
	latex_tabular_end( product_guide, "0.15cm" )
	latex_command( product_guide, "end", [["center",UNICODE_ACCOLADE],])

	latex_subsubsection( product_guide, "AXI4 stream data bus features" )
	_paragraph = "Current IP version allows you to route some of the non-default AXI4 stream signals\n"
	_paragraph += "through the core:\n\n"
	product_guide.write( _paragraph )

	items = []
	items.append( "{0:s}\\tt TLAST{1:s} {2:s}: route frame marker through the core".format(UNICODE_ACCOLADE[0],UNICODE_ACCOLADE[1],CUSTOM_COMMAND_NAMES[0]))
	items.append( "{0:s}\\tt TREADY{1:s} {2:s}: allow back-pressure to be applied on the IP core".format(UNICODE_ACCOLADE[0],UNICODE_ACCOLADE[1],CUSTOM_COMMAND_NAMES[0]))
	items.append( "{0:s}\\tt TID{1:s} {2:s}: current version does not support frame identifier".format(UNICODE_ACCOLADE[0],UNICODE_ACCOLADE[1],CUSTOM_COMMAND_NAMES[1]))
	latex_listing( product_guide, "itemize", items )

	latex_subsection( product_guide, "IP parameters" )
	_paragraph = "Several parameters are available to customize the IP core.\n"
	product_guide.write( _paragraph )

	_items = ["parameter1", "parameter2"]
	latex_listing( product_guide, LATEX_ITEMIZE_LISTING, _items )

	latex_subsection( product_guide, "Pinout diagram" )
	_paragraph = "Pinout diagram is not provided yet.\n%"
	product_guide.write( _paragraph )
	
	_paragraph = latex_figure( "pinout_diagram.pdf", "0.75", "pinout_diagram" )
	product_guide.write( _paragraph.replace("\n", "\n%" ))
	product_guide.write( "\n\n" ) 

	latex_subsection(product_guide, "Example of use")
	_paragraph = "Example of use is not provided yet.\n%"
	product_guide.write( _paragraph )
	
	_paragraph = latex_figure( "example_diagram.pdf", "0.75", "example_diagram" )
	product_guide.write( _paragraph.replace("\n", "\n%" ))
	product_guide.write( "\n\n" ) 

def build_simulation_section_template(fd, ip_name, ip_category=None):
	"""
	Builds section template to explain how to simulate the IP core
	"""
	latex_section(fd, "Simulation")
	content = "The IP core is integrated to the IP simulation library.\n\n"
	content += "\\noindent\nUse the generic command line interface to simulate the IP core: \n"
	fd.write(content)
	
	latex_command(fd, "begin", [["verbatim", UNICODE_ACCOLADE],])
	content = "   cd $FPGA/simulation\n"
	if (ip_category is None):
		content += "   make TARGET={:s}".format(ip_name)
	else:
		content += "   make TARGET={:s}{:s}".format(ip_category,ip_name)
	fd.write(content)
	latex_command(fd, "end", [["verbatim", UNICODE_ACCOLADE],])

	content = "Open simulation project in Vivado (gui) with the following command:\n"
	fd.write(content)
	latex_command(fd, "begin", [["verbatim", UNICODE_ACCOLADE],])
	if (ip_category is None):
		content = "   vivado $FPGA/simulation/{:s}/simulation.xpr &\n".format(ip_name)
	else:
		content = "   vivado $FPGA/simulation/{:s}/{:s}/simulation.xpr &\n".format(ip_category,ip_name)
	fd.write(content)
	latex_command(fd, "end", [["verbatim", UNICODE_ACCOLADE],])

	content = "Use the following command to rerun simulation with a new stimuli set:\n" 
	fd.write(content)
	latex_command(fd, "begin", [["verbatim", UNICODE_ACCOLADE],])
	content = "   cd $FPGA/simulation\n"
	if (ip_category is None):
		content += "   make TARGET={:s} pre-simulation".format(ip_name)
	else:
		content += "   make TARGET={:s}{:s} pre-simulation".format(ip_category,ip_name)
	fd.write(content)
	latex_command(fd, "end", [["verbatim", UNICODE_ACCOLADE],])

	content = "Use the following command to rerun post simulation analysis:\n" 
	fd.write(content)
	latex_command(fd, "begin", [["verbatim", UNICODE_ACCOLADE],])
	content = "   cd $FPGA/simulation\n"
	if (ip_category is None):
		content += "   make TARGET={:s} post-simulation".format(ip_name)
	else:
		content += "   make TARGET={:s}{:s} post-simulation".format(ip_category,ip_name)
	fd.write(content)
	latex_command(fd, "end", [["verbatim", UNICODE_ACCOLADE],])

	content = "Simulation flags can be stacked, rerun complete simulation with:"
	fd.write(content)
	latex_command(fd, "begin", [["verbatim", UNICODE_ACCOLADE],])
	if (ip_category is None):
		content += "   make TARGET={:s} pre-simulation simulate post-simulation".format(ip_name)
	else:
		content += "   make TARGET={:s}{:s} pre-simulation simulate post-simulation".format(ip_category,ip_name)
	fd.write(content)
	latex_command(fd, "end", [["verbatim", UNICODE_ACCOLADE],])

	fd.write("\n")

	build_introduction_template(fd, ip_name, 
		ip_category=ip_category, OpenSource=OpenSource
	)
	
	build_specifications_section_template(fd)
	build_simulation_section_template(fd, ip_name, ip_category=ip_category)
	latex_end_doc(fd)

	fd.close()
	return 0

def print_script_help():
	for k in range(0, len(KNOWN_ARGS)):
		_status = KNOWN_ARGS_INFO[k]
		if _status is None:
			_status = ""
		else:
			_status = "[{:s}]".format(_status)
		print( "{:s}: {:s} {:s}".format(KNOWN_ARGS[k], KNOWN_ARGS_INFO[k], _status))

	print("\nExample of use:")
	print("./product-guide --author=me --ip-name=my-ip  [basic]\n")
	print("./product-guide --author=me --ip-name=my-ip  --ip-version=1.1 [basic]\n")
	print("./product-guide --author=me --ip-name=my-ip  --ip-version=1.1 --ip-category=lib [basic]\n")
	print("./product-guide --author=me --ip-name=my-ip  --ip-version=1.1 --ip-category=lib \n\t\t --company-logo=logo.png --company-website=https://me.domain.org [customized]\n")
	print('./product-guide --author=me --ip-name=my-ip  --font="Helvetica" [customized]\n')
	print('./product-guide --author=me --ip-name=my-ip  --date=10_05_2015 [customized]\n')
		
class Credentials:
	
	def __init__(self, args):
		self.firstName = ""
		self.midName = None
		self.lastName = None
		self.email = None
		
		for i in range(0, len(args)):
			key = args[i].split("=")[0]
			value = args[i].split("=")[1]
			
			if key == "--name":
				self.name = value
			elif key == "--midname":
				self.midname = value
			elif key == "--lastname":
				self.lastname = value
			elif key == "--email":
				self.email = value
	
	def getName(self):
		string = self.firstName
		if (self.midName):
			string += ' {:s}'.format(self.midName)
		if (self.lastName):
			string += ' {:s}'.format(self.lastName)
		return string

	def __str__(self):
		return self.getName()

	def getEmail(self):
		return self.email

	def hasEmail(self):
		if self.email:
			return True
		else:
			return False
	
class ProductGuideProperties:

	def __init__(self, args):
		self.docName = "template.tex" 
		self.font = "Helvetica"
		self.date = None

		self.version = "1.0"
		self.encrypted = False
		self.opensource = False
		self.license = None
		
		self.logo = None
		self.website = None

		self.packages = []
		self.custom_commands = []
		self.page_style = []

		self.supported_devices = ["Zynq-7"]

		for i in range(0, len(args)):
			key = args[i].split("=")[0]
			value = args[i].split("=")[1]

			if key == "docName":
				self.docName = value
			elif key == "date":
				self.date = strptime(value, 'Y/M/d')
			
			elif key == "font":
				self.font = value

			elif key == "version":
				self.version = value
			elif key == "encrypted":
				self.enctrypted = value
			elif key == "openSource":
				self.opensource = value
			elif key == "licenseFile":
				self.license = value
			
			elif key == "logo":
				self.logo = value
			elif key == "website":
				self.website = value

			elif key == "supported-device":
				self.addDevice(value)

	def getFont(self):
		return self.font

	def getVersion(self):
		return self.version
	
	def getDocName(self):
		return self.docName

	def addDevice(self, device):
		"""
		Adds given device to
		list of supported device
		"""
		supported_devices = [
			"Zynq-7",
			"7 Series",
			"6 Series",
			"Spartan6",
			"Spartan3",
			"UltraScale", 
			"UltraScale+"
			"MPSoC"
		]

		if not(device in supported_devices):
			raise ValueError("Device is not in list of possible devices: {:s}".format(",".join(supported_devices)))
		else:
			if not(device in self.supported_devices):
				self.supported_devices.append(device)

	def getSupportedDevices(self):
		return ",".join(self.supported_devices)

	def isEncrypted(self):
		return self.encrypted

	def isOpenSource(self):
		return self.opensource
	
	def hasLicenseFile(self):
		if (self.license):
			return True
		else:
			return False
	
	def getLicense(self):
		"""
		Returns licence file content
		"""
		fd=open(self.license())
		content = fd.read()
		fd.close()
		return content

	def hasLogo(self):
		"""
		Returns true if logo has been specified
		& will be included
		"""
		if (self.logo):
			return True
		else:
			return False

	def getLogo(self):
		"""
		Returns optionnal company logo
		"""
		return self.logo

	def hasDate(self):
		if (self.date):
			return True
		else:
			return False
	
	def getDate(self):
		return self.date

	def hasWebsite(self):
		if (self.website):
			return True
		else:
			return False
	
	def getWebsite(self):
		return self.website

	def addPackage(self, pkg, attribute):
		"""
		Appends package to required packages list
		"""
		self.packages.append([pkg,attribute])

	def getPackages(self):
		return self.packages

	def addCommand(self, name, code):
		"""
		Adds a custom command to be declared
		"""
		self.custom_commands.append([name,code])

	def getCustomCommands(self):
		return self.custom_commands

	def addPageStyleProperty(self, cmd, attribute, value):
		self.page_style.append([cmd,attribute,value])

	def getPageStyleProperties(self):
		return self.page_style
	
class ProductGuide:

	def __init__(self, args):
		self.properties = ProductGuideProperties(args)
		self.credentials = Credentials(args)

		# default stuff
		default_lang_packages = ["inputenc", "babel", "fontenc", "moresize"]
		default_lang_packages_attributes = ["latin1", "english", "T1", None]

		default_graphx_packages = ["graphicx", "float"]
		default_graphx_packages_attributes = [None, None]

		default_tab_packages = ["adjustbox", "multirow", "multicol"]
		default_tab_packages_attributes = [None, None, None]

		default_url_packages = ["hyperref"]
		default_url_packages_attributes = ["hidelinks"]

		default_maths_packages = ["mathtools", "amsfonts", "amsmath", "mathrsfs", "amssymb"]
		default_maths_packages_attributes = [None, None, None, None, None]

		default_toc_packages = ["titlesec", "tocbibind"]
		default_toc_packages_attributes = [None, "nottoc, notlof, notlot"]

		default_packages = [*default_lang_packages,
			*default_graphx_packages,
			*default_tab_packages,
			*default_url_packages,
			*default_maths_packages,
			*default_toc_packages
		]

		default_packages_attributes = [*default_lang_packages_attributes,
			*default_graphx_packages_attributes,
			*default_tab_packages_attributes,
			*default_url_packages_attributes,
			*default_maths_packages_attributes,
			*default_toc_packages_attributes
		]

		for i in range(0, len(default_packages)):
			self.properties.addPackage(
				default_packages[i], 
				default_packages_attributes[i]
			)

		# fancy stuff
		custom_graphx_packages = ["pifont", "fancyhdr", "geometry", "color", "xcolor"]
		custom_graphx_packages_attributes = [None, None, None, None, "dvipsnames"]

		for i in range(0, len(custom_graphx_packages)):
			self.properties.addPackage(
				custom_graphx_packages[i], 
				custom_graphx_packages_attributes[i]
			)

		# custom latex commands
		self.properties.addCommand(
			"\\cmark",
			"\\ding{:s}51{:s}".format(UNICODE_ACCOLADE[0],UNICODE_ACCOLADE[1])
		)

		self.properties.addCommand(
			"\\xmark",
			"\\ding{:s}55{:s}".format(UNICODE_ACCOLADE[0],UNICODE_ACCOLADE[1])
		)
		
		# page style properties
		page_style_commands = [
			"pagestyle",
			"addtolength", 
			"addtolength", 
			"addtolength",
			"setlength", 
			"setlength",
			"setlength",
			"setlength"
		]

		page_style_attributes = [
			"fancy",
			"\\voffset",
			"\\hoffset",
			"\\textwidth",
			"\\footskip",
			"\\tabcolsep",
			"\\headheight",
			"\\parindent"
		]
	
		page_style_values = [
			"",
			"-1cm", 
			"-1.5cm", 
			"3.5cm",
			"-4.5cm", 
			"0.5em",
			"30pt",
			"0pt"
		]

		for i in range(0, len(page_style_commands)):
			self.properties.addPageStyleProperty(
				page_style_commands[i],
				page_style_attributes[i],
				page_style_values[i]
			)

		self.fd = open(self.properties.getDocName(), "w")

		document_class(self.fd)
		
		self.include_packages()
		self.declare_custom_commands()
		
		self.set_document_font()
		self.set_page_style()
		self.set_sections_style()
		self.make_title()
		
		latex_begin_doc(self.fd)
		latex_make_title(self.fd)
		
		self.introduction_template()
		self.toc()	

		self.main_section_template()
		self.sim_section_template()

		latex_end_doc(self.fd)

		self.fd.close()
		print("Document '{:s}' has been created".format(self.properties.getDocName()))
	
	def include_packages(self):
		latex_comment(self.fd, "Required packages")
		packages = self.properties.getPackages()
		for i in range(0, len(packages)):
			# build cmd
			pkg = packages[i][0]
			attribute = packages[i][1]
			if (attribute is not None):
				cmd = [[attribute,UNICODE_BRAKET],[pkg,UNICODE_ACCOLADE]]
			else:
				cmd = [[pkg,UNICODE_ACCOLADE],]
			latex_command(self.fd, "usepackage", cmd)
		self.fd.write("\n")

	def declare_custom_commands(self):
		latex_comment(self.fd, "Custom commands")
		commands = self.properties.getCustomCommands()
		for i in range(0, len(commands)):
			name = commands[i][0]
			code = commands[i][1]
			cmd = [[name, UNICODE_ACCOLADE], [code, UNICODE_ACCOLADE],]
			latex_command(self.fd, "newcommand", cmd)
		self.fd.write("\n")

	def set_document_font(self):
		"""
		Sets fonts for document body
		"""
		latex_comment(self.fd, "Document body font")
		self.fd.write(latex_font_selection(self.properties.getFont(), "large")+"\n")

	def introduction_template(self):
		"""
		Builds introduction template
		"""

		latex_section(self.fd, "Introduction", "introduction", True)

		content = "{:s} core release notes\n".format(self.properties.getDocName())
		self.fd.write(content) 
	
		latex_section(self.fd, "Features", "features", True)
	
		_items = ["High performance implementation", 
			"Fully AXI4S compliant", 
			"Extra stuff1",
			"Extra stuff2",
		]
	
		latex_listing(self.fd, LATEX_ITEMIZE_LISTING, _items)
	
		self.fd.write("\\hfill\n\n")

		latex_tabular_begin(self.fd, "|l|r|")
		self.fd.write("\\hline\n")
		latex_command(self.fd, "multicolumn", [["2",UNICODE_ACCOLADE],["|c|",UNICODE_ACCOLADE],["Release notes",UNICODE_ACCOLADE]])
		self.fd.write("\\\\ \\hline\n")
		
		self.fd.write("Supported device(s) &")
		self.fd.write("{:s} \\\\ \n".format(self.properties.getSupportedDevices()))

		self.fd.write("\\hline\n")
		self.fd.write("Timing & See IP \\\\\nPerformances & specifications: {:s}\\\\\n".format(latex_reference("ip_specifications", "blue")))
		self.fd.write("\\hline\n")

		latex_command(
			self.fd, "multicolumn", [["2",UNICODE_ACCOLADE],["|c|",UNICODE_ACCOLADE],["Provided with the IP core",UNICODE_ACCOLADE]]
		)

		self.fd.write("\\\\ \\hline\n")
		if (self.properties.isOpenSource()):
			self.fd.write("Open source & \\cmark \\\\\n")
		
		if (self.properties.isEncrypted()):
			self.fd.write("Source files & Encrypted \\\\\n")
		else:
			self.fd.write("Source files & Readable \\\\\n")

		if (self.properties.hasLicenseFile()):
			self.fd.write("License file provided & \\cmark see next page \\\\\n")
		else:
			self.fd.write("License file provided & \\xmark \\\\\n")

		self.fd.write("\\hline\n")
		self.fd.write( "Example design & Not provided \\\\\n")
		self.fd.write("\\hline\n")
		self.fd.write("RTL  & VHDL \\\\\n")
		self.fd.write("\\hline\n")
		self.fd.write("Test bench & VHDL \\\\\n")
		self.fd.write("\\hline\n")
		self.fd.write("Constraint files & XDC \\\\\n")
		self.fd.write("\\hline\n")
		latex_tabular_end(self.fd, "1cm") 
	
	def toc(self):
		"""
		Writes table of content
		in open doc
		"""
		latex_command(self.fd, "newpage", [])
		latex_command(self.fd, "\n\\tableofcontents", [])
		latex_command(self.fd, "newpage", [])
		self.fd.write("\n")
	
	def main_section_template(self):
		print("main template")

	def sim_section_template(self):
		print("sim template")
	
	def set_page_style(self):
		"""
		Sets custom page style
		doc name / version @upper left corner

		logo: if included: upper right corner

		date: bottom left can be overriden
		"""
		latex_comment(self.fd, "Custom page style")
		properties = self.properties.getPageStyleProperties()
		for i in range(0, len(properties)):
			cmd = properties[i][0]
			attribute = properties[i][1]
			value = properties[i][2]
			latex_command(self.fd, cmd, [[attribute,UNICODE_ACCOLADE], [value, UNICODE_ACCOLADE]])
		self.fd.write("\n\n")

		if (self.properties.hasLogo()):
			cmd = "\\includegraphics[scale=0.3]{:s}{:s}{:s}".format(UNICODE_ACCOLADE[0], self.properties.getLogo(), UNICODE_ACCOLADE[1])

			cmd = [cmd, UNICODE_ACCOLADE]
			latex_command(self.fd, "fancyhead[L]", [cmd,], disable_underscore_correction=True)

		cmd = "{:s} v{:s}".format(self.properties.getDocName(), self.properties.getVersion())

		if self.properties.hasDate():
			cmd += "\\\\ \\date{:s}{:s}{:s}".format(UNICODE_ACCOLADE[0], self.properties.getDate(), UNICODE_ACCOLADE[1])
		else:
			content = "\\\\ \\today" # use built in compile time
		
		cmd = [cmd, UNICODE_ACCOLADE]
		latex_command(self.fd, "fancyfoot[L]", [cmd,])

		if self.properties.hasWebsite():
			cmd = latex_hyper_reference(self.properties.getWebsite(), self.properties.getWebsite(), "blue", True)
			cmd = [cmd, UNICODE_ACCOLADE]
			latex_command(self.fd, "fancyfoot[C]", [cmd,])

		self.fd.write("\n")

	def set_sections_style(self):
		"""
		Sets sections & subsections fonts and style
		#TODO: improve with common font & dependent size
		"""
		latex_comment(self.fd, "Custom sections style")
		self.fd.write("\\titleformat{0:s}\\section{1:s}{0:s}\\normalfont\\sffamily\\huge\\bfseries{1:}{0:s}{1:}{0:s}0em{1:s}{0:s}{1:s}\n".format(UNICODE_ACCOLADE[0],UNICODE_ACCOLADE[1]))
		self.fd.write("\\titleformat{0:s}\\subsection{1:s}{0:s}\\normalfont\\sffamily\\Large\\bfseries{1:s}{0:s}{1:s}{0:s}0em{1:s}{0:s}{1:s}\n".format(UNICODE_ACCOLADE[0],UNICODE_ACCOLADE[1]))
		self.fd.write("\\titleformat{0:s}\\subsubsection{1:s}{0:s}\\normalfont\\sffamily\\large\\bfseries{1:s}{0:s}{1:s}{0:s}0em{1:s}{0:s}{1:s}\n".format(UNICODE_ACCOLADE[0],UNICODE_ACCOLADE[1]))
		self.fd.write("\n")

	def make_title(self):
		"""
		Builds document title
		"""
		latex_comment(self.fd, "title")
	
		content = "\\title{:s} \n".format(UNICODE_ACCOLADE[0])
	
		if (self.properties.hasLogo()):
			content += "  \\includegraphics[scale=0.3]{:s}{:s}{:s}\\\\\n".format(UNICODE_ACCOLADE[0], self.properties.getLogo(), UNICODE_ACCOLADE[1])

		if (self.properties.hasWebsite()):
			content += latex_hyper_reference(self.properties.getWebsite(), self.properties.getWebsite(), "blue", True)+"\n"

		self.fd.write(content)

		latex_command(self.fd, "vspace", [["0.5cm",UNICODE_ACCOLADE],])
	
		content = "  IP: {0:s}\\tt {1:s} v{2:s}{3:s} \\\\ \n".format(UNICODE_ACCOLADE[0], self.properties.getDocName(), self.properties.getVersion(), UNICODE_ACCOLADE[1])

		content += " author: {:s}, \\\\ \n".format(str(self.credentials))
	
		#if (author_email is not None):
		#	_lines += " email: {:s} \\\\ \n".format(latex_hyper_reference("mailto:{:s}".format(author_email), author_email, "blue", True))

		content += " \\date{:s}{:s} \n".format(UNICODE_ACCOLADE[0], UNICODE_ACCOLADE[1])
		content += "{:s}\n".format(UNICODE_ACCOLADE[1])
		self.fd.write(content+"\n")

if __name__ == "__main__":
	ProductGuide(sys.argv[1:])

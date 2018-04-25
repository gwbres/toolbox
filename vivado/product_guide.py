#! /usr/bin/env python3

#########################
# Guillaume W. Bres, 2016    <guillaume.bres@noisext.com>
#########################
# product-guide.py
# generates a .pdf file to describe HDL IPs in a unified document suite
# resulting pdf can be included in Vivado packager directly 

#############
# TODO
# logo scale should be passed from CLI

import os 
import sys 
import datetime 

sys.path.append("../latex")
from latex import *

#TODO underline marche sur la ligne suivante

# Command line interface
KNOWN_ARGS = [
	"--help",
	"--author", 
	"--output",
	"--date",
	# IP settings
	"--ip-name", 
	"--ip-version", 
	"--ip-category", 
	"--ip-encrypted",
	# Author / company
	"--author-email", 
	"--company-website",
	"--company-logo",
]

KNOWN_ARGS_INFO = [
	"Print script help",  
	"Set IP author/vendor name", 
	"Set output file (default is 'template.tex')",
	"Set packaging date (override build time)",
	# IP settings
	"Set IP name", 
	"Set IP version", 
	"Set IP category (seen in Vivado IP library)",
	"IP source files are encrypted",
	# Author / company
	"Set author email",
	"Refer to company website",
	"Add IP logo on document",
]

# language packages
DEFAULT_LANGUAGE_PACKAGES = ["inputenc", "babel", "fontenc", "moresize"]
DEFAULT_LANGUAGE_PACKAGES_ATTRIBUTES = ["latin1", "english", "T1", None]

# graphics packages
DEFAULT_GRAPHICS_PACKAGES = ["graphicx", "float"]
DEFAULT_GRAPHICS_PACKAGES_ATTRIBUTES = [None, None]

# tab packages
DEFAULT_TAB_PACKAGES = ["adjustbox", "multirow", "multicol"]
DEFAULT_TAB_PACKAGES_ATTRIBUTES = [None, None, None]

# url packages
DEFAULT_URL_PACKAGES = ["hyperref"]
DEFAULT_URL_PACKAGES_ATTRIBUTES = ["hidelinks"]

# toc packages
DEFAULT_TOC_PACKAGES = ["titlesec", "tocbibind"]
DEFAULT_TOC_PACKAGES_ATTRIBUTES = [None, "nottoc, notlof, notlot"]

# maths packages
DEFAULT_MATHS_PACKAGES = ["mathtools", "amsfonts", "amsmath", "mathrsfs", "amssymb"]
DEFAULT_MATHS_PACKAGES_ATTRIBUTES = [None, None, None, None, None]

# all default packages
DEFAULT_PACKAGES = [
	*DEFAULT_LANGUAGE_PACKAGES,
	*DEFAULT_GRAPHICS_PACKAGES, 
	*DEFAULT_URL_PACKAGES, 
	*DEFAULT_TAB_PACKAGES,
	*DEFAULT_TOC_PACKAGES,
	*DEFAULT_MATHS_PACKAGES ] 

DEFAULT_PACKAGES_ATTRIBUTES = [ 
	*DEFAULT_LANGUAGE_PACKAGES_ATTRIBUTES,
	*DEFAULT_GRAPHICS_PACKAGES_ATTRIBUTES, 
	*DEFAULT_URL_PACKAGES_ATTRIBUTES, 
	*DEFAULT_TAB_PACKAGES_ATTRIBUTES,
	*DEFAULT_TOC_PACKAGES_ATTRIBUTES,
	*DEFAULT_MATHS_PACKAGES_ATTRIBUTES ] 

DEFAULT_PACKAGES_COMMENT = "default packages"

# custom graphics
CUSTOM_GRAPHICS_PACKAGES = ["pifont", "fancyhdr", "geometry", "color", "xcolor"]
CUSTOM_GRAPHICS_PACKAGES_ATTRIBUTES = [None, None, None, None, "dvipsnames"]

# custom packages
CUSTOM_PACKAGES = [ *CUSTOM_GRAPHICS_PACKAGES ]
CUSTOM_PACKAGES_ATTRIBUTES = [ *CUSTOM_GRAPHICS_PACKAGES_ATTRIBUTES ]
CUSTOM_PACKAGES_COMMENT = "custom packages"

# custom commands
CUSTOM_COMMAND_NAMES = [ "\\cmark","\\xmark" ]
CUSTOM_COMMAND_CODE = [ "\\ding{:s}51{:s}".format(UNICODE_ACCOLADE[0],UNICODE_ACCOLADE[1]), "\\ding{:s}55{:s}".format(UNICODE_ACCOLADE[0],UNICODE_ACCOLADE[1])] 

# custom doc properties
CUSTOM_DOC_PROPERTIES_COMMANDS = [ 
	"addtolength", 
	"addtolength", 
	"addtolength",
	"setlength", 
	"pagestyle",
	"setlength",
	"setlength",
	"setlength"]

CUSTOM_DOC_PROPERTIES_ATTRIBUTES = [ 
	"\\voffset",
	"\\hoffset",
	"\\textwidth",
	"\\footskip",
	"fancy",
	"\\tabcolsep",
	"\\headheight",
	"\\parindent"]

CUSTOM_DOC_PROPERTIES_VALUES = [ 
	"-1cm", 
	"-1.5cm", 
	"3.5cm",
	"-4.5cm", 
	"",
	"0.5em",
	"30pt",
	"0pt"]


# includes all default packages
def include_default_packages( product_guide ):
	latex_comment( product_guide, DEFAULT_PACKAGES_COMMENT )
	for package, attribute in zip( DEFAULT_PACKAGES, DEFAULT_PACKAGES_ATTRIBUTES ):
		if attribute is not None:
			_command = [[attribute,UNICODE_BRAKET],[package,UNICODE_ACCOLADE]]
		else:
			_command = [[package,UNICODE_ACCOLADE],]
		latex_command( product_guide, "usepackage", _command ) 
	product_guide.write("\n")

# includes all custom packages
def include_custom_packages( product_guide ):
	latex_comment( product_guide, CUSTOM_PACKAGES_COMMENT )
	for package, attribute in zip( CUSTOM_PACKAGES, CUSTOM_PACKAGES_ATTRIBUTES ):
		if attribute is not None:
			_command = [[attribute,UNICODE_BRAKET],[package,UNICODE_ACCOLADE]]
		else:
			_command = [[package,UNICODE_ACCOLADE],]
		latex_command( product_guide, "usepackage", _command ) 
	product_guide.write("\n")

# declares all custom commands
def declare_custom_commands( product_guide ):
	latex_comment( product_guide, "custom commands" )
	for name, code in zip( CUSTOM_COMMAND_NAMES, CUSTOM_COMMAND_CODE ):
		_command = [[name,UNICODE_ACCOLADE],[code,UNICODE_ACCOLADE],]
		latex_command( product_guide, "newcommand", _command )
	product_guide.write("\n")

# sets all custom properties
def set_custom_properties( product_guide ):
	latex_comment( product_guide, "custom properties" )
	for index in range( 0, len( CUSTOM_DOC_PROPERTIES_COMMANDS )):
		_command = CUSTOM_DOC_PROPERTIES_COMMANDS[index]
		_attribute = CUSTOM_DOC_PROPERTIES_ATTRIBUTES[index]
		_value = CUSTOM_DOC_PROPERTIES_VALUES[index]
		latex_command( product_guide, _command, [[_attribute,UNICODE_ACCOLADE],[_value,UNICODE_ACCOLADE]] )
	product_guide.write("\n")

def set_custom_page_style(fd, 
	ip_name, ip_version, 
	author_email=None,
	font=None, 
	logo=None, website=None, 
	date=None):

	"""
	sets the custom page style
	puts ip_name/ip_version  @upper left corner of each page
	
	if logo: [image.png, scale=0.3] is defined
	puts company logo @upper right corner

	if website is defined, writes url at bottom page

	font: selects custom font for fancy page style text,
	default is Helvetica

	date: default latex build time can be overriden
	"""
	latex_comment(fd, "custom page style")

	if (logo is not None):
		content = "\\includegraphics[scale=0.3]{:s}{:s}{:s}".format(UNICODE_ACCOLADE[0], logo, UNICODE_ACCOLADE[1])
		command = [content, UNICODE_ACCOLADE]
		latex_command(fd, "fancyhead[L]", [command,], disable_underscore_correction=True)

	# font
	if (font is None):
		font = "Helvetica" 
	latex_comment(fd, "fancy page style font")
	fd.write(latex_font_selection(font, "large")+"\n")

	# date
	if (date is None):
		content = " {0:s} v{1:s}\\\\ \\today".format(ip_name, ip_version)
	else:
		content = " {0:s} v{1:s}\\\\ \\date{2:s}{3:s}{4:s}".format(ip_name, ip_version, UNICODE_ACCOLADE[0], date, UNICODE_ACCOLADE[1])
	command = [content, UNICODE_ACCOLADE]
	latex_command(fd, "fancyfoot[L]", [command,])

	if (website is not None):
		content = " " + latex_hyper_reference(website, website, "blue", True)
		command = [content, UNICODE_ACCOLADE]
		latex_command(fd, "fancyfoot[C]", [command,])
	fd.write("\n")

def set_sections_style(product_guide):
	"""
	Sets sections & subsections fonts and style
	#TODO: improve with common font & dependent size
	"""
	latex_comment(product_guide, "custom parts font")
	product_guide.write("\\titleformat{0:s}\\section{1:s}{0:s}\\normalfont\\sffamily\\huge\\bfseries{1:}{0:s}{1:}{0:s}0em{1:s}{0:s}{1:s}\n".format(UNICODE_ACCOLADE[0],UNICODE_ACCOLADE[1]))
	product_guide.write("\\titleformat{0:s}\\subsection{1:s}{0:s}\\normalfont\\sffamily\\Large\\bfseries{1:s}{0:s}{1:s}{0:s}0em{1:s}{0:s}{1:s}\n".format(UNICODE_ACCOLADE[0],UNICODE_ACCOLADE[1]))
	product_guide.write("\\titleformat{0:s}\\subsubsection{1:s}{0:s}\\normalfont\\sffamily\\large\\bfseries{1:s}{0:s}{1:s}{0:s}0em{1:s}{0:s}{1:s}\n".format(UNICODE_ACCOLADE[0],UNICODE_ACCOLADE[1]))
	product_guide.write("\n")

def build_title(fd, author_name, ip_name, 
		ip_version="1.0", ip_category=None, 
		logo=None, website=None,
		author_email=None):

	"""
	Builds document title
	"""
	latex_comment(fd, "title")

	_lines = "\n\\title{:s} \n".format(UNICODE_ACCOLADE[0])

	if (logo is not None):
		_lines += "  \\includegraphics[scale=0.3]{:s}{:s}{:s}\\\\\n".format(UNICODE_ACCOLADE[0], logo, UNICODE_ACCOLADE[1])

	if (website is not None):
		_lines += latex_hyper_reference(website, website, "blue", True)+"\n"

	fd.write(_lines)

	latex_command(fd, "vspace", [["0.5cm",UNICODE_ACCOLADE],])
	
	ip_name = ip_name.replace("_", "{:s}_".format(UNICODE_BACKSLASH))
	_lines = "  IP: {0:s}\\tt {1:s} v{2:s}{3:s} \\\\ \n".format(UNICODE_ACCOLADE[0], ip_name, ip_version, UNICODE_ACCOLADE[1])

	if (ip_category is not None):
		ip_category = ip_category.replace("_", "{:s}_".format(UNICODE_BACKSLASH))
		_lines += "  IP category: {0:s}\\tt {1:s} {2:s} \\\\ \n".format(UNICODE_ACCOLADE[0], ip_category, UNICODE_ACCOLADE[1])
	
	_lines += " author: {:s}, \\\\ \n".format(author_name)

	if (author_email is not None):
		_lines += " email: {:s} \\\\ \n".format(latex_hyper_reference("mailto:{:s}".format(author_email), author_email, "blue", True))

	_lines += " \\date{:s}{:s} \n".format(UNICODE_ACCOLADE[0], UNICODE_ACCOLADE[1])
	_lines += "{:s}\n".format(UNICODE_ACCOLADE[1])

	fd.write(_lines+"\n")

def set_document_font(product_guide, font="Helvetica"):
	"""
	Sets font for entire document body
	"""
	latex_comment(product_guide, "body font")
	product_guide.write(latex_font_selection(font, "large")+"\n")

def build_introduction_template(fd, ip_name, ip_category=None, OpenSource=True):
	"""
	Builds introduction template
	"""

	latex_section(fd, "Introduction", "introduction", True)

	latex_command(fd, "noindent", [])
	if (ip_category is None):
		ip_category = "generic IP core"

	content = "The {:s} IP core is a {:s}.\n".format(ip_name.replace("_","\_"), ip_category)
	fd.write(content) 
	
	latex_section(fd, "Features", "features", True)
	
	_items = ["High performance implementation", 
		"Fully AXI4S compliant", 
		"Supports some non-default AXI4S signals", 
		"Several architectures available"
	]
	
	latex_listing(fd, LATEX_ITEMIZE_LISTING, _items)
	
	fd.write("\\hfill\n\n")

	latex_tabular_begin(fd, "|l|r|")
	fd.write("\\hline\n")
	latex_command(fd, "multicolumn", [["2",UNICODE_ACCOLADE],["|c|",UNICODE_ACCOLADE],["Release notes",UNICODE_ACCOLADE]])
	fd.write("\\\\ \\hline\n")
	fd.write("Supported & Zynq-7 \\\\\n device family & 7 Series \\\\\n" )
	fd.write("\\hline\n")
	fd.write("Timing & See IP \\\\\nPerformances & specifications: {:s}\\\\\n".format(latex_reference("ip_specifications", "blue")))
	fd.write("\\hline\n")

	latex_command(
		fd, "multicolumn", [["2",UNICODE_ACCOLADE],["|c|",UNICODE_ACCOLADE],["Provided with the IP core",UNICODE_ACCOLADE]]
	)

	fd.write("\\\\ \\hline\n")
	if (OpenSource == True):
		fd.write("Source files & Open source \\\\\n")
	else:
		fd.write("Source files & Encrypted \\\\\n")

	fd.write("\\hline\n")
	fd.write( "Example design & Not provided \\\\\n")
	fd.write("\\hline\n")
	fd.write("RTL  & VHDL \\\\\n")
	fd.write("\\hline\n")
	fd.write("Test bench & VHDL \\\\\n")
	fd.write("\\hline\n")
	fd.write("Constraint files & XDC \\\\\n")
	fd.write("\\hline\n")
	latex_tabular_end(fd, "1cm") 

	latex_command(fd, "newpage", [])
	latex_command(fd, "\n\\tableofcontents", [])
	latex_command(fd, "newpage", [])
	fd.write("\n")

# builds a template of ip specifications
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

# builds product guide
def product_guide(
	fp,
	author, 
	ip_name, 
	ip_version="1.0", ip_category=None,
	author_email=None, 
	logo=None, website=None,
	OpenSource=True,
	font=None,
	date=None):

	fd = open(fp, "w")
	
	# header
	document_class(fd)
	
	# default packages
	include_default_packages(fd)
	# required packages
	include_custom_packages(fd)
	declare_custom_commands(fd)
	# custom doc properties
	set_custom_properties(fd)
	
	# fancy page style
	set_custom_page_style(
		fd, 
		ip_name, 
		ip_version=ip_version, 
		author_email=author_email,
		logo=logo, website=website,
		font=font,
		date=date,
	)
	
	set_sections_style(fd) # custom sections style

	# body
	latex_begin_doc(fd)
	set_document_font(fd, font=font) 
	
	build_title(fd, 
		author, 
		ip_name, ip_version=ip_version, ip_category=ip_category, 
		logo=logo, website=website,
		author_email=author_email
	)

	latex_make_title(fd)
	
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
		
def main(argv):
	argv=argv[1:]

	if (len(argv) == 0):
		print_script_help()
		return 0

	# default doc. properties
	font = "Helvetica"
	output = "template.tex"

	# default packaging env.
	date = None
	ip_author = None
	ip_name = None
	ip_version = "1.0"
	ip_category = None
	author_email = None
	company_logo = None
	company_website = None
	OpenSource = True

	for arg in argv:
		key = arg.split("=")[0]
		value = arg.split("=")[1]
		
		if (key not in KNOWN_ARGS):
			print("Unknown flag {:s}".format(key))
			return -1

		if key == "--author":
			author = value.replace("_"," ")
		elif key == "--author-email":
			author_email = value
		elif key == "--ip-name":
			ip_name = value.replace("_"," ")
		elif key == "--ip-version":
			ip_version = value
		elif key == "--ip-category":
			ip_category = value.replace("_"," ")
		elif key == "--ip-encrypted":
			OpenSource = False
		elif key == "--date":
			date = value.replace("_"," ")
		elif key == "--company-logo":
			company_logo = value
		elif key == "--company-website":
			company_website = value
		elif key == "--font":
			font = value
		elif key == "--output":
			output = value

	# mandatory arguments
	if (author is None):
		print("mandatory value --author was not defined")
		return -1
	
	if (ip_name is None):
		print("mandatory flag --ip-name was not defined")
		return -1

	product_guide(
		output,
		author, 
		ip_name, 
		font=font,
		ip_version=ip_version, 
		ip_category=ip_category, 
		author_email=author_email, 
		logo=company_logo,
		website=company_website,
		OpenSource=OpenSource,
		date=date
	)
	
	print('Product guide model "{:s}" has been created'.format(output))
	return 0

if __name__ == "__main__":
	main(sys.argv)

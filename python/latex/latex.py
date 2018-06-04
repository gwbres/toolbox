# unicode
UNICODE_BACKSLASH = "\u005C"
UNICODE_ACCOLADE = ["\u007B", "\u007D"]
UNICODE_BRAKET = ["\u005B", "\u005D"]

# latex language 
LATEX_COMMENT = "%"
LATEX_SUPPORTED_MARKERS = [UNICODE_ACCOLADE, UNICODE_BRAKET]
LATEX_ENUMERATE_LISTING = "enumerate"
LATEX_ITEMIZE_LISTING = "itemize"
LATEX_SUPPORTED_LISTING_TYPES = [LATEX_ENUMERATE_LISTING, LATEX_ITEMIZE_LISTING]
LATEX_SUPPORTED_DOCUMENT_CLASSES = ["article", "paper"]

# supported fonts
LATEX_FONTS_NAMES = [ 
	"Avant Garde", 
	"Bitstream Vera Sans", 
	"Bookman", 
	"Charter", 
	"Computer Concrete", 
	"Computer Modern", 
	"Courier", 
	"Garamond", 
	"Helvetica", 
	"Inconsolata", 
	"Latin Modern", 
	"Latin Modern Sans", 
	"Latin Modern Typewriter", 
	"Linux Biolinum", 
	"Linux Libertine", 
	"New Century Schoolbook", 
	"Palatino", 
	"Times", 
	"Uncial", 
	"Utopia", 
	"Zapf Chancery" ]

LATEX_FONTS = [ 
	"pag", 
	"fvs", 
	"pbk", 
	"bch", 
	"ccr", 
	"cmr", 
	"pcr", 
	"mdugm", 
	"phv", 
	"fi4", 
	"lmr", 
	"lmss", 
	"lmtt", 
	"LinuxBiolinumT-0sf", 
	"LinuxLibertineT-0sf", 
	"pnc", 
	"ppl", 
	"ptm", 
	"uncl", 
	"put", 
	"pzc" ] 

# latex_comment
# writes a latex compliant comment
def latex_comment( document, comment ):
	document.write( "{:s} {:s}\n".format( LATEX_COMMENT, comment ))

# latex_command
# writes a latex compliant command
def latex_command( document, command, params=None, disable_underscore_correction=None ): 
	_formated_string = "{:s}{:s}".format( UNICODE_BACKSLASH, command ) # default

	for param in params:
		value = param[0]
		markers = param[1]

		if disable_underscore_correction is None:
			underscore = value.find("_") # convenient for ip name & stuff with underscores
			if underscore > 0:
				value = value.replace( "_", "{:s}_".format( UNICODE_BACKSLASH ))

		_formated_string += "{:s}{:s}{:s}".format( markers[0], value, markers[1] )  # append attributes

	document.write( "{:s}\n".format( _formated_string )) 
	
# latex_font_selection
# returns select font command according to specified font_name
def latex_font_selection( font_name, size=None ):
	index = LATEX_FONTS_NAMES.index( font_name )
	font_pkg = LATEX_FONTS[index]
	_string = "\\fontfamily{0:s}{1:s}{2:s}\\selectfont".format( UNICODE_ACCOLADE[0], font_pkg, UNICODE_ACCOLADE[1] )
	if size is not None:
		_string += "\\{:s}".format(size)
	return _string

# latex_hyper_reference
# inserts an \href
def latex_hyper_reference( ref, display, color=None, isUnderlined=None ):
	if color is None:
		_string = "\\href{0:s}{1:s}{2:s}{0:s}{3:s}{2:s}".format( UNICODE_ACCOLADE[0], ref, UNICODE_ACCOLADE[1], display )
	else:
		if isUnderlined is None:
			_string = "\\href{0:s}{1:s}{2:s}{0:s}\\color{0:s}{3:s}{2:s}{0:s}{4:s}{2:s}{2:s}".format( UNICODE_ACCOLADE[0], ref, UNICODE_ACCOLADE[1], color, display )
		else:
			_string = "\\href{0:s}{1:s}{2:s}{0:s}\\color{0:s}{3:s}{2:s}{0:s}\\underline{0:s}{4:s}{2:s}{2:s}{2:s}".format( UNICODE_ACCOLADE[0], ref, UNICODE_ACCOLADE[1], color, display )
	return _string

# latex_reference
# inserts a \ref
def latex_reference( ref, color ):
	_string = "{0:s}\\color{0:s}{1:s}{2:s}\\underline{0:s}\\ref{0:s}{3:s}{2:s}{2:s}{2:s}".format( UNICODE_ACCOLADE[0], color, UNICODE_ACCOLADE[1], ref )
	return _string

# latex_listing()
# builds a list of item to the specificed format
def latex_listing( document, type_of_listing, items ):
	if type_of_listing not in LATEX_SUPPORTED_LISTING_TYPES:
		print( "type of listing: {:s} is not supported\n" )
		return -1
	
	latex_command( document, "begin", [[type_of_listing,UNICODE_ACCOLADE],])
	for item in items:
		document.write( "  \\item {:s}\n".format(item))
	latex_command( document, "end", [[type_of_listing,UNICODE_ACCOLADE],])

# latex_footnote()
# sets input string as a footnote
def latex_footnote( document, note ):
	latex_command( document, "footnote", [[note,UNICODE_ACCOLADE],])

# latex_tabular_begin()
# declares a tabular with specified format
#TODO arraystretch devrait etre programmable
#TODO liseret couleur companie ds tabula
def latex_tabular_begin( document, tab_format, vspace=None ):
	if vspace is not None:
		latex_command( document, "vspace", [[vspace, UNICODE_ACCOLADE,]])

	document.write( "{0:s}\\renewcommand{0:s}\\arraystretch{1:s}{0:s}1.3{1:s}\n".format(UNICODE_ACCOLADE[0], UNICODE_ACCOLADE[1]))
	latex_command( document, "begin", [["adjustbox", UNICODE_ACCOLADE],["max width=0.99\\linewidth",UNICODE_ACCOLADE]])
	latex_command( document, "begin", [["tabular", UNICODE_ACCOLADE], ["{:s}".format(tab_format), UNICODE_ACCOLADE]] )
	document.write("\n")

# latex_tabular_end()
# stops tabular declaration
def latex_tabular_end( document, vspace=None ):
	latex_command( document, "end", [["tabular", UNICODE_ACCOLADE],])
	latex_command( document, "end", [["adjustbox", UNICODE_ACCOLADE],])
	document.write("{:s}\n".format(UNICODE_ACCOLADE[1]))
	if vspace is not None:
		latex_command( document, "vspace", [[vspace, UNICODE_ACCOLADE,]])

# latex_figure()
# command to insert a figure
def latex_figure( fig, linewidth, caption=None ):
	_string = "\\begin{0:s}figure{1:s}\n".format(UNICODE_ACCOLADE[0],UNICODE_ACCOLADE[1])
	_string += "  \\includegraphis[width={0:s}\\linewidth]{1:s}{2:s}{3:s}\n".format( linewidth,UNICODE_ACCOLADE[0], fig, UNICODE_ACCOLADE[1])
	if caption is not None:
		_string += "  \\caption{:s}{:s}{:s}\n".format(UNICODE_ACCOLADE[0],caption,UNICODE_ACCOLADE[1])
	_string += "\\end{:s}figure{:s}\n".format(UNICODE_ACCOLADE[0],UNICODE_ACCOLADE[1])
	return _string

def latex_tt_format( string ):
	_string = "{:s}\\tt {:s}{:s}".format(UNICODE_ACCOLADE[0], string.replace("_","\_"),UNICODE_ACCOLADE[1])
	return _string

def latex_minipage( document, linewidth ):
	latex_command( document, "begin", [["minipage",UNICODE_ACCOLADE],["{:s}\\linewidth".format(linewidth),UNICODE_ACCOLADE],])

def latex_end_minipage( document ):
	latex_command( document, "end", [["minipage",UNICODE_ACCOLADE],])

def latex_position( document, pos ):
	latex_command( document, "begin", [[pos,UNICODE_ACCOLADE],])

def latex_end_position( document, pos ):
	latex_command( document, "end", [[pos,UNICODE_ACCOLADE],])

def document_class(document, docclass="article"):
	"""
	Sets document class,
	default is article
	"""
	latex_comment(document, "document class")
	latex_command(document, "documentclass", [[docclass, UNICODE_ACCOLADE],])
	document.write("\n")

# latex_begin_doc
# begins document
def latex_begin_doc( document ):
	latex_comment( document, "begin doc" )
	latex_command( document, "begin", [["document", UNICODE_ACCOLADE],])
	document.write("\n")

# latex_make_title
# displays title
def latex_make_title( document ):
	latex_comment( document, "make title and force new page" )
	latex_command( document, "maketitle", [] )
	latex_command( document, "newpage", [] )
	document.write("\n")

# latex_end_doc
# ends document
def latex_end_doc( document ):
	latex_comment( document, "end doc" )
	latex_command( document, "end", [["document", UNICODE_ACCOLADE],])

# latex_section
# writes a section with optional label & visibility in ToC
def latex_section( document, section, label=None, hideFromToc=None ):
	if hideFromToc is None:
		latex_command( document, "section", [["{:s}".format(section), UNICODE_ACCOLADE],] )
	else:
		latex_command( document, "section*", [["{:s}".format(section), UNICODE_ACCOLADE],] )

	if label is not None:
		latex_command( document, "label", [["{:s}".format(label), UNICODE_ACCOLADE],], True )
	document.write("\n")

# latex_subsection
# writes a subsection with optional label
def latex_subsection( document, section, label=None ):
	latex_command( document, "subsection", [["{:s}".format(section), UNICODE_ACCOLADE],] )
	if label is not None:
		latex_command( document, "label", [["{:s}".format(label), UNICODE_ACCOLADE],])
	document.write("\n")

# latex_subsubsection
# writes a subsubsection with optional label
def latex_subsubsection( document, section, label=None ):
	latex_command( document, "subsubsection", [["{:s}".format(section), UNICODE_ACCOLADE],] )
	if label is not None:
		latex_command( document, "label", [["{:s}".format(label), UNICODE_ACCOLADE],])
	document.write("\n")

#! /usr/bin/env python3

import sys

def print_help():
	print(">> latex_parser")
	print("use --doc-content to parse whole latex document content")
	print("use --from-section=section1 to parse content from section1 to EOF")
	print("use --from-section=section1 --to-section=section2 to parse content in between two sections")
	print("use --sections to parse all available sections content")
	print("use --sections=1 to parse 1st section content")
	print("use --tables to parse all available tables")
	print("use --tables=2 to parse 2nd table content")
	print("use --packages to parse all packages included in document")

# Returns first line number 
# where item has been identified
def find_in_file(fp, item):
	index = 0
	indexes = []
	f=open(fp,"r")
	for line in f:
		if not("titleformat" in line): # avoid settings
			if item in line:
				indexes.append(index)
		index += 1
	f.close()
	return indexes

# Returns document content
# between sof and eof (both excluded)
def retrieve_content(fp, sof, eof):
	content = ""
	f=open(fp,"r")
	index = 0
	for line in f:
		if (index > sof):
			if (index < eof):
				content += line
			else:
				return content
		index += 1
	f.close()
	return content

# Returns number of lines in given file
def number_of_lines(fp):
	f=open(fp,"r")
	index = 0
	for line in f:
		index += 1
	f.close()
	return index

# Returns array containing all content
# in between given marker
def parse_latex_content(latex, latex_key):
	indexes = find_in_file(latex, latex_key)
	if (len(indexes) < 2):
		print('No marker "{:s}" were found in file "{:s}"'.format(latex_key, latex))
		return None
	
	results = []
	pos = 0
	while (pos < len(indexes)-1):
		sof = indexes[pos+0]
		eof = indexes[pos+1]
		results.append(retrieve_content(latex, sof, eof))
		pos += 2

	return results

def main(argv):
	argv=argv[1:]

	fp = "" 
	method = None
	section1 = ""
	section2 = ""
	tabular_id = None

	if (len(argv) == 0):
		# CLI
		print_help()
		return -1
	else:
		for arg in argv:
			key = arg.split("=")[0]
			value = arg.split("=")[-1]

			if key == "--help":
				print_help()
				return 0
			
			elif key == "--doc-content":
				method = "doc-content"

			elif key == "--from-section":
				method = "sections-method"
				parsed = value.split("_")
				for p in parsed:
					section1 += p
					if parsed.index(p) != len(parsed)-1:
						section1 += " "

			elif key == "--to-section":
				method = "sections-method"
				parsed = value.split("_")
				for p in parsed:
					section2 += p
					if parsed.index(p) != len(parsed)-1:
						section2 += " "

			elif key == "--tables":
				method = "tables"

			elif key == "--table":
				method = "table"
				table_id = int(value)

			elif key == "--path":
				fp = value

			elif key == "--sections":
				method = "sections"

			elif key == "--section":
				method = "section"
				section_id = int(value)

			elif key == "--packages":
				method = "packages"

	# prints latex document content
	if method == "doc-content":
		indexes = find_in_file(fp, "begin{document}")
		if (len(indexes) == 0):
			print("file {:s} is not latex compliant".format(fp))
			return -1

		sof = indexes[0]

		indexes = find_in_file(fp, "\end{document}")
		if (len(indexes) == 0):
			print("\end{document} was not found in file {:s}".format(fp))
			return -1

		eof = indexes[0]

		content = retrieve_content(fp, sof, eof-1)
		print(content)

	# prints latex content between section1 and section2 (all included)
	elif method == "sections-method":		
		indexes = find_in_file(fp, section1)
		
		if (len(indexes) == 0):
			print('Section #1 "{:s}" was not found in document {:s}'.format(section1, fp))
			return -1
		else:
			sof = indexes[0]-1
		
		if (len(section2) == 0): # assume end of file
			indexes = find_in_file(fp, "end{document}")
		else:
			indexes = find_in_file(fp, section2)

		if (len(indexes) == 0):
			print('Section #2 "{:s}" was not found in document {:s}'.format(section2, fp))
			return -1
		else:
			eof = indexes[0]

		content = retrieve_content(fp, sof, eof)
		print(content)

	# Returns an array containing all available tables in latex document
	elif method == "tables":
		tables = parse_latex_content(fp, "tabular")
		for t in tables:
			print("table [{:d}]".format(tables.index(t)))
			print(t)

	elif method == "table":
		print(parse_latex_content(fp, "tabular")[table_id-1])

	elif method == "sections":
		sections = parse_latex_content(fp, "section")
		for s in sections:
			print("section [{:d}]".format(sections.index(s)))
			print(s)
	
	elif method == "section":
		print(parse_latex_content(fp, "section")[section_id-1])

	elif method == "packages":
		print(parse_all_packages(fp))

	return 0

if __name__ == "__main__":
	main(sys.argv)

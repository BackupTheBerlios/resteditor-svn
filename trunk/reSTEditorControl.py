"""
This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
"""

"""
This module defines the reStructuredTextEditorControl-class with all its methods
that are necessary for the implementation of the reStructuredTextEditor.
"""

import os, os.path
import subprocess
import tempfile

try:
	import win32process
except:
	win32process = None

from time import time
from docutils.core import publish_file

class reSTEditorControl:
	"""Define all methods for reSTEditor."""
	
	def transformRST(self, workingFile):
		"""
		Transform the content of given reST-file into html and write html-code to a file.
		Return filename of html-file.
		Return nothing if no filename is given. FAils when the txt-file is in a directory the user has no write access to
		
		Keyword arguments:
		workingFile -- name of reST-file (string)
		
		"""
		
		if workingFile: # only if filename is given - otherwise there would be an empty tempfile generated and not deleted
			#tmpFile must be created in a directory the user has write-access to -> using directory containing the txt-file.
			tmpFilename = "\\".join(workingFile.split("\\")[:-1]) + "\\reSTtempFile"+str(time())+".html" # i would love to use the python "tempfile"-module at this place
			outputFile = open(tmpFilename, "w")			  # but i can't, 'cause the generated files would be destroyed at the end of this method.
			outputFile.write(publish_file(open(workingFile, "r"), writer_name="html"))
			return tmpFilename
		else:
			return

	def getTXTFileContent(self, workingFile):
		"""Return all lines of a textfile in one list.
		
		Keyword arguments:
		workingFile -- path and name of textfile (string)
		
		"""
		file = open(workingFile, "r")
		lines=file.readlines()
		file.close()
		lines.reverse()
		return lines
	
	def setTXTFileContent(self, workingFile, inputCtrlText):
		"""Write text into a textfile.
		
		Keyword arguments:
		workingFile -- path and name of output-file (string)
		inputCtrlText -- text to write into textfile (string)
		
		"""
		file = open(workingFile, "w")
		file.write(inputCtrlText.encode('latin-1'))
		file.close()
	
	def saveFile(self, workingFile, inputCtrlText, duringExport, exportValues):
		"""Save text to a file, transform it into reST, save reST into file and return reST-filename
		
		When output-file dosn't exist, create it.
		
		Keyword arguments:
		workingFile -- path and name of file to write text to (string)
		inputCtrlText -- text to write into file and to transform into reST (string)
		duringExport -- indicating, if the file is saved during an export or just during editing (boolean)
		exportValues -- dictionary indicating export-status of every export-format (dictionary)
				      exportValues.keys: "HTML", "XML", "LaTeX", "DVI", "PDF"
		
		"""
		if not duringExport:
			self.cleanFilesUp(workingFile, False, exportValues)
		if workingFile =="": # if new file was created (no workingFile yet), save content of self.inputCtrl to file
			print "No filename given - file won't be saved"
			return False
		else:
			self.setTXTFileContent(workingFile, inputCtrlText)
		return self.transformRST(workingFile)
	
	def exportHTML(self, workingFile, explicit=False):
		"""Export given reST-file as html. Name of html-file is the same as name of given txt-file.
		
		Keyword arguments:
		workingFile -- path and name of reST-file (string)
		explicit -- indicates, if html-export is the only (explicit) export.
			      When true, the xml-, tex-, dvi- and pdf-files with the same name will be deleted,
			      otherwise they'll remain.
		
		"""
		outputFile = open(workingFile[:-3]+"html", "w")
		outputFile.write(publish_file(open(workingFile, "r"), writer_name="html"))
		if explicit:
			self.cleanFilesUp(workingFile, True, None, "html")
	
	def exportXML(self, workingFile, explicit=False):
		"""Export given reST-file as docbook/xml. Name of xml-file is the same as name of given txt-file.
		
		Keyword arguments:
		workingFile -- path and name of reST-file (string)
		explicit -- indicates, if docbook/xml-export is the only (explicit) export.
			      When true, the html-, tex-, dvi- and pdf-files with the same name will be deleted,
			      otherwise they'll remain.
		"""
		outputFile = open(workingFile[:-3]+"xml", "w")
		outputFile.write(publish_file(open(workingFile, "r"), writer_name="xml"))
		if explicit:
			self.cleanFilesUp(workingFile, True, None, "xml")
	
	def exportLaTeX(self, workingFile, explicit=False):
		"""Export given reST-file as LaTeX-code. Name of tex-file is the same as name of given txt-file.
		
		Keyword arguments:
		workingFile -- path and name of reST-file (string)
		explicit -- indicates, if LaTeX-export is the only (explicit) export.
			      When true, the html-, xml-, dvi- and pdf-files with the same name will be deleted,
			      otherwise they'll remain.
		"""
		
		outputFile = open(workingFile[:-3]+"tex", "w")
		outputFile.write(publish_file(open(workingFile, "r"), writer_name="latex"))
		if explicit:
			self.cleanFilesUp(workingFile, True, None, "tex")
	
	def exportDVI(self, workingFile, explicit=False):
		"""Export given reST-file as dvi. Name of dvi-file is the same as name of given txt-file.
		   Requires an installed LaTeX-environment.
		   Return False if LaTeX isn't installed, else return True.
		
		Keyword arguments:
		workingFile -- path and name of reST-file (string)
		explicit -- indicates, if dvi-export is the only (explicit) export.
			      When true, the html-, xml-, tex- and pdf-files with the same name will be deleted,
			      otherwise they'll remain.
		"""
		
		outputFile = open(workingFile[:-3]+"tex", "w")
		outputFile.write(publish_file(open(workingFile, "r"), writer_name="latex"))
		outputFile.close()
		try:
			os.chdir(os.path.dirname(workingFile)) # change working-directory into that one, that contains the tex-file
			if not win32process:
				subprocess.Popen(('latex', workingFile[:-3]+"tex")).wait()
			else:
				subprocess.Popen(('latex', workingFile[:-3]+"tex"), creationflags=win32process.CREATE_NO_WINDOW).wait()
		except WindowsError:
			return False
		if explicit:
			self.cleanFilesUp(workingFile, True, None, "dvi")
		return True
	
	def exportPDF(self, workingFile, explicit=False):
		"""Export given reST-file as pdf. Name of pdf-file is the same as name of given txt-file.
		   Requires an installed LaTeX-environment.
		   Return False if pdfLaTeX isn't installed, else return True.
		
		Keyword arguments:
		workingFile -- path and name of reST-file (string)
		explicit -- indicates, if pdf-export is the only (explicit) export.
			      When true, the html-, xml-, tex- and dvi-files with the same name will be deleted,
			      otherwise they'll remain.
		"""
		
		outputFile = open(workingFile[:-3]+"tex", "w")
		outputFile.write(publish_file(open(workingFile, "r"), writer_name="latex"))
		outputFile.close()
		try:
			os.chdir(os.path.dirname(workingFile)) # change working-directory into that one, that contains the tex-file
			if not win32process:
				subprocess.Popen(('latex', workingFile[:-3]+"tex")).wait()
			else:
				subprocess.Popen(('pdflatex', workingFile[:-3]+"tex"), creationflags=win32process.CREATE_NO_WINDOW).wait()
		except WindowsError:
			return False
		fileEndings = ["out", "log", "aux"]
		for fileEnding in fileEndings:
			try:
				os.remove(workingFile[:-3]+fileEnding)
			except OSError:
				pass
		if explicit:
			self.cleanFilesUp(workingFile, True, None, "pdf")
		return True
	
	def cleanFilesUp(self, workingFile, afterExplicitExport, exportValues, explicitFileEnding=""):
		"""Delete 
		
		Keyword arguments:
		workingFile -- path and name of reST-file (string)
		afterExplicitExport -- indicates, if the clean-up  follows during an explicit export (otherwise, all types
					    defined in exportValues will stay) (boolean)
		exportValues -- dictionary indicating export-status of every export-format (dictionary)
				      exportValues.keys: "HTML", "XML", "LaTeX", "DVI", "PDF"
		explicitFileEnding -- fileending of the filetype explicit exported (all other will be deleted) (string)
		
		"""
		
		if not afterExplicitExport:
			if not exportValues['HTML']:
				try:
					os.remove(workingFile[:-3]+"html")
				except OSError:
					pass
			if not exportValues['XML']:
				try:
					os.remove(workingFile[:-3]+"xml")
				except OSError:
					pass
			if not exportValues['LaTeX']:
				try:
					os.remove(workingFile[:-3]+"tex")
				except OSError:
					pass
			if not exportValues['DVI']:
				try:
					os.remove(workingFile[:-3]+"dvi")
				except OSError:
					pass
			if not exportValues['PDF']:
				try:
					os.remove(workingFile[:-3]+"pdf")
				except OSError:
					pass
			fileEndings = ["out", "log", "aux"]
			for fileEnding in fileEndings:
				try:
					os.remove(workingFile[:-3]+fileEnding)
				except OSError:
					pass
		else:
			fileEndings = ["html", "xml", "tex", "dvi", "pdf", "out", "log", "aux"]
			for fileEnding in fileEndings:
				if fileEnding == explicitFileEnding:
					pass
				else:
					try:
						os.remove(workingFile[:-3]+fileEnding)
					except OSError:
						pass
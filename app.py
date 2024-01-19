from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.graphics import shapes

import json
import os

def getStringWithCorrectWidth(string, size, startW, endW, font):
	wholeWidtn = stringWidth(string, font, size)
	if wholeWidtn < endW - startW:
		return [string]
	
	oneChar = stringWidth("M", font, size)
	splittedStr = string.split(" ")
	ret = []
	curLine = splittedStr[0]

	for word in splittedStr[1:]:
		if stringWidth(word + curLine, font, size) > endW - startW:
			ret.append(curLine)
			curLine = ""
		curLine += " "
		curLine += word
	ret.append(curLine)

	return ret

def writeSplittedText(cc, textArea, font, fontSize, startHor, endHor, startVert):
	height = A4[1]
	cc.setFont(font, fontSize)

	text = textArea["value"]

	splittedText = getStringWithCorrectWidth(text, fontSize, startHor, endHor, font)
	offset = startVert
	for line in splittedText:
		cc.drawString(startHor, height - offset, line)
		offset += fontSize

	if textArea["type"] == "link":
		cc.linkURL(textArea["link"], (startHor, height - offset + fontSize, endHor, height - startVert + fontSize))

	return offset

def drawLeftSideBar(cc, width, color):
	cc.setFillColor(color)
	cc.rect(0, 0, width, A4[1], stroke = 0, fill = 1)

def writeSideBarText(cc, sideWidth, data):
	cc.setFillColor(colors.white)
	
	height = A4[1]
	paddingLeft = 20
	paddingRight = 10

	offset = 40
	textFontSize = 11

	for ii, elem in enumerate(data["cv"]["sideBar"]):
		offset = writeSplittedText(cc, elem["title"], "Helvetica-Bold", 13, paddingLeft, sideWidth - paddingRight, offset)
		offset += 8

		for value in elem["values"]:
			cc.setFont("Helvetica", 11)
			offset = writeSplittedText(cc, value, "Helvetica", textFontSize, paddingLeft, sideWidth - paddingRight, offset)
			offset += 5
		offset += 20

def writeDetails(cc, sidebarWidth, data, paddingLeft, paddingRight):
	nameFontSize = 25
	nameFont = "Helvetica-Bold"

	professionFontSize = 12
	professionFont = "Helvetica"

	locationFontSize = 10
	details = data["cv"]["mainPage"]["details"]

	cc.setFont("Helvetica-Bold", nameFontSize)

	height = A4[1]

	offset = nameFontSize + 20

	# NAME
	offset = writeSplittedText(cc, details["name"], nameFont, nameFontSize, sidebarWidth + paddingLeft, A4[0] - paddingRight, offset)

	offset -= 5

	# PROFESSION
	offset = writeSplittedText(cc, details["profession"], professionFont, professionFontSize, sidebarWidth + paddingLeft, A4[0] - paddingRight, offset)
	
	offset += 25
	return offset

def drawBackgroundDetails(cc, sidebarWidth, data, paddingLeft, paddingRight, startOffset):
	backgroundDetails = data["cv"]["mainPage"]["background"]

	titleFontSize = 20
	titleFont = "Helvetica-Bold"

	placeFontSize = 15
	placeFont = "Helvetica"

	timeFontSize = 8
	timeFont = "Helvetica"

	labelFontSize = 12
	labelFont = "Helvetica"

	descFontSize = 10
	descFont = "Helvetica"

	pageHeight = A4[1]
	pageWidth = A4[0]

	offset = startOffset
	
	for elem in backgroundDetails:
		cc.setFont(titleFont, titleFontSize)
		# TITLE
		# offset += 5
		offset = writeSplittedText(cc, elem["title"], titleFont, titleFontSize, sidebarWidth + paddingLeft, pageWidth - paddingRight, offset)
		# offset -= 13

		for value in elem["values"]:
			# PLACE
			offset += 8
			offset = writeSplittedText(cc, value["place"], placeFont, placeFontSize, sidebarWidth + paddingLeft, pageWidth - paddingRight, offset)

			# LABEL
			offset = writeSplittedText(cc, value["label"], labelFont, labelFontSize, sidebarWidth + paddingLeft, pageWidth - paddingRight, offset)
			
			# TIME
			offset = writeSplittedText(cc, value["duration"], timeFont, timeFontSize, sidebarWidth + paddingLeft, pageWidth - paddingRight, offset)
			# time = "(" + value["start"] + " - " + value["end"] + ")"
			# labelSplitted = getStringWithCorrectWidth(time, timeFontSize, sidebarWidth + paddingLeft, pageWidth - paddingRight, timeFont)
			# for line in labelSplitted:
				# cc.drawString(sidebarWidth + paddingLeft, pageHeight - offset - timeFontSize, line)
				# offset += timeFontSize + 5

			offset += 8
			# DESCRIPTION
			offset = writeSplittedText(cc, value["description"], descFont, descFontSize, sidebarWidth + paddingLeft, pageWidth - paddingRight, offset)

			offset += 10
		offset += 20


def drawMainPage(cc, sidebarWidth, data):
	cc.setFillColor(colors.black)
	paddingLeft = 20
	paddingRight = 20

	offset = writeDetails(cc, sidebarWidth, data, paddingLeft, paddingRight)
	offset = drawBackgroundDetails(cc, sidebarWidth, data, paddingLeft, paddingRight, offset)

def createPdf(data):
	cc = canvas.Canvas("cvGenerated.pdf", pagesize=A4)
	cc.setTitle("My CV")

	sidebarWidth = 200

	width, height = A4

	drawLeftSideBar(cc, sidebarWidth, colors.darkslategray)
	writeSideBarText(cc, sidebarWidth, data)
	drawMainPage(cc, sidebarWidth, data)
	
	cc.save()

def readJson(fname):
	with open(fname, 'r') as ff:
		data = json.load(ff)

	return data

if __name__ == "__main__":
	createPdf(readJson("cv.json"))

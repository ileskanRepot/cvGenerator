from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.graphics import shapes
from requests import get

import sys
import json
import os


MSG = "EMPTYMSG"

def getStringWithCorrectWidth(string, size, startW, endW, font):
	wholeWidtn = stringWidth(string, font, size)
	if wholeWidtn < endW - startW:
		return [string]
	
	oneChar = stringWidth("M", font, size)
	splittedStr = string
	ret = []
	curLine = splittedStr[0]

	for word in splittedStr[1:]:
		if stringWidth(word + curLine, font, size) > endW - startW:
			ret.append(curLine)
			curLine = ""
		curLine += ""
		curLine += word
	ret.append(curLine)

	return ret

def writeSplittedText(cc, text, font, fontSize, startHor, endHor, startVert):
	height = A4[1]
	cc.setFont(font, fontSize)

	splittedText = getStringWithCorrectWidth(text, fontSize, startHor, endHor, font)
	offset = startVert
	for line in splittedText:
		cc.drawString(startHor, height - offset, line)
		offset += fontSize

	return offset

def writeSplittedObject(cc, textArea, font, fontSize, startHor, endHor, startVert):
	height = A4[1]
	cc.setFont(font, fontSize)


	offset = startVert

	if textArea["type"] == "text":
		text = textArea["value"]
		offset = writeSplittedText(cc, text, font, fontSize, startHor, endHor, startVert)

	elif textArea["type"] == "image":
		path = textArea["path"]
		ww = textArea["width"]
		hh = textArea["height"]
		cc.drawInlineImage(path, 30, height - (10 + hh), ww, hh)
		offset += hh + 10

	elif textArea["type"] == "link":
		text = textArea["value"]
		offset = writeSplittedText(cc, text, font, fontSize, startHor, endHor, startVert)
		cc.linkURL(f'https://links.ileska.fi/?nextURL={textArea["link"]}&msg={MSG}', (startHor, height - offset + fontSize, endHor, height - startVert + fontSize))

	elif textArea["type"] == "list":
		for elem in textArea["values"]:
			elem["value"] = elem["value"]
			offset = writeSplittedObject(cc, elem, font, fontSize, startHor, endHor, offset)

	return offset


def drawLeftSideBar(cc, width, color):
	cc.setFillColor(color)
	cc.rect(0, 0, width, A4[1], stroke = 0, fill = 1)

def writeSideBarText(cc, sideWidth, data):
	cc.setFillColor(colors.white)
	
	height = A4[1]
	paddingLeft = 20
	paddingRight = 10

	offset = 10
	textFontSize = 11

	for ii, elem in enumerate(data["cv"]["sideBar"]):
		offset = writeSplittedObject(cc, elem["title"], "Helvetica-Bold", 13, paddingLeft, sideWidth - paddingRight, offset)
		offset += 8

		for value in elem["values"]:
			cc.setFont("Helvetica", 11)
			offset = writeSplittedObject(cc, value, "Helvetica", textFontSize, paddingLeft, sideWidth - paddingRight, offset)
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
	offset = writeSplittedObject(cc, details["name"], nameFont, nameFontSize, sidebarWidth + paddingLeft, A4[0] - paddingRight, offset)

	offset -= 5

	# PROFESSION
	offset = writeSplittedObject(cc, details["profession"], professionFont, professionFontSize, sidebarWidth + paddingLeft, A4[0] - paddingRight, offset)

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
		offset = writeSplittedObject(cc, elem["title"], titleFont, titleFontSize, sidebarWidth + paddingLeft, pageWidth - paddingRight, offset)
		# offset -= 13

		for value in elem["values"]:
			# PLACE
			offset += 8
			offset = writeSplittedObject(cc, value["place"], placeFont, placeFontSize, sidebarWidth + paddingLeft, pageWidth - paddingRight, offset)

			# LABEL
			offset = writeSplittedObject(cc, value["label"], labelFont, labelFontSize, sidebarWidth + paddingLeft, pageWidth - paddingRight, offset)

			# TIME
			if len(value["duration"]["value"]) != 0:
				# print(value["place"]["value"], len(value["duration"]["value"]))
				offset = writeSplittedObject(cc, value["duration"], timeFont, timeFontSize, sidebarWidth + paddingLeft, pageWidth - paddingRight, offset)
				offset += 8

			# DESCRIPTION
			offset = writeSplittedObject(cc, value["description"], descFont, descFontSize, sidebarWidth + paddingLeft, pageWidth - paddingRight, offset)

			offset += 10
		offset += 20

def drawLotTextOneline(cc, text, start, yy):
	fontSize = 1
	stringSplitted = getStringWithCorrectWidth(text, fontSize, start, A4[0], "Helvetica")
	cc.setFont("Helvetica", fontSize)
	for line in stringSplitted:
		cc.drawString(start, yy, line)
def fetchRandomText():
	with open("tech_buzzwords.csv", "r") as ff:
		ret = ff.read()
	return ret
def drawRandomText(cc):
	cc.setFillColor(colors.white)
	textToWrite = fetchRandomText()
	drawLotTextOneline(cc, textToWrite, 200, 1)

def drawMainPage(cc, sidebarWidth, data):
	cc.setFillColor(colors.black)
	paddingLeft = 20
	paddingRight = 20

	offset = writeDetails(cc, sidebarWidth, data, paddingLeft, paddingRight)
	offset = drawBackgroundDetails(cc, sidebarWidth, data, paddingLeft, paddingRight, offset)

def createPdf(data):
	cc = canvas.Canvas("CV_AKSELI_LEINO.pdf", pagesize=A4)
	cc.setTitle("My CV")

	sidebarWidth = 200

	width, height = A4

	drawRandomText(cc)
	drawLeftSideBar(cc, sidebarWidth, colors.purple)
	writeSideBarText(cc, sidebarWidth, data)
	drawMainPage(cc, sidebarWidth, data)

	cc.save()

def readJson(fname):
	with open(fname, 'r') as ff:
		data = json.load(ff)

	return data

if __name__ == "__main__":
	if len(sys.argv) >= 2:
		MSG = sys.argv[1]
	createPdf(readJson("cv.json"))

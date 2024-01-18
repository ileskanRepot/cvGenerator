from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.graphics import shapes

import json
import os

def drawLeftSideBar(cc, width, color):
	cc.setFillColor(color)
	cc.rect(0, 0, width, A4[1], stroke = 0, fill = 1)

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

def writeSideBarText(cc, sideWidth, data):
	cc.setFillColor(colors.white)
	
	height = A4[1]
	paddingLeft = 20
	paddingRight = 10

	offset = 40
	textFontSize = 11

	for ii, elem in enumerate(data["cv"]["sideBar"]):
		cc.setFont("Helvetica-Bold", 13)
		cc.drawString(paddingLeft, height - offset, elem["title"])
		offset += 20

		for value in elem["values"]:
			cc.setFont("Helvetica", 11)

			splitted = getStringWithCorrectWidth(value["value"], textFontSize, paddingLeft, sideWidth - paddingRight, "Helvetica")
			offsetStart = offset
			for text in splitted:
				cc.drawString(paddingLeft, height - offset, text)
				offset += 10

			if value["type"] == "link":
				cc.linkURL(value["link"], (paddingLeft, height - offset + textFontSize, sideWidth - paddingRight, height - offsetStart + textFontSize))

			offset += 5
		offset += 20

def writeDetails(cc, sidebarWidth, data, paddingLeft, paddingRight):
	nameFontSize = 25
	professionFontSize = 12
	locationFontSize = 10
	details = data["cv"]["mainPage"]["details"]

	cc.setFont("Helvetica-Bold", nameFontSize)

	height = A4[1]

	offset = 20

	# NAME
	nameSplitted = getStringWithCorrectWidth(details["name"], nameFontSize, sidebarWidth + paddingLeft, A4[0] - paddingRight, "Helvetica-Bold")
	for line in nameSplitted:
		cc.drawString(sidebarWidth + paddingLeft, height - offset - nameFontSize, line)
		offset += 20

	# PROFESSION
	cc.setFont("Helvetica", professionFontSize)
	professionSplitted = getStringWithCorrectWidth(details["profession"], nameFontSize, sidebarWidth + paddingLeft, A4[0] - paddingRight, "Helvetica-Bold")
	for line in professionSplitted:
		cc.drawString(sidebarWidth + paddingLeft, height - offset - nameFontSize, line)
		offset += 15

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
		titleSplitted = getStringWithCorrectWidth(elem["title"], titleFontSize, sidebarWidth + paddingLeft, pageWidth - paddingRight, titleFont)
		# TITLE
		for line in titleSplitted:
			cc.drawString(sidebarWidth + paddingLeft, pageHeight - offset - titleFontSize, line)
			offset += titleFontSize + 5

		for value in elem["values"]:
			# PLACE
			cc.setFont(placeFont, placeFontSize)
			placeSplitted = getStringWithCorrectWidth(value["place"], placeFontSize, sidebarWidth + paddingLeft, pageWidth - paddingRight, placeFont)
			for line in placeSplitted:
				cc.drawString(sidebarWidth + paddingLeft, pageHeight - offset - titleFontSize, line)
				offset += placeFontSize
			offset += 10

			# LABEL
			cc.setFont(labelFont, labelFontSize)
			labelSplitted = getStringWithCorrectWidth(value["label"], labelFontSize, sidebarWidth + paddingLeft, pageWidth - paddingRight, labelFont)
			for line in labelSplitted:
				cc.drawString(sidebarWidth + paddingLeft, pageHeight - offset - labelFontSize, line)
				offset += labelFontSize + 5

			# TIME
			cc.setFont(timeFont, timeFontSize)
			time = "(" + value["start"] + " - " + value["end"] + ")"
			labelSplitted = getStringWithCorrectWidth(time, timeFontSize, sidebarWidth + paddingLeft, pageWidth - paddingRight, timeFont)
			for line in labelSplitted:
				cc.drawString(sidebarWidth + paddingLeft, pageHeight - offset - timeFontSize, line)
				offset += timeFontSize + 5

			# DESCRIPTION
			cc.setFont(descFont, descFontSize)
			descSplitted = getStringWithCorrectWidth(value["description"], descFontSize, sidebarWidth + paddingLeft, pageWidth - paddingRight, descFont)
			for line in descSplitted:
				cc.drawString(sidebarWidth + paddingLeft, pageHeight - offset - descFontSize, line)
				offset += descFontSize + 2

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

	sidebarWidth = 200

	width, height = A4

	drawLeftSideBar(cc, sidebarWidth, colors.darkslategray)
	writeSideBarText(cc, sidebarWidth, data)
	drawMainPage(cc, sidebarWidth, data)
	# dd = shapes.Drawing(100, 100)
	# rr = shapes.Rect(0, 0, 100, 100, fillColor=colors.purple, strokeColor=colors.black)
	# dd.add(rr)

	cc.save()

def readJson(fname):
	with open(fname, 'r') as ff:
		data = json.load(ff)

	return data

if __name__ == "__main__":
	createPdf(readJson("cv.json"))

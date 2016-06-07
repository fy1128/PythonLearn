#!/usr/bin/env python

from PIL import Image

CharArray = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'. "
def GetChar(r,g,b,alpha = 256) :
	if 0 == alpha :
		return ' '
	gray = int(0.2126 * r + 0.7152 * g + 0.0722 * b)
	return CharArray[int((gray * len(CharArray))/(256.0))]
	
if __name__ == '__main__' :
	
	im = Image.open('1.png')
	im = im.resize((100,100),Image.NEAREST)
	
	text = ''
	for i in range(100) :
		for j in range(100) :
			text += GetChar(*im.getpixel((j,i)))
		text += '\n'
	
	print text
	
	open('b.txt','w').write(text)

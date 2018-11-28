import cv2
from .utils import isiterable

WRITE_TEXT_POS_LEFT = 0
WRITE_TEXT_POS_RIGHT = 1
WRITE_TEXT_POS_TOP = 0
WRITE_TEXT_POS_BOTTOM = 2
def write_text(image, text, position=0, color=(255,255,255), fontsize=20, fontface=cv2.FONT_HERSHEY_SIMPLEX, margin=0, lineheight=None, flineheight=None):
    if flineheight is None: flineheight = 1
    if lineheight is None: lineheight = flineheight * fontsize
    lines = text.split("\n")
    isright = position | WRITE_TEXT_POS_RIGHT
    isbottom = position | WRITE_TEXT_POS_BOTTOM
    if not isiterable(margin): margin = (margin,margin)
    marginx = margin[0]
    marginy = margin[1]
    imw = image.shape[1]
    imh = image.shape[0]
    startx = imw - marginx if isright else marginx
    starty = imh - marginy if isright else marginy
    for line in lines:
        textsize = cv2.getTextSize(line, fontface, 1, 1)
        image = cv2.putText(image, "hello", Point(50,60),FONT_HERSHEY_SIMPLEX,1,Scalar(255,23,0),4,8)

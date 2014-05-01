import re
import sys
import math 
import ntpath
import urllib
import os.path
import unicodedata
from Debug import * 
from Version import __VERSION__  # for {{EVAL()}}, display in settings page
import Settings, ATVSettings
import PlexAPI

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from PIL import ImageFilter

# Layered Fullscreen Background
# usage:
# {{LFBG(<TEMPLATE>,                           
#  1     <TITLE>,                               
#  2     <SUBTILE>,                             
#  3     <FANART>,                              
#  4     <RESOLUTION>                          
#  5  [, <FONT>,                                
#  6     <TITLESIZEATV2>,                      
#  7     <SUBTITLESIZEATV2>,                          
#  8     <TITLECOLOR>,                    
#  9     <SUBTITLECOLOR>,                       
# 10     <ANCHOR-X>,                            
# 11     <ANCHOR-Y>,                            
# 12     <ANCHOR-X-OFFSET>,                     
# 13     <ANCHOR-Y-OFFSET>,                     
# 14     <IMAGEBLUR>,                           
# 15     <LAYERNAME-1>,...<LAYERNAME-N> ]       
# )}}
#
# return a png-Filename

def generate(self, src, srcXML, param):
    # Catch the Params
    params = eval('['+self._(param.replace(' ','+'))+']')
    fanartpath = sys.path[0]+"/assets/fanart"
    cachepath = fanartpath+"/cache"  
    stylepath = fanartpath+"/styles/"+params[0]
    cachefile = createFileHandle(params)

    # Setup Background
    if params[3] != "":
      urllib.urlretrieve(urllib.unquote(params[3]), cachepath+"/tmp.png")  
      background = Image.open(cachepath+"/tmp.png") 
    else:
      if os.path.isfile(stylepath+"/blank.jpg"):
        background = Image.open(stylepath+"/blank.jpg")
      else:
        background = Image.open(fanartpath+"/blank.jpg")
    background = background.convert('RGB') 
      
    # Already created?
    if os.path.isfile(cachepath+"/"+cachefile+".png"):
      return cachefile+".png" # Bye Bye  
    # No it's not
    else:             
      # Set Resolution and Merge Layers
      if params[4] == "720":
        im = resizedMerge(background, params, fanartpath) 
      else: # 1080
        im = resizedMerge(background, params, fanartpath)               
      # Setup Title Type Space
      if params[1] != None and params[1] != "":
        im = textToImage(1, im, params, fanartpath)  
      # Setup Subtitle Type Space
      if params[2] != None and params[2] != "":
        im = textToImage(2, im, params, fanartpath)  
      # Save to Cache
      im.save(sys.path[0]+"/assets/fanart/cache/"+cachefile+".png")   
    return cachefile+".png"

def textToImage(index, im, params, fanartpath):
    # Set Font      
    if params[5] != None and params[5] != "":  
      font = fanartpath+"/styles/"+params[0]+"/"+params[5]
    else: # Default Font
      font = fanartpath+"/HelveticaBold.ttf"  
    # Set Font Size
    if params[index+5] != None and params[index+5] != "": 
      fontsize = int(params[index+5])
    else: # Default Size
      if index == 2:
        fontsize = int(params[4]) / 36
      else:
        fontsize = int(params[4]) / 24
    # Set Color From Hex Value
    if params[index+7] != None and params[index+7] != "": 
      if is_hex(str(params[index+7])):
        textcolor = params[index+7]
        textcolor = tuple(int(textcolor[i:i+len(textcolor)/3], 16) for i in range(0, len(textcolor), len(textcolor)/3)) 
      else:
        textcolor = params[index+7]
    else: # Default Color
      textcolor = (255, 255, 255) 
    # Text & TypeSpace
    text = unicode(urllib.unquote(params[index]), 'utf-8').replace('+',' ').strip()
    draw = ImageDraw.Draw(im)
    width, height = draw.textsize(text, ImageFont.truetype(font, int(fontsize)))  
    # Anchor and Offset X
    if params[10] != None or params[10] != "" or params[12] != None or params[12] != "": 
      if params[10] == "right":
        offsetx = 1280 - width - int(params[12])
      elif params[10] == "center":
        offsetx = ( 1280 - width ) / 2
      elif params[10] == "left":
        offsetx = int(params[12])
      else:
       offsetx = 80
    else:
      offsetx = 80
    # Anchor and Offset Y
    if ( params[11] != None or params[11] != "" ) or ( params[13] != None or params[13] != "" ): 
      if params[11] == "bottom":
        offsety = 720 - height - int(params[13])
      elif params[11] == "middle":
        offsety = ( 720 - height ) / 2
      elif params[11] == "top" or params[11] == "":
        offsety = int(params[13])
      else:
        offsety = 80
      # Subtitle   
      if index == 2 and ( params[1] != None or params[1] != "" ):
        title = unicode(urllib.unquote(params[1]), 'utf-8').replace('+',' ').strip()
        titledraw = ImageDraw.Draw(im)
        if params[6] != None and params[6] != "": 
          titlefontsize = int(params[6])
        else: # Default Size
          titlefontsize = int(params[4]) / 24
        titlewidth, titleheight = titledraw.textsize(title, ImageFont.truetype(font, int(titlefontsize)))
        offsety = offsety + (titleheight * 120 / 100)        
    else:
      offsety = 80    
    # Handle 1080 / atv3 Text
    if params[4] == "1080":
      fontsize = fullHDtext(fontsize)  
      offsetx = fullHDtext(offsetx)   
      offsety = fullHDtext(offsety)   
    # Write    
    draw.text((int(offsetx), int(offsety)), text , font=ImageFont.truetype(font, int(fontsize)), fill=textcolor)
    return im    

def resizedMerge (background, params, fanartpath):  
    height = int(params[4])
    if height == 720:
      width = 1280
    else:
      width = 1920
    im = Image.new("RGB", (width, height), "black")
    background = background.resize((width, height), Image.ANTIALIAS)
    # Blur BG
    if params[14] != None and params[14] != "":
      for i in range(0,int(params[14])):
        background = background.filter(ImageFilter.BLUR)
    im.paste(background, (0, 0), 0)
    # Layers    
    layerrange = range(15, len(params))
    for layercounter in layerrange:
      if params[layercounter] != None:
        layer = Image.open(fanartpath+"/styles/"+params[0]+"/"+params[layercounter]+".png")
        layer = layer.resize((width, height), Image.ANTIALIAS)
        im.paste(layer, ( 0, 0),layer)
    return im 
    
def createFileHandle(params):
    # filter text
    cachefileStyle = normalizeString(params[0])
    cachefileTitle = normalizeString(params[1])
    cachefileSubtitle = normalizeString(params[2])
    # add layers
    layerrange = range(15, len(params))
    cachefileLayers = ""
    for layercounter in layerrange:
       if params[layercounter] != None:
         cachefileLayers = cachefileLayers+"+"+normalizeString(params[layercounter])   
    # fix for extra long subtitles 
    if len(cachefileSubtitle) > 50:
      cachefileSubtitle = cachefileSubtitle[0:50]    
    cachefile = cachefileTitle+"+"+cachefileSubtitle+"+"+cachefileStyle+cachefileLayers  

    return cachefile
    
def normalizeString(str):
    str = urllib.unquote(str).replace(' ','+')
    str = unicodedata.normalize('NFKD',unicode(str,"utf8")).encode("ascii","ignore")  # Only ASCII CHARS
    str = re.sub(r'\W+', '+', str) # No Special Chars  
    return str
    
def fullHDtext(number):
    number = int(number)*1080/720
    return number
    
def is_hex(s):
    hex_digits = set("0123456789abcdefABCDEF")
    for char in s:
        if not (char in hex_digits):
            return False
    return True
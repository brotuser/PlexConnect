import re
import sys
import math 
import ntpath
import urllib
import os.path
import unicodedata
from Debug import * 
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
#  6      <TITLESIZEATV2>,                      
#  7     <TITLECOLOR>,                          
#  8     <SUBTITLESIZEATV2>,                    
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
    param = param.replace(' ','+')
    params = eval('['+self._(param)+']')
    # Catch the Params
    param = param.replace(' ','+')
    params = eval('['+self._(param)+']')
    fanartpath = sys.path[0]+"/assets/fanart"
    cachepath = fanartpath+"/cache"
    # cachefile = urllib.unquote(params[1]).replace(' ','+')+"+"+urllib.unquote(params[2]).replace(' ','+')+"+"+ntpath.basename(urllib.unquote(params[3])).replace("&width=1920",'+').replace("&height=1080",'+') # Cache Filname
    cachefile = urllib.unquote(params[1]).replace(' ','+')+"+"+urllib.unquote(params[2]).replace(' ','+') # Cache Filname
    cachefile = unicodedata.normalize('NFKD',unicode(cachefile,"utf8")).encode("ascii","ignore")  # Only ASCII CHARS
    cachefile = re.sub(r'\W+', '+', cachefile) # No Special Chars         
    cachefile = cachefile+"+"+params[0];
    layerrange = range(15, len(params))
    for layercounter in layerrange:
       if params[layercounter] != None:
         cachefile = cachefile+"+"+params[layercounter]
    cachefile = cachefile+"+"+params[4]
    
    # Already created?
    if os.path.isfile(cachepath+"/"+cachefile+".png"):
        return cachefile+".png" # Bye Bye
        
    # No it's not
    else:
        
        # Setup Background
        if params[3] != "":
            urllib.urlretrieve(urllib.unquote(params[3]), cachepath+"/tmp.png")                
            background = Image.open(cachepath+"/tmp.png") 
        else:
            if os.path.isfile(fanartpath+"/styles/"+params[0]+"/blank.jpg"):
              background = Image.open(fanartpath+"/styles/"+params[0]+"/blank.jpg")
            else:
              background = Image.open(fanartpath+"/blank.jpg")
        background = background.convert('RGB')
                    
        # Set Resolution and Merge Layers
        if params[4] == "720":
            im = Image.new("RGB", (1280, 720), "black")
            background = background.resize((1280, 720), Image.ANTIALIAS)
            # Blur BG
            if params[14] != None and params[14] != "":
              for i in range(0,int(params[14])):
                background = background.filter(ImageFilter.BLUR)
            im.paste(background, (0, 0), 0)
            
            layerrange = range(15, len(params))
            for layercounter in layerrange:
              if params[layercounter] != None:
                layer = Image.open(fanartpath+"/styles/"+params[0]+"/"+params[layercounter]+".png")
                layer = layer.resize((1280, 720), Image.ANTIALIAS)
                im.paste(layer, ( 0, 0),layer)

        else: # 1080
            im = Image.new("RGB", (1920, 1080), "black")
            background = background.resize((1920, 1080), Image.ANTIALIAS)
            if params[14] != None and params[14] != "":
              for i in range(0,int(params[14])):
                background = background.filter(ImageFilter.BLUR)
            im.paste(background, (0, 0), 0)
            
            layerrange = range(15, len(params))
            for layercounter in layerrange:
              if params[layercounter] != None:
               layer = Image.open(fanartpath+"/styles/"+params[0]+"/"+params[layercounter]+".png")
               layer = layer.resize((1920, 1080), Image.ANTIALIAS)
               im.paste(layer, ( 0, 0),layer)                              
        
                    
        # Set Title Color From Hex
        if params[7] != None and len(params[7]) > 0:
            titlecolor = tuple(int(params[7][i:i+len(params[7])/3], 16) for i in range(0, len(params[7]), len(params[7])/3)) 
        else: # Default Subtitle Color
          titlecolor = (206, 127, 26) 

        # Set Subtitle Color From Hex
        if params[9] != None and len(params[9]) > 0:
          subtitlecolor = tuple(int(params[9][i:i+len(params[9])/3], 16) for i in range(0, len(params[9]), len(params[9])/3)) 
        else: # Default Subtitle Color
          subtitlecolor = (255, 255, 255)        
        
        # Set Font      
        if params[5] != None and params[5] != "":  
          font = fanartpath+"/styles/"+params[0]+"/"+params[5]
        else: # Default Font
          font = fanartpath+"/HelveticaBold.ttf"
        
        # Set Title Font Size
        if params[6] != None and params[6] != "": 
          titlefontsize = int(params[6])
        else: # Default Title Size
          titlefontsize = int(params[4]) / 24
        
        # Set Subtitle Font Size
        if params[8] != None and params[8] != "":
          subtitlefontsize = int(params[8])
        else:  # Default Subtitle Size
          subtitlefontsize = int(params[4])/36

        # Setup Title Type Space
        if params[1] != None and params[1] != "":
          title = unicode(urllib.unquote(params[1]), 'utf-8').replace('+',' ').strip()
          titledraw = ImageDraw.Draw(im)
          titlewidth, titleheight = titledraw.textsize(title, ImageFont.truetype(font, int(titlefontsize)))
        
        # Setup Subtitle Type Space
        if params[2] != None and params[2] != "":
          subtitle = unicode(urllib.unquote(params[2]), 'utf-8').replace('+',' ').strip()
          subtitledraw = ImageDraw.Draw(im)
          subtitlewidth, subtitleheight = subtitledraw.textsize(subtitle, ImageFont.truetype(font, int(subtitlefontsize)))

        # Anchor and Offset X
        if params[10] != None or params[10] != "" or params[12] != None or params[12] != "": 
          if params[10] == "right":
            titlex = 1280 - titlewidth - int(params[12])
            subtitlex = 1280 - subtitlewidth - int(params[12])
          elif params[10] == "center":
            titlex = ( 1280 - titlewidth ) / 2
            subtitlex = ( 1280 - subtitlewidth ) / 2
          else:
            titlex = int(params[12])
            subtitlex = int(params[12])
        else:
          titlex = 80
          subtitlex = 80
          
        # Anchor and Offset Y
        if params[11] != None or params[11] != "" or params[13] != None or params[13] != "": 
          if params[11] == "bottom":
            titley = 720 - titleheight - int(params[13])
          elif params[11] == "middle":
            titley = ( 720 - titleheight ) / 2
          else:
            titley = int(params[13])
        else:
          titley = 80
        
        subtitley = int(titley) + (int(titlefontsize) * 130 / 100)
          
        # Handle 1080 / atv3 Text
        if params[4] == "1080":
            titlefontsize = int(titlefontsize)*1080/720
            subtitlefontsize = int(subtitlefontsize)*1080/720  
            titlex = int(titlex)*1080/720
            titley = int(titley)*1080/720
            if subtitlex:
              subtitlex = int(subtitlex)*1080/720 
            if subtitley:
              subtitley = int(subtitley)*1080/720 
          
        # Write    
        if params[1] != None and params[1] != "":
          titledraw.text((int(titlex), int(titley)), title , font=ImageFont.truetype(font, int(titlefontsize)), fill=titlecolor)
        if params[2] != None and params[2] != "":
          subtitledraw.text((int(subtitlex), int(subtitley)), subtitle, font=ImageFont.truetype(font, int(subtitlefontsize)), fill=subtitlecolor)

        # Save to Cache
        im.save(sys.path[0]+"/assets/fanart/cache/"+cachefile+".png")
            
    return cachefile+".png"

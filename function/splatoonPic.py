from PIL import Image

def pvpPic(im1, im2):
    dst = Image.new('RGB', (im1.width + im2.width, im1.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (im1.width, 0))
    return dst

def salmonrunPic(stage,weapon1,weapon2,weapon3,weapon4):
    dst = Image.new('RGB',(stage.width,stage.height))
    dst.paste(stage,(0,0))
    dst.paste(weapon1,(0,370))
    dst.paste(weapon2,(70,370))
    dst.paste(weapon3,(140,370))
    dst.paste(weapon4,(210,370))
    return dst
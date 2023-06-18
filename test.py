from PIL import Image


im = Image.open("Images/walkable_0.png")
im.rotate(270)
im.save("Map.png")
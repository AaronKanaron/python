import os
from PIL import Image, ImageOps, ImageSequence
import time
import requests
from io import BytesIO


character_sets = [
    ["@", "&", "#", "B", "G", "5", "Y", "J", "?", "7", "!", "~", "^", ":", ".", " "], #0
    ["@", "#", "&", "B", "0", "G", "5", "Y", "J", "?", "7", "*", "!", "~", "^", ":", ",", ".", " "], #1
    ["@", "#", "$", "%", "&", "8", "B", "M", "W", "*", "m", "w", "q", "p", "d", "b", "k", "h", "a", "o", "Q", "0", "O", "Z", "X", "Y", "U", "J", "C", "L", "t", "f", "j", "z", "x", "n", "u", "v", "c", "r", "]", "[", "}", "{", "1", ")", "(", "|", "\\", "/", "?", "I", "l", "!", "i", ">", "<", "+", "_", "-", "~", ";", "\"", ":", "^", ",", "`", "'", ".", " "] #2
    ]

# =- Config -= #
# Symbols are not the same height as width, depending on how much you want to strech the image (x,y)
character_compensator = (2,1) 
# If you want to scale the image up in resolution ( smaller (0,5) - bigger (2) )
resolution_multiplier = 4
# When saving to a text file, put the path here. If output.txt does not exist, it will be created.
output_path = "output.txt"
# Depending on how much detail you want, less colors can give better results
characters = character_sets[0] # values from 0 to 2

frames = []


#Both for GIFS and Images

def pixel_iter(image):
    piX,piY = image.size
    result = ""

    for y in range(piY):
        for x in range(piX):
            luminosity = image.getpixel((x,y))
            idx = int((luminosity / 255) * (len(characters)-1))
            result += characters[idx]
        result += "\n"
    return result

def ratio_resize(image, invert = False, char_compensator = (1.9,1), max_size=(104,55)):
    width,height = image.size
    ratio = min(max_size[0]/width, max_size[1]/height)
    new_width, new_height = (width*ratio*char_compensator[0]*resolution_multiplier, height*ratio*char_compensator[1]*resolution_multiplier)
    image = ImageOps.invert(image) if not invert else image
    image = image.resize((int(new_width),int(new_height)), Image.Resampling.LANCZOS)
    return image

def color_transparency(image, orig_color = (0,0,0,0), new_color = (255,255,255,255)): #Extremely slow
    try:
        ctX,ctY = image.size
        image = image.convert("RGBA")
        for x in range(ctX):
            for y in range(ctY):
                if image.getpixel((x,y)) == (0,0,0,0) or image.getpixel((x,y)) == (255,255,255,0):
                    image.putpixel((x,y), (255,255,255,255))
        return image
    except Exception as e:
        print(f"Could not convert into rgba, continuing with black transparancy due to: " + e)
        return image
    
def find_transparency(image):
    if image.info.get("transparency", None) is not None:
        return True
    if image.mode == "P":
        transparent = image.info.get("transparency", -1)
        for _, index in image.getcolors():
            if index == transparent:
                return True
    elif image.mode == "RGBA":
        extrema = image.getextrema()
        if extrema[3][0] < 255:
            return True
    return False

# For GIFS

def frame_iter(image):
    for fr in ImageSequence.Iterator(image):
        frame = fr.convert("L")
        frame = ratio_resize(frame)
        frame = pixel_iter(frame)

        frames.append(frame)


def animate(seq_arr,repeat,time_between_frames): #Time in ms
    for _ in range(repeat):
        for i in range(len(seq_arr)):
            print("\n"*80+seq_arr[i])
            time.sleep(time_between_frames / 1000)
    print("done!")
    
    
    
# Main Function

def for_gifs(image):
    image = frame_iter(image)
    animate(frames, 3, 100)

def for_image(image):
    if find_transparency(image):
        transparent_white = True if "y" == input("Do you want to make the transparent background white? (y/n)\n") else False
        image = color_transparency(image) if transparent_white else image

    invert = True if "y" == input("Invert the image? (y/n)") else False
    image = image.convert("L")
    image = ratio_resize(image, invert, character_compensator)
    image = pixel_iter(image)
    print(image)

def main():
    try:
        # Inputs from user
        image_path = input("Drag and drop the image or white the image path\n").replace(" ", "")
        try:
            _, file_extension = os.path.splitext(image_path)
            if file_extension != ".gif" or not image.n_frames:
                image = Image.open(image_path)
                for_image(image)
            else: #It is an image
                image = Image.open(image_path)
                for_gifs(image)
        except Exception as e:
            if "https://" in image_path:
                print("is url")
                response = requests.get(image_path)
                img = Image.open(BytesIO(response.content))

                if image_path[:-3] != "gif" or not img.n_frames:
                    print("Is img")
                    for_image(img)
                else: #is gif
                    print("Is gif")
                    for_gifs(img)
            else:
                print("is invalid: " + str(e))
            
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()
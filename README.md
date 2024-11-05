Hello,

 this is for creating a simple Slideshow, best used with this HA plugin: https://github.com/matteobrusa/HASlideshow

 It create takes as input a Folder (and all subfolder), get jpgs from there, converts them to the given size, (without croping, it will get a black Background or a blurred version of the Picture)

It will keep track of the files and when you call the script again, only the new or removed files will be changed.

 To use it you have to replace some values:
 - input_folder = "***"  # Change this to your input folder path
 - output_folder = "***"  # Change this to your output folder path
 - blurred_background = True # The a blurry variant of the picture
 - target_height = 1200 # Target Height
 - target_width = 2000 # Target Width

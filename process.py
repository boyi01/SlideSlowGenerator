from PIL import Image, ImageFilter, ImageOps
import os
import json

def crop_to_aspect_ratio(image, target_ratio):
    """
    Crop an image to a specified aspect ratio, centered on the middle of the image.
    
    Parameters:
        image (PIL.Image): The input image to be cropped.
        target_ratio (float): The target aspect ratio (width / height).
        
    Returns:
        PIL.Image: The cropped image with the specified aspect ratio.
    """
    # Get original image dimensions
    original_width, original_height = image.size
    original_ratio = original_width / original_height
    
    # Determine new dimensions for cropping
    if original_ratio > target_ratio:
        # Image is wider than target ratio: crop width (centered horizontally)
        new_width = int(original_height * target_ratio)
        new_height = original_height
        left = (original_width - new_width) // 2
        upper = 0
    else:
        # Image is taller than target ratio: crop height (centered vertically)
        new_width = original_width
        new_height = int(original_width / target_ratio)
        left = 0
        upper = (original_height - new_height) // 2

    # Calculate right and lower boundaries based on left and upper to maintain centered crop
    right = left + new_width
    lower = upper + new_height

    # Crop and return the image, centered on the middle
    return image.crop((left, upper, right, lower))

def process_image(input_path, output_path,blurred_background, target_width, target_height):
    # Open the image
    img = Image.open(input_path)
    img = ImageOps.exif_transpose(img)
    # Ensure image is in RGB mode (no transparency issues)
    if img.mode != "RGB":
        img = img.convert("RGB")

    original_width, original_height = img.size
    aspect_ratio = original_width / original_height

    # Set target dimensions
    target_width = target_width
    target_height = target_height
    target_aspect_ratio = 5 / 3

    # Determine new dimensions with padding to achieve 5:3 aspect ratio
    if aspect_ratio > target_aspect_ratio:
        new_width = original_width
        new_height = int(new_width / target_aspect_ratio)
    else:
        new_height = original_height
        new_width = int(new_height * target_aspect_ratio)

    paste_position = ((new_width - original_width) // 2, (new_height - original_height) // 2)

    if blurred_background:


        # Create a blurred version of the original image
        new_background = img.filter(ImageFilter.GaussianBlur(25))
        new_background = crop_to_aspect_ratio(new_background,target_aspect_ratio)
        # Resize the blurred image to match the new dimensions
        new_background = ImageOps.contain(new_background, (new_width, new_height))
    else:
        
        # Create a new image with black background and the desired aspect ratio
        new_background = Image.new("RGB", (new_width, new_height), (0, 0, 0))

    # Use the blurred background to fill the black areas
    new_background.paste(img,paste_position)



    new_background=new_background.resize((target_width, target_height))

    # Save the final image
    new_background.save(output_path)
    print(f"Image processed and saved as {output_path}")

def load_processed_images(json_file):
    if os.path.exists(json_file):
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                return data if isinstance(data, list) else []  # Ensure it returns a list
        except (json.JSONDecodeError, ValueError):
            print(f"Warning: {json_file} is empty or contains invalid JSON. Starting fresh.")
            return []
    return []

def save_processed_images(json_file, processed_images):
    with open(json_file, 'w') as f:
        json.dump(processed_images, f, indent=4)

def resize_images_in_folder(input_folder, output_folder, json_file, blurred_background,target_width, target_height):
    # Load processed images from JSON log
    processed_images = load_processed_images(json_file)
    processed_paths = {img['input_path'] for img in processed_images}
    image_index = len(processed_images)  # Start numbering from the last count
    if image_index != 0:
        image_index += 1
    # Walk through all files in input directory and subdirectories
    current_input_paths = set()
    for root, _, files in os.walk(input_folder):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                input_path = os.path.join(root, file)
                current_input_paths.add(input_path)
                
                # Skip already processed images
                if input_path in processed_paths:
                    print(f"Skipping {input_path} (already processed)")
                    continue

                # Define output path with numbered filename
                output_path = os.path.join(output_folder, f"{image_index}.jpg")
                process_image(input_path, output_path, blurred_background,target_width,target_height)

                # Add to the processed images list
                processed_images.append({
                    "input_path": input_path,
                    "output_path": output_path
                })
                processed_paths.add(input_path)
                image_index += 1

    # Remove output images for deleted input images
    updated_processed_images = []
    for img in processed_images:
        if img['input_path'] not in current_input_paths:
            # If the input image no longer exists, delete the output image
            if os.path.exists(img['output_path']):
                os.remove(img['output_path'])
                print(f"Deleted output image {img['output_path']} because the input was removed.")
        else:
            updated_processed_images.append(img)

    # Save the updated processed images list
    save_processed_images(json_file, updated_processed_images)

if __name__ == "__main__":
    input_folder = "***"  # Change this to your input folder path
    output_folder = "***"  # Change this to your output folder path
    blurred_background = True # The a blurry variant of the picture
    target_height = 1200 # Target Height
    target_width = 2000 # Target Width
    json_file = os.path.join(output_folder, "processed_images.json")


    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Start resizing images in the input folder
    resize_images_in_folder(input_folder, output_folder, json_file,blurred_background,target_height,target_width)

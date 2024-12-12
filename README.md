# Copy-to-Clone
This is an Inkscape extension to find and replace copied images with a clone while keeping the transformations.

I had the problem in a very large Inkscape document where I had a lot of copied images (icons) and needed to replace them with copies in order to make the SVG smaller. 

# Algorithm: Convert Copies to Clones 

1. Select the Original Image

Prompt the user to select an image to be the "original".

2. Check for Existing Clones

Scan the SVG document for any existing clones.
If the selected image is already a clone:
Identify the original image it's cloned from.
Update the selection to the original image.
Store the x, y, width, and height attributes of the original image.
If the selected image is the "original" for other clones, proceed to the next step. Otherwise, make it a clone of the existing original and exit.

3.Identify Copies

Find all images in the document with the same xlink:href attribute as the original image.

4. Transform Copies into Clones

For each identified copy:
Calculate the transformation matrix needed to position and scale the copy relative to the original image. This might involve using the inkex.transforms module and considering the x, y, width, and height attributes of both the original and the copy.
Create a clone of the original image.
Apply the calculated transformation matrix to the clone.
Delete the original copy.
Update the SVG Document

5. Save the modified SVG document.

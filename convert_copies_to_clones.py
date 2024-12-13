import inkex
import datetime
import numpy as np
from lxml import etree  # Import etree from lxml


class ConvertCopiesToClones(inkex.EffectExtension):
    def __init__(self):
        inkex.EffectExtension.__init__(self)
        self.log_file = 'extension_log.txt'
        self.enable_logging = True

    def effect(self):
        if self.enable_logging:
            with open(self.log_file, 'a') as f:
                f.write(f"--- ConvertCopiesToClones ---\n")
                f.write(f"{datetime.datetime.now()}\n")

        # 1. Select the Original Image
        selected_image = self.svg.selection.get(inkex.Image)
        if not selected_image:
            inkex.errormsg("Please select an image.")
            return

        # 2. Check for Existing Clones
        original_image = self.get_original_image(selected_image[0])
        if original_image is None:
            inkex.errormsg("Selected image is not part of a clone group or is already the original.")
            return

        # Store original image data
        original_x = float(original_image.get('x'))
        original_y = float(original_image.get('y'))
        original_width = float(original_image.get('width'))
        original_height = float(original_image.get('height'))

        # 3. Identify Copies
        xlink_href = original_image.get('xlink:href')
        copies = self.svg.xpath(f'//svg:image[@xlink:href="{xlink_href}"]')

        # 4. Transform Copies into Clones
        for copy in copies:
            if copy is not original_image:
                # Calculate transformation matrix
                transform = self.calculate_transform(
                    copy, original_x, original_y, original_width, original_height
                )

                # Create a <use> element for the clone
                clone = etree.SubElement(copy.getparent(), 'use')
                clone.set('xlink:href', '#' + original_image.get('id'))
                clone.set('transform', transform)  # Apply the calculated transform

                # Delete the original copy
                copy.getparent().remove(copy)

        # 5. Update the SVG Document
        self.document.write(self.options.input_file)

        if self.enable_logging:
            with open(self.log_file, 'a') as f:
                f.write('\n\n')

    def get_original_image(self, image):
        """
        If the image is a clone, returns the original image.
        Otherwise, returns the image itself if it's not a clone.
        """
        try:
            clone_of = image.get('sodipodi:clone-of')
            if clone_of:
                # If the image is a clone, find the original
                original = self.svg.getElementById(clone_of)
                return original
            else:
                # If the image is not a clone, return itself
                return image
        except Exception as e:
            self.print_to_log(f"Error getting original image: {e}")
            return None

    def calculate_transform(self, copy, original_x, original_y, original_width, original_height):
        """Calculates the transformation matrix for the copy relative to the original."""
        try:
            copy_x = float(copy.get('x'))
            copy_y = float(copy.get('y'))
            copy_width = float(copy.get('width'))
            copy_height = float(copy.get('height'))

            # Calculate scaling factors
            scale_x = copy_width / original_width
            scale_y = copy_height / original_height

            # Calculate translation (using the discovered relationship)
            translate_x = copy_x - (scale_x * original_x)
            translate_y = copy_y - (scale_y * original_y)  # Apply the same relation for y

            # Create the scaling matrix
            scale_matrix = np.array([
                [scale_x, 0, 0],
                [0, scale_y, 0],
                [0, 0, 1]
            ])

            # Combine transformations
            transform = np.identity(3)  # Start with an identity matrix

            copy_transform = copy.get('transform')
            if copy_transform:
                copy_transform_matrix = self.parse_transform(copy_transform)
                transform = transform @ copy_transform_matrix  # Apply copy transform first (if any)

            transform = transform @ scale_matrix  # Apply scaling

            # Set the translation values directly (corrected)
            transform[0, 2] = translate_x  # Set x translation
            transform[1, 2] = translate_y  # Set y translation

            # Extract the a-f values from the matrix (corrected)
            a, c, e, b, d, f = transform.flatten()[:6]

            # Construct the new transform string
            new_transform_str = f"matrix({a} {b} {c} {d} {e} {f})"
            self.print_to_log(f"{new_transform_str}")

            return new_transform_str

        except Exception as e:
            self.print_to_log(f"Error calculating transform: {e}")
            return ""

    def parse_transform(self, transform_str):
        """Parses a transform string into a numpy matrix."""
        try:
            # Use inkex.transforms.Transform to parse any transform
            transform = inkex.transforms.Transform(transform_str)
            return np.array([
                [transform.a, transform.c, transform.e],
                [transform.b, transform.d, transform.f],
                [0, 0, 1]
            ])
        except Exception as e:
            self.print_to_log(f"Error parsing transform: {e}")
            return np.identity(3)  # Return an identity matrix on error


    def print_to_log(self, message):
        """Prints a message to the log file if logging is enabled."""
        if self.enable_logging:
            with open(self.log_file, 'a') as f:
                f.write(message + '\n')

if __name__ == '__main__':
    ConvertCopiesToClones().run()
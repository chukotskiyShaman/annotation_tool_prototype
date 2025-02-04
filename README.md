# Description:
- Uploading images: Clicking on the "Load Images" button opens a dialog box to select a folder with images. The images are loaded and displayed on the canvas.

- Marking objects: The user can draw bounding boxes on the image by holding down the left mouse button and stretching the rectangle.

- Saving the markup: When you click on the "Save Annotations" button, the markup is saved to a text file with the same name as the image, but with the .txt extension.

- Image Navigation: The "Next Image" button allows you to navigate to the next image in the folder.

# Annotation file format:

## Each line in the annotation file corresponds to a single bounding box and contains the following values:

- class_id: ID of the object's class.

- x_center, y_center: Coordinates of the center of the bounding box relative to the width and height of the image (normalized values from 0 to 1).

- width, height: The width and height of the bounding box relative to the width and height of the image (normalized values from 0 to 1).

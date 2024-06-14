from PIL import Image, ImageEnhance, ImageColor, ImageFilter

def modify_image(image_path):
    # Open the image
    image = Image.open(image_path)

    # Display the original image
    image.show()

    # Display some basic information about the image
    print("Image format:", image.format)
    print("Image size:", image.size)

    # RESIZING of the Image
    size = (270, 180)
    new_image = image.resize(size)

    # IMAGE INFORMATION
    print("New image size:", new_image.size)
    print("Image path:", image_path)
    print("Image format:", new_image.format)
    print("Image format description:", new_image.format_description)

    # ROTATE an image
    image_rotate = new_image.rotate(60, expand=True, fillcolor=ImageColor.getcolor('black', 'RGB'))
    image_rotate.show()

    # FLIP an image
    image_horizontal = new_image.transpose(Image.FLIP_LEFT_RIGHT)
    image_vertical = new_image.transpose(Image.FLIP_TOP_BOTTOM)
    image_transpose = new_image.transpose(Image.TRANSPOSE)
    image_transverse = new_image.transpose(Image.TRANSVERSE)
    image_rotate_90 = new_image.transpose(Image.ROTATE_90)
    image_rotate_90.show()

    # using filters
    image_contour = new_image.filter(ImageFilter.CONTOUR)
    image_detail = new_image.filter(ImageFilter.DETAIL)
    image_edge = new_image.filter(ImageFilter.EDGE_ENHANCE)
    image_edge_more = new_image.filter(ImageFilter.EDGE_ENHANCE_MORE)
    image_find = new_image.filter(ImageFilter.FIND_EDGES)
    image_sharp = new_image.filter(ImageFilter.SHARPEN)

    # Rank filters
    image_min = new_image.filter(ImageFilter.MinFilter(size=5))
    image_median = new_image.filter(ImageFilter.MedianFilter(size=5))

    # Combine filters

    # Resize the image to 270x180 pixels
    size = (270, 180)
    new_image = new_image.resize(size)

    # Display the modified image
    new_image.show()

    return new_image

new_image = modify_image('cin.jpg')

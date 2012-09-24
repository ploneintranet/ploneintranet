# monkey Products.PlonePAS image scales
# until PLIP 12870 is merged

from Products.PlonePAS import utils


def monkey_scale_image(image_file, max_size=None, default_format=None):
    import pdb; pdb.set_trace()
    if not max_size:
        max_size = (225, 300)
    return utils._old_scale_image(image_file, max_size, default_format)

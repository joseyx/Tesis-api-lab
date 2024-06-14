from django.core.exceptions import ValidationError


def validate_image_file_extension(value):
    import os
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.jpg', '.png,', '.jpeg']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension. Must be: jpg, png or jpeg')

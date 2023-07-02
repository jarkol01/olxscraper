from django.core.exceptions import ValidationError

def validate_url_has_brackets(value):
    if '{}' not in value:
        raise ValidationError('URL must contain {} after price param.')
    
def validate_url_page(value):
    if 'page=' in value:
        raise ValidationError('Page param should not occur in URL. It will be added automaticly.')
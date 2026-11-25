def validation_error(errors):
    return {'success': False, 'message': 'Errors in data validation', 'validation-errors': errors}, 400

def error(message, status):
    return {'success': False, 'message': message}, status

def page_data(items, page, per_page, total, key, serializer):
    pages=(total+per_page-1)//per_page if per_page > 0 else 0
    return {'data':[serializer(item) for item in items], 'meta':{
        'page':page, 'per_page':per_page, 'total_pages':pages, key:total,
        'has_next':page < pages, 'has_prev':page > 1}}


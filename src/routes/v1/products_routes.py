from flask import Blueprint, jsonify, request
from src.models.products import Products
from src.models.categoris import Categories
from src.models.users import Role
from src.utils.auth import token_required, role_required
from src.utils.responses import validation_error, error, page_data
products_bp=Blueprint('products_v1',__name__,url_prefix='/api/v1')
def product_json(p): return {'id':p.id,'name':p.name,'description':p.description,'price':p.price,'stock':p.stock,'category_id':p.category_id,'active':p.active}

@products_bp.get('/products')
@token_required
@role_required(Role.ADMIN,Role.SELLER)
def get_products():
    page=max(request.args.get('page',1,type=int),1); per_page=max(request.args.get('per_page',3,type=int),1)
    items,total=Products.get_paginated(page,per_page)
    return jsonify(page_data(items,page,per_page,total,'total_products',product_json)),200

@products_bp.get('/products/<int:product_id>')
@token_required
@role_required(Role.ADMIN,Role.SELLER)
def get_product_by_id(product_id):
    p=Products.get_by_id(product_id)
    return (jsonify(product_json(p)),200) if p else (jsonify(error('Product not found',404)[0]),404)

@products_bp.post('/products')
@token_required
@role_required(Role.ADMIN)
def post_products():
    data=request.get_json(silent=True) or {}; errors={}
    name=data.get('name'); price=data.get('price'); stock=data.get('stock',0); category_id=data.get('category_id')
    if not name: errors['name']='name is required'
    elif Products.get_by_name(name): errors['name']='name must be unique'
    if price is None: errors['price']='price is required'
    else:
        try: price=float(price)
        except (TypeError,ValueError): errors['price']='price must be a number'
        else:
            if price<0: errors['price']='price must be a non-negative number'
    try: stock=float(stock)
    except (TypeError,ValueError): errors['stock']='stock must be a number'
    else:
        if stock<0: errors['stock']='stock must be a non-negative number'
    if category_id is None: errors['category_id']='category_id is required'
    elif not Categories.get_by_id(category_id): errors['category_id']='category_id does not exist'
    if errors: return validation_error(errors)
    p=Products(name,price,category_id,data.get('description'),stock); p.save()
    return jsonify(product_json(p)),201

@products_bp.put('/products/<int:product_id>')
@token_required
@role_required(Role.ADMIN)
def put_products(product_id):
    p=Products.get_by_id(product_id)
    if not p: return jsonify({'success':False,'message':'Product not found'}),404
    data=request.get_json(silent=True) or {}; errors={}; values={}
    for field in ('name','description','price','stock','category_id'):
        if field in data: values[field]=data[field]
    if values.get('name') is not None and values['name']!=p.name:
        other=Products.get_by_name(values['name'])
        if other and other.id!=p.id: errors['name']='name must be unique'
    for field in ('price','stock'):
        if field in values and values[field] is not None:
            try: values[field]=float(values[field])
            except (TypeError,ValueError): errors[field]=f'{field} must be a number'
            else:
                if values[field]<0: errors[field]=f'{field} must be a non-negative number'
    if values.get('category_id') is not None and not Categories.get_by_id(values['category_id']): errors['category_id']='category_id does not exist'
    if errors: return validation_error(errors)
    for field,value in values.items():
        if value is not None: setattr(p,field,value)
    p.update(); return jsonify(product_json(p)),200
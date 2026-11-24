from flask import Blueprint, jsonify, request
from src.models.Clients import Clients, DocumentType
from src.models.users import Role
from src.utils.auth import token_required, role_required
from src.utils.responses import validation_error, page_data
clients_bp=Blueprint('clients_v1',__name__,url_prefix='/api/v1')
def client_json(c): return {'id':c.id,'document_type':c.document_type,'document_number':c.document_number,'name':c.name,'email':c.email,'phone':c.phone,'address':c.address,'active':c.active}
def validate(data,current=None,partial=False):
    errors={}; vals={}
    fields=('document_type','document_number','name','email','phone','address')
    for f in fields:
        if not partial and f not in data: vals[f]=None
        elif f in data: vals[f]=data[f]
    for f in fields:
        v=vals.get(f)
        if partial and f not in vals: continue
        if f=='document_type':
            if not v: errors[f]='document_type is required'
            elif v not in [x.value for x in DocumentType]: errors[f]='document_type must be one of: CC, NIT, CE'
        elif f in ('document_number','name','phone','address'):
            if not v: errors[f]=f'{f} is required'
        elif f=='email':
            if not v: errors[f]='email is required'
            elif '@' not in v: errors[f]='email is not valid'
    if 'document_number' in vals and vals['document_number']:
        existing=Clients.get_by_document_number(vals['document_number'])
        if existing and (current is None or existing.id!=current.id): errors['document_number']='document_number must be unique'
    if 'active' in data and data['active'] is not None:
        if data['active'] not in (0,1): errors['active']='active must be 0 or 1'
        else: vals['active']=data['active']
    return vals,errors

@clients_bp.get('/clients')
@token_required
@role_required(Role.ADMIN,Role.SELLER)
def get_clients():
    page=max(request.args.get('page',1,type=int),1); per=max(request.args.get('per_page',3,type=int),1)
    items,total=Clients.get_paginated(page,per)
    return jsonify(page_data(items,page,per,total,'total_clients',client_json)),200

@clients_bp.get('/clients/<int:client_id>')
@token_required
@role_required(Role.ADMIN,Role.SELLER)
def get_client(client_id):
    c=Clients.get_by_id(client_id)
    return (jsonify(client_json(c)),200) if c else (jsonify({'success':False,'message':'Client not found'}),404)

@clients_bp.post('/clients')
@token_required
@role_required(Role.ADMIN)
def post_client():
    data=request.get_json(silent=True) or {}; vals,errors=validate(data)
    if errors: return validation_error(errors)
    c=Clients(vals['document_type'],vals['document_number'],vals['name'],vals['email'],vals['phone'],vals['address']); c.save()
    return jsonify(client_json(c)),201

@clients_bp.put('/clients/<int:client_id>')
@token_required
@role_required(Role.ADMIN)
def put_client(client_id):
    c=Clients.get_by_id(client_id)
    if not c: return jsonify({'success':False,'message':'Client not found'}),404
    vals,errors=validate(request.get_json(silent=True) or {},c,True)
    if errors: return validation_error(errors)
    for f,v in vals.items(): setattr(c,f,v)
    c.update(); return jsonify(client_json(c)),200

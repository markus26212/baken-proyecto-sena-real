from flask import Blueprint, jsonify, request, g
from src.models.invoices import Invoices
from src.models.Clients import Clients
from src.models.users import Users, Role
from src.models.invoice_details import InvoiceDetails
from src.models.products import Products
from src.utils.auth import token_required, role_required
from src.utils.responses import validation_error, page_data
invoices_bp=Blueprint('invoices_v1',__name__,url_prefix='/api/v1')
def invoice_json(i): return {'id':i.id,'client_id':i.client_id,'user_id':i.user_id,'date':i.date.isoformat(),'total':i.total,'completed':i.completed,'active':i.active}
def invoice_state_error(i):
    if i.active==0: return 'Invoice is cancelled and cannot be modified'
    if i.completed: return 'Invoice is completed and cannot be modified'
    return None
def validate_refs(data, partial=False):
    errors={}; vals={}
    for field,model,label in [('client_id',Clients,'client'),('user_id',Users,'user')]:
        if field not in data:
            if not partial: errors[field]=f'{field} is required'
            continue
        value=data[field]; vals[field]=value
        if value is None: errors[field]=f'{field} is required'; continue
        obj=model.get_by_id(value)
        if not obj: errors[field]=f'{field} does not exist'; continue
        if obj.active==0: errors[field]=f'{label} must be active'; continue
        if field=='user_id' and obj.role!=Role.SELLER.value: errors[field]='user must have SELLER role'
    return vals,errors

@invoices_bp.post('/invoices')
@token_required
@role_required(Role.ADMIN,Role.SELLER)
def post_invoice():
    data=request.get_json(silent=True) or {}; vals,errors=validate_refs(data)
    if g.current_user.role==Role.SELLER.value and vals.get('user_id') is not None and vals['user_id']!=g.current_user.id:
        errors['user_id']='SELLER can only create invoices with their own user_id'
    if errors: return validation_error(errors)
    i=Invoices(vals['client_id'],vals['user_id']); i.save(); return jsonify(invoice_json(i)),201

@invoices_bp.get('/invoices')
@token_required
@role_required(Role.ADMIN,Role.SELLER)
def get_invoices():
    page=max(request.args.get('page',1,type=int),1); per=max(request.args.get('per_page',3,type=int),1)
    items,total=Invoices.get_paginated(page,per)
    return jsonify(page_data(items,page,per,total,'total_invoices',invoice_json)),200

@invoices_bp.get('/invoices/<int:invoice_id>')
@token_required
@role_required(Role.ADMIN,Role.SELLER)
def get_invoice(invoice_id):
    i=Invoices.get_by_id(invoice_id)
    return (jsonify(invoice_json(i)),200) if i else (jsonify({'success':False,'message':'Invoice not found'}),404)

@invoices_bp.put('/invoices/<int:invoice_id>/complete')
@token_required
@role_required(Role.ADMIN,Role.SELLER)
def complete_invoice(invoice_id):
    i=Invoices.get_by_id(invoice_id)
    if not i: return jsonify({'success':False,'message':'Invoice not found'}),404
    if i.active==0: return jsonify({'success':False,'message':'Invoice is cancelled and cannot be modified'}),409
    if i.completed: return jsonify({'success':False,'message':'Invoice is already completed'}),409
    if not InvoiceDetails.get_by_invoice(invoice_id): return jsonify({'success':False,'message':'Invoice has no details and cannot be completed'}),409
    i.completed=True; i.update(); return jsonify(invoice_json(i)),200

@invoices_bp.put('/invoices/<int:invoice_id>')
@token_required
@role_required(Role.ADMIN)
def update_invoice(invoice_id):
    i=Invoices.get_by_id(invoice_id)
    if not i: return jsonify({'success':False,'message':'Invoice not found'}),404
    state=invoice_state_error(i)
    if state: return jsonify({'success':False,'message':state}),409
    vals,errors=validate_refs(request.get_json(silent=True) or {},True)
    if errors: return validation_error(errors)
    for f,v in vals.items(): setattr(i,f,v)
    i.update(); return jsonify(invoice_json(i)),200

@invoices_bp.delete('/invoices/<int:invoice_id>')
@token_required
@role_required(Role.ADMIN)
def cancel_invoice(invoice_id):
    i=Invoices.get_by_id(invoice_id)
    if not i: return jsonify({'success':False,'message':'Invoice not found'}),404
    if i.active==0: return jsonify({'success':False,'message':'Invoice is already cancelled'}),409
    for detail in InvoiceDetails.get_by_invoice(invoice_id):
        product=Products.get_by_id(detail.product_id)
        if product: product.stock += detail.quantity
    i.active=0; i.update(); return jsonify(invoice_json(i)),200

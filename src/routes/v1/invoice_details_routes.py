from flask import Blueprint, jsonify, request
from src.models.invoices import Invoices
from src.models.invoice_details import InvoiceDetails
from src.models.products import Products
from src.models.users import Role
from src.utils.auth import token_required, role_required
from src.utils.responses import validation_error
invoice_details_bp=Blueprint('invoice_details_v1',__name__,url_prefix='/api/v1')
def detail_json(d): return {'id':d.id,'invoice_id':d.invoice_id,'product_id':d.product_id,'quantity':d.quantity,'unit_price':d.unit_price,'subtotal':round(d.quantity*d.unit_price,2)}
def get_invoice_checked(invoice_id):
    i=Invoices.get_by_id(invoice_id)
    if not i: return None,({'success':False,'message':'Invoice not found'},404)
    if i.active==0: return None,({'success':False,'message':'Invoice is cancelled and cannot be modified'},409)
    if i.completed: return None,({'success':False,'message':'Invoice is completed and cannot be modified'},409)
    return i,None

@invoice_details_bp.post('/invoices/<int:invoice_id>/details')
@token_required
@role_required(Role.ADMIN,Role.SELLER)
def add_detail(invoice_id):
    invoice,error_response=get_invoice_checked(invoice_id)
    if error_response: return jsonify(error_response[0]),error_response[1]
    data=request.get_json(silent=True) or {}; errors={}; pid=data.get('product_id'); quantity=data.get('quantity')
    product=None
    if pid is None: errors['product_id']='product_id is required'
    else:
        product=Products.get_by_id(pid)
        if not product: errors['product_id']='product_id does not exist'
        elif product.active==0: errors['product_id']='product must be active'
    if quantity is None: errors['quantity']='quantity is required'
    else:
        try: quantity=float(quantity)
        except (TypeError,ValueError): errors['quantity']='quantity must be a number'
        else:
            if quantity<=0: errors['quantity']='quantity must be greater than 0'
    if product and 'quantity' not in errors and quantity>product.stock:
        errors['quantity']=f'not enough stock, available: {product.stock}'
    if errors: return validation_error(errors)
    detail=InvoiceDetails.get_by_invoice_and_product(invoice_id,pid); created=detail is None
    if created: detail=InvoiceDetails(invoice_id,pid,quantity,product.price)
    else: detail.quantity += quantity
    product.stock -= quantity; invoice.total=round(invoice.total+quantity*detail.unit_price,2)
    if created: detail.save()
    else: detail.update()
    return jsonify(detail_json(detail)),201 if created else 200

@invoice_details_bp.get('/invoices/<int:invoice_id>/details')
@token_required
@role_required(Role.ADMIN,Role.SELLER)
def get_details(invoice_id):
    invoice=Invoices.get_by_id(invoice_id)
    if not invoice: return jsonify({'success':False,'message':'Invoice not found'}),404
    return jsonify({'invoice_id':invoice.id,'total':invoice.total,'data':[detail_json(d) for d in InvoiceDetails.get_by_invoice(invoice_id)]}),200

@invoice_details_bp.put('/invoices/<int:invoice_id>/details/<int:detail_id>')
@token_required
@role_required(Role.ADMIN)
def update_detail(invoice_id,detail_id):
    invoice,error_response=get_invoice_checked(invoice_id)
    if error_response: return jsonify(error_response[0]),error_response[1]
    detail=InvoiceDetails.get_by_id(detail_id)
    if not detail or detail.invoice_id!=invoice_id: return jsonify({'success':False,'message':'Invoice detail not found'}),404
    data=request.get_json(silent=True) or {}; quantity=data.get('quantity'); errors={}
    if quantity is None: errors['quantity']='quantity is required'
    else:
        try: quantity=float(quantity)
        except (TypeError,ValueError): errors['quantity']='quantity must be a number'
        else:
            if quantity<=0: errors['quantity']='quantity must be greater than 0'
    product=Products.get_by_id(detail.product_id); difference=None
    if 'quantity' not in errors:
        difference=quantity-detail.quantity
        if difference>product.stock: errors['quantity']=f'not enough stock, available: {product.stock}'
    if errors: return validation_error(errors)
    product.stock-=difference; invoice.total=round(invoice.total+difference*detail.unit_price,2); detail.quantity=quantity
    detail.update(); return jsonify(detail_json(detail)),200

@invoice_details_bp.delete('/invoices/<int:invoice_id>/details/<int:detail_id>')
@token_required
@role_required(Role.ADMIN)
def delete_detail(invoice_id,detail_id):
    invoice,error_response=get_invoice_checked(invoice_id)
    if error_response: return jsonify(error_response[0]),error_response[1]
    detail=InvoiceDetails.get_by_id(detail_id)
    if not detail or detail.invoice_id!=invoice_id: return jsonify({'success':False,'message':'Invoice detail not found'}),404
    product=Products.get_by_id(detail.product_id); product.stock+=detail.quantity
    invoice.total=round(invoice.total-detail.quantity*detail.unit_price,2)
    detail.delete(); return jsonify({'success':True,'message':'Invoice detail deleted'}),200

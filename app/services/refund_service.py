from app.configs.database_configs import db
from app.models.refund_request import RefundRequest
from datetime import datetime

class RefundService:
    @staticmethod
    def create_refund_request(order_id,amount,reason):
        new_refund_request = RefundRequest(
            order_id=order_id,
            amount=amount,
            reason=reason,
            created_at=datetime.utcnow()
        )
        db.session.add(new_refund_request)
        db.session.commit()
        return new_refund_request
    
    @staticmethod
    def get_refund_request_by_id(refund_id):
        return RefundRequest.query.get(refund_id)
    
    @staticmethod
    def update_refund_request_status(refund_id, status):
        refund_request = RefundRequest.query.get(refund_id)
        refund_request.status = status
        db.session.commit()
        return refund_request
    
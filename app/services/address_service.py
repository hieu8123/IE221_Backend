from app.configs.database_configs import db
from app.models.address import Address
from datetime import datetime

class AddressService:
    @staticmethod
    def create_address(user_id, address_line, city, country="Vietnam", postal_code=None, note=None):
        new_address = Address(
            user_id=user_id,
            address_line=address_line,
            city=city,
            country=country,
            postal_code=postal_code,
            note=note,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(new_address)
        db.session.commit()
        return new_address

    @staticmethod
    def get_all_addresses():
        return Address.query.all()

    @staticmethod
    def get_user_addresses(user_id):
        return Address.query.filter_by(user_id=user_id).all()

    @staticmethod
    def get_address_by_id(address_id):
        return Address.query.get(address_id)

    @staticmethod
    def update_address(address_id, address_line=None, city=None, country=None, postal_code=None, note=None):
        address = Address.query.get(address_id)
        if address:
            if address_line is not None:
                address.address_line = address_line
            if city is not None:
                address.city = city
            if country is not None:
                address.country = country
            if postal_code is not None:
                address.postal_code = postal_code
            if note is not None:
                address.note = note
            address.updated_at = datetime.utcnow()
            db.session.commit()
            return address
        return None

    @staticmethod
    def delete_address(address_id):
        address = Address.query.get(address_id)
        if address:
            db.session.delete(address)
            db.session.commit()
            return True
        return False

from app.configs.database_configs import db
from app.models.order import Order, OrderDetail
from app.models.product import Product
from app.models.user import User
from app.models.brand import Brand
from app.models.category import Category
from sqlalchemy import func
from datetime import datetime, timedelta
from collections import defaultdict
from calendar import monthrange
from datetime import datetime

class StatisticsService:
    @staticmethod
    def get_over_view():
        total_orders = Order.query.count()
        total_users = User.query.count()
        total_products = Product.query.count()
        total_revenue = db.session.query(db.func.sum(Order.total)).scalar()
        return {
            'total_orders': total_orders,
            'total_users': total_users,
            'total_revenue': total_revenue,
            'total_products': total_products
        }
    
    @staticmethod
    def get_top_products_of_week(limit=10):
        # Lấy ngày đầu tiên và ngày cuối cùng của tuần hiện tại
        now = datetime.utcnow()
        start_of_week = now - timedelta(days=now.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        # Query dữ liệu
        results = (
            db.session.query(
                Product.id.label("product_id"),
                Product.name.label("product_name"),
                func.sum(OrderDetail.price * OrderDetail.quantity).label("total_revenue")
            )
            .join(OrderDetail, Product.id == OrderDetail.product_id)
            .join(Order, Order.id == OrderDetail.order_id)
            .filter(Order.created_at >= start_of_week, Order.created_at <= end_of_week)
            .filter(Order.status == "paid")  # Chỉ tính các đơn hàng đã thanh toán
            .group_by(Product.id, Product.name)
            .order_by(func.sum(OrderDetail.price * OrderDetail.quantity).desc())  # Sắp xếp theo doanh thu giảm dần
            .limit(limit)  # Giới hạn số lượng kết quả trả về
            .all()
        )

        # Trả về kết quả dưới dạng list dictionary
        return [{"product_id": row.product_id, "product_name": row.product_name, "total_revenue": row.total_revenue} for row in results]
    
    @staticmethod
    def get_top_products_of_month(limit=10):
        # Lấy ngày đầu tiên và ngày cuối cùng của tháng hiện tại
        now = datetime.utcnow()
        start_of_month = datetime(now.year, now.month, 1)
        next_month = start_of_month + timedelta(days=32)
        end_of_month = datetime(next_month.year, next_month.month, 1) - timedelta(seconds=1)

        # Query dữ liệu
        results = (
            db.session.query(
                Product.id.label("product_id"),
                Product.name.label("product_name"),
                func.sum(OrderDetail.price * OrderDetail.quantity).label("total_revenue")
            )
            .join(OrderDetail, Product.id == OrderDetail.product_id)
            .join(Order, Order.id == OrderDetail.order_id)
            .filter(Order.created_at >= start_of_month, Order.created_at <= end_of_month)
            .filter(Order.status == "paid")  # Chỉ tính các đơn hàng đã thanh toán
            .group_by(Product.id, Product.name)
            .order_by(func.sum(OrderDetail.price * OrderDetail.quantity).desc())  # Sắp xếp theo doanh thu giảm dần
            .limit(limit)  # Giới hạn số lượng kết quả trả về
            .all()
        )

        # Trả về kết quả dưới dạng list dictionary
        return [{"product_id": row.product_id, "product_name": row.product_name, "total_revenue": row.total_revenue} for row in results]
    
    @staticmethod
    def get_top_users_of_month(limit=10):
        # Lấy ngày đầu tiên và ngày cuối cùng của tháng hiện tại
        now = datetime.utcnow()
        start_of_month = datetime(now.year, now.month, 1)
        next_month = start_of_month + timedelta(days=32)
        end_of_month = datetime(next_month.year, next_month.month, 1) - timedelta(seconds=1)

        # Query dữ liệu
        results = (
            db.session.query(
                User.id.label("user_id"),
                User.fullname.label("user_name"),
                func.count(Order.id).label("total_orders")
            )
            .join(Order, User.id == Order.user_id)
            .filter(Order.created_at >= start_of_month, Order.created_at <= end_of_month)
            .filter(Order.status == "paid")  # Chỉ tính các đơn hàng đã thanh toán
            .group_by(User.id, User.fullname)
            .order_by(func.count(Order.id).desc())  # Sắp xếp theo số lượng đơn hàng giảm dần
            .limit(limit)  # Giới hạn số lượng kết quả trả về
            .all()
        )

        # Trả về kết quả dưới dạng list dictionary
        return [{"user_id": row.user_id, "user_name": row.user_name, "total_orders": row.total_orders} for row in results]

    @staticmethod
    def get_monthly_revenue(year=None):
        if not year:
            year = datetime.today().year
        if not isinstance(year, int):
            raise ValueError("Year must be an integer.")
        
        # Lấy doanh thu theo tháng từ CSDL
        results = (
            db.session.query(
                func.extract('month', Order.created_at).label('month'),
                func.sum(Order.total).label('total_revenue')
            )
            .filter(func.extract('year', Order.created_at) == year)
            .filter(Order.status == "paid")  # Chỉ tính đơn hoàn tất
            .group_by(func.extract('month', Order.created_at))
            .order_by(func.extract('month', Order.created_at))
            .all()
        )

        # Chuyển đổi kết quả từ truy vấn thành danh sách với tất cả các tháng
        monthly_revenue = {int(row.month): row.total_revenue for row in results}

        # Trả về danh sách đầy đủ các tháng trong năm, nếu không có doanh thu cho tháng đó thì gán doanh thu là 0
        return [{"month": month, "total_revenue": monthly_revenue.get(month, 0)} for month in range(1, 13)]

    @staticmethod
    def get_daily_revenue(year=None, month=None):
        if not year:
            year = datetime.today().year
        if not month:
            month = datetime.today().month
        if not isinstance(year, int) or not isinstance(month, int):
            raise ValueError("Year and month must be integers.")
        
        # Tính số ngày trong tháng
        _, last_day = monthrange(year, month)

        # Lấy doanh thu theo ngày từ CSDL
        results = (
            db.session.query(
                func.extract('day', Order.created_at).label('day'),
                func.sum(Order.total).label('total_revenue')
            )
            .filter(func.extract('year', Order.created_at) == year)
            .filter(func.extract('month', Order.created_at) == month)
            .filter(Order.status == "paid")  # Chỉ tính đơn hoàn tất
            .group_by(func.extract('day', Order.created_at))
            .order_by(func.extract('day', Order.created_at))
            .all()
        )

        # Chuyển đổi kết quả từ truy vấn thành danh sách với tất cả các ngày trong tháng
        daily_revenue = {int(row.day): row.total_revenue for row in results}

        # Trả về danh sách đầy đủ các ngày trong tháng, nếu không có doanh thu cho ngày đó thì gán doanh thu là 0
        return [{"day": day, "total_revenue": daily_revenue.get(day, 0)} for day in range(1, last_day + 1)]


    @staticmethod
    def get_revenue_by_brand(start_date=None, end_date=None):
        # Nếu không truyền ngày tháng, mặc định lấy doanh thu tháng trước
        if not start_date and not end_date:
            today = datetime.today()
            first_day_last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
            last_day_last_month = today.replace(day=1) - timedelta(days=1)
            start_date = first_day_last_month
            end_date = last_day_last_month
        else:
            # Kiểm tra định dạng ngày tháng
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
                end_date = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
            except ValueError:
                raise ValueError("Invalid date format. Please use 'YYYY-MM-DD'.")

        # Query dữ liệu doanh thu từ đơn hàng
        results = (
            db.session.query(
                Brand.id.label("brand_id"),
                Brand.name.label("brand_name"),
                func.sum(OrderDetail.price * OrderDetail.quantity).label("total_revenue")
            )
            .join(Product, Product.id == OrderDetail.product_id)
            .join(Brand, Brand.id == Product.brand_id)
            .join(Order, Order.id == OrderDetail.order_id)
            .filter(Order.created_at >= start_date, Order.created_at <= end_date)
            .group_by(Brand.id, Brand.name)
            .order_by(func.sum(OrderDetail.price * OrderDetail.quantity).desc())
            .all()
        )

        # Lấy danh sách tất cả các thương hiệu (brand)
        all_brands = db.session.query(Brand.id, Brand.name).all()

        # Tạo một dictionary để dễ dàng tra cứu doanh thu theo thương hiệu
        revenue_by_brand = {row.brand_id: row.total_revenue for row in results}

        # Chuẩn bị kết quả với doanh thu, nếu không có doanh thu cho thương hiệu thì gán 0
        revenue_data = []
        for brand in all_brands:
            brand_id, brand_name = brand
            revenue = revenue_by_brand.get(brand_id, 0)  # Nếu không có doanh thu thì là 0
            revenue_data.append({
                "brand_id": brand_id,
                "brand_name": brand_name,
                "total_revenue": revenue
            })

        return revenue_data
    
    @staticmethod
    def get_revenue_by_category(start_date=None, end_date=None):
            # Nếu không truyền ngày tháng, mặc định lấy doanh thu tháng trước
        if not start_date and not end_date:
            today = datetime.today()
            first_day_last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
            last_day_last_month = today.replace(day=1) - timedelta(days=1)
            start_date = first_day_last_month
            end_date = last_day_last_month
        else:
            # Kiểm tra định dạng ngày tháng
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
                end_date = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
            except ValueError:
                raise ValueError("Invalid date format. Please use 'YYYY-MM-DD'.")

        # Query dữ liệu doanh thu từ đơn hàng
        results = (
            db.session.query(
                Category.id.label("category_id"),
                Category.name.label("category__name"),
                func.date(Order.created_at).label("created_date"),
                func.sum(OrderDetail.price * OrderDetail.quantity).label("total_revenue")
            )
            .join(Product, Product.id == OrderDetail.product_id)
            .join(Category, Category.id == Product.category_id)
            .join(Order, Order.id == OrderDetail.order_id)
            .filter(Order.created_at >= start_date, Order.created_at <= end_date)
            .group_by(Category.id, Category.name)
            .order_by(func.sum(OrderDetail.price * OrderDetail.quantity).desc())
            .all()
        )


        # Lấy danh sách tất cả các thương hiệu (brand)
        all_categories = db.session.query(Category.id, Category.name).all()

        # Tạo một dictionary để dễ dàng tra cứu doanh thu theo thương hiệu
        revenue_by_category = defaultdict(list)
        for row in results:
            revenue_by_category[row.category_id].append({
                "category_id": row.category_id,
                "created_date": row.created_date,
                "total_revenue": row.total_revenue
            })

        print(revenue_by_category)
        print("All categories:", all_categories)

        # Chuẩn bị kết quả với doanh thu, nếu không có doanh thu cho thương hiệu thì gán 0
        revenue_data = []
        for category in all_categories:
            category_id, category_name = category
            daily_revenue = revenue_by_category.get(category_id, [])
            revenue_data.append({
                "category_id": category_id,
                "category_name": category_name,
                "daily_revenue": daily_revenue
            })

        return revenue_data
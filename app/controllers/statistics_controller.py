from flask import Blueprint, jsonify, request
from app.services.statistics_service import StatisticsService
from app.middlewares.auth import admin_required


# Tạo Blueprint cho module auth
statistics_blueprint = Blueprint('statistics', __name__)

@statistics_blueprint.route('/overview', methods=['GET'])
@admin_required
def get_overview():
    return jsonify(StatisticsService.get_over_view())

@statistics_blueprint.route('/top-products-of-week', methods=['GET'])
@admin_required
def get_top_products_of_week():
    limit = int(request.args.get('limit', 10))
    print(1)
    return jsonify(StatisticsService.get_top_products_of_week(limit=limit))

@statistics_blueprint.route('/top-products-of-month', methods=['GET'])
@admin_required
def get_top_products_of_month():
    limit = int(request.args.get('limit', 10))
    return jsonify(StatisticsService.get_top_products_of_month(limit=limit))

@statistics_blueprint.route('/revenue-by-brand', methods=['GET'])
@admin_required
def get_revenue_by_brand():
    start_date = request.args.get('start_date', None)
    end_date = request.args.get('end_date', None)
    return jsonify(StatisticsService.get_revenue_by_brand(start_date=start_date, end_date=end_date))

@statistics_blueprint.route('/revenue-by-category', methods=['GET'])
@admin_required
def get_revenue_by_category():
    start_date = request.args.get('start_date', None)
    end_date = request.args.get('end_date', None)
    return jsonify(StatisticsService.get_revenue_by_category(start_date=start_date, end_date=end_date))

@statistics_blueprint.route('/monthly-revenue', methods=['GET'])
@admin_required
def get_monthly_revenue():
    year_str = request.args.get('year', None)
    year = int(year_str) if year_str is not None else None
    return jsonify(StatisticsService.get_monthly_revenue(year=year))

@statistics_blueprint.route('/daily-revenue', methods=['GET'])
@admin_required
def get_daily_revenue():
    year_str = request.args.get('year', None)
    month_str = request.args.get('month', None)
    
    year = int(year_str) if year_str is not None else None
    month = int(month_str) if month_str is not None else None
    return jsonify(StatisticsService.get_daily_revenue(year=year, month=month))





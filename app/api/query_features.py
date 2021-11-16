"""This module stores query features: pagination, filtering, sorting (API)."""
import re
from flask_sqlalchemy import BaseQuery, DefaultMeta
from flask import request, url_for, current_app
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.sql.expression import BinaryExpression
from sqlalchemy.types import DateTime
from datetime import datetime

SIGNS_REGEX = re.compile(r'(.*)\[(gte|gt|lte|lt)\]')


def get_pagination(sql_query, api_func_name):
    """Paginate SQL query results.

    :param sql_query: The SQL Query
    :type sql_query: BaseQuery
    :param api_func_name: Name of api function
    :type api_func_name: str
    :return: Results of SQL query with pagination and information about pagination
    :rtype: tuple[list, dict]
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', current_app.config.get('POSTS_PER_PAGE', 10), type=int)
    request_params = {key: value for key, value in request.args.items() if key != 'page'}
    paginate_object = sql_query.paginate(page=page, per_page=per_page, error_out=False)
    pagination = {
        'number_of_all_pages': paginate_object.pages,
        'number_of_all_records': paginate_object.total,
        'current_page_url': url_for(api_func_name, page=page, **request_params)
    }

    if paginate_object.has_next:
        pagination['next_page'] = url_for(api_func_name, page=paginate_object.next_num, **request_params)

    if paginate_object.has_prev:
        pagination['previous_page'] = url_for(api_func_name, page=paginate_object.prev_num, **request_params)

    return paginate_object.items, pagination


def get_args(json, params):
    """Filter json dict by params.

    :param json: json
    :type json: dict
    :param params: Parameters separated by a comma which will be excluded in a dict
    :type params: str
    :return: json without keys (parameters)
    :rtype: dict
    """
    params_list = params.split(',')
    json_dict = json
    for param in params_list:
        json_dict = {key: json_dict[key] for key in json_dict.keys() - {param}}
    return json_dict


def sort_by(sql_query, model):
    """Sort SQL query by params.

    :param sql_query: SQL query
    :type sql_query: BaseQuery
    :param model: Name of model
    :type model: DefaultMeta
    :return: Sorted SQL query
    :rtype: BaseQuery
    """
    sorting_by = request.args.get('sort', None)
    if sorting_by:
        sorting_values = sorting_by.split(',')
        desc = False
        for value in sorting_values:
            if value.startswith('-'):
                value = value[1:]
                desc = True
            attribute = getattr(model, value, None)
            if attribute is not None:
                sql_query = sql_query.order_by(attribute.desc()) if desc else sql_query.order_by(attribute.asc())

    return sql_query


def _get_filter(column, sign, value):
    """Map filter.

    :param column: SQL query
    :type column: InstrumentedAttribute
    :param sign: Name of model
    :type sign: str
    :param value: Name of model
    :type value: str
    :return: Mapped expression
    :rtype: BinaryExpression
    """

    if isinstance(column.type, DateTime):
        value = datetime.strptime(value, '%Y-%m-%d')
    operator_mapping = {
        "lte": column <= value,
        "lt": column < value,
        "gte": column >= value,
        "gt": column > value,
        "=": column == value
    }

    return operator_mapping[sign]


def apply_filter(sql_query, model):
    """Filter SQL query.

    :param sql_query: SQL query
    :type sql_query: BaseQuery
    :param model: Name of model
    :type model: DefaultMeta
    :return: Filtered SQL query
    :rtype: BaseQuery
    """
    for filter_by, value in request.args.items():
        if filter_by not in {'sort', 'page', 'per_page'}:
            sign = "="
            match = SIGNS_REGEX.match(filter_by)
            if match:
                filter_by, sign = match.groups()
            attribute_name = getattr(model, filter_by, None)
            if attribute_name:
                filtered = _get_filter(attribute_name, sign, value)
                sql_query = sql_query.filter(filtered)

    return sql_query

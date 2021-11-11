"""This module stores query features: pagination, filtering (API)."""
from flask_sqlalchemy import BaseQuery
from flask import request, url_for, current_app


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
        json_dict = {key: json_dict[key] for key in json_dict.keys() - set([param])}
    return json_dict

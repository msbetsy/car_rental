"""This module stores tests for API - cars module."""
import unittest
import math
from datetime import datetime
from app import create_app, db
from app.models import Role, Car, Rental
from tests.api_functions import token, create_user, create_admin, create_moderator, check_missing_token_value, \
    check_missing_token_wrong_value, check_missing_token, request_with_features, check_content_type, check_permissions

cars_data = [{"name": "Car name", "price": 200, "year": 2000, "model": "Car model", "image": "car_image.jpg"},
             {"name": "Car name2", "price": 123, "year": 2020, "model": "Car model", "image": "car_image.jpg"}]

cars_data_invalid = [
    ({"name": 123, "price": 200, "year": 2000, "model": "Car model"}, "name"),
    ({"price": 200, "year": 2000, "model": "Car model"}, "name", "edit"),
    ({"name": "Car name", "price": "200", "year": 2000, "model": "Car model"}, "price"),
    ({"name": "Car name", "year": 2000, "model": "Car model"}, "price", "edit"),
    ({"name": "Car name", "price": 200, "year": datetime.today().year + 1, "model": "Car model"}, "year"),
    ({"name": "Car name", "price": 200, "model": "Car model"}, "year", "edit"),
    ({"name": "Car name", "price": 200, "year": 2000, "model": 123}, "model"),
    ({"name": "Car name", "price": 200, "year": 2000}, "model", "edit"),
    ({"name": "Car name", "price": 200, "year": 2000, "model": "car model"}, "car_to_edit_id", "edit"),
    ({"name": "Car name", "price": 200, "year": 2000, "model": "Car model", "image": "wrong.pdf"}, "image"),
    ({"name": "Car name", "price": 200, "year": 2000, "model": "Car model", "image": "wrong.pdf"}, "image", "edit")
]


def make_cars():
    """Function that adds cars to db."""
    for item in cars_data:
        car = Car(**item)
        db.session.add(car)
        db.session.commit()


def change_dict_to_json(dict_name):
    """Change dict to json format.

    :param dict_name: Name of the dictionary.
    :type dict_name: dict
    :return: Changed dict format
    :rtype: dict
    """
    changed_dict = dict_name.copy()
    if "car_to_edit_id" not in changed_dict:
        if "image" in changed_dict:
            changed_dict["image"] = "".join(('/static/img/', changed_dict["image"]))
        else:
            changed_dict["image"] = "".join(('/static/img/', "no_img.jpg"))

        changed_dict["price"] = float(changed_dict["price"])
        try:
            changed_dict["id"] = Car.query.filter_by(name=dict_name["name"], price=dict_name["price"],
                                                     year=dict_name["year"],
                                                     model=dict_name["model"], image=dict_name["image"]).first().id
        except KeyError:
            last_id = Car.query.all()[-1].id
            changed_dict["id"] = last_id
    else:
        if "image" in changed_dict:
            changed_dict["image"] = "".join(('/static/img/', changed_dict["image"]))
        else:
            changed_dict["image"] = "".join(('/static/img/', "no_img.jpg"))
        if "price" in changed_dict:
            changed_dict["price"] = float(changed_dict["price"])
        changed_dict["id"] = changed_dict["car_to_edit_id"]
        del changed_dict["car_to_edit_id"]
    all_car_rentals = Rental.query.filter_by(cars_id=changed_dict["id"]).all()
    changed_dict["rentals_number"] = len(all_car_rentals)
    changed_dict["rentals_url"] = []
    for item in all_car_rentals:
        changed_dict["rentals_url"].append(
            f"/api/v1/rentals/car{item.cars_id}/user{item.users_id}/from{item.from_date.strftime('%Y%m%d%H%M')}/")
    return changed_dict


def remove_params_from_dict(dict_name, params=None):
    """Change dict to format matching the response.

    :param dict_name: Name of the dictionary.
    :type dict_name: dict
    :param params: Parameters not displayed in response.
    :type params: list
    :return: Changed dict
    :rtype: dict
    """
    changed_dict = dict_name.copy()
    if params is not None:
        for param in params:
            del changed_dict[param]
    return changed_dict


class CarsTestCase(unittest.TestCase):
    """Test cars module."""

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client()
        self.user = create_user()
        self.token = token(self.client, self.user)
        self.user_admin = create_admin()
        self.token_admin = token(self.client, self.user_admin)
        self.user_moderator = create_moderator()
        self.token_moderator = token(self.client, self.user_moderator)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def get_api_headers(self):
        """Method that returns response headers.

         :return: Headers
         :rtype: dict
         """

        return {
            'Authorization': f'Bearer {self.token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def get_api_headers_moderator(self):
        """Method that returns response headers for moderator.

         :return: Headers
         :rtype: dict
         """

        return {
            'Authorization': f'Bearer {self.token_moderator}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def get_api_headers_admin(self):
        """Method that returns response headers for admin.

         :return: Headers
         :rtype: dict
         """

        return {
            'Authorization': f'Bearer {self.token_admin}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    # Test get_car
    def test_get_car(self):
        """Test api for get_car with filtering variables, correct data."""
        car_id = 1
        # Headers
        api_headers = self.get_api_headers()
        del api_headers["Authorization"]

        # Test request without features, no cars in db
        # Request
        response = self.client.get(f'/api/v1/cars/{car_id}/', headers=api_headers)
        response_data = response.get_json()
        # Tests
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertFalse(response_data['success'])
        self.assertEqual(f'Car with id {car_id} not found', response_data['error'])

        # Add cars to db
        make_cars()
        # Change dict to json format
        cars = []
        for car in cars_data:
            car = car.copy()
            cars.append(change_dict_to_json(car))

        # Test request without features
        # Request
        response = self.client.get(f'/api/v1/cars/{car_id}/', headers=api_headers)
        response_data = response.get_json()
        # Expected result
        filtered_cars = [item for item in cars if item['id'] == car_id]
        expected_result = {'success': True,
                           'data': filtered_cars[0]}
        # Tests
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertDictEqual(expected_result, response_data)

        # Test request with feature: params
        request_features = {'params': 'image,model'}
        response = self.client.get(request_with_features(url=f'/api/v1/cars/{car_id}/', **request_features),
                                   headers=api_headers)
        response_data = response.get_json()
        # Expected results
        expected_result = {'success': True,
                           'data': {
                               **remove_params_from_dict(filtered_cars[0], ["image", "model"])
                           }}
        # Tests
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertDictEqual(expected_result, response_data)

    def test_get_car_invalid_data(self):
        """Test api for get_car."""
        # Headers
        api_headers = self.get_api_headers()
        del api_headers["Authorization"]
        # Test request without features
        response = self.client.get('/api/v1/cars/car_id/', headers=api_headers)
        response_data = response.get_json()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertFalse(response_data['success'])
        self.assertIn(response_data['error'], 'not found')

    # Test get_all_cars
    def test_get_all_cars(self):
        """Test api for get_all_cars with pagination, sorting, filtering records, correct data."""
        # Headers
        api_headers = self.get_api_headers()
        del api_headers["Authorization"]

        # No cars in db
        # Request
        response = self.client.get('/api/v1/cars/', headers=api_headers)
        response_data = response.get_json()
        # Expected result
        expected_result = {'success': True,
                           'number_of_records': len(Car.query.all()),
                           'data': []
                           }
        # Tests
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertDictEqual(expected_result, response_data)

        # Add cars to db
        make_cars()
        # Add car rental
        rental = Rental(cars_id=1, users_id=1, from_date=datetime(2020, 5, 27), to_date=datetime(2020, 5, 28),
                        available_from=datetime(2020, 5, 28, 1, 0, 0))
        db.session.add(rental)
        db.session.commit()
        # Change dict to json format
        cars = []
        for car in cars_data:
            car = car.copy()
            cars.append(change_dict_to_json(car))

        # Test request without features
        # Request
        response = self.client.get('/api/v1/cars/', headers=api_headers)
        response_data = response.get_json()
        # Expected result
        expected_result = {'success': True,
                           'number_of_records': len(Car.query.all()),
                           'data': cars
                           }
        # Tests
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertDictEqual(expected_result, response_data)

        # Test request with features: sort_by, params
        # Request
        request_features = {'sort_by': '-id',
                            'params': 'image,model'}
        response = self.client.get(request_with_features(url='/api/v1/cars/', **request_features), headers=api_headers)
        response_data = response.get_json()
        # Expected result
        sorted_cars = sorted(cars, key=lambda car_item: car_item['id'], reverse=True)
        sorted_cars_params = []
        for item in sorted_cars:
            sorted_cars_params.append(remove_params_from_dict(item, ["image", "model"]))
        expected_result = {'success': True,
                           'number_of_records': len(Car.query.all()),
                           'data': sorted_cars_params}
        # Tests
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertDictEqual(expected_result, response_data)

        # Test request with features: apply_filter, apply_args_filter, pagination
        # Request
        request_features = {'sort_by': '-id',
                            'per_page': '6',
                            'filters': 'price[gte]=200',
                            'filer_values': 'rentals_number=1'}
        response = self.client.get(request_with_features(url='/api/v1/cars/', **request_features), headers=api_headers)
        response_data = response.get_json()
        # Expected result
        filtered_cars_price = [item for item in cars if item['price'] >= 200]
        filtered_cars = [item for item in filtered_cars_price if item['rentals_number'] == 1]
        filtered_cars_sorted = sorted(filtered_cars, key=lambda car_item: car_item['id'], reverse=True)
        expected_result = {'success': True,
                           'number_of_records': len(filtered_cars_sorted),
                           'data': filtered_cars_sorted[:6],
                           'pagination': {
                               'current_page_url':
                                   '/api/v1/cars/?page=1&sort=-id&per_page=6&price%5Bgte%5D=200&rentals_number=1',
                               'number_of_all_pages': math.ceil(len(filtered_cars_sorted) / 6),
                               'number_of_all_records': len(filtered_cars_sorted)}
                           }
        # Tests
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertDictEqual(expected_result, response_data)

    # Test add_car
    def test_add_car(self):
        """Test api for add_car, correct data."""
        car_dict = {"name": "Car name", "price": 200, "year": 2000, "model": "Car model"}
        # Moderator
        # Request
        response = self.client.post('/api/v1/cars/', json={**car_dict}, headers=self.get_api_headers_moderator())
        response_data = response.get_json()
        # Expected result
        expected_result = {'success': True,
                           'data': {**change_dict_to_json(car_dict)}
                           }
        # Tests
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertDictEqual(expected_result, response_data)

        # Admin
        # Request
        response = self.client.post('/api/v1/cars/', json={**car_dict}, headers=self.get_api_headers_admin())
        response_data = response.get_json()
        # Expected result
        expected_result = {'success': True,
                           'data': {**change_dict_to_json(car_dict)}
                           }
        # Tests
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertDictEqual(expected_result, response_data)

    def test_add_car_invalid_data(self):
        """Test api for add_car."""
        for car in cars_data_invalid:
            if len(car) == 2:
                response = self.client.post('/api/v1/cars/', json=car[0], headers=self.get_api_headers_moderator())
                response_data = response.get_json()
                self.assertEqual(response.status_code, 400)
                self.assertFalse(response_data['success'])
                self.assertEqual(response_data['error_value_key'], car[1])

    # Test edit_car
    def test_edit_car(self):
        """Test api for edit_car, correct data."""
        car_dict = {"name": "Car name new", "price": 123987, "year": 2002, "model": "Car model new"}
        # Add cars to db
        make_cars()
        # Request
        response = self.client.put('/api/v1/cars/', json={**car_dict, "car_to_edit_id": 1},
                                   headers=self.get_api_headers_moderator())
        response_data = response.get_json()
        # Expected result
        car_dict["car_to_edit_id"] = 1
        expected_result = {'success': True,
                           'data': {**change_dict_to_json(car_dict)}
                           }
        # Tests
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertDictEqual(expected_result, response_data)

    def test_edit_car_invalid_data(self):
        """Test api for edit_car, invalid data."""
        # Add cars to db
        make_cars()

        # Invalid data
        for car in cars_data_invalid:
            if len(car) == 3:
                if car[1] != "car_to_edit_id":
                    # Request
                    response = self.client.put('/api/v1/cars/', json={**car[0], "car_to_edit_id": 1},
                                               headers=self.get_api_headers_moderator())
                    response_data = response.get_json()
                    # Tests
                    self.assertEqual(response.status_code, 400)
                    self.assertFalse(response_data['success'])
                    self.assertEqual(response_data['error_value_key'], car[1])

                else:
                    # Request
                    response = self.client.put('/api/v1/cars/', json={}, headers=self.get_api_headers_moderator())
                    response_data = response.get_json()
                    # Tests
                    self.assertEqual(response.status_code, 400)
                    self.assertFalse(response_data['success'])
                    self.assertEqual(response_data['error'], 'bad request')
                    self.assertEqual(response_data['message'], 'No car_to_edit_id')

    # Testing methods connected with values of request (content-type, tokens)
    def test_invalid_content_type(self):
        """Check if content type is 'application/json'"""
        api_headers = self.get_api_headers_moderator()
        del api_headers['Content-Type']

        # Check add_car
        response = self.client.post('/api/v1/cars/',
                                    data={"name": "Car name", "price": 200, "year": 2000, "model": "Car model"},
                                    headers=api_headers)
        check_content_type(response, self.assertEqual, self.assertFalse)

        # Check edit_car
        response = self.client.put('/api/v1/cars/', data={"name": "Car name"}, headers=api_headers)
        check_content_type(response, self.assertEqual, self.assertFalse)

    def test_missing_token_value(self):
        """Test if token has no value."""
        api_headers = self.get_api_headers_moderator()
        api_headers['Authorization'] = 'Bearer'

        # Check add_car
        response = self.client.post('/api/v1/cars/',
                                    json={"name": "Car name", "price": 200, "year": 2000, "model": "Car model"},
                                    headers=api_headers)
        check_missing_token_value(response, self.assertEqual, self.assertFalse, self.assertNotIn)

        # Check edit_car
        response = self.client.put('/api/v1/cars/', json={"name": "Car name"}, headers=api_headers)
        check_missing_token_value(response, self.assertEqual, self.assertFalse, self.assertNotIn)

    def test_missing_token_wrong_value(self):
        """Check if token has wrong value"""
        api_headers = self.get_api_headers_moderator()
        api_headers['Authorization'] = 'Bearer token'

        # Check add_car
        response = self.client.post('/api/v1/cars/',
                                    json={"name": "Car name", "price": 200, "year": 2000, "model": "Car model"},
                                    headers=api_headers)
        check_missing_token_wrong_value(response, self.assertEqual, self.assertFalse, self.assertNotIn)

        # Check edit_car
        response = self.client.put('/api/v1/cars/', json={"name": "Car name"}, headers=api_headers)
        check_missing_token_wrong_value(response, self.assertEqual, self.assertFalse, self.assertNotIn)

    def test_missing_token(self):
        """Check if token exists"""
        api_headers = self.get_api_headers()
        del api_headers['Authorization']

        # Check add_car
        response = self.client.post('/api/v1/cars/',
                                    json={"name": "Car name", "price": 200, "year": 2000, "model": "Car model"},
                                    headers=api_headers)
        check_missing_token(response, self.assertEqual, self.assertFalse, self.assertNotIn)

        # Check edit_car
        response = self.client.put('/api/v1/cars/', json={"name": "Car name"}, headers=api_headers)
        check_missing_token(response, self.assertEqual, self.assertFalse, self.assertNotIn)

    # Test permissions
    def test_insufficient_permissions(self):
        """Test permissions."""
        car_dict = {"name": "Car name", "price": 200, "year": 2000, "model": "Car model"}

        # Check permissions for add_car
        response = self.client.post('/api/v1/cars/', json={**car_dict}, headers=self.get_api_headers())
        check_permissions(response, self.assertEqual, self.assertFalse)

        # Check permissions for edit_car
        response = self.client.put('/api/v1/cars/', json={**car_dict}, headers=self.get_api_headers())
        check_permissions(response, self.assertEqual, self.assertFalse)

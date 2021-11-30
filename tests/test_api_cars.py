"""This module stores tests for API - cars module."""
import unittest
from datetime import datetime
from app import create_app, db
from app.models import Role, Car, Rental
from tests.api_functions import token, create_user, create_admin, create_moderator, check_missing_token_value, \
    check_missing_token_wrong_value, check_missing_token, request_with_features, check_content_type, check_permissions


def change_dict_to_json(dict_name, params=None):
    """Change dict to json format matching the response.

    :param dict_name: Name of the dictionary.
    :type dict_name: dict
    :param params: Parameters not displayed in response.
    :type params: list
    :return: Changed dict format
    :rtype: dict
    """
    changed_dict = dict_name.copy()
    if "image" in changed_dict:
        changed_dict["image"] = "".join(('/static/img/', changed_dict["image"]))
    else:
        changed_dict["image"] = "".join(('/static/img/', "no_img.jpg"))

    changed_dict["price"] = float(changed_dict["price"])
    if params is not None:
        for param in params:
            del changed_dict[param]
    return changed_dict


def make_car():
    """Function that contains possible car data - all cases are wrong.

     :return: car
     :rtype: list
     """
    car_data = [
        ({"name": 123, "price": 200, "year": 2000, "model": "Car model"}, "name"),
        ({"name": "Car name", "price": "200", "year": 2000, "model": "Car model"}, "price"),
        ({"name": "Car name", "price": 200, "year": datetime.today().year + 1, "model": "Car model"}, "year"),
        ({"name": "Car name", "price": 200, "year": 2000, "model": 123}, "model"),
        ({"name": "Car name", "price": 200, "year": 2000, "model": "Car model", "image": "wrong.pdf"}, "image")
    ]
    return car_data


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

    def test_get_car(self):
        """Test api for get_car with filtering variables, correct data."""

        car_dict = {"name": "Car name", "price": 123, "year": 2000, "model": "Car model", "image": "car_image.jpg"}
        car = Car(**car_dict)
        db.session.add(car)
        db.session.commit()
        api_headers = self.get_api_headers()
        del api_headers["Authorization"]

        # Test request without features
        response = self.client.get('/api/v1/cars/1/', headers=api_headers)
        response_data = response.get_json()
        expected_result = {'success': True,
                           'data': {
                               'id': 1,
                               'rentals_number': 0,
                               'rentals_url': [],
                               **change_dict_to_json(car_dict)
                           }}
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertDictEqual(expected_result, response_data)

        # Test request with feature: params
        response = self.client.get(request_with_features(url='/api/v1/cars/1/', params="image,model"),
                                   headers=api_headers)
        response_data = response.get_json()
        expected_result = {'success': True,
                           'data': {
                               'id': 1,
                               'rentals_number': 0,
                               'rentals_url': [],
                               **change_dict_to_json(car_dict, params=["image", "model"])
                           }}
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertDictEqual(expected_result, response_data)

    def test_get_car_invalid_data(self):
        """Test api for get_car."""

        api_headers = self.get_api_headers()
        del api_headers["Authorization"]
        # Test request without features
        response = self.client.get('/api/v1/cars/1/', headers=api_headers)
        response_data = response.get_json()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertFalse(response_data['success'])
        self.assertIn("1", response_data['error'])

    def test_get_all_cars(self):
        """Test api for get_all_cars with pagination, sorting, filtering records, correct data."""

        car_first_dict = {"name": "Car name", "price": 200, "year": 2000, "model": "Car model",
                          "image": "car_image.jpg"}
        car_first = Car(**car_first_dict)
        car_second_dict = {"name": "Car name2", "price": 123, "year": 2020, "model": "Car model",
                           "image": "car_image.jpg"}
        car_second = Car(**car_second_dict)
        db.session.add_all([car_first, car_second])
        db.session.commit()
        api_headers = self.get_api_headers()
        del api_headers["Authorization"]
        # Add car rental
        rental = Rental(cars_id=1, users_id=1, from_date=datetime(2020, 5, 27), to_date=datetime(2020, 5, 28),
                        available_from=datetime(2020, 5, 28, 1, 0, 0))
        db.session.add(rental)
        db.session.commit()

        # Test request without features
        response = self.client.get('/api/v1/cars/', headers=api_headers)
        response_data = response.get_json()
        expected_result = {'success': True,
                           'number_of_records': len(Car.query.all()),
                           'data': [{
                               'id': 1,
                               'rentals_number': 1,
                               'rentals_url': ['/api/v1/rentals/car1/user1/from202005270000/'],
                               **change_dict_to_json(car_first_dict)},
                               {'id': 2,
                                'rentals_number': 0,
                                'rentals_url': [],
                                **change_dict_to_json(car_second_dict)}
                           ]}
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertDictEqual(expected_result, response_data)

        # Test request with features: sort_by, params
        response = self.client.get(
            request_with_features(url='/api/v1/cars/', sort_by="-id", params="image,model"),
            headers=api_headers)
        response_data = response.get_json()
        expected_result = {'success': True,
                           'number_of_records': len(Car.query.all()),
                           'data': [
                               {'id': 2,
                                'rentals_number': 0,
                                'rentals_url': [],
                                **change_dict_to_json(car_second_dict, ["image", "model"])
                                },
                               {'id': 1,
                                'rentals_number': 1,
                                'rentals_url': ['/api/v1/rentals/car1/user1/from202005270000/'],
                                **change_dict_to_json(car_first_dict, ["image", "model"])
                                }
                           ]}

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertDictEqual(expected_result, response_data)

        # Test request with features: apply_filter, apply_args_filter, pagination
        response = self.client.get(
            request_with_features(url='/api/v1/cars/', sort_by="-id", per_page="6", filters="price[gte]=200",
                                  filer_values="rentals_number=1"), headers=api_headers)

        response_data = response.get_json()
        expected_result = {'success': True,
                           'number_of_records': 1,
                           'data': [
                               {'id': 1,
                                'rentals_number': 1,
                                'rentals_url': ['/api/v1/rentals/car1/user1/from202005270000/'],
                                **change_dict_to_json(car_first_dict),
                                }],
                           'pagination': {
                               'current_page_url':
                                   '/api/v1/cars/?page=1&sort=-id&per_page=6&price%5Bgte%5D=200&rentals_number=1',
                               'number_of_all_pages': 1,
                               'number_of_all_records': 1}
                           }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertDictEqual(expected_result, response_data)

    def test_add_car(self):
        """Test api for add_car, correct data."""
        car_dict = {"name": "Car name", "price": 200, "year": 2000, "model": "Car model"}
        # Moderator
        response = self.client.post('/api/v1/cars/', json={**car_dict}, headers=self.get_api_headers_moderator())
        response_data = response.get_json()
        expected_result = {'success': True,
                           'data':
                               {'id': 1,
                                'rentals_number': 0,
                                'rentals_url': [],
                                'image': 'no_img.jpg',
                                **change_dict_to_json(car_dict)
                                }
                           }
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertDictEqual(expected_result, response_data)

        # Admin
        response = self.client.post('/api/v1/cars/', json={**car_dict}, headers=self.get_api_headers_admin())
        response_data = response.get_json()
        expected_result = {'success': True,
                           'data':
                               {'id': 2,
                                'rentals_number': 0,
                                'rentals_url': [],
                                'image': 'no_img.jpg',
                                **change_dict_to_json(car_dict)
                                }
                           }
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertDictEqual(expected_result, response_data)

    def test_add_car_invalid_data(self):
        """Test api for add_car."""

        for car in make_car():
            response = self.client.post('/api/v1/cars/', json=car[0], headers=self.get_api_headers_moderator())
            response_data = response.get_json()
            self.assertEqual(response.status_code, 400)
            self.assertFalse(response_data['success'])
            self.assertEqual(response_data['error_value_key'], car[1])

    def test_edit_car(self):
        """Test api for edit_car, correct data."""
        car_dict = {"name": "Car name", "price": 123, "year": 2000, "model": "Car model", "image": "car_image.jpg"}
        car = Car(**car_dict)
        db.session.add(car)
        db.session.commit()
        new_year = 1990
        car_dict["year"] = new_year
        response = self.client.put('/api/v1/cars/', json={"year": new_year, "car_to_edit_id": 1},
                                   headers=self.get_api_headers_moderator())
        response_data = response.get_json()
        expected_result = {'success': True,
                           'data':
                               {'id': 1,
                                'rentals_number': 0,
                                'rentals_url': [],
                                **change_dict_to_json(car_dict)
                                }
                           }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertDictEqual(expected_result, response_data)

    def test_edit_car_invalid_data(self):
        """Test api for edit_car, invalid data."""
        car_dict = {"name": "Car name", "price": 123, "year": 2000, "model": "Car model", "image": "car_image.jpg"}
        car = Car(**car_dict)
        db.session.add(car)
        db.session.commit()

        # Invalid data
        for car in make_car():
            response = self.client.put('/api/v1/cars/', json={**car[0], "car_to_edit_id": 1},
                                       headers=self.get_api_headers_moderator())
            response_data = response.get_json()
            self.assertEqual(response.status_code, 400)
            self.assertFalse(response_data['success'])
            self.assertEqual(response_data['error_value_key'], car[1])

        # Wrong request
        response = self.client.put('/api/v1/cars/', json={**car[0]}, headers=self.get_api_headers_moderator())
        response_data = response.get_json()
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

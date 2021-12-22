"""This module stores tests for API - rentals module."""
import unittest
from datetime import datetime, timedelta
import random
from app import create_app, db
from app.models import Role, Rental, Car, User
from tests.api_functions import token, create_user, create_admin, create_moderator, check_missing_token_value, \
    check_missing_token_wrong_value, check_missing_token, request_with_features, check_content_type, check_permissions


def change_dict_to_json(dict_name):
    """Change dict to json format matching the response.

    :param dict_name: Name of the dictionary.
    :type dict_name: dict
    :return: Changed dict format
    :rtype: dict
    """
    changed_dict = dict_name.copy()
    car_id = None
    user_id = None
    if "users_id" in changed_dict:
        changed_dict["user_url"] = "".join(('/api/v1/users/', str(changed_dict["users_id"]), '/'))
        user_id = changed_dict["users_id"]
        del changed_dict["users_id"]

    if "cars_id" in changed_dict:
        changed_dict["car_url"] = "".join(('/api/v1/cars/', str(changed_dict["cars_id"]), '/'))
        car_id = changed_dict["cars_id"]
        del changed_dict["cars_id"]

    if isinstance(changed_dict["from_date"], datetime):
        changed_dict["from_date"] = changed_dict["from_date"].strftime("%d/%m/%Y, %H:%M:%S")
    elif isinstance(changed_dict["from_date"], int):
        date_str = str(changed_dict["from_date"])
        changed_dict[
            "from_date"] = f'{date_str[6:8]}/{date_str[4:6]}/{date_str[:4]}, {date_str[8:10]}:{date_str[-2:]}:00'

    if isinstance(changed_dict["to_date"], datetime):
        changed_dict["to_date"] = changed_dict["to_date"].strftime("%d/%m/%Y, %H:%M:%S")
    elif isinstance(changed_dict["to_date"], int):
        date_str = str(changed_dict["to_date"])
        changed_dict["to_date"] = f'{date_str[6:8]}/{date_str[4:6]}/{date_str[:4]}, {date_str[8:10]}:{date_str[-2:]}:00'

    if "available_from" in changed_dict:
        if isinstance(changed_dict["available_from"], datetime):
            changed_dict["available_from"] = changed_dict["available_from"].strftime("%d/%m/%Y, %H:%M:%S")
        changed_dict["id"] = {"car": car_id, "from": changed_dict["from_date"][:-3], "user": user_id}

    if "available" in changed_dict:
        changed_dict["available_from"] = changed_dict["available"].strftime("%d/%m/%Y, %H:%M:%S")
        del changed_dict["available"]

        changed_dict["car_url"] = "".join(('/api/v1/cars/', str(changed_dict["car_id"]), '/'))
        car_id = changed_dict["car_id"]
        del changed_dict["car_id"]

        changed_dict["user_url"] = "".join(('/api/v1/users/', str(changed_dict["user_id_rental"]), '/'))
        user_id = changed_dict["user_id_rental"]
        del changed_dict["user_id_rental"]

        changed_dict["id"] = {"car": car_id, "from": changed_dict["from_date"][:-3], "user": user_id}
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


TODAY = datetime.strptime(datetime.now().strftime("%Y-%m-%d"), '%Y-%m-%d')

rentals_data = [
    {"cars_id": 1, "users_id": 2, "from_date": TODAY + timedelta(minutes=30),
     "to_date": TODAY + timedelta(hours=1), "available_from": TODAY + timedelta(minutes=61)},
    {"cars_id": 1, "users_id": 1, "from_date": TODAY + timedelta(minutes=90),
     "to_date": TODAY + timedelta(minutes=100), "available_from": TODAY + timedelta(minutes=101)},
    {"cars_id": 1, "users_id": 1,
     "from_date": datetime.strptime((datetime.now() + timedelta(minutes=30)).strftime("%Y-%m-%d, %H:%M"),
                                    "%Y-%m-%d, %H:%M"),
     "to_date": datetime.strptime((datetime.now() + timedelta(minutes=60)).strftime("%Y-%m-%d, %H:%M"),
                                  "%Y-%m-%d, %H:%M"),
     "available_from": datetime.strptime((datetime.now() + timedelta(minutes=61)).strftime("%Y-%m-%d, %H:%M"),
                                         "%Y-%m-%d, %H:%M")}
]
rentals_invalid_data = [
    ({"car_id": 1, "from_date": int((datetime.now() + timedelta(minutes=30)).strftime('%Y%m%d%H%M')),
      "to_date": int((datetime.now() + timedelta(hours=1)).strftime('%Y%m%d%H%M'))}, "user_id_rental"),
    ({"user_id_rental": 1, "from_date": int((datetime.now() + timedelta(minutes=30)).strftime('%Y%m%d%H%M')),
      "to_date": int((datetime.now() + timedelta(hours=1)).strftime('%Y%m%d%H%M'))}, "required", "car_id"),
    ({"car_id": 1, "user_id_rental": 1, "to_date": int((datetime.now() + timedelta(hours=1)).strftime('%Y%m%d%H%M'))},
     "required", "from_date"),
    ({"user_id_rental": 1, "car_id": 1,
      "from_date": int((datetime.now() + timedelta(minutes=30)).strftime('%Y%m%d%H%M'))}, "required", "to_date"),
    ({"car_id": 10, "from_date": int((datetime.now() + timedelta(minutes=30)).strftime('%Y%m%d%H%M')),
      "to_date": int((datetime.now() + timedelta(hours=1)).strftime('%Y%m%d%H%M')), "user_id_rental": 1}, "car_id"),
    ({"car_id": 1, "to_date": int((datetime.now() - timedelta(minutes=30)).strftime('%Y%m%d%H%M')),
      "from_date": int((datetime.now() + timedelta(hours=1)).strftime('%Y%m%d%H%M')), "user_id_rental": 1}, "date",
     "to_date"),
    ({"car_id": 1, "to_date": int((datetime.now() + timedelta(minutes=30)).strftime('%Y%m%d%H%M')),
      "from_date": int((datetime.now() - timedelta(hours=1)).strftime('%Y%m%d%H%M')), "user_id_rental": 1}, "date",
     "from_date"),
    ({"car_id": 1, "from_date": (datetime.now() + timedelta(minutes=30)).strftime('%Y%m%d%H%M'),
      "to_date": int((datetime.now() + timedelta(hours=1)).strftime('%Y%m%d%H%M')), "user_id_rental": 1}, "type",
     "from_date"),
    ({"car_id": 1, "from_date": int((datetime.now() + timedelta(minutes=30)).strftime('%Y%m%d%H%M')),
      "to_date": (datetime.now() + timedelta(hours=1)).strftime('%Y%m%d%H%M'), "user_id_rental": 1}, "type", "to_date"),
    ({"car_id": 1, "to_date": int((datetime.now() + timedelta(minutes=30)).strftime('%Y%m%d%H%M')),
      "from_date": int((datetime.now() + timedelta(hours=1)).strftime('%Y%m%d%H%M%S')), "user_id_rental": 1},
     "date_length"),
    ({"car_id": 1, "to_date": int((datetime.now() + timedelta(minutes=30)).strftime('%Y%m%d%H')),
      "from_date": int((datetime.now() + timedelta(hours=1)).strftime('%Y%m%d%H%M')), "user_id_rental": 1},
     "date_length"),
    ({"car_id": 1, "from_date": int((datetime.now() + timedelta(minutes=-30)).strftime('%Y%m%d%H%M')),
      "to_date": int((datetime.now() + timedelta(hours=1)).strftime('%Y%m%d%H%M')), "user_id_rental": 1},
     "date_before_now", "from_date"),
    ({"car_id": 1, "from_date": int((datetime.now() + timedelta(minutes=30)).strftime('%Y%m%d%H%M')),
      "to_date": int((datetime.now() - timedelta(hours=1)).strftime('%Y%m%d%H%M')), "user_id_rental": 1},
     "date_before_now", "to_date"),
    ({"car_id": 1, "from_date": 200014301200,
      "to_date": int((datetime.now() + timedelta(hours=1)).strftime('%Y%m%d%H%M')), "user_id_rental": 1},
     "date_format", "from_date"),
    ({"car_id": 1, "to_date": 200014301200,
      "from_date": int((datetime.now() + timedelta(hours=1)).strftime('%Y%m%d%H%M')), "user_id_rental": 1},
     "date_format", "to_date"),
    ({"car_id": 1, "from_date": int((datetime.now() + timedelta(minutes=10)).strftime('%Y%m%d%H%M')),
      "to_date": int((datetime.now() + timedelta(hours=2)).strftime('%Y%m%d%H%M')), "user_id_rental": 1},
     "reserved"),
    ({"car_id": 1, "from_date": int((datetime.now() + timedelta(minutes=60)).strftime('%Y%m%d%H%M')),
      "to_date": int((datetime.now() + timedelta(hours=2)).strftime('%Y%m%d%H%M')), "user_id_rental": 1},
     "reserved")
]


def make_rentals():
    """Function that adds rentals to db."""
    for item in rentals_data:
        rental = Rental(**item)
        db.session.add(rental)
        db.session.commit()


class RentalsTestCase(unittest.TestCase):
    """Test rentals module."""

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client()
        self.user = create_user()
        self.token = token(self.client, self.user)
        self.user_moderator = create_moderator()
        self.token_moderator = token(self.client, self.user_moderator)
        self.user_admin = create_admin()
        self.token_admin = token(self.client, self.user_admin)

        # Add car
        car_data = {"name": "Car 1", "price": 123, "year": 2000, "model": "model", "image": "no_img.jpg"}
        car = Car(**car_data)
        db.session.add(car)
        db.session.commit()

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

    # Test show_rentals
    def test_show_rentals(self):
        """Test api for show_rentals, valid data."""
        # Request, no rentals in db
        # Request
        response = self.client.get('/api/v1/rentals/', headers=self.get_api_headers_admin())
        response_data = response.get_json()
        # Tests
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['data'], [])

        # Add rentals to db
        make_rentals()
        # Change dict to json format
        rentals = []
        for rental in rentals_data:
            rental = rental.copy()
            rentals.append(change_dict_to_json(rental))

        # Request
        response = self.client.get('/api/v1/rentals/', headers=self.get_api_headers_admin())
        response_data = response.get_json()

        # Expected results
        expected_result = {'success': True,
                           'data': rentals
                           }
        # Tests
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertDictEqual(expected_result, response_data)

        # Request with features: sort_by, apply_filter
        request_features = {'sort_by': 'from_date',
                            'filters': 'users_id[lt]=2'}
        response = self.client.get(request_with_features('/api/v1/rentals/', **request_features),
                                   headers=self.get_api_headers_admin())
        response_data = response.get_json()
        # Expected results
        filtered_rentals = [item for item in rentals if item['id']['user'] < 2]
        filtered_rentals_sorted = sorted(filtered_rentals, key=lambda item: item['from_date'])
        expected_result = {'success': True,
                           'data': filtered_rentals_sorted
                           }
        # Tests
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertDictEqual(expected_result, response_data)

    # Test show_rental
    def test_show_rental(self):
        """Test api for show_rental."""
        # No rentals
        # Request
        response = self.client.get('/api/v1/rentals/car1/user1/from202002022145/', headers=self.get_api_headers_admin())
        response_data = response.get_json()
        # Tests
        self.assertEqual(response.status_code, 404)
        self.assertFalse(response_data["success"])
        self.assertEqual(response_data["error"], "Rental not found")

        # Add rentals to db
        make_rentals()
        # Change dict to json format
        rentals = []
        for rental in rentals_data:
            rental = rental.copy()
            rentals.append(change_dict_to_json(rental))

        rental = Rental.query.all()[0]
        rental_from = rental.from_date.strftime("%Y%m%d%H%M")

        filtered_rental = [item for item in rentals if
                           item["id"]["car"] == rental.cars_id and item["id"]["user"] == rental.users_id and item[
                               "from_date"] == rental.from_date.strftime("%d/%m/%Y, %H:%M:%S")][0]

        # Request without params
        response = self.client.get(f'/api/v1/rentals/car{rental.cars_id}/user{rental.users_id}/from{rental_from}/',
                                   headers=self.get_api_headers_admin())
        response_data = response.get_json()
        # Expected results
        expected_result = {'success': True,
                           'data': filtered_rental
                           }
        # Tests
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertDictEqual(expected_result, response_data)

        # Request with params
        # Request
        request_features = {'params': 'id,user_url,available_from'}
        response = self.client.get(
            request_with_features(url=f'/api/v1/rentals/car{rental.cars_id}/user{rental.users_id}/from{rental_from}/',
                                  **request_features), headers=self.get_api_headers_admin())
        response_data = response.get_json()
        # Expected results
        expected_result = {'success': True,
                           'data': remove_params_from_dict(filtered_rental, ["id", "user_url", "available_from"])
                           }
        # Tests
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertDictEqual(expected_result, response_data)

    def test_show_rental_invalid_request(self):
        """Test api for show_rental, invalid request."""
        # Add rentals to db
        make_rentals()
        # data
        rental = Rental.query.all()[0]
        rental_from = rental.from_date.strftime("%Y%m%d")
        # Invalid data
        invalid_data = [(rental_from, "format"), ("200040101210", "format"), (datetime(1000, 2, 20), "not found")]

        # Requests
        for item in invalid_data:
            # Request
            response = self.client.get(f'/api/v1/rentals/car{rental.cars_id}/user{rental.users_id}/from{item[0]}/',
                                       headers=self.get_api_headers_admin())
            response_data = response.get_json()

            # Tests
            if item[1] == "format":
                self.assertEqual(response_data['message'], 'Wrong from: acceptable format: YmdHM')
                self.assertEqual(response_data['error'], 'bad request')
                self.assertEqual(response.status_code, 400)
            else:
                self.assertEqual(response_data['error'], 'not found')
                self.assertEqual(response.status_code, 404)

            self.assertFalse(response_data['success'])

    # Test add_rental
    def test_add_rental(self):
        """Test api for add_rental."""
        user_id = User.query.filter_by(email="test@test.com").first().id

        # Test admin
        # Data
        rental_data = {"car_id": 1, "from_date": int((datetime.now() + timedelta(minutes=30)).strftime('%Y%m%d%H%M')),
                       "to_date": int((datetime.now() + timedelta(hours=1)).strftime('%Y%m%d%H%M'))}

        available = datetime.strptime(str(rental_data["to_date"]), '%Y%m%d%H%M') + timedelta(hours=1)
        # Expected results
        rental = rental_data.copy()
        rental["available"] = available
        rental["user_id_rental"] = user_id
        expected_result = {'success': True,
                           'data': change_dict_to_json(rental)
                           }
        # Request
        response = self.client.post('/api/v1/rentals/', json={"user_id_rental": user_id, **rental_data},
                                    headers=self.get_api_headers_admin())
        response_data = response.get_json()
        # Tests
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertDictEqual(expected_result, response_data)

        # Test User
        # Data
        rental_data = {"car_id": 1, "from_date": int((datetime.now() + timedelta(hours=4)).strftime('%Y%m%d%H%M')),
                       "to_date": int((datetime.now() + timedelta(hours=5)).strftime('%Y%m%d%H%M'))}
        available = datetime.strptime(str(rental_data["to_date"]), '%Y%m%d%H%M') + timedelta(hours=1)
        # Expected results
        rental = rental_data.copy()
        rental["available"] = available
        rental["user_id_rental"] = user_id
        expected_result = {'success': True,
                           'data': change_dict_to_json(rental)
                           }
        # Request
        response = self.client.post('/api/v1/rentals/', json={**rental_data}, headers=self.get_api_headers())
        response_data = response.get_json()
        # Tests
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertDictEqual(expected_result, response_data)

    def test_add_rental_invalid_data(self):
        """Test api for add_rental, invalid data."""
        # Add rentals to db
        make_rentals()

        # Request
        for item in rentals_invalid_data:
            response = self.client.post('/api/v1/rentals/', json={**item[0]}, headers=self.get_api_headers_admin())
            response_data = response.get_json()

            # Tests
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            self.assertFalse(response_data['success'])
            if item[1] == "user_id_rental":
                self.assertEqual(response_data['error'], 'bad request')
                self.assertEqual(response_data['message'], "No user_id_rental, can't add rental")
            else:
                self.assertEqual(response_data['error']['error'], 'bad request')
                if item[1] == "required":
                    self.assertEqual(response_data['error']['message'], f"{item[2]} can't be null")
                    self.assertEqual(response_data['error_value_key'], item[2])
                elif item[1] == "car_id":
                    self.assertEqual(response_data['error_value_key'], item[1])
                elif item[1] == "date":
                    self.assertIn(f"Wrong value, date can't be before {datetime.now().strftime('%Y-%m-%d')}",
                                  response_data['error']['message'])
                    self.assertIn(response_data['error_value_key'], item[2])
                elif item[1] == "type":
                    self.assertEqual(response_data['error']['message'], 'Wrong value, not int.')
                    self.assertEqual(response_data['error_value_key'], item[2])
                elif item[1] == "date_length":
                    self.assertEqual(response_data['error']['message'], 'Wrong value, not 12 chars.')
                elif item[1] == "date_before_now":
                    self.assertIn(f"Wrong value, date can't be before {datetime.now().strftime('%Y-%m-%d')}",
                                  response_data['error']['message'])
                    self.assertEqual(response_data['error_value_key'], item[2])
                elif item[1] == "date_format":
                    self.assertEqual(response_data['error']['message'], "Wrong value, not YmdHM format."),
                    self.assertEqual(response_data['error_value_key'], item[2])
                else:
                    rental = Rental.query.get(
                        {"cars_id": rentals_data[2]["cars_id"], "users_id": rentals_data[2]["users_id"],
                         "from_date": rentals_data[2]["from_date"]})
                    self.assertEqual(response_data['error']['message'],
                                     f"Wrong dates, available before: "
                                     f"{(rental.from_date + timedelta(minutes=-61)).strftime('%Y-%m-%d %H:%M')}"
                                     f",available after:"
                                     f"{(rental.available_from + timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M')}"),
                    self.assertEqual(response_data['error_value_key'], "dates")

    # Test delete_rental
    def test_delete_rental(self):
        """Test api for delete_rental."""
        # No rentals
        response = self.client.delete(f'/api/v1/rentals/car1/user1/from200010201000/',
                                      headers=self.get_api_headers_admin())
        response_data = response.get_json()
        # Tests
        self.assertEqual(response_data['error'], 'Rental not found')
        self.assertEqual(response.status_code, 404)

        # Add rentals to db
        make_rentals()
        # Choose rental
        rental = random.choice(Rental.query.all())
        rental_date = rental.from_date.strftime('%Y%m%d%H%M')
        # Request
        response = self.client.delete(f'/api/v1/rentals/car{rental.cars_id}/user{rental.users_id}/from{rental_date}/',
                                      headers=self.get_api_headers_admin())
        response_data = response.get_json()

        # Tests
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertTrue(response_data['success'])

    def test_delete_rental_invalid_data(self):
        """Test api for delete_rental, invalid data."""
        invalid_data = [({"car_id": 1, "user_id": 1, "date_time": 1234}, "format"),
                        ({"car_id": 1, "user_id": 1, "date_time": 200014901200}, "format")]

        # Request
        for item in invalid_data:
            response = self.client.delete(
                f'/api/v1/rentals/car{item[0]["car_id"]}/user{item[0]["user_id"]}/from{item[0]["date_time"]}/',
                headers=self.get_api_headers_admin())
            response_data = response.get_json()

            # Tests
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            self.assertFalse(response_data['success'])
            self.assertEqual(response_data['error'], 'bad request')
            self.assertEqual(response_data['message'], 'Wrong from: acceptable format: YmdHM')
            self.assertEqual(response.status_code, 400)

    # Testing methods connected with values of request (content-type, tokens)
    def test_invalid_content_type(self):
        """Check if content type is 'application/json'"""
        api_headers = self.get_api_headers_moderator()
        del api_headers['Content-Type']

        # Check add_rental
        response = self.client.post('/api/v1/rentals/', data={"user_id_rental": 3,
                                                              "car_id": 2,
                                                              "from_date": 202308122020,
                                                              "to_date": 202309282021}, headers=api_headers)
        check_content_type(response, self.assertEqual, self.assertFalse)

    def test_missing_token_value(self):
        """Test if token has no value."""
        api_headers = self.get_api_headers()
        api_headers['Authorization'] = 'Bearer'

        # Check show_rentals
        response = self.client.get('/api/v1/rentals/', headers=api_headers)
        check_missing_token_value(response, self.assertEqual, self.assertFalse, self.assertNotIn)

        # Check show_rental
        response = self.client.get('/api/v1/rentals/car1/user1/from200010032000/', headers=api_headers)
        check_missing_token_value(response, self.assertEqual, self.assertFalse, self.assertNotIn)

        # Check add_rental
        response = self.client.post('/api/v1/rentals/', json={"user_id_rental": 3,
                                                              "car_id": 2,
                                                              "from_date": 202308122020,
                                                              "to_date": 202309282021}, headers=api_headers)
        check_missing_token_value(response, self.assertEqual, self.assertFalse, self.assertNotIn)

        # Check delete_rental
        response = self.client.delete('/api/v1/rentals/car1/user1/from200010032000/', headers=api_headers)
        check_missing_token_value(response, self.assertEqual, self.assertFalse, self.assertNotIn)

    def test_missing_token_wrong_value(self):
        """Check if token has wrong value"""
        api_headers = self.get_api_headers_moderator()
        api_headers['Authorization'] = 'Bearer token'

        # Check show_rentals
        response = self.client.get('/api/v1/rentals/', headers=api_headers)
        check_missing_token_wrong_value(response, self.assertEqual, self.assertFalse, self.assertNotIn)

        # Check show_rental
        response = self.client.get('/api/v1/rentals/car1/user1/from200010032000/', headers=api_headers)
        check_missing_token_wrong_value(response, self.assertEqual, self.assertFalse, self.assertNotIn)

        # Check add_rental
        response = self.client.post('/api/v1/rentals/', json={"user_id_rental": 3,
                                                              "car_id": 2,
                                                              "from_date": 202308122020,
                                                              "to_date": 202309282021}, headers=api_headers)
        check_missing_token_wrong_value(response, self.assertEqual, self.assertFalse, self.assertNotIn)

        # Check delete_rental
        response = self.client.delete('/api/v1/rentals/car1/user1/from200010032000/', headers=api_headers)
        check_missing_token_wrong_value(response, self.assertEqual, self.assertFalse, self.assertNotIn)

    def test_missing_token(self):
        """Check if token exists"""
        api_headers = self.get_api_headers()
        del api_headers['Authorization']

        # Check show_rentals
        response = self.client.get('/api/v1/rentals/', headers=api_headers)
        check_missing_token(response, self.assertEqual, self.assertFalse, self.assertNotIn)

        # Check show_rental
        response = self.client.get('/api/v1/rentals/car1/user1/from200010032000/', headers=api_headers)
        check_missing_token(response, self.assertEqual, self.assertFalse, self.assertNotIn)

        # Check add_rental
        response = self.client.post('/api/v1/rentals/', json={"user_id_rental": 3,
                                                              "car_id": 2,
                                                              "from_date": 202308122020,
                                                              "to_date": 202309282021}, headers=api_headers)
        check_missing_token(response, self.assertEqual, self.assertFalse, self.assertNotIn)

        # Check delete_rental
        response = self.client.delete('/api/v1/rentals/car1/user1/from200010032000/', headers=api_headers)
        check_missing_token(response, self.assertEqual, self.assertFalse, self.assertNotIn)

    # Test permissions
    def test_insufficient_permissions(self):
        """Test permissions."""
        permission_headers = [self.get_api_headers(), self.get_api_headers_moderator()]
        for header in permission_headers:
            # Check show_rentals
            response = self.client.get('/api/v1/rentals/', headers=header)
            check_permissions(response, self.assertEqual, self.assertFalse)

            # Check show_rental
            response = self.client.get('/api/v1/rentals/car1/user1/from200010032000/', headers=header)
            check_permissions(response, self.assertEqual, self.assertFalse)

            # Check delete_rental
            response = self.client.delete('/api/v1/rentals/car1/user1/from200010032000/', headers=header)
            check_permissions(response, self.assertEqual, self.assertFalse)

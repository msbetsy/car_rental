"""This module stores tests for client app.main routes."""
import unittest
import re
from datetime import datetime, timedelta
from app import create_app, db
from app.models import Role, Car, Rental, User, NewsPost
from tests.api_functions import create_user, create_moderator

car_valid_data = [{"name": "first", "price": 100, "year": 2001, "model": "first one", "image": "first.jpg"},
                  {"name": "second", "price": 200, "year": 2002, "model": "second one", "image": "second.jpg"},
                  {"name": "third", "price": 300, "year": 2003, "model": "third one", "image": "third.jpg"}
                  ]
news_post_valid_data = [{"author_id": 1, "title": "one", "date": "2020-01-01", "body": "first", "img_url": "1.jpg"},
                        {"author_id": 1, "title": "two", "date": "2000-01-02", "body": "second", "img_url": "2.jpg"},
                        {"author_id": 2, "title": "three", "date": "2022-01-01", "body": "third", "img_url": "3.jpg"},
                        {"author_id": 2, "title": "four", "date": "2019-01-01", "body": "fourth", "img_url": "4.jpg"},
                        {"author_id": 3, "title": "five", "date": "2018-01-01", "body": "fifth", "img_url": "5.jpg"},
                        {"author_id": 3, "title": "six", "date": "2002-01-01", "body": "sixth", "img_url": "6.jpg"},
                        {"author_id": 1, "title": "seven", "date": "2000-01-01", "body": "seventh", "img_url": "7.jpg"},
                        {"author_id": 2, "title": "eight", "date": "2007-01-01", "body": "eighth", "img_url": "8.jpg"},
                        {"author_id": 3, "title": "nine", "date": "2009-01-01", "body": "ninth", "img_url": "9.jpg"},
                        {"author_id": 1, "title": "ten", "date": "2020-02-01", "body": "tenth", "img_url": "10.jpg"},
                        {"author_id": 2, "title": "eleven", "date": "2020-01-30", "body": "eleventh",
                         "img_url": "11.jpg"}]


class FlaskClientMainTestCase(unittest.TestCase):
    """Test all routes for app.main."""

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client()
        self.user = create_user()
        self.moderator = create_moderator()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self, email, password):
        """Login user.

        :param email: User's email
        :type email: str
        :param password: User's password
        :type password: str
        :return: Response for the login query
        :rtype: flask.wrappers.Response
        """
        return self.client.post('/auth/login', data=dict(email=email, password=password), follow_redirects=True)

    def add_cars_to_db(self):
        """Method for adding cars from car_valid_data to db."""
        for item in car_valid_data:
            car = Car(**item)
            db.session.add(car)
            db.session.commit()

    def add_posts_to_db(self):
        """Method for adding posts from news_post_valid_data to db."""
        for item in news_post_valid_data:
            post = NewsPost(**item)
            db.session.add(post)
            db.session.commit()

    # Test for routes without decorators

    # Test home page
    def test_home_page(self):
        """Test route for index."""
        response = self.client.get('/', content_type='html/text')
        response_data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Your Perfect Wedding Getaway Car', response_data)
        self.assertIn('Carcall', response_data)
        self.assertIn('About', response_data)
        self.assertIn('Register', response_data)
        self.assertIn('Log In', response_data)
        self.assertIn('Contact', response_data)
        self.assertIn('Big choice', response_data)
        self.assertNotIn('My account', response_data)
        self.assertNotIn('Logout', response_data)

    # Test contact page
    def test_contact(self):
        """Test route for contact, valid data."""
        # Anonymous user
        response_get = self.client.get('/contact')
        response_data_get = response_get.get_data(as_text=True)
        self.assertEqual(response_get.status_code, 200)
        self.assertIn('name="name" required type="text" value=""', response_data_get)
        self.assertIn('name="subject" required type="text" value=""', response_data_get)
        self.assertIn('name="email" required type="text" value=""', response_data_get)
        self.assertIn('name="telephone" required type="tel" value=""', response_data_get)
        self.assertIn('name="message" required', response_data_get)
        response = self.client.post('/contact',
                                    data={"name": "My name", "subject": "My subject", "email": "my@email.com",
                                          "telephone": "1234", "message": "my message"})
        response_data = response.get_data(as_text=True)
        self.assertIn("Thanks for sending e-mail.", response_data)

        # Log in user
        self.login("test@test.com", "password")
        response_get = self.client.get('/contact')
        response_data_get = response_get.get_data(as_text=True)
        self.assertEqual(response_get.status_code, 200)
        self.assertIn('name="name" required type="text" value="name surname"', response_data_get)
        self.assertIn('name="subject" required type="text" value=""', response_data_get)
        self.assertIn('name="email" required type="text" value="test@test.com"', response_data_get)
        self.assertIn('name="telephone" required type="tel" value="12345"', response_data_get)
        self.assertIn('name="message" required', response_data_get)
        response = self.client.post('/contact', data={"subject": "My subject", "message": "my message"})
        response_data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Thanks for sending e-mail.", response_data)

    def test_contact_invalid_data(self):
        """Test route for contact, invalid data."""
        invalid_data = [({"name": "", "subject": "My subject", "email": "my@email.com", "telephone": "1234",
                          "message": "my message"}, "required"),
                        ({"name": "My name", "subject": "", "email": "my@email.com", "telephone": "1234",
                          "message": "my message"}, "required"),
                        ({"name": "My name", "subject": "My subject", "email": "", "telephone": "1234",
                          "message": "my message"}, "required"),
                        ({"name": "My name", "subject": "My subject", "email": "my@email.com", "telephone": "",
                          "message": "my message"}, "required"),
                        ({"name": "My name", "subject": "My subject", "email": "my.email.com", "telephone": "1234",
                          "message": "my message"}, "invalid_mail"),
                        ({"name": "My name", "subject": "My subject",
                          "email": "myemailemailemailemailemailemailemailemailemailemailemailemailemailemail@email.com",
                          "telephone": "1234", "message": "my message"}, "mail_too_long")
                        ]
        for item in invalid_data:
            response = self.client.post('/contact', data=item[0])
            response_data = response.get_data(as_text=True)
            self.assertEqual(response.status_code, 200)
            self.assertNotIn("Thanks for sending e-mail.", response_data)
            if item[1] == "required":
                self.assertIn("This field is required.", response_data)
            elif item[1] == "invalid_mail":
                self.assertIn("Invalid email address.", response_data)
            else:
                self.assertIn("Field must be between 1 and 80 characters long.", response_data)
                self.assertIn("Invalid email address.", response_data)

    # Test show_models
    def test_show_models(self):
        """Test route for show_models."""
        response = self.client.get('/cars')
        response_data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("There are no cars in our offer", response_data)

        # Add cars
        self.add_cars_to_db()

        response = self.client.get('/cars')
        response_data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("/static/img/first.jpg", response_data)
        self.assertIn("/cars/first", response_data)
        self.assertIn("/static/img/second.jpg", response_data)
        self.assertIn("/cars/second", response_data)
        self.assertIn("/static/img/third.jpg", response_data)
        self.assertIn("/cars/third", response_data)
        self.assertNotIn("Add New Car", response_data)

        # Log in with WRITE Permission
        self.login("moderator@test.com", "password")
        response = self.client.get('/cars')
        response_data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Add New Car", response_data)

    # Test show_car
    def test_show_car(self):
        """Test route for show_car."""
        response = self.client.get('/cars/first')
        response_data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 404)
        self.assertIn("Page Not Found", response_data)

        # Add cars
        self.add_cars_to_db()

        response = self.client.get('/cars/first')
        response_data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(f'Model: {car_valid_data[0]["model"]}', response_data)
        self.assertIn(f'Year: {car_valid_data[0]["year"]}', response_data)
        self.assertIn(f'Price: {round(float(car_valid_data[0]["price"]), 1)}$', response_data)
        self.assertIn(car_valid_data[0]["name"], response_data)
        self.assertIn("Please, log in to see the calendar.", response_data)
        self.assertNotIn("Choose date and time:", response_data)
        self.assertNotIn("Start date:", response_data)
        self.assertNotIn("Start time:", response_data)
        self.assertNotIn("End date:", response_data)
        self.assertNotIn("End time:", response_data)
        # Log in
        self.login("test@test.com", "password")
        # Add reservation
        valid_date = datetime.now().strftime("%Y-%m-%d")
        response = self.client.post('/cars/first',
                                    data={
                                        "start_date": valid_date,
                                        "start_time": "12:00",
                                        "end_date": valid_date,
                                        "end_time": "14:00"
                                    }, follow_redirects=True)

        response_data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Reservation saved!", response_data)
        self.assertIn("first", response_data)
        self.assertIn(valid_date, response_data)
        self.assertIn("My profile", response_data)

    def test_show_car_invalid_data(self):
        """Test route for show_car, invalid data."""
        # Add cars
        self.add_cars_to_db()

        # Add reservations

        # Add reservation to db
        user_id = User.query.filter_by(email="test@test.com").first().id
        from_date_time = datetime.now() + timedelta(hours=5)
        to_date_time = datetime.now() + timedelta(hours=10)
        available_from = to_date_time + timedelta(hours=1)
        reservation_dict = {"cars_id": 1, "users_id": user_id, "from_date": from_date_time, "to_date": to_date_time,
                            'available_from': available_from}
        rental = Rental(**reservation_dict)
        db.session.add(rental)
        db.session.commit()

        # Add reservation - POST data
        date_ok = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        date_for_invalid_start_time = (available_from + timedelta(days=12)).strftime("%Y-%m-%d")
        invalid_data = [
            ({"start_date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
              "start_time": "12:00", "end_date": date_ok, "end_time": "14:00"}, "wrong_dates"),
            ({"start_date": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
              "start_time": "12:00", "end_date": date_ok, "end_time": "14:00"}, "start_date"),
            ({"start_date": "", "start_time": "14:00", "end_date": date_ok, "end_time": "12:00"}, "required"),
            ({"start_date": date_ok, "start_time": "", "end_date": date_ok, "end_time": "14:00"}, "required"),
            ({"start_date": date_ok, "start_time": "12:00", "end_date": "", "end_time": "14:00"}, "required"),
            ({"start_date": date_ok, "start_time": "12:00", "end_date": date_ok, "end_time": ""}, "required"),
            ({"start_date": (from_date_time - timedelta(hours=1)).strftime("%Y-%m-%d"),
              "start_time": (from_date_time - timedelta(hours=1)).strftime("%H:%M"), "end_date": date_ok,
              "end_time": "14:00"}, "change_dates"),
            ({"start_date": (from_date_time + timedelta(hours=1)).strftime("%Y-%m-%d"),
              "start_time": (from_date_time + timedelta(hours=1)).strftime("%H:%M"), "end_date": date_ok,
              "end_time": "14:00"}, "change_dates"),
            ({"start_date": date_for_invalid_start_time, "start_time": "14:00", "end_date": date_for_invalid_start_time,
              "end_time": "12:00"}, "start_time")
        ]
        # Log in
        self.login("test@test.com", "password")
        # Add reservation
        valid_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        for item in invalid_data:
            response = self.client.post('/cars/first', data=item[0], follow_redirects=True)
            response_data = response.get_data(as_text=True)
            self.assertEqual(response.status_code, 200)
            self.assertNotIn("Reservation saved!", response_data)
            self.assertNotIn("My profile", response_data)
            self.assertNotIn("My reservations", response_data)

            if item[1] == "required":
                self.assertIn("This field is required.", response_data)
            elif item[1] == "wrong_dates":
                self.assertIn("Change dates to future dates!", response_data)
            elif item[1] == "start_date":
                self.assertIn("Start date is later than end date!", response_data)
            elif item[1] == "change_dates":
                self.assertIn("Change dates!", response_data)
                self.assertIn(
                    f'Available before: {(from_date_time + timedelta(minutes=-61)).strftime("%Y-%m-%d %H:%M")}',
                    response_data)
                self.assertIn(f'Available after: {(available_from + timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M")}',
                              response_data)
            elif item[1] == "start_time":
                self.assertIn("Start time is later than end time!", response_data)

    # Test add_opinion
    def test_add_opinion(self):
        """Test route for add_opinion."""
        # Test when no opinions
        response = self.client.get('/opinions')
        response_data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Add your opinion", response_data)
        self.assertNotIn("opinion1.jpg", response_data)
        self.assertNotIn("opinion2.jpg", response_data)
        self.assertNotIn("opinion3.jpg", response_data)

        # Add opinion, without log in
        response = self.client.post('/opinions', data={"opinion_text": "my opinion"}, follow_redirects=True)
        response_data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Add your opinion", response_data)
        self.assertIn("You need to login or register to add opinion.", response_data)
        self.assertIn("Email:", response_data)
        self.assertIn("Password:", response_data)

        # Add opinion, after log in
        self.login("test@test.com", "password")
        response = self.client.post('/opinions', data={"opinion_text": "my opinion"}, follow_redirects=True)
        response_data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Thank you for your feedback.", response_data)

    def test_add_opinion_invalid_data(self):
        """Test route for add_opinion, invalid data."""
        self.login("test@test.com", "password")
        response = self.client.post('/opinions', data={"opinion_text": ""}, follow_redirects=True)
        response_data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("This field is required.", response_data)

    # Test show_news
    def test_show_news(self):
        """Test route for show_news."""
        # No news
        response = self.client.get('/news')
        response_data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("There is no news.", response_data)
        self.assertNotIn('<div class="pagination">', response_data)

        # Add news
        self.add_posts_to_db()
        response = self.client.get('/news')
        response_data = response.get_data(as_text=True)
        dates_desc_first_page = re.findall(r'Posted by\n.*\n.*on.(.{10})\n.*<\/p>', response_data)
        all_dates = []
        for item in news_post_valid_data:
            all_dates.append(item["date"])
        all_dates.sort(reverse=True)
        if len(dates_desc_first_page) != len(all_dates):
            per_page = len(dates_desc_first_page)
            all_dates = all_dates[:per_page]
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("There is no news.", response_data)
        self.assertIn('<div class="pagination">', response_data)
        self.assertEqual(dates_desc_first_page, all_dates)

    # Test show_post
    def test_show_post(self):
        """Test route for show_post."""
        # No posts
        response = self.client.get('/news/1')
        response_data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 404)
        self.assertIn("Page Not Found", response_data)

        # Add news
        self.add_posts_to_db()

        # With posts
        post = NewsPost.query.all()[1]
        response = self.client.get(f'/news/{post.id}')
        response_data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(post.title, response_data)
        self.assertIn(post.body, response_data)
        self.assertIn(post.date, response_data)
        self.assertIn(post.img_url, response_data)
        self.assertIn(User.query.get(post.author_id).name, response_data)
        self.assertIn("Add comment", response_data)

        # Add comment, not login
        response = self.client.post(f'/news/{post.id}', data={"text": "my comment", "submit_comment": "Add"},
                                    follow_redirects=True)
        response_data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("You need to login or register to comment.", response_data)

        # After log in
        self.login("test@test.com", "password")
        user = User.query.filter_by(email="test@test.com").first()
        response = self.client.post(f'/news/{post.id}', data={"text": "my comment", "submit_comment": "Add"},
                                    follow_redirects=True)
        date = datetime.now()
        response_data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("You need to login or register to comment.", response_data)
        self.assertIn("Thank you for comment.", response_data)
        self.assertIn("my comment", response_data)
        self.assertIn(user.name, response_data)
        self.assertIn(user.surname, response_data)
        self.assertIn(date.strftime("%Y-%m-%d %H:%M:%S"), response_data)
        self.assertIn("Reply", response_data)

        # Add comment comment
        response = self.client.post(f'/news/{post.id}', data={"text": "my comment 2", "parentID": 1, "submit": "Reply"},
                                    follow_redirects=True)
        date = datetime.now()
        response_data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Thank you for comment.", response_data)
        self.assertIn("my comment", response_data)
        self.assertIn(user.name, response_data)
        self.assertIn(user.surname, response_data)
        self.assertIn(date.strftime("%Y-%m-%d %H:%M:%S"), response_data)
        self.assertIn("Reply", response_data)

    def test_show_post_invalid_data(self):
        """Test route for show_post, invalid data."""
        # Add news
        self.add_posts_to_db()
        # Log in
        self.login("test@test.com", "password")

        # Request - comment
        post = NewsPost.query.all()[1]
        user = User.query.filter_by(email="test@test.com").first()
        response = self.client.post(f'/news/{post.id}', data={"text": "", "submit_comment": "Add"},
                                    follow_redirects=True)
        date = datetime.now()
        response_data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("This field is required.", response_data)
        self.assertNotIn("Thank you for comment.", response_data)

        # Request - comment comment
        # Add comment
        post = NewsPost.query.all()[1]
        self.client.post(f'/news/{post.id}', data={"text": "Comment", "submit_comment": "Add"}, follow_redirects=True)
        # Add comment comment
        invalid_data = [{"text": "", "parentID": 1, "submit": "Reply"},
                        {"text": "text", "parentID": "", "submit": "Reply"}]
        for item in invalid_data:
            response = self.client.post(f'/news/{post.id}', data=item, follow_redirects=True)
            response_data = response.get_data(as_text=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn("This field is required.", response_data)
            self.assertNotIn("Thank you for comment.", response_data)

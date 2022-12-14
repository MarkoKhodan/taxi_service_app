from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse, reverse_lazy

from taxi.models import Car, Manufacturer

INDEX_URL = reverse("taxi:index")
CAR_DETAIL_URL = reverse("taxi:car-detail", kwargs={"pk": 1})
MANUFACTURER_LIST_URL = reverse("taxi:manufacturer-list")
CARS_LIST_URL = reverse("taxi:car-list")
CAR_CREATE_URL = reverse("taxi:car-create")
CAR_UPDATE_URL = reverse("taxi:car-update", kwargs={"pk": 1})
CAR_DELETE_URL = reverse("taxi:car-delete", kwargs={"pk": 1})
MANUFACTURER_ID = 1
DRIVER_ID = 1


class LoginRequiredTest(TestCase):
    """Test login required decorator and mixin with redirection to the right page after login"""

    @classmethod
    def setUpTestData(cls):
        get_user_model().objects.create_user(username="Test", password="Test123")

        manufacturer = Manufacturer.objects.create(name="Test", country="test")

        Car.objects.create(model="Test", manufacturer=manufacturer)

    def test_index(self):

        response = self.client.get(INDEX_URL)

        self.assertRedirects(response, "/accounts/login/?next=/")

    def test_drivers_list(self):

        url = reverse("taxi:driver-list")
        response = self.client.get(url)

        self.assertRedirects(response, "/accounts/login/?next=/drivers/")

    def test_cars_list(self):

        response = self.client.get(CARS_LIST_URL)

        self.assertRedirects(response, "/accounts/login/?next=/cars/")

    def test_manufacturers_list(self):

        response = self.client.get(MANUFACTURER_LIST_URL)

        self.assertRedirects(response, "/accounts/login/?next=/manufacturers/")

    def test_driver_detail(self):
        url = reverse("taxi:driver-detail", kwargs={"pk": 1})
        response = self.client.get(url)

        self.assertRedirects(response, "/accounts/login/?next=/drivers/1/")

    def test_car_detail(self):

        response = self.client.get(CAR_DETAIL_URL)

        self.assertRedirects(response, "/accounts/login/?next=/cars/1/")


class IndexViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        get_user_model().objects.create_user(username="Test", password="Test123")

        manufacturer = Manufacturer.objects.create(name="Test", country="test")

        Car.objects.create(model="Test", manufacturer=manufacturer)

    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="Test123", password="Test12345", license_number="Tes12345"
        )

        self.client.force_login(self.user)
        self.response = self.client.get(INDEX_URL)

    def test_context_variables_values(self):
        self.assertEqual(self.response.context["num_cars"], 1)
        self.assertEqual(self.response.context["num_manufacturers"], 1)
        self.assertEqual(self.response.context["num_drivers"], 2)
        self.assertEqual(self.response.context["num_visits"], 1)

    def test_uses_correct_template(self):
        self.assertTemplateUsed(self.response, "taxi/index.html")


class AssignCarToDriverViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        get_user_model().objects.create_user(username="Test", password="Test123")

        manufacturer = Manufacturer.objects.create(name="Test", country="test")

        Car.objects.create(model="Test", manufacturer=manufacturer)

    def setUp(self) -> None:
        self.client.force_login(get_user_model().objects.get(id=1))

    def test_car_is_not_assigned_to_driver(self):
        response = self.client.get(CAR_DETAIL_URL)

        self.assertContains(response, "Assign me to this car")

    def test_car_is_assigned_to_driver(self):
        user = get_user_model().objects.get(id=1)
        car = Car.objects.get(id=1)
        user.cars.add(car)

        response = self.client.get(CAR_DETAIL_URL)

        self.assertContains(response, "Delete me from this car")


class ManufacturerListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        get_user_model().objects.create_user(username="Test", password="Test123")
        Manufacturer.objects.create(name="TEST", country="test country")
        Manufacturer.objects.create(name="TEST1", country="test country")

    def setUp(self) -> None:
        self.client.force_login(get_user_model().objects.get(id=1))
        self.response = self.client.get(MANUFACTURER_LIST_URL)
        self.manufactures = Manufacturer.objects.all()

    def test_context_variable_value(self):
        self.assertEqual(
            list(self.response.context["manufacturer_list"]), list(self.manufactures)
        )

    def test_uses_correct_template(self):
        self.assertTemplateUsed(self.response, "taxi/manufacturer_list.html")

    def test_pagination_is_correct(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertTrue("is_paginated" in self.response.context)
        self.assertTrue(len(self.response.context["manufacturer_list"]) == 2)


class ManufacturerCreateUpdateDeleteViewsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        get_user_model().objects.create_user(username="Test", password="Test123")

    def setUp(self) -> None:
        self.client.force_login(get_user_model().objects.get(id=1))

    def test_success_url(self):
        post = {"name": "test", "country": "test country"}

        success_url = MANUFACTURER_LIST_URL
        response_create = self.client.post(reverse("taxi:manufacturer-create"), post)
        response_update = self.client.post(
            reverse("taxi:manufacturer-update", kwargs={"pk": 1}), post
        )
        response_delete = self.client.post(
            reverse("taxi:manufacturer-delete", kwargs={"pk": 1})
        )

        self.assertEqual(response_create.status_code, 302)
        self.assertRedirects(response_create, success_url)

        self.assertEqual(response_update.status_code, 302)
        self.assertRedirects(response_update, success_url)

        self.assertEqual(response_delete.status_code, 302)
        self.assertRedirects(response_delete, success_url)


class CarListViewsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        get_user_model().objects.create_user(username="Test", password="Test123")

        manufacturer = Manufacturer.objects.create(name="TEST1", country="test country")

        Car.objects.create(model="test1", manufacturer=manufacturer)

        Car.objects.create(model="test2", manufacturer=manufacturer)

        Car.objects.create(model="test3", manufacturer=manufacturer)

    def setUp(self) -> None:
        self.client.force_login(get_user_model().objects.get(id=1))

    def test_search_form(self):
        response_first_page = self.client.get(f"{CARS_LIST_URL}?title=test1&page=1")
        response_second_page = self.client.get(f"{CARS_LIST_URL}??title=test1&page=2")
        self.assertContains(response_first_page, "test1")
        self.assertContains(response_first_page, "test2")
        self.assertContains(response_second_page, "test3")


class CarCreateUpdateDeleteViewsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        get_user_model().objects.create_user(username="Test", password="Test123")

        Manufacturer.objects.create(name="TEST12", country="test country")

        Car.objects.create(model="test", manufacturer=Manufacturer.objects.get(id=1))

    def setUp(self) -> None:
        self.client.force_login(get_user_model().objects.get(id=1))

    def test_create_success_url(self):

        post = {"model": "test", "manufacturer": MANUFACTURER_ID, "drivers": DRIVER_ID}

        response = self.client.post(CAR_CREATE_URL, post)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, CARS_LIST_URL)

    def test_update_success_url(self):

        post = {"model": "test", "manufacturer": MANUFACTURER_ID, "drivers": DRIVER_ID}

        response = self.client.post(CAR_UPDATE_URL, post)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, CAR_DETAIL_URL)

    def test_delete_success_url(self):

        post = {"model": "test", "manufacturer": MANUFACTURER_ID, "drivers": DRIVER_ID}

        response = self.client.post(CAR_DELETE_URL)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, CARS_LIST_URL)

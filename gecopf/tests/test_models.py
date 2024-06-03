from django.test import TestCase

# Create your tests here.
class YourTestClass(TestCase):

    @classmethod
    def setUpTestData(cls):
        print("setUpTestData: Ejecute una vez para configurar datos no modificados para todos los métodos de clase.") ##
        pass

    def setUp(self):
        print("setUp: Ejecutar una vez por cada método de prueba para configurar datos limpios.") ##
        pass

    def test_false_is_false(self):
        print("Method: test_false_is_false.") ##
        self.assertFalse(False)

    def test_false_is_true(self):
        print("Method: test_false_is_true.") ##
        self.assertTrue(False)

    def test_one_plus_one_equals_two(self):
        print("Method: test_one_plus_one_equals_two.") ##
        self.assertEqual(1 + 1, 2)

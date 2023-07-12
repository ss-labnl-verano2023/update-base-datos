import unittest
from google_api import *    # type: ignore


class TestIsExpired(unittest.TestCase):
    def test_is_expired_false(self):
        # I/O (inputs & outputs)
        test_input_id = [get_id_index(1), get_id_index(13)]
        expected_output = [False, False]

        for iteration in range(len(test_input_id)):
            # Result
            result = is_expired(test_input_id[iteration])
            self.assertEqual(expected_output[iteration], result)

    def test_is_expired_true(self):
        # I/O (inputs & outputs)
        test_input_id = [get_id_index(51), get_id_index(10)]
        expected_output = [True, True]

        for iteration in range(len(test_input_id)):
            # Result
            result = is_expired(test_input_id[iteration])
            self.assertEqual(expected_output[iteration], result)

    def test_is_expired_exception_nodate(self):
        # I/O (inputs & outputs)
        test_input_id = 14

        # Result
        with self.assertRaises(Exception) as context:
            is_expired(test_input_id)

        # Check exception message
        self.assertEqual(str(context.exception), 'No hay fecha de expiración')

    def test_is_expired_excpetion_httperror(self):
        with self.assertRaises(Exception) as context:
            is_expired(-1)


# TODO: implementar las test unit para update_static_data con mock objects
class TestUpdateStaticData(unittest.TestCase):
    def test_update_static_data(self):
        # I/O (inputs & outputs)
        test_input_id = 1
        #Result
        update_static_data(test_input_id)


# TODO: implementar las test unit para update_static_data con mock objects
class TestUpdateDynamicData(unittest.TestCase):
    def test_update_dynamic_data(self):
        # I/O (inputs & outputs)
        test_input_id = get_id_index(1)
        #Result
        update_dynamic_data(test_input_id)


if __name__ == '__main__':
    unittest.main()

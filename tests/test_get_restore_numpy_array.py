import pytest
from sympl import (
    DataArray, set_dimension_names, get_numpy_array,
    restore_dimensions, get_numpy_arrays_with_properties,
    restore_data_arrays_with_properties, InvalidStateException)
import numpy as np
import unittest

"""
get_numpy_arrays_with_properties:
    - returns numpy arrays in the dict
    - those numpy arrays should have same dtype as original data
        * even when unit conversion happens
    - they should actually be the same numpy arrays (with memory) as original data if no conversion happens
        * even when units are specified (so long as they match)
    - should be the same quantities as requested by the properties
        * contain all
        * not contain extra
        * raise exception if some are missing
    - units
        * converts if requested and present, with correct value and units attribute
        * does nothing if not requested whether or not present
        * does nothing if requested but not present
    - requires "dims" to be specified, raises exception if they aren't
    - dims_like
        * should work if matched dimensions are identical
        * should raise exception if matched dimensions are not identical
        * should require value to be a quantity in property_dictionary

restore_data_arrays_with_properties:
    - should return a dictionary of DataArrays
    - DataArray values should be the same arrays as original data if no conversion happens
    - if conversion does happen, dtype should be the same as the input
    - should return same quantities as requested by the properties
        * contain all
        * not contain extra
        * raise exception if some are missing
    - units
        * should be the same value as specified in output_properties dict
    - requires dims_like to be specified, raises exception if it's not
        * returned DataArray should have same dimensions as dims_like object
        * exception should be raised if dims_like is wrong (shape is incompatible)

Should add any created exceptions to the docstrings for these functions
"""

def test_get_numpy_array_3d_no_change():
    array = DataArray(
        np.random.randn(2, 3, 4),
        dims=['x', 'y', 'z'],
        attrs={'units': ''},
    )
    numpy_array = get_numpy_array(array, ['x', 'y', 'z'])
    assert np.byte_bounds(numpy_array) == np.byte_bounds(array.values)
    assert np.all(numpy_array == array.values)
    assert numpy_array.base is array.values


def test_get_numpy_array_3d_reverse():
    array = DataArray(
        np.random.randn(2, 3, 4),
        dims=['x', 'y', 'z'],
        attrs={'units': ''},
    )
    numpy_array = get_numpy_array(array, ['z', 'y', 'x'])
    assert numpy_array.shape == (4, 3, 2)
    assert np.all(np.transpose(numpy_array, (2, 1, 0)) == array.values)
    assert np.byte_bounds(numpy_array) == np.byte_bounds(array.values)
    assert numpy_array.base is array.values


def test_get_numpy_array_2d_reverse():
    array = DataArray(
        np.random.randn(2, 3),
        dims=['y', 'z'],
        attrs={'units': ''},
    )
    numpy_array = get_numpy_array(array, ['z', 'y'])
    assert numpy_array.shape == (3, 2)
    assert np.all(np.transpose(numpy_array, (1, 0)) == array.values)
    assert np.byte_bounds(numpy_array) == np.byte_bounds(array.values)
    assert numpy_array.base is array.values


def test_get_numpy_array_1d():
    array = DataArray(
        np.random.randn(2),
        dims=['y'],
        attrs={'units': ''},
    )
    numpy_array = get_numpy_array(array, ['y'])
    assert numpy_array.shape == (2,)
    assert np.all(numpy_array == array.values)
    assert np.byte_bounds(numpy_array) == np.byte_bounds(array.values)
    assert numpy_array.base is array.values


def test_get_numpy_array_creates_new_dim():
    array = DataArray(
        np.random.randn(2),
        dims=['x'],
        attrs={'units': ''},
    )
    numpy_array = get_numpy_array(array, ['x', 'y'])
    assert numpy_array.shape == (2, 1)
    assert np.all(numpy_array[:, 0] == array.values)
    assert np.byte_bounds(numpy_array) == np.byte_bounds(array.values)
    assert numpy_array.base is array.values


def test_get_numpy_array_creates_new_dim_in_front():
    array = DataArray(
        np.random.randn(2),
        dims=['x'],
        attrs={'units': ''},
    )
    numpy_array = get_numpy_array(array, ['y', 'x'])
    assert numpy_array.shape == (1, 2)
    assert np.all(numpy_array[0, :] == array.values)
    assert np.byte_bounds(numpy_array) == np.byte_bounds(array.values)
    assert numpy_array.base is array.values


def test_get_numpy_array_retrieves_explicit_dimensions():
    array = DataArray(
        np.random.randn(2, 3),
        dims=['alpha', 'zeta'],
        attrs={'units': ''},
    )
    numpy_array = get_numpy_array(array, ['zeta', 'alpha'])
    assert numpy_array.shape == (3, 2)
    assert np.all(np.transpose(numpy_array, (1, 0)) == array.values)
    assert np.byte_bounds(numpy_array) == np.byte_bounds(array.values)
    assert numpy_array.base is array.values


def test_get_numpy_array_invalid_dimension_raises_value_error():
    array = DataArray(
        np.random.randn(2),
        dims=['sheep'],
        attrs={'units': ''},
    )
    try:
        numpy_array = get_numpy_array(array, ['y'])
    except ValueError:
        pass
    except Exception as err:
        raise err
    else:
        raise AssertionError('Expected ValueError but no error was raised')


def test_get_numpy_array_invalid_dimension_collected_by_asterisk():
    array = DataArray(
        np.random.randn(2),
        dims=['sheep'],
        attrs={'units': ''},
    )
    numpy_array = get_numpy_array(array, ['*'])
    assert numpy_array.shape == (2,)
    assert np.all(numpy_array == array.values)
    assert np.byte_bounds(numpy_array) == np.byte_bounds(array.values)
    assert numpy_array.base is array.values


def test_get_numpy_array_dimension_not_listed_raises_value_error():
    array = DataArray(
        np.random.randn(2),
        dims=['z'],
        attrs={'units': ''},
    )
    try:
        numpy_array = get_numpy_array(array, ['y'])
    except ValueError:
        pass
    except Exception as err:
        raise err
    else:
        raise AssertionError('Expected ValueError but no error was raised')


def test_get_numpy_array_no_dimensions_listed_raises_value_error():
    array = DataArray(
        np.random.randn(2),
        dims=['z'],
        attrs={'units': ''},
    )
    try:
        numpy_array = get_numpy_array(array, [])
    except ValueError:
        pass
    except Exception as err:
        raise err
    else:
        raise AssertionError('Expected ValueError but no error was raised')


def test_get_numpy_array_multiple_dims_on_same_direction():
    try:
        set_dimension_names(x=['lon'])
        array = DataArray(
            np.random.randn(2, 3),
            dims=['x', 'lon'],
            attrs={'units': ''},
        )
        try:
            numpy_array = get_numpy_array(array, ['x', 'y'])
        except ValueError:
            pass
        except Exception as err:
            raise err
        else:
            raise AssertionError('Expected ValueError but no error was raised')
    finally:
        set_dimension_names(x=[], y=[], z=[])


def test_get_numpy_array_not_enough_out_dims():
    array = DataArray(
        np.random.randn(2, 3),
        dims=['x', 'y'],
        attrs={'units': ''},
    )
    try:
        numpy_array = get_numpy_array(array, ['x'])
    except ValueError:
        pass
    except Exception as err:
        raise err
    else:
        raise AssertionError('Expected ValueError but no error was raised')


def test_get_numpy_array_asterisk_creates_new_dim():
    array = DataArray(
        np.random.randn(2),
        dims=['x'],
        attrs={'units': ''},
    )
    numpy_array = get_numpy_array(array, ['x', '*'])
    assert numpy_array.shape == (2, 1)
    assert np.all(numpy_array[:, 0] == array.values)
    assert np.byte_bounds(numpy_array) == np.byte_bounds(array.values)
    assert numpy_array.base is array.values


def test_get_numpy_array_asterisk_creates_new_dim_reversed():
    array = DataArray(
        np.random.randn(2),
        dims=['x'],
        attrs={'units': ''},
    )
    numpy_array = get_numpy_array(array, ['*', 'x'])
    assert numpy_array.shape == (1, 2)
    assert np.all(numpy_array[0, :] == array.values)
    assert np.byte_bounds(numpy_array) == np.byte_bounds(array.values)
    assert numpy_array.base is array.values


def test_get_numpy_array_asterisk_flattens():
    array = DataArray(
        np.random.randn(2, 3),
        dims=['y', 'z'],
        attrs={'units': ''},
    )
    numpy_array = get_numpy_array(array, ['*'])
    assert numpy_array.shape == (6,)
    assert np.all(numpy_array.reshape((2, 3)) == array.values)
    assert np.byte_bounds(numpy_array) == np.byte_bounds(array.values)
    assert numpy_array.base is array.values


def test_get_numpy_array_complicated_asterisk():
    array = DataArray(
        np.random.randn(2, 3, 4, 5),
        dims=['x', 'h', 'y', 'q'],
        attrs={'units': ''}
    )
    numpy_array = get_numpy_array(array, ['*', 'x', 'y'])
    for i in range(2):
        for j in range(4):
            assert np.allclose(numpy_array[:, i, j], array.values[i, :, j, :].flatten())
    # copying may take place in this case, so no more asserts


def test_get_numpy_array_zyx_to_starz_doesnt_copy():
    array = DataArray(
        np.random.randn(2, 3, 4),
        dims=['z', 'y', 'x'],
        attrs={'units': ''}
    )
    original_array = array.values
    numpy_array = get_numpy_array(array, ['*', 'z'])
    for i in range(2):
        assert np.all(numpy_array[:, i] == array.values[i, :, :].flatten())
    assert original_array is array.values
    assert np.byte_bounds(numpy_array) == np.byte_bounds(array.values)
    assert numpy_array.base is array.values


def test_restore_dimensions_complicated_asterisk():
    array = DataArray(
        np.random.randn(2, 3, 4, 5),
        dims=['x', 'h', 'y', 'q'],
        attrs={'units': ''}
    )
    numpy_array = get_numpy_array(array, ['*', 'x', 'y'])
    restored_array = restore_dimensions(
        numpy_array, from_dims=['*', 'x', 'y'], result_like=array)
    assert np.all(restored_array.values == array.values)
    assert len(restored_array.attrs) == 0


def test_restore_dimensions_transpose_alpha_beta():
    array = DataArray(
        np.random.randn(2, 3),
        dims=['alpha', 'beta'],
        attrs={'units': ''}
    )
    numpy_array = get_numpy_array(array, ['beta', 'alpha'])
    restored_array = restore_dimensions(
        numpy_array, from_dims=['beta', 'alpha'], result_like=array)
    assert np.all(restored_array.values == array.values)
    assert len(restored_array.attrs) == 0


def test_restore_dimensions_starz_to_zyx():
    array = DataArray(
        np.random.randn(2, 3, 4),
        dims=['z', 'y', 'x'],
        attrs={'units': ''}
    )
    numpy_array = get_numpy_array(array, ['*', 'z'])
    restored_array = restore_dimensions(
        numpy_array, from_dims=['*', 'z'], result_like=array)
    assert np.all(restored_array.values == array.values)
    assert len(restored_array.attrs) == 0


def test_restore_dimensions_starz_to_zalphabeta():
    array = DataArray(
        np.random.randn(2, 3, 4),
        dims=['z', 'alpha', 'beta'],
        attrs={'units': ''}
    )
    numpy_array = get_numpy_array(array, ['*', 'z'])
    restored_array = restore_dimensions(
        numpy_array, from_dims=['*', 'z'], result_like=array)
    assert np.all(restored_array.values == array.values)
    assert len(restored_array.attrs) == 0


def test_restore_dimensions_starz_to_zyx():
    array = DataArray(
        np.random.randn(2, 3, 4),
        dims=['z', 'y', 'x'],
        attrs={'units': ''}
    )
    numpy_array = get_numpy_array(array, ['*', 'z'])
    restored_array = restore_dimensions(
        numpy_array, from_dims=['*', 'z'], result_like=array)
    assert np.all(restored_array.values == array.values)
    assert len(restored_array.attrs) == 0


def test_restore_dimensions_starz_to_zyx_has_no_attrs():
    array = DataArray(
        np.random.randn(2, 3, 4),
        dims=['z', 'y', 'x'],
        attrs={'units': ''}
    )
    numpy_array = get_numpy_array(array, ['*', 'z'])
    restored_array = restore_dimensions(
        numpy_array, from_dims=['*', 'z'], result_like=array)
    assert len(restored_array.attrs) == 0


def test_restore_dimensions_starz_to_zyx_doesnt_copy():
    array = DataArray(
        np.random.randn(2, 3, 4),
        dims=['z', 'y', 'x'],
        attrs={'units': ''}
    )
    numpy_array = get_numpy_array(array, ['*', 'z'])
    restored_array = restore_dimensions(
        numpy_array, from_dims=['*', 'z'], result_like=array)
    assert np.byte_bounds(restored_array.values) == np.byte_bounds(
        array.values)
    assert restored_array.values.base is array.values


def test_restore_dimensions_starz_to_zyx_with_attrs():
    array = DataArray(
        np.random.randn(2, 3, 4),
        dims=['z', 'y', 'x'],
        attrs={'units': ''}
    )
    numpy_array = get_numpy_array(array, ['*', 'z'])
    restored_array = restore_dimensions(
        numpy_array, from_dims=['*', 'z'], result_like=array, result_attrs={'units': 'K'})
    assert np.all(restored_array.values == array.values)
    assert len(restored_array.attrs) == 1
    assert 'units' in restored_array.attrs
    assert restored_array.attrs['units'] == 'K'


def test_restore_dimensions_3d_reverse():
    array = DataArray(
        np.random.randn(2, 3, 4),
        dims=['z', 'y', 'x'],
        attrs={'units': ''}
    )
    numpy_array = get_numpy_array(array, ['x', 'y', 'z'])
    restored_array = restore_dimensions(
        numpy_array, from_dims=['x', 'y', 'z'], result_like=array)
    assert np.all(restored_array.values == array.values)
    assert len(restored_array.attrs) == 0
    assert np.byte_bounds(restored_array.values) == np.byte_bounds(
        array.values)
    assert restored_array.values.base is array.values


def test_restore_dimensions_1d_flatten():
    array = DataArray(
        np.random.randn(2),
        dims=['z'],
        attrs={'units': ''}
    )
    numpy_array = get_numpy_array(array, ['*'])
    restored_array = restore_dimensions(
        numpy_array, from_dims=['*'], result_like=array)
    assert np.all(restored_array.values == array.values)
    assert len(restored_array.attrs) == 0
    assert np.byte_bounds(restored_array.values) == np.byte_bounds(
        array.values)
    assert restored_array.values.base is array.values


def test_restore_dimensions_2d_flatten():
    array = DataArray(
        np.random.randn(2, 3),
        dims=['z', 'y'],
        attrs={'units': ''}
    )
    numpy_array = get_numpy_array(array, ['*'])
    restored_array = restore_dimensions(
        numpy_array, from_dims=['*'], result_like=array)
    assert np.all(restored_array.values == array.values)
    assert len(restored_array.attrs) == 0
    assert np.byte_bounds(restored_array.values) == np.byte_bounds(
        array.values)
    assert restored_array.values.base is array.values


def test_restore_dimensions_removes_dummy_axes():
    array = DataArray(
        np.random.randn(2),
        dims=['z'],
        attrs={'units': ''}
    )
    numpy_array = get_numpy_array(array, ['x', 'y', 'z'])
    restored_array = restore_dimensions(
        numpy_array, from_dims=['x', 'y', 'z'], result_like=array)
    assert np.all(restored_array.values == array.values)
    assert len(restored_array.attrs) == 0
    assert np.byte_bounds(restored_array.values) == np.byte_bounds(
        array.values)
    assert restored_array.values.base is array.values


class GetNumpyArraysWithPropertiesTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        set_dimension_names(x=(), y=(), z=())

    def test_returns_numpy_array(self):
        T_array = np.zeros([2, 3, 4], dtype=np.float64) + 280.
        property_dictionary = {
            'air_temperature': {
                'units': 'degK',
                'dims': ['x', 'y', 'z'],
            },
        }
        state = {
            'air_temperature': DataArray(
                T_array,
                dims=['x', 'y', 'z'],
                attrs={'units': 'degK'},
            ),
        }
        return_value = get_numpy_arrays_with_properties(state, property_dictionary)
        assert isinstance(return_value, dict)
        assert len(return_value.keys()) == 1
        assert isinstance(return_value['air_temperature'], np.ndarray)
        assert np.byte_bounds(return_value['air_temperature']) == np.byte_bounds(
            T_array)
        assert return_value['air_temperature'].base is T_array

    def test_returns_scalar_array(self):
        T_array = np.array(0.)
        property_dictionary = {
            'air_temperature': {
                'units': 'degK',
                'dims': [],
            },
        }
        state = {
            'air_temperature': DataArray(
                T_array,
                dims=[],
                attrs={'units': 'degK'},
            ),
        }
        return_value = get_numpy_arrays_with_properties(state, property_dictionary)
        assert isinstance(return_value, dict)
        assert len(return_value.keys()) == 1
        assert isinstance(return_value['air_temperature'], np.ndarray)
        assert np.byte_bounds(return_value['air_temperature']) == np.byte_bounds(
            T_array)

    def test_scalar_becomes_multidimensional_array(self):
        T_array = np.array(0.)
        property_dictionary = {
            'air_temperature': {
                'units': 'degK',
                'dims': ['z'],
            },
        }
        state = {
            'air_temperature': DataArray(
                T_array,
                dims=[],
                attrs={'units': 'degK'},
            ),
        }
        return_value = get_numpy_arrays_with_properties(state, property_dictionary)
        assert isinstance(return_value, dict)
        assert len(return_value.keys()) == 1
        assert isinstance(return_value['air_temperature'], np.ndarray)
        assert len(return_value['air_temperature'].shape) == 1
        assert np.byte_bounds(return_value['air_temperature']) == np.byte_bounds(
            T_array)
        assert return_value['air_temperature'].base is T_array

    def test_collects_wildcard_dimension(self):
        set_dimension_names(z=['mid_levels'])
        T_array = np.zeros([2, 3, 4], dtype=np.float64) + 280.
        property_dictionary = {
            'air_temperature': {
                'units': 'degK',
                'dims': ['x', 'y', 'z'],
            },
        }
        state = {
            'air_temperature': DataArray(
                T_array,
                dims=['x', 'y', 'mid_levels'],
                attrs={'units': 'degK'},
            ),
        }
        return_value = get_numpy_arrays_with_properties(state, property_dictionary)
        assert isinstance(return_value, dict)
        assert len(return_value.keys()) == 1
        assert isinstance(return_value['air_temperature'], np.ndarray)
        assert np.byte_bounds(return_value['air_temperature']) == np.byte_bounds(
            T_array)
        assert return_value['air_temperature'].base is T_array
        assert return_value['air_temperature'].shape == (2, 3, 4)

    def test_raises_on_missing_explicit_dimension(self):
        set_dimension_names(z=['mid_levels'])
        T_array = np.zeros([2, 3, 4], dtype=np.float64) + 280.
        property_dictionary = {
            'air_temperature': {
                'units': 'degK',
                'dims': ['x', 'y', 'mid_levels'],
            },
        }
        state = {
            'air_temperature': DataArray(
                T_array,
                dims=['x', 'y', 'z'],
                attrs={'units': 'degK'},
            ),
        }
        try:
            return_value = get_numpy_arrays_with_properties(state, property_dictionary)
        except InvalidStateException:
            pass
        else:
            raise AssertionError('should have raised InvalidStateException')

    def test_creates_length_1_dimensions(self):
        T_array = np.zeros([4], dtype=np.float64) + 280.
        property_dictionary = {
            'air_temperature': {
                'dims': ['x', 'y', 'z'],
                'units': 'degK',
            },
        }
        state = {
            'air_temperature': DataArray(
                T_array,
                dims=['z'],
                attrs={'units': 'degK'},
            ),
        }
        return_value = get_numpy_arrays_with_properties(state, property_dictionary)
        assert isinstance(return_value, dict)
        assert len(return_value.keys()) == 1
        assert isinstance(return_value['air_temperature'], np.ndarray)
        assert np.byte_bounds(
            return_value['air_temperature']) == np.byte_bounds(
            T_array)
        assert return_value['air_temperature'].base is T_array
        assert return_value['air_temperature'].shape == (1, 1, 4)

    def test_only_requested_properties_are_returned(self):
        property_dictionary = {
            'air_temperature': {
                'dims': ['x', 'y', 'z'],
                'units': 'degK',
            },
        }
        state = {
            'air_temperature': DataArray(
                np.zeros([4], dtype=np.float64),
                dims=['z'],
                attrs={'units': 'degK'},
            ),
            'air_pressure': DataArray(
                np.zeros([2,2,4], dtype=np.float64),
                dims=['x', 'y', 'z'],
                attrs={'units': 'Pa'},
            )
        }
        return_value = get_numpy_arrays_with_properties(state, property_dictionary)
        assert isinstance(return_value, dict)
        assert len(return_value.keys()) == 1
        assert 'air_temperature' in return_value.keys()

    def test_all_requested_properties_are_returned(self):
        property_dictionary = {
            'air_temperature': {
                'dims': ['x', 'y', 'z'],
                'units': 'degK',
            },
            'air_pressure': {
                'dims': ['x', 'y', 'z'],
                'units': 'Pa',
            },
        }
        state = {
            'air_temperature': DataArray(
                np.zeros([4], dtype=np.float64),
                dims=['z'],
                attrs={'units': 'degK'},
            ),
            'air_pressure': DataArray(
                np.zeros([2,2,4], dtype=np.float64),
                dims=['x', 'y', 'z'],
                attrs={'units': 'Pa'},
            ),
            'eastward_wind': DataArray(
                np.zeros([2,2,4], dtype=np.float64),
                attrs={'units': 'm/s'}
            ),
        }
        return_value = get_numpy_arrays_with_properties(state, property_dictionary)
        assert isinstance(return_value, dict)
        assert len(return_value.keys()) == 2
        assert 'air_temperature' in return_value.keys()
        assert 'air_pressure' in return_value.keys()
        assert np.all(return_value['air_temperature'] == 0.)
        assert np.all(return_value['air_pressure'] == 0.)

    def test_raises_exception_on_missing_quantity(self):
        property_dictionary = {
            'air_temperature': {
                'dims': ['x', 'y', 'z'],
                'units': 'degK',
            },
            'air_pressure': {
                'dims': ['x', 'y', 'z'],
                'units': 'Pa',
            },
        }
        state = {
            'air_temperature': DataArray(
                np.zeros([4], dtype=np.float64),
                dims=['z'],
                attrs={'units': 'degK'},
            ),
            'eastward_wind': DataArray(
                np.zeros([2,2,4], dtype=np.float64),
                attrs={'units': 'm/s'}
            ),
        }
        try:
            get_numpy_arrays_with_properties(state, property_dictionary)
        except InvalidStateException:
            pass
        else:
            raise AssertionError('should have raised InvalidStateException')

    def test_converts_units(self):
        property_dictionary = {
            'air_temperature': {
                'dims': ['x', 'y', 'z'],
                'units': 'degC',
            },
        }
        state = {
            'air_temperature': DataArray(
                np.zeros([4], dtype=np.float64),
                dims=['z'],
                attrs={'units': 'degK'},
            ),
        }
        return_value = get_numpy_arrays_with_properties(state, property_dictionary)
        assert isinstance(return_value, dict)
        assert len(return_value.keys()) == 1
        assert 'air_temperature' in return_value.keys()
        assert np.all(return_value['air_temperature'] == -273.15)

    def test_unit_conversion_doesnt_modify_input(self):
        property_dictionary = {
            'air_temperature': {
                'dims': ['x', 'y', 'z'],
                'units': 'degC',
            },
        }
        state = {
            'air_temperature': DataArray(
                np.zeros([4], dtype=np.float64),
                dims=['z'],
                attrs={'units': 'degK'},
            ),
        }
        return_value = get_numpy_arrays_with_properties(state, property_dictionary)
        assert np.all(state['air_temperature'].values == 0.)
        assert state['air_temperature'].attrs['units'] is 'degK'

    def test_raises_if_units_property_undefined(self):
        property_dictionary = {
            'air_temperature': {
                'dims': ['x', 'y', 'z'],
            },
        }
        state = {
            'air_temperature': DataArray(
                np.zeros([4], dtype=np.float64),
                dims=['z'],
                attrs={'units': 'degK'},
            ),
        }
        try:
            return_value = get_numpy_arrays_with_properties(state, property_dictionary)
        except ValueError:
            pass
        else:
            raise AssertionError('should have raised ValueError')

    def test_raises_if_state_quantity_units_undefined(self):
        property_dictionary = {
            'air_temperature': {
                'dims': ['x', 'y', 'z'],
                'units': 'degK',
            },
        }
        state = {
            'air_temperature': DataArray(
                np.zeros([4], dtype=np.float64),
                dims=['z'],
            ),
        }
        try:
            return_value = get_numpy_arrays_with_properties(state, property_dictionary)
        except InvalidStateException:
            pass
        else:
            raise AssertionError('should have raised InvalidStateException')

    def test_raises_if_no_units_undefined(self):
        property_dictionary = {
            'air_temperature': {
                'dims': ['x', 'y', 'z'],
            },
        }
        state = {
            'air_temperature': DataArray(
                np.zeros([4], dtype=np.float64),
                dims=['z'],
            ),
        }
        try:
            return_value = get_numpy_arrays_with_properties(state, property_dictionary)
        except ValueError:
            pass
        except InvalidStateException:
            pass
        else:
            raise AssertionError('should have raised ValueError or InvalidStateException')

    def test_raises_if_dims_property_not_specified(self):
        property_dictionary = {
            'air_temperature': {
                'units': 'degK',
            },
        }
        state = {
            'air_temperature': DataArray(
                np.zeros([4], dtype=np.float64),
                dims=['z'],
                attrs={'units': 'degK'},
            ),
        }
        try:
            get_numpy_arrays_with_properties(state, property_dictionary)
        except ValueError:
            pass
        else:
            raise AssertionError('should have raised ValueError')

    def test_dims_like_accepts_valid_case(self):
        set_dimension_names(z=['mid_levels', 'full_levels'])
        property_dictionary = {
            'air_temperature': {
                'dims': ['x', 'y', 'mid_levels'],
                'units': 'degK',
            },
            'air_pressure': {
                'dims': ['x', 'y', 'full_levels'],
                'units': 'Pa',
                'match_dims_like': 'air_temperature'
            },
        }
        state = {
            'air_temperature': DataArray(
                np.zeros([4], dtype=np.float64),
                dims=['z'],
                attrs={'units': 'degK'},
            ),
            'air_pressure': DataArray(
                np.zeros([2,2,4], dtype=np.float64),
                attrs={'units': 'Pa'}
            ),
        }
        return_value = get_numpy_arrays_with_properties(state, property_dictionary)
        assert isinstance(return_value, dict)
        assert len(return_value.keys()) == 2
        assert 'air_temperature' in return_value.keys()
        assert 'air_pressure' in return_value.keys()



if __name__ == '__main__':
    pytest.main([__file__])

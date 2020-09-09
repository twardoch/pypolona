
#include "nuitka/prelude.h"

// Sentinel PyObject to be used for all our call iterator endings. It will
// become a PyCObject pointing to NULL. It's address is unique, and that's
// enough for us to use it as sentinel value.
PyObject *_sentinel_value = NULL;

PyObject *const_int_0;
PyObject *const_int_pos_1;
PyObject *const_str_empty;
PyObject *const_dict_empty;
PyObject *const_tuple_empty;
PyObject *const_str_plain_rb;
PyObject *const_str_plain_int;
PyObject *const_str_plain_len;
PyObject *const_str_plain_sum;
PyObject *const_str_plain_dict;
PyObject *const_str_plain_iter;
PyObject *const_str_plain_keys;
PyObject *const_str_plain_long;
PyObject *const_str_plain_name;
PyObject *const_str_plain_open;
PyObject *const_str_plain_read;
PyObject *const_str_plain_repr;
PyObject *const_str_plain_site;
PyObject *const_str_plain_type;
PyObject *const_str_plain_level;
PyObject *const_str_plain_range;
PyObject *const_str_plain_tuple;
PyObject *const_str_plain_format;
PyObject *const_str_plain_locals;
PyObject *const_str_plain_xrange;
PyObject *const_str_plain___all__;
PyObject *const_str_plain___cmp__;
PyObject *const_str_plain___doc__;
PyObject *const_str_plain_compile;
PyObject *const_str_plain_globals;
PyObject *const_str_plain_inspect;
PyObject *const_str_plain___dict__;
PyObject *const_str_plain___exit__;
PyObject *const_str_plain___file__;
PyObject *const_str_plain___iter__;
PyObject *const_str_plain___main__;
PyObject *const_str_plain___name__;
PyObject *const_str_plain___path__;
PyObject *const_str_plain_exc_type;
PyObject *const_str_plain_fromlist;
PyObject *const_str_plain___class__;
PyObject *const_str_plain___enter__;
PyObject *const_str_plain_bytearray;
PyObject *const_str_plain_exc_value;
PyObject *const_str_plain___import__;
PyObject *const_str_plain___module__;
PyObject *const_str_plain___delattr__;
PyObject *const_str_plain___getattr__;
PyObject *const_str_plain___package__;
PyObject *const_str_plain___setattr__;
PyObject *const_str_plain_classmethod;
PyObject *const_str_plain___builtins__;
PyObject *const_str_plain___internal__;
PyObject *const_str_plain_staticmethod;
PyObject *const_str_plain___metaclass__;
PyObject *const_str_plain_exc_traceback;
PyObject *const_str_digest_16e7c1393f9b82a0983ae3fdc6f2027b;
PyObject *const_str_digest_25731c733fd74e8333aa29126ce85686;
PyObject *const_str_digest_45e4dde2057b0bf276d6a84f4c917d27;
PyObject *const_str_digest_5cf0452130fc4fd9d925cac8f015f9d1;
PyObject *const_str_digest_7bb187c562694df4ba2daaaf74308c83;
PyObject *const_str_digest_9816e8d1552296af90d250823c964059;
PyObject *const_str_digest_adc474dd61fbd736d69c1bac5d9712e0;
PyObject *const_tuple_348b0f87df4fe8a3ab054c1f070c95b2_tuple;

static void _createGlobalConstants( void )
{
    NUITKA_MAY_BE_UNUSED PyObject *exception_type, *exception_value;
    NUITKA_MAY_BE_UNUSED PyTracebackObject *exception_tb;

#ifdef _MSC_VER
    // Prevent unused warnings in case of simple programs, the attribute
    // NUITKA_MAY_BE_UNUSED doesn't work for MSVC.
    (void *)exception_type; (void *)exception_value; (void *)exception_tb;
#endif

    const_int_0 = PyInt_FromLong( 0l );
    const_int_pos_1 = PyInt_FromLong( 1l );
    const_str_empty = UNSTREAM_STRING( &constant_bin[ 0 ], 0, 0 );
    const_dict_empty = _PyDict_NewPresized( 0 );
    assert( PyDict_Size( const_dict_empty ) == 0 );
    const_tuple_empty = PyTuple_New( 0 );
    const_str_plain_rb = UNSTREAM_STRING( &constant_bin[ 2126 ], 2, 1 );
    const_str_plain_int = UNSTREAM_STRING( &constant_bin[ 138 ], 3, 1 );
    const_str_plain_len = UNSTREAM_STRING( &constant_bin[ 2128 ], 3, 1 );
    const_str_plain_sum = UNSTREAM_STRING( &constant_bin[ 2131 ], 3, 1 );
    const_str_plain_dict = UNSTREAM_STRING( &constant_bin[ 1086 ], 4, 1 );
    const_str_plain_iter = UNSTREAM_STRING( &constant_bin[ 2134 ], 4, 1 );
    const_str_plain_keys = UNSTREAM_STRING( &constant_bin[ 2138 ], 4, 1 );
    const_str_plain_long = UNSTREAM_STRING( &constant_bin[ 2142 ], 4, 1 );
    const_str_plain_name = UNSTREAM_STRING( &constant_bin[ 1284 ], 4, 1 );
    const_str_plain_open = UNSTREAM_STRING( &constant_bin[ 2146 ], 4, 1 );
    const_str_plain_read = UNSTREAM_STRING( &constant_bin[ 2150 ], 4, 1 );
    const_str_plain_repr = UNSTREAM_STRING( &constant_bin[ 2154 ], 4, 1 );
    const_str_plain_site = UNSTREAM_STRING( &constant_bin[ 2039 ], 4, 1 );
    const_str_plain_type = UNSTREAM_STRING( &constant_bin[ 2158 ], 4, 1 );
    const_str_plain_level = UNSTREAM_STRING( &constant_bin[ 2162 ], 5, 1 );
    const_str_plain_range = UNSTREAM_STRING( &constant_bin[ 2167 ], 5, 1 );
    const_str_plain_tuple = UNSTREAM_STRING( &constant_bin[ 2172 ], 5, 1 );
    const_str_plain_format = UNSTREAM_STRING( &constant_bin[ 116 ], 6, 1 );
    const_str_plain_locals = UNSTREAM_STRING( &constant_bin[ 2177 ], 6, 1 );
    const_str_plain_xrange = UNSTREAM_STRING( &constant_bin[ 2183 ], 6, 1 );
    const_str_plain___all__ = UNSTREAM_STRING( &constant_bin[ 2189 ], 7, 1 );
    const_str_plain___cmp__ = UNSTREAM_STRING( &constant_bin[ 2196 ], 7, 1 );
    const_str_plain___doc__ = UNSTREAM_STRING( &constant_bin[ 2203 ], 7, 1 );
    const_str_plain_compile = UNSTREAM_STRING( &constant_bin[ 2210 ], 7, 1 );
    const_str_plain_globals = UNSTREAM_STRING( &constant_bin[ 2217 ], 7, 1 );
    const_str_plain_inspect = UNSTREAM_STRING( &constant_bin[ 2224 ], 7, 1 );
    const_str_plain___dict__ = UNSTREAM_STRING( &constant_bin[ 2231 ], 8, 1 );
    const_str_plain___exit__ = UNSTREAM_STRING( &constant_bin[ 2239 ], 8, 1 );
    const_str_plain___file__ = UNSTREAM_STRING( &constant_bin[ 2247 ], 8, 1 );
    const_str_plain___iter__ = UNSTREAM_STRING( &constant_bin[ 2255 ], 8, 1 );
    const_str_plain___main__ = UNSTREAM_STRING( &constant_bin[ 1521 ], 8, 1 );
    const_str_plain___name__ = UNSTREAM_STRING( &constant_bin[ 2263 ], 8, 1 );
    const_str_plain___path__ = UNSTREAM_STRING( &constant_bin[ 2271 ], 8, 1 );
    const_str_plain_exc_type = UNSTREAM_STRING( &constant_bin[ 2279 ], 8, 1 );
    const_str_plain_fromlist = UNSTREAM_STRING( &constant_bin[ 2287 ], 8, 1 );
    const_str_plain___class__ = UNSTREAM_STRING( &constant_bin[ 2295 ], 9, 1 );
    const_str_plain___enter__ = UNSTREAM_STRING( &constant_bin[ 2304 ], 9, 1 );
    const_str_plain_bytearray = UNSTREAM_STRING( &constant_bin[ 2313 ], 9, 1 );
    const_str_plain_exc_value = UNSTREAM_STRING( &constant_bin[ 2322 ], 9, 1 );
    const_str_plain___import__ = UNSTREAM_STRING( &constant_bin[ 2331 ], 10, 1 );
    const_str_plain___module__ = UNSTREAM_STRING( &constant_bin[ 2341 ], 10, 1 );
    const_str_plain___delattr__ = UNSTREAM_STRING( &constant_bin[ 2351 ], 11, 1 );
    const_str_plain___getattr__ = UNSTREAM_STRING( &constant_bin[ 2362 ], 11, 1 );
    const_str_plain___package__ = UNSTREAM_STRING( &constant_bin[ 2373 ], 11, 1 );
    const_str_plain___setattr__ = UNSTREAM_STRING( &constant_bin[ 2384 ], 11, 1 );
    const_str_plain_classmethod = UNSTREAM_STRING( &constant_bin[ 2395 ], 11, 1 );
    const_str_plain___builtins__ = UNSTREAM_STRING( &constant_bin[ 2406 ], 12, 1 );
    const_str_plain___internal__ = UNSTREAM_STRING( &constant_bin[ 2418 ], 12, 1 );
    const_str_plain_staticmethod = UNSTREAM_STRING( &constant_bin[ 2430 ], 12, 1 );
    const_str_plain___metaclass__ = UNSTREAM_STRING( &constant_bin[ 2442 ], 13, 1 );
    const_str_plain_exc_traceback = UNSTREAM_STRING( &constant_bin[ 2455 ], 13, 1 );
    const_str_digest_16e7c1393f9b82a0983ae3fdc6f2027b = UNSTREAM_STRING( &constant_bin[ 2468 ], 99, 0 );
    const_str_digest_25731c733fd74e8333aa29126ce85686 = UNSTREAM_STRING( &constant_bin[ 2567 ], 2, 0 );
    const_str_digest_45e4dde2057b0bf276d6a84f4c917d27 = UNSTREAM_STRING( &constant_bin[ 2569 ], 7, 0 );
    const_str_digest_5cf0452130fc4fd9d925cac8f015f9d1 = UNSTREAM_STRING( &constant_bin[ 2576 ], 12, 0 );
    const_str_digest_7bb187c562694df4ba2daaaf74308c83 = UNSTREAM_STRING( &constant_bin[ 2588 ], 9, 0 );
    const_str_digest_9816e8d1552296af90d250823c964059 = UNSTREAM_STRING( &constant_bin[ 2597 ], 46, 0 );
    const_str_digest_adc474dd61fbd736d69c1bac5d9712e0 = UNSTREAM_STRING( &constant_bin[ 2643 ], 47, 0 );
    const_tuple_348b0f87df4fe8a3ab054c1f070c95b2_tuple = PyTuple_New( 3 );
    PyTuple_SET_ITEM( const_tuple_348b0f87df4fe8a3ab054c1f070c95b2_tuple, 0, (PyObject *)&PyFunction_Type ); Py_INCREF( (PyObject *)&PyFunction_Type );
    PyTuple_SET_ITEM( const_tuple_348b0f87df4fe8a3ab054c1f070c95b2_tuple, 1, (PyObject *)&PyCFunction_Type ); Py_INCREF( (PyObject *)&PyCFunction_Type );
    PyTuple_SET_ITEM( const_tuple_348b0f87df4fe8a3ab054c1f070c95b2_tuple, 2, (PyObject *)&PyMethod_Type ); Py_INCREF( (PyObject *)&PyMethod_Type );

#if _NUITKA_EXE
    /* Set the "sys.executable" path to the original CPython executable. */
    PySys_SetObject(
        (char *)"executable",
        const_str_digest_16e7c1393f9b82a0983ae3fdc6f2027b
    );
#endif
}

// In debug mode we can check that the constants were not tampered with in any
// given moment. We typically do it at program exit, but we can add extra calls
// for sanity.
#ifndef __NUITKA_NO_ASSERT__
void checkGlobalConstants( void )
{

}
#endif

void createGlobalConstants( void )
{
    if ( _sentinel_value == NULL )
    {
#if PYTHON_VERSION < 300
        _sentinel_value = PyCObject_FromVoidPtr( NULL, NULL );
#else
        // The NULL value is not allowed for a capsule, so use something else.
        _sentinel_value = PyCapsule_New( (void *)27, "sentinel", NULL );
#endif
        assert( _sentinel_value );

        _createGlobalConstants();
    }
}

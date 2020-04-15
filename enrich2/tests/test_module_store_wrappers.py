import os
from collections import OrderedDict as Od
import pandas as pd
from unittest import TestCase

from ..base.store_wrappers import HDFStore


class TestHDFStore(TestCase):
    def setUp(self):
        self.store = None
        self.path = ""
        self.data_dir = os.path.join(os.path.dirname(__file__), "data/hdfstore/")

    def tearDown(self):
        if self.store:
            self.store.close()
        if self.path:
            os.remove(self.path)

    def test_h5_file_init(self):
        self.store = HDFStore()
        self.assertEqual(self.store._store, None)
        self.assertFalse(self.store.is_open())
        with self.assertRaises(ValueError):
            self.store.is_empty()
        with self.assertRaises(ValueError):
            self.store.ensure_open()

    def test_h5_file_open_non_existing_file(self):
        self.path = os.path.join(self.data_dir, "test.h5")
        self.store = HDFStore(self.path, mode="a")
        self.store.ensure_open()
        self.assertTrue(self.store.is_open())
        self.assertTrue(self.store.is_empty())
        self.assertEqual(self.store.filename, self.path)

    def test_store_close(self):
        self.path = os.path.join(self.data_dir, "test.h5")
        self.store = HDFStore(self.path, mode="a")
        self.store.ensure_open()
        self.store.close()

        self.assertFalse(self.store.is_open())
        with self.assertRaises(ValueError):
            self.store.is_empty()
        self.assertEqual(self.store.filename, "")
        self.assertEqual(self.store._store, None)

    def test_open_write_mode(self):
        self.path = os.path.join(self.data_dir, "test.h5")
        data = pd.DataFrame({"count": [1, 2, 3]}, index=["AAA", "AAC", "AAG"])

        self.store = HDFStore(self.path, mode="a")
        self.store.put("test_table", data)
        self.assertTrue(self.store.is_open())
        self.assertFalse(self.store.is_empty())
        self.assertTrue(len(self.store.keys()) == 1)

        self.store.open(self.path, mode="w")
        self.assertTrue(self.store.is_open())
        self.assertTrue(self.store.is_empty())
        self.assertTrue(len(self.store.keys()) == 0)

    def test_put_places_new_data_correctly(self):
        self.path = os.path.join(self.data_dir, "test.h5")
        data = pd.DataFrame({"count": [1, 2, 3]}, index=["AAA", "AAC", "AAG"])

        self.store = HDFStore(self.path, mode="w")
        self.store.put("/test_table", data)
        result = self.store.get("/test_table")
        self.assertTrue(data.equals(result))

    def test_put_append_appends_correctly(self):
        self.path = os.path.join(self.data_dir, "test.h5")
        data = pd.DataFrame({"count": [1, 2, 3]}, index=["AAA", "AAC", "AAG"])

        self.store = HDFStore(self.path, mode="w")
        self.store.put("/test_table", data)
        self.store.put("/test_table", data, append=True)
        result = self.store.get("/test_table")
        expected = pd.DataFrame(
            {"count": [1, 2, 3, 1, 2, 3]},
            index=["AAA", "AAC", "AAG", "AAA", "AAC", "AAG"],
        )
        self.assertTrue(expected.equals(result))

    def test_put_overwrites_same_index(self):
        self.path = os.path.join(self.data_dir, "test.h5")
        data1 = pd.DataFrame({"count": [1, 2, 3]}, index=["AAA", "AAC", "AAG"])
        data2 = pd.DataFrame({"count": [4, 5, 6]}, index=["AAA", "AAC", "AAG"])

        self.store = HDFStore(self.path, mode="w")
        self.store.put("/test_table", data1)
        self.store.put("/test_table", data2, append=False)
        result = self.store.get("/test_table")
        self.assertTrue(data2.equals(result))

    def test_append_appends_correctly(self):
        self.path = os.path.join(self.data_dir, "test.h5")
        data = pd.DataFrame({"count": [1, 2, 3]}, index=["AAA", "AAC", "AAG"])

        self.store = HDFStore(self.path, mode="w")
        self.store.put("/test_table", data)
        self.store.append("/test_table", data)
        result = self.store.get("/test_table")
        expected = pd.DataFrame(
            {"count": [1, 2, 3, 1, 2, 3]},
            index=["AAA", "AAC", "AAG", "AAA", "AAC", "AAG"],
        )
        self.assertTrue(expected.equals(result))

    def test_remove_existing_key(self):
        self.path = os.path.join(self.data_dir, "test.h5")
        data = pd.DataFrame({"count": [1, 2, 3]}, index=["AAA", "AAC", "AAG"])

        self.store = HDFStore(self.path, mode="w")
        self.store.put("/test_table", data)
        self.store.remove("/test_table")
        with self.assertRaises(KeyError):
            self.store["/test_table"]

    def test_remove_existing_key_where_count_less_than_3(self):
        self.path = os.path.join(self.data_dir, "test.h5")
        data = pd.DataFrame({"count": [1, 2, 3]}, index=["AAA", "AAC", "AAG"])

        self.store = HDFStore(self.path, mode="w")
        self.store.put("/test_table", data)
        self.store.remove("/test_table", where="count<3")
        expected = pd.DataFrame({"count": [3]}, index=["AAG"])
        self.assertTrue(expected.equals(self.store.get("/test_table")))

    def test_remove_non_existant_key(self):
        self.path = os.path.join(self.data_dir, "test.h5")
        data = pd.DataFrame({"count": [1, 2, 3]}, index=["AAA", "AAC", "AAG"])

        self.store = HDFStore(self.path, mode="w")
        self.store.put("/test_table", data)
        with self.assertRaises(KeyError):
            self.store.remove("/foo_bar")

    def test_store_clear_deletes_all_data(self):
        self.path = os.path.join(self.data_dir, "test.h5")
        data = pd.DataFrame({"count": [1, 2, 3]}, index=["AAA", "AAC", "AAG"])

        self.store = HDFStore(self.path, mode="w")
        self.store.put("/test_table", data)
        self.store.clear()

        self.assertNotEqual(self.store._store, None)
        self.assertTrue(self.store.is_empty())
        self.assertTrue(self.store.is_open())

    def test_check_key_in_store(self):
        self.path = os.path.join(self.data_dir, "test.h5")
        data = pd.DataFrame({"count": [1, 2, 3]}, index=["AAA", "AAC", "AAG"])

        self.store = HDFStore(self.path, mode="w")
        self.store.put("/test_table", data)
        self.assertTrue(self.store.check("/test_table"))
        self.assertFalse(self.store.check("/foo_bar"))

    def test_get_key_from_store(self):
        self.path = os.path.join(self.data_dir, "test.h5")
        data = pd.DataFrame({"count": [1, 2, 3]}, index=["AAA", "AAC", "AAG"])

        self.store = HDFStore(self.path, mode="w")
        self.store.put("/test_table", data)
        result = self.store.get("/test_table")
        self.assertTrue(data.equals(result))

    def test_error_get_key_from_store(self):
        self.path = os.path.join(self.data_dir, "test.h5")
        self.store = HDFStore(self.path, mode="w")
        with self.assertRaises(KeyError):
            self.store.get("/test_table")

    def test_set_new_metadata(self):
        self.path = os.path.join(self.data_dir, "test.h5")
        data = pd.DataFrame({"count": [1, 2, 3]}, index=["AAA", "AAC", "AAG"])
        metadata = {"hello": "world"}

        self.store = HDFStore(self.path, mode="w")
        self.store.put("/test_table", data)
        self.store.set_metadata("/test_table", metadata, update=False)

        result = self.store.get_metadata("/test_table")
        self.assertTrue(metadata == result)

    def test_set_existing_metadata_update_true(self):
        self.path = os.path.join(self.data_dir, "test.h5")
        data = pd.DataFrame({"count": [1, 2, 3]}, index=["AAA", "AAC", "AAG"])
        metadata1 = {"hello": "world"}
        metadata2 = {"foo": "bar"}

        self.store = HDFStore(self.path, mode="w")
        self.store.put("/test_table", data)

        self.store.set_metadata("/test_table", metadata1, update=False)
        result = self.store.get_metadata("/test_table")
        self.assertTrue(metadata1 == result)

        self.store.set_metadata("/test_table", metadata2, update=True)
        result = self.store.get_metadata("/test_table")
        metadata1.update(metadata2)
        self.assertTrue(result == metadata1)

    def test_set_existing_metadata_update_false(self):
        self.path = os.path.join(self.data_dir, "test.h5")
        data = pd.DataFrame({"count": [1, 2, 3]}, index=["AAA", "AAC", "AAG"])
        metadata1 = {"hello": "world"}
        metadata2 = {"foo": "bar"}

        self.store = HDFStore(self.path, mode="w")
        self.store.put("/test_table", data)

        self.store.set_metadata("/test_table", metadata1, update=False)
        result = self.store.get_metadata("/test_table")
        self.assertTrue(metadata1 == result)

        self.store.set_metadata("/test_table", metadata2, update=False)
        result = self.store.get_metadata("/test_table")
        self.assertTrue(result == metadata2)

    def test_error_set_bad_type_metadata(self):
        self.path = os.path.join(self.data_dir, "test.h5")
        data = pd.DataFrame({"count": [1, 2, 3]}, index=["AAA", "AAC", "AAG"])
        metadata = []

        self.store = HDFStore(self.path, mode="w")
        self.store.put("/test_table", data)
        with self.assertRaises(TypeError):
            self.store.set_metadata("/test_table", metadata, update=False)

    def test_keyerror_set_metadata(self):
        self.path = os.path.join(self.data_dir, "test.h5")
        self.store = HDFStore(self.path, mode="w")
        with self.assertRaises(KeyError):
            self.store.set_metadata("/test_table", {}, update=False)

    def test_get_metadata_from_key(self):
        self.path = os.path.join(self.data_dir, "test.h5")
        data = pd.DataFrame({"count": [1, 2, 3]}, index=["AAA", "AAC", "AAG"])
        metadata = {"hello": "world"}

        self.store = HDFStore(self.path, mode="w")
        self.store.put("/test_table", data)

        self.store.set_metadata("/test_table", metadata, update=False)
        result = self.store.get_metadata("/test_table")
        self.assertTrue(metadata == result)

    def test_error_get_metadata_from_key(self):
        self.path = os.path.join(self.data_dir, "test.h5")
        self.store = HDFStore(self.path, mode="w")
        with self.assertRaises(KeyError):
            self.store.get_metadata("/test_table")

    def test_select_using_where(self):
        self.path = os.path.join(self.data_dir, "test.h5")
        data = pd.DataFrame({"count": [1, 2, 3]}, index=["AAA", "AAC", "AAG"])

        self.store = HDFStore(self.path, mode="w")
        self.store.put("/test_table", data)

        result = self.store.select("/test_table", where="count<3")
        expected = pd.DataFrame({"count": [1, 2]}, index=["AAA", "AAC"])
        self.assertTrue(result.equals(expected))

        result = self.store.select("/test_table", where="count>4")
        self.assertTrue(result.empty)

    def test_select_using_columns(self):
        self.path = os.path.join(self.data_dir, "test.h5")
        data = pd.DataFrame(
            {"count": [1, 2, 3], "score": [0.1, 0.2, 0.3]}, index=["AAA", "AAC", "AAG"]
        )

        self.store = HDFStore(self.path, mode="w")
        self.store.put("/test_table", data)

        result = self.store.select("/test_table", where="count<3", columns=["score"])
        expected = pd.DataFrame({"score": [0.1, 0.2]}, index=["AAA", "AAC"])
        self.assertTrue(result.equals(expected))

    def test_error_select_using_wherecolumns(self):
        self.path = os.path.join(self.data_dir, "test.h5")
        data = pd.DataFrame(
            {"count": [1, 2, 3], "score": [0.1, 0.2, 0.3]}, index=["AAA", "AAC", "AAG"]
        )

        self.store = HDFStore(self.path, mode="w")
        self.store.put("/test_table", data)

        with self.assertRaises(ValueError):
            self.store.select("/test_table", where='columns=["score"] & count<3')

    def test_select_with_chunks(self):
        self.path = os.path.join(self.data_dir, "test.h5")
        data = pd.DataFrame(
            {"count": [1, 2, 3], "score": [0.1, 0.2, 0.3]}, index=["AAA", "AAC", "AAG"]
        )

        self.store = HDFStore(self.path, mode="w")
        self.store.put("/test_table", data)

        result = self.store.select(
            "/test_table", where="count<3", columns=["score"], chunk=True
        )
        expected = pd.DataFrame({"score": [0.1, 0.2]}, index=["AAA", "AAC"])
        for df in result:
            self.assertTrue(df.equals(expected))

    def test_valueerror_use_chunks_with_where_columns(self):
        self.path = os.path.join(self.data_dir, "test.h5")
        data = pd.DataFrame(
            {"count": [1, 2, 3], "score": [0.1, 0.2, 0.3]}, index=["AAA", "AAC", "AAG"]
        )

        self.store = HDFStore(self.path, mode="w")
        self.store.put("/test_table", data)

        with self.assertRaises(ValueError):
            self.store.select(
                "/test_table", where='columns=["count"] & count<3', chunk=True
            )
        with self.assertRaises(ValueError):
            self.store.select(
                "/test_table", where='column=["count"] & count<3', chunk=True
            )

    def test_select_columns(self):
        self.path = os.path.join(self.data_dir, "test.h5")
        data = pd.DataFrame(
            {"count": [1, 2, 3], "score": [0.1, 0.2, 0.3]}, index=["AAA", "AAC", "AAG"]
        )

        self.store = HDFStore(self.path, mode="w")
        self.store.put("/test_table", data)

        result = self.store.select_column("/test_table", "score")
        expected = pd.Series([0.1, 0.2, 0.3])
        self.assertTrue(result.equals(expected))

    def test_select_multiple_using_where(self):
        self.path = os.path.join(self.data_dir, "test.h5")
        data1 = pd.DataFrame(
            {"count1": [1, 2, 3], "score1": [0.1, 0.2, 0.3]},
            index=["AAA", "AAC", "AAG"],
        )
        data2 = pd.DataFrame(
            {"count2": [4, 5, 6], "score2": [0.4, 0.5, 0.6]},
            index=["AAA", "AAC", "AAG"],
        )

        self.store = HDFStore(self.path, mode="w")
        self.store.put("/test_table_1", data1)
        self.store.put("/test_table_2", data2)

        result = self.store.select_as_multiple(
            keys=["/test_table_1", "/test_table_2"], where="count1=2"
        )
        data = Od(count1=[2], score1=[0.2], count2=[5], score2=[0.5])
        expected = pd.DataFrame(data, index=["AAC"])
        self.assertTrue(result.equals(expected))

    def test_select_multiple_using_columns(self):
        self.path = os.path.join(self.data_dir, "test.h5")
        data1 = pd.DataFrame(
            {"count1": [1, 2, 3], "score1": [0.1, 0.2, 0.3]},
            index=["AAA", "AAC", "AAG"],
        )
        data2 = pd.DataFrame(
            {"count2": [4, 5, 6], "score2": [0.4, 0.5, 0.6]},
            index=["AAA", "AAC", "AAG"],
        )

        self.store = HDFStore(self.path, mode="w")
        self.store.put("/test_table_1", data1)
        self.store.put("/test_table_2", data2)

        result = self.store.select_as_multiple(
            keys=["/test_table_1", "/test_table_2"], columns=["score1", "score2"]
        )
        expected = Od(score1=[0.1, 0.2, 0.3], score2=[0.4, 0.5, 0.6])
        expected = pd.DataFrame(expected, index=["AAA", "AAC", "AAG"])
        self.assertTrue(result.equals(expected))

    def test_select_multiple_using_where_and_columns(self):
        self.path = os.path.join(self.data_dir, "test.h5")
        data1 = pd.DataFrame(
            {"count1": [1, 2, 3], "score1": [0.1, 0.2, 0.3]},
            index=["AAA", "AAC", "AAG"],
        )
        data2 = pd.DataFrame(
            {"count2": [4, 5, 6], "score2": [0.4, 0.5, 0.6]},
            index=["AAA", "AAC", "AAG"],
        )

        self.store = HDFStore(self.path, mode="w")
        self.store.put("/test_table_1", data1)
        self.store.put("/test_table_2", data2)

        result = self.store.select_as_multiple(
            keys=["/test_table_1", "/test_table_2"],
            where="count1=2",
            columns=["score2"],
        )
        expected = pd.DataFrame({"score2": [0.5]}, index=["AAC"])
        self.assertTrue(result.equals(expected))

    def test_select_multiple_with_chunks(self):
        self.path = os.path.join(self.data_dir, "test.h5")
        data1 = pd.DataFrame(
            {"count1": [1, 2, 3], "score1": [0.1, 0.2, 0.3]},
            index=["AAA", "AAC", "AAG"],
        )
        data2 = pd.DataFrame(
            {"count2": [4, 5, 6], "score2": [0.4, 0.5, 0.6]},
            index=["AAA", "AAC", "AAG"],
        )

        self.store = HDFStore(self.path, mode="w")
        self.store.put("/test_table_1", data1)
        self.store.put("/test_table_2", data2)

        result = self.store.select_as_multiple(
            keys=["/test_table_1", "/test_table_2"],
            where="count1=2",
            columns=["score2"],
            chunk=True,
        )
        expected = pd.DataFrame({"score2": [0.5]}, index=["AAC"])
        for df in result:
            self.assertTrue(df.equals(expected))

    def test_select_multiple_with_selector(self):
        self.path = os.path.join(self.data_dir, "test.h5")
        data1 = pd.DataFrame(
            {"count1": [1, 2, 3], "score1": [0.1, 0.2, 0.3]},
            index=["AAA", "AAC", "AAG"],
        )
        data2 = pd.DataFrame(
            {"count2": [4, 5, 6], "score2": [0.4, 0.5, 0.6]},
            index=["AAA", "AAC", "AAG"],
        )

        self.store = HDFStore(self.path, mode="w")
        self.store.put("/test_table_1", data1)
        self.store.put("/test_table_2", data2)

        result = self.store.select_as_multiple(
            keys=["/test_table_1", "/test_table_2"],
            selector="/test_table_2",
            where="count2=6",
            columns=["score1", "score2"],
        )
        expected = Od(score1=[0.3], score2=[0.6])
        expected = pd.DataFrame(expected, index=["AAG"])
        self.assertTrue(result.equals(expected))

    def test_select_multiple_throws_correct_errors(self):
        self.path = os.path.join(self.data_dir, "test.h5")
        data = pd.DataFrame(
            {"count": [1, 2, 3], "score": [0.1, 0.2, 0.3]}, index=["AAA", "AAC", "AAG"]
        )

        self.store = HDFStore(self.path, mode="w")
        self.store.put("/test_table", data)

        with self.assertRaises(ValueError):
            self.store.select_as_multiple(
                ["/test_table"], where='columns=["count"] & count<3', chunk=True
            )
        with self.assertRaises(ValueError):
            self.store.select_as_multiple(
                ["/test_table"], where='column=["count"] & count<3', chunk=True
            )

        with self.assertRaises(TypeError):
            self.store.select_as_multiple(["/test_table"], columns=25)

        with self.assertRaises(TypeError):
            self.store.select_as_multiple(["/test_table"], selector=99)

        with self.assertRaises(TypeError):
            self.store.select_as_multiple(["/test_table"], where=[])

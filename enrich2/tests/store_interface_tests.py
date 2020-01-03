#  Copyright 2016-2017 Alan F Rubin, Daniel C Esposito
#
#  This file is part of Enrich2.
#
#  Enrich2 is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Enrich2 is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Enrich2. If not, see <http://www.gnu.org/licenses/>.


import os
import pandas as pd
import numpy as np
import unittest
import tempfile
import operator

from enrich2.tests.config import StoreInterfaceBeingTested


class StoreInterfaceTest(unittest.TestCase):
    def __init_subclass__(cls, StoreInterface, **kwargs):
        cls.StoreInterface = StoreInterface
        super().__init_subclass__(**kwargs)


class TestStore(StoreInterfaceTest, StoreInterface=StoreInterfaceBeingTested):
    def test_initial_state(self) -> None:
        store = self.StoreInterface()
        self.assertIsNone(store._store)
        self.assertFalse(store.is_open())
        self.assertRaises(ValueError, store.raise_if_not_open)

    def test_is_empty(self) -> None:
        # should throw an error if no file is open
        store = self.StoreInterface()
        self.assertRaises(ValueError, store.is_empty)

        data = pd.DataFrame({"count": [1, 2, 3]}, index=["AAA", "AAC", "AAG"])

        with tempfile.TemporaryDirectory() as data_dir:
            store_path = os.path.join(data_dir, "test.h5")
            store = self.StoreInterface(store_path, mode="a")

            self.assertTrue(store.is_empty())

            store.put("/test_table", data)
            self.assertFalse(store.is_empty())

            store.close()


class TestStoreFileOps(StoreInterfaceTest, StoreInterface=StoreInterfaceBeingTested):
    def test_open_new_file(self) -> None:
        # both write and append should create a new empty file
        for mode in ["w", "a"]:
            with self.subTest(mode=mode):
                with tempfile.TemporaryDirectory() as data_dir:
                    store_path = os.path.join(data_dir, "test.h5")
                    store = self.StoreInterface(store_path, mode=mode)
                    self.assertTrue(store.is_open())
                    self.assertTrue(store.is_empty())
                    self.assertEqual(store.filename, store_path)
                    store.close()

        # both read and read/write should throw an error since the file doesn't exist
        for mode in ["r", "r+"]:
            with self.subTest(mode=mode):
                with tempfile.TemporaryDirectory() as data_dir:
                    store_path = os.path.join(data_dir, "test.h5")
                    self.assertRaises(IOError, self.StoreInterface, store_path, mode)

        # an invalid mode should throw an error
        for mode in ["x", "w+"]:
            with self.subTest(mode=mode):
                with tempfile.TemporaryDirectory() as data_dir:
                    store_path = os.path.join(data_dir, "test.h5")
                    self.assertRaises(ValueError, self.StoreInterface, store_path, mode)

    def test_overwrite_existing_file(self) -> None:
        data = pd.DataFrame({"count": [1, 2, 3]}, index=["AAA", "AAC", "AAG"])

        with tempfile.TemporaryDirectory() as data_dir:
            store_path = os.path.join(data_dir, "test.h5")

            # create a file and put some data in it
            store = self.StoreInterface(store_path, mode="a")
            store.put("/test_table", data)
            self.assertFalse(store.is_empty())

            # overwrite the file and make sure it's now empty
            store.open(store_path, mode="w")
            self.assertTrue(store.is_open())
            self.assertTrue(store.is_empty())

            store.close()

    def test_close_file(self) -> None:
        with tempfile.TemporaryDirectory() as data_dir:
            store_path = os.path.join(data_dir, "test.h5")
            store = self.StoreInterface(store_path, mode="a")
            store.close()

            self.assertFalse(store.is_open())
            self.assertRaises(ValueError, store.is_empty)
            self.assertIsNone(store.filename)
            self.assertIsNone(store._store)


class TestStorePut(StoreInterfaceTest, StoreInterface=StoreInterfaceBeingTested):
    def test_put_new_key(self) -> None:
        data = pd.DataFrame({"count": [1, 2, 3]}, index=["AAA", "AAC", "AAG"])

        for append in [True, False]:
            with self.subTest(append=append):
                with tempfile.TemporaryDirectory() as data_dir:
                    store_path = os.path.join(data_dir, "test.h5")
                    store = self.StoreInterface(store_path, mode="w")

                    store.put("/test_table", data, append=append)
                    self.assertListEqual(store.keys(), ["/test_table"])
                    result = store.get("/test_table")
                    pd.testing.assert_frame_equal(result, data)

                    store.close()

    def test_put_append(self) -> None:
        data1 = pd.DataFrame({"count": [1, 2, 3]}, index=["AAA", "AAC", "AAG"])
        data2 = pd.DataFrame({"count": [4, 5, 6]}, index=["AAA", "AAC", "AAG"])

        with tempfile.TemporaryDirectory() as data_dir:
            store_path = os.path.join(data_dir, "test.h5")
            store = self.StoreInterface(store_path, mode="w")

            store.put("/test_table", data1)
            store.put("/test_table", data2, append=True)
            self.assertListEqual(store.keys(), ["/test_table"])
            result = store.get("/test_table")
            pd.testing.assert_frame_equal(result, data1.append(data2))

            store.close()

    def test_put_overwrite(self) -> None:
        data1 = pd.DataFrame({"count": [1, 2, 3]}, index=["AAA", "AAC", "AAG"])
        data2 = pd.DataFrame({"count": [4, 5, 6]}, index=["AAA", "AAC", "AAG"])

        with tempfile.TemporaryDirectory() as data_dir:
            store_path = os.path.join(data_dir, "test.h5")
            store = self.StoreInterface(store_path, mode="w")

            store.put("/test_table", data1)
            store.put("/test_table", data2, append=False)
            self.assertListEqual(store.keys(), ["/test_table"])
            result = store.get("/test_table")
            pd.testing.assert_frame_equal(result, data2)

            store.close()


class TestStoreAppend(StoreInterfaceTest, StoreInterface=StoreInterfaceBeingTested):
    def test_append_new_key(self) -> None:
        data = pd.DataFrame({"count": [1, 2, 3]}, index=["AAA", "AAC", "AAG"])

        with tempfile.TemporaryDirectory() as data_dir:
            store_path = os.path.join(data_dir, "test.h5")
            store = self.StoreInterface(store_path, mode="w")

            store.append("/test_table", data)
            self.assertListEqual(store.keys(), ["/test_table"])
            result = store.get("/test_table")
            pd.testing.assert_frame_equal(result, data)

            store.close()

    def test_append(self) -> None:
        data1 = pd.DataFrame({"count": [1, 2, 3]}, index=["AAA", "AAC", "AAG"])
        data2 = pd.DataFrame({"count": [4, 5, 6]}, index=["AAA", "AAC", "AAG"])

        with tempfile.TemporaryDirectory() as data_dir:
            store_path = os.path.join(data_dir, "test.h5")
            store = self.StoreInterface(store_path, mode="w")

            store.put("/test_table", data1)
            store.append("/test_table", data2)
            self.assertListEqual(store.keys(), ["/test_table"])
            result = store.get("/test_table")
            pd.testing.assert_frame_equal(result, data1.append(data2))

            store.close()


class TestStoreRemove(StoreInterfaceTest, StoreInterface=StoreInterfaceBeingTested):
    def test_remove_key(self) -> None:
        data = pd.DataFrame({"count": [1, 2, 3]}, index=["AAA", "AAC", "AAG"])

        with tempfile.TemporaryDirectory() as data_dir:
            store_path = os.path.join(data_dir, "test.h5")
            store = self.StoreInterface(store_path, mode="w")

            store.put("/test_table", data)
            store.remove("/test_table")
            self.assertTrue(store.is_empty())

            store.close()

    def test_remove_missing_key(self) -> None:
        with tempfile.TemporaryDirectory() as data_dir:
            store_path = os.path.join(data_dir, "test.h5")
            store = self.StoreInterface(store_path, mode="w")

            self.assertRaises(KeyError, store.remove, "/test_table")

            store.close()

    def test_clear(self) -> None:
        data = pd.DataFrame({"count": [1, 2, 3]}, index=["AAA", "AAC", "AAG"])

        with tempfile.TemporaryDirectory() as data_dir:
            store_path = os.path.join(data_dir, "test.h5")
            store = self.StoreInterface(store_path, mode="w")

            store.put("/test_table", data)
            store.clear()
            self.assertRaises(KeyError, operator.itemgetter("/test_table"), store)
            self.assertTrue(store.is_empty())
            self.assertTrue(store.is_open())

            store.close()


class TestStoreCheckKeyExists(
    StoreInterfaceTest, StoreInterface=StoreInterfaceBeingTested
):
    def test_has_key(self) -> None:
        data = pd.DataFrame({"count": [1, 2, 3]}, index=["AAA", "AAC", "AAG"])

        with tempfile.TemporaryDirectory() as data_dir:
            store_path = os.path.join(data_dir, "test.h5")
            store = self.StoreInterface(store_path, mode="w")

            store.put("/test_table", data)
            self.assertIn("/test_table", store)
            self.assertNotIn("/foo_bar", store)

            store.close()


class TestStoreGetKey(StoreInterfaceTest, StoreInterface=StoreInterfaceBeingTested):
    def test_get_key(self) -> None:
        data = pd.DataFrame({"count": [1, 2, 3]}, index=["AAA", "AAC", "AAG"])

        with tempfile.TemporaryDirectory() as data_dir:
            store_path = os.path.join(data_dir, "test.h5")
            store = self.StoreInterface(store_path, mode="w")

            store.put("/test_table", data)
            result = store.get("/test_table")
            pd.testing.assert_frame_equal(result, data)

            store.close()

    def test_get_missing_key(self) -> None:
        with tempfile.TemporaryDirectory() as data_dir:
            store_path = os.path.join(data_dir, "test.h5")
            store = self.StoreInterface(store_path, mode="w")
            self.assertRaises(KeyError, store.get, "/test_table")
            store.close()

    def test_dictionary_access(self) -> None:
        data = pd.DataFrame({"count": [1, 2, 3]}, index=["AAA", "AAC", "AAG"])

        with tempfile.TemporaryDirectory() as data_dir:
            store_path = os.path.join(data_dir, "test.h5")
            store = self.StoreInterface(store_path, mode="w")

            self.assertRaises(KeyError, operator.itemgetter("/test_table"), store)

            store.put("/test_table", data)
            result = store["/test_table"]
            pd.testing.assert_frame_equal(result, data)

            store.close()


class TestStoreMetadata(StoreInterfaceTest, StoreInterface=StoreInterfaceBeingTested):
    def test_get_set_metadata(self) -> None:
        data = pd.DataFrame({"count": [1, 2, 3]}, index=["AAA", "AAC", "AAG"])
        metadata = {"hello": "world"}

        with tempfile.TemporaryDirectory() as data_dir:
            store_path = os.path.join(data_dir, "test.h5")
            store = self.StoreInterface(store_path, mode="w")

            store.put("/test_table", data)
            store.set_metadata("/test_table", metadata)
            result = store.get_metadata("/test_table")
            self.assertDictEqual(result, metadata)

            store.close()

    def test_update_metadata(self) -> None:
        data = pd.DataFrame({"count": [1, 2, 3]}, index=["AAA", "AAC", "AAG"])
        metadata1 = {"hello": "world"}
        metadata2 = {"foo": "bar"}

        with tempfile.TemporaryDirectory() as data_dir:
            store_path = os.path.join(data_dir, "test.h5")
            store = self.StoreInterface(store_path, mode="w")

            store.put("/test_table", data)
            store.set_metadata("/test_table", metadata1)
            store.set_metadata("/test_table", metadata2, update=True)
            result = store.get_metadata("/test_table")
            self.assertDictEqual(result, {**metadata1, **metadata2})

            store.close()

    def test_update_metadata_same_key(self) -> None:
        data = pd.DataFrame({"count": [1, 2, 3]}, index=["AAA", "AAC", "AAG"])
        metadata1 = {"hello": "world"}
        metadata2 = {"hello": "everyone"}

        with tempfile.TemporaryDirectory() as data_dir:
            store_path = os.path.join(data_dir, "test.h5")
            store = self.StoreInterface(store_path, mode="w")

            store.put("/test_table", data)
            store.set_metadata("/test_table", metadata1)
            store.set_metadata("/test_table", metadata2, update=True)
            result = store.get_metadata("/test_table")
            self.assertDictEqual(result, metadata2)

            store.close()

    def test_replace_metadata(self) -> None:
        data = pd.DataFrame({"count": [1, 2, 3]}, index=["AAA", "AAC", "AAG"])
        metadata1 = {"hello": "world"}
        metadata2 = {"foo": "bar"}

        with tempfile.TemporaryDirectory() as data_dir:
            store_path = os.path.join(data_dir, "test.h5")
            store = self.StoreInterface(store_path, mode="w")

            store.put("/test_table", data)
            store.set_metadata("/test_table", metadata1)
            store.set_metadata("/test_table", metadata2, update=False)
            result = store.get_metadata("/test_table")
            self.assertDictEqual(result, metadata2)

            store.close()

    def test_bad_metadata_type(self) -> None:
        data = pd.DataFrame({"count": [1, 2, 3]}, index=["AAA", "AAC", "AAG"])
        metadata = ["hello", "world"]

        with tempfile.TemporaryDirectory() as data_dir:
            store_path = os.path.join(data_dir, "test.h5")
            store = self.StoreInterface(store_path, mode="w")

            store.put("/test_table", data)
            self.assertRaises(TypeError, store.set_metadata, "/test_table", metadata)

            store.close()

    def test_set_metadata_missing_key(self) -> None:
        metadata = {"hello": "world"}

        with tempfile.TemporaryDirectory() as data_dir:
            store_path = os.path.join(data_dir, "test.h5")
            store = self.StoreInterface(store_path, mode="w")

            self.assertRaises(KeyError, store.set_metadata, "/test_table", metadata)

            store.close()

    def test_get_metadata_missing_key(self) -> None:
        with tempfile.TemporaryDirectory() as data_dir:
            store_path = os.path.join(data_dir, "test.h5")
            store = self.StoreInterface(store_path, mode="w")

            self.assertRaises(KeyError, store.get_metadata, "/test_table")

            store.close()


class TestStoreSelect(StoreInterfaceTest, StoreInterface=StoreInterfaceBeingTested):
    def test_select_by_where(self) -> None:
        data = pd.DataFrame(
            {"count": [1, 2, 3], "score": [0.1, 0.2, 0.3]}, index=["AAA", "AAC", "AAG"]
        )

        with tempfile.TemporaryDirectory() as data_dir:
            store_path = os.path.join(data_dir, "test.h5")
            store = self.StoreInterface(store_path, mode="w")

            store.put("/test_table", data)

            result = store.select("/test_table", where="count < 3")
            pd.testing.assert_frame_equal(
                result,
                pd.DataFrame(
                    {"count": [1, 2], "score": [0.1, 0.2,]}, index=["AAA", "AAC"]
                ),
            )

            store.close()

    def test_select_by_where_no_matches(self) -> None:
        data = pd.DataFrame(
            {"count": [1, 2, 3], "score": [0.1, 0.2, 0.3]}, index=["AAA", "AAC", "AAG"]
        )

        with tempfile.TemporaryDirectory() as data_dir:
            store_path = os.path.join(data_dir, "test.h5")
            store = self.StoreInterface(store_path, mode="w")

            store.put("/test_table", data)

            result = store.select("/test_table", where="count > 5")
            self.assertTrue(result.empty)

            store.close()

    def test_select_by_columns(self) -> None:
        data = pd.DataFrame(
            {"count": [1, 2, 3], "score": [0.1, 0.2, 0.3]}, index=["AAA", "AAC", "AAG"]
        )

        with tempfile.TemporaryDirectory() as data_dir:
            store_path = os.path.join(data_dir, "test.h5")
            store = self.StoreInterface(store_path, mode="w")

            store.put("/test_table", data)

            result = store.select("/test_table", columns=["score"])
            pd.testing.assert_frame_equal(result, data.loc[:, ["score"]])

            store.close()

    def test_select_by_columns_no_matches(self) -> None:
        data = pd.DataFrame(
            {"count": [1, 2, 3], "score": [0.1, 0.2, 0.3]}, index=["AAA", "AAC", "AAG"]
        )

        with tempfile.TemporaryDirectory() as data_dir:
            store_path = os.path.join(data_dir, "test.h5")
            store = self.StoreInterface(store_path, mode="w")

            store.put("/test_table", data)

            result = store.select("/test_table", columns=["foo"])
            self.assertTrue(result.empty)

            store.close()

    def test_get_column(self) -> None:
        data = pd.DataFrame(
            {"count": [1, 2, 3], "score": [0.1, 0.2, 0.3]}, index=["AAA", "AAC", "AAG"]
        )

        with tempfile.TemporaryDirectory() as data_dir:
            store_path = os.path.join(data_dir, "test.h5")
            store = self.StoreInterface(store_path, mode="w")

            store.put("/test_table", data)

            result = store.get_column("/test_table", "score")
            np.testing.assert_array_equal(result.values, data["score"].values)

            store.close()

    def test_get_column_no_matches(self) -> None:
        data = pd.DataFrame(
            {"count": [1, 2, 3], "score": [0.1, 0.2, 0.3]}, index=["AAA", "AAC", "AAG"]
        )

        with tempfile.TemporaryDirectory() as data_dir:
            store_path = os.path.join(data_dir, "test.h5")
            store = self.StoreInterface(store_path, mode="w")

            store.put("/test_table", data)

            self.assertRaises(KeyError, store.get_column, "/test_table", "foo")

            store.close()

    @unittest.expectedFailure
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

        self.store = self.StoreInterface(self.path, mode="w")
        self.store.put("/test_table_1", data1)
        self.store.put("/test_table_2", data2)

        result = self.store.select_as_multiple(
            keys=["/test_table_1", "/test_table_2"], where="count1=2"
        )
        data = dict(count1=[2], score1=[0.2], count2=[5], score2=[0.5])
        expected = pd.DataFrame(data, index=["AAC"])
        self.assertTrue(result.equals(expected))

    @unittest.expectedFailure
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

        self.store = self.StoreInterface(self.path, mode="w")
        self.store.put("/test_table_1", data1)
        self.store.put("/test_table_2", data2)

        result = self.store.select_as_multiple(
            keys=["/test_table_1", "/test_table_2"], columns=["score1", "score2"]
        )
        expected = dict(score1=[0.1, 0.2, 0.3], score2=[0.4, 0.5, 0.6])
        expected = pd.DataFrame(expected, index=["AAA", "AAC", "AAG"])
        self.assertTrue(result.equals(expected))

    @unittest.expectedFailure
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

        self.store = self.StoreInterface(self.path, mode="w")
        self.store.put("/test_table_1", data1)
        self.store.put("/test_table_2", data2)

        result = self.store.select_as_multiple(
            keys=["/test_table_1", "/test_table_2"],
            where="count1=2",
            columns=["score2"],
        )
        expected = pd.DataFrame({"score2": [0.5]}, index=["AAC"])
        self.assertTrue(result.equals(expected))

    @unittest.expectedFailure
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

        self.store = self.StoreInterface(self.path, mode="w")
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

    @unittest.expectedFailure
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

        self.store = self.StoreInterface(self.path, mode="w")
        self.store.put("/test_table_1", data1)
        self.store.put("/test_table_2", data2)

        result = self.store.select_as_multiple(
            keys=["/test_table_1", "/test_table_2"],
            selector="/test_table_2",
            where="count2=6",
            columns=["score1", "score2"],
        )
        expected = dict(score1=[0.3], score2=[0.6])
        expected = pd.DataFrame(expected, index=["AAG"])
        self.assertTrue(result.equals(expected))

    @unittest.expectedFailure
    def test_select_multiple_throws_correct_errors(self):
        self.path = os.path.join(self.data_dir, "test.h5")
        data = pd.DataFrame(
            {"count": [1, 2, 3], "score": [0.1, 0.2, 0.3]}, index=["AAA", "AAC", "AAG"]
        )

        self.store = self.StoreInterface(self.path, mode="w")
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

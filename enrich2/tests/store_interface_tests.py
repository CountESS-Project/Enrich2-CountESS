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


import pathlib
import pandas as pd
import dask.dataframe as dd
import numpy as np
import unittest
import tempfile

from enrich2.tests.config import StoreInterfaceBeingTested


__all__ = [
    "TestStorePath",
    "TestStoreReopen",
    "TestStorePut",
    "TestStoreDrop",
    "TestStoreGet",
    "TestStoreMetadata",
]


class StoreInterfaceTest(unittest.TestCase):
    def setUp(self) -> None:
        self._temp_dir = tempfile.TemporaryDirectory()
        self.path = pathlib.Path(
            self._temp_dir.name, f"temp{self.StoreInterface.file_extensions[0]}"
        )
        self.store = self.StoreInterface(self.path)

    def tearDown(self) -> None:
        self._temp_dir.cleanup()

    def __init_subclass__(cls, StoreInterface, **kwargs):
        cls.StoreInterface = StoreInterface
        super().__init_subclass__(**kwargs)


class TestStorePath(StoreInterfaceTest, StoreInterface=StoreInterfaceBeingTested):
    def test_path(self) -> None:
        # tests the default implemented in StoreInterfaceTest.setUp()
        self.assertEqual(self.store.path, self.path)

    def test_path_as_pathlike(self) -> None:
        test_path = pathlib.Path(
            self._temp_dir.name, f"test_path{self.StoreInterface.file_extensions[0]}"
        )
        test_store = self.StoreInterface(test_path)
        self.assertEqual(test_store.path, test_path)

    def test_path_as_string(self) -> None:
        test_path = str(
            pathlib.Path(
                self._temp_dir.name,
                f"test_path{self.StoreInterface.file_extensions[0]}",
            )
        )
        test_store = self.StoreInterface(test_path)
        self.assertEqual(str(test_store.path), test_path)

    def test_path_as_invalid_type(self) -> None:
        test_path = 1234
        self.assertRaises(TypeError, self.StoreInterface, test_path)

    def test_path_bad_extension(self) -> None:
        test_path = pathlib.Path(self._temp_dir.name, f"test_path.mp3")
        self.assertRaises(ValueError, self.StoreInterface, test_path)

    def test_path_no_extension(self) -> None:
        test_path = pathlib.Path(self._temp_dir.name, f"test_path")
        self.assertRaises(ValueError, self.StoreInterface, test_path)


class TestStoreReopen(StoreInterfaceTest, StoreInterface=StoreInterfaceBeingTested):
    def test_reopen_empty(self) -> None:
        store_2 = self.StoreInterface(self.path)
        self.assertListEqual(self.store.keys(), store_2.keys())

    def test_reopen_with_data(self) -> None:
        index = pd.Index(["AAA", "AAC", "AAG"], name="index")
        data = pd.DataFrame({"count": [1, 2, 3]}, index=index)

        self.store.put("test_table", dd.from_pandas(data, npartitions=2))

        store_2 = self.StoreInterface(self.path)
        self.assertListEqual(self.store.keys(), store_2.keys())

        result_1 = self.store.get("test_table")
        result_2 = store_2.get("test_table")
        pd.testing.assert_frame_equal(result_1.compute(), result_2.compute())

    def test_reopen_with_delete(self) -> None:
        index = pd.Index(["AAA", "AAC", "AAG"], name="index")
        data = pd.DataFrame({"count": [1, 2, 3]}, index=index)

        self.store.put("test_table", dd.from_pandas(data, npartitions=2))
        self.store.drop("test_table")

        store_2 = self.StoreInterface(self.path)
        self.assertListEqual(self.store.keys(), store_2.keys())


class TestStorePut(StoreInterfaceTest, StoreInterface=StoreInterfaceBeingTested):
    def test_put_new(self) -> None:
        index = pd.Index(["AAA", "AAC", "AAG"], name="index")
        data = pd.DataFrame({"count": [1, 2, 3]}, index=index)

        self.store.put("test_table", dd.from_pandas(data, npartitions=2))
        self.assertListEqual(self.store.keys(), ["test_table"])
        result = self.store.get("test_table")
        pd.testing.assert_frame_equal(result.compute(), data)

    def test_put_overwrite(self) -> None:
        index = pd.Index(["AAA", "AAC", "AAG"], name="index")
        data1 = pd.DataFrame({"count": [1, 2, 3]}, index=index)
        data2 = pd.DataFrame({"count": [4, 5, 6]}, index=index)

        self.store.put("test_table", dd.from_pandas(data1, npartitions=2))
        self.store.put("test_table", dd.from_pandas(data2, npartitions=2))
        self.assertListEqual(self.store.keys(), ["test_table"])
        result = self.store.get("test_table")
        pd.testing.assert_frame_equal(result.compute(), data2)

    def test_is_empty(self) -> None:
        index = pd.Index(["AAA", "AAC", "AAG"], name="index")
        data = pd.DataFrame({"count": [1, 2, 3]}, index=index)

        self.assertTrue(self.store.is_empty())

        self.store.put("test_table", dd.from_pandas(data, npartitions=2))
        self.assertFalse(self.store.is_empty())


class TestStoreDrop(StoreInterfaceTest, StoreInterface=StoreInterfaceBeingTested):
    def test_drop(self) -> None:
        index = pd.Index(["AAA", "AAC", "AAG"], name="index")
        data = pd.DataFrame({"count": [1, 2, 3]}, index=index)

        self.store.put("test_table", dd.from_pandas(data, npartitions=2))
        self.store.drop("test_table")
        self.assertTrue(self.store.is_empty())

    def test_drop_missing(self) -> None:
        self.assertRaises(KeyError, self.store.drop, "test_table")


class TestStoreGet(StoreInterfaceTest, StoreInterface=StoreInterfaceBeingTested):
    def test_get(self) -> None:
        index = pd.Index(["AAA", "AAC", "AAG"], name="index")
        data = pd.DataFrame({"count": [1, 2, 3]}, index=index)

        self.store.put("test_table", dd.from_pandas(data, npartitions=2))
        self.assertListEqual(self.store.keys(), ["test_table"])
        result = self.store.get("test_table")
        pd.testing.assert_frame_equal(result.compute(), data)

    def test_get_missing(self) -> None:
        self.assertRaises(KeyError, self.store.get, "test_table")

    def test_get_column(self) -> None:
        index = pd.Index(["AAA", "AAC", "AAG"], name="index")
        data = pd.DataFrame({"count": [1, 2, 3], "score": [0.1, 0.2, 0.3]}, index=index)

        self.store.put("test_table", dd.from_pandas(data, npartitions=2))

        result = self.store.get_column("test_table", "score")
        np.testing.assert_array_equal(result, data["score"].values)

    def test_get_missing_column(self) -> None:
        index = pd.Index(["AAA", "AAC", "AAG"], name="index")
        data = pd.DataFrame({"count": [1, 2, 3], "score": [0.1, 0.2, 0.3]}, index=index)

        self.store.put("test_table", dd.from_pandas(data, npartitions=2))

        self.assertRaises(
            (KeyError, ValueError), self.store.get_column, "test_table", "missing"
        )

    def test_get_with_merge(self):
        index = pd.Index(["AAA", "AAC", "AAG"], name="index")
        data1 = pd.DataFrame(
            {"count": [1, 2, 3], "score1": [0.1, 0.2, 0.3]}, index=index
        )
        data2 = pd.DataFrame(
            {"count": [1, 2, 3], "score2": [0.4, 0.5, 0.6]}, index=index
        )

        self.store.put("test_table_1", dd.from_pandas(data1, npartitions=2))
        self.store.put("test_table_2", dd.from_pandas(data2, npartitions=2))

        result = self.store.get_with_merge(keys=["test_table_1", "test_table_2"])
        expected = data1.merge(data2, how="inner", left_index=True, right_index=True)
        pd.testing.assert_frame_equal(result.compute(), expected)

    def test_get_with_merge_partial(self):
        index1 = pd.Index(["AAA", "AAC", "CCC"], name="index")
        index2 = pd.Index(["AAA", "AAC", "AAG"], name="index")
        data1 = pd.DataFrame(
            {"count": [1, 2, 3], "score1": [0.1, 0.2, 0.3]}, index=index1
        )
        data2 = pd.DataFrame(
            {"count": [1, 2, 3], "score2": [0.4, 0.5, 0.6]}, index=index2
        )

        self.store.put("test_table_1", dd.from_pandas(data1, npartitions=2))
        self.store.put("test_table_2", dd.from_pandas(data2, npartitions=2))

        result = self.store.get_with_merge(keys=["test_table_1", "test_table_2"])
        expected = data1.merge(data2, how="inner", left_index=True, right_index=True)
        pd.testing.assert_frame_equal(result.compute(), expected)

    def test_get_with_merge_empty(self):
        index1 = pd.Index(["CCC", "GGG", "TTT"], name="index")
        index2 = pd.Index(["AAA", "AAC", "AAG"], name="index")
        data1 = pd.DataFrame(
            {"count": [1, 2, 3], "score1": [0.1, 0.2, 0.3]}, index=index1
        )
        data2 = pd.DataFrame(
            {"count": [1, 2, 3], "score2": [0.4, 0.5, 0.6]}, index=index2
        )

        self.store.put("test_table_1", dd.from_pandas(data1, npartitions=2))
        self.store.put("test_table_2", dd.from_pandas(data2, npartitions=2))

        self.assertRaises(
            ValueError,
            self.store.get_with_merge,
            keys=["test_table_1", "test_table_2"],
        )


class TestStoreMetadata(StoreInterfaceTest, StoreInterface=StoreInterfaceBeingTested):
    def test_get_set_metadata(self) -> None:
        index = pd.Index(["AAA", "AAC", "AAG"], name="index")
        data = pd.DataFrame({"count": [1, 2, 3]}, index=index)
        metadata = {"hello": "world"}

        self.store.put("test_table", dd.from_pandas(data, npartitions=2))
        self.store.set_metadata("test_table", metadata)
        result = self.store.get_metadata("test_table")
        self.assertDictEqual(result, metadata)

    def test_get_metadata_unset(self) -> None:
        index = pd.Index(["AAA", "AAC", "AAG"], name="index")
        data = pd.DataFrame({"count": [1, 2, 3]}, index=index)

        self.store.put("test_table", dd.from_pandas(data, npartitions=2))

        result = self.store.get_metadata("test_table")
        self.assertDictEqual(result, {})

    def test_update_metadata(self) -> None:
        index = pd.Index(["AAA", "AAC", "AAG"], name="index")
        data = pd.DataFrame({"count": [1, 2, 3]}, index=index)
        metadata1 = {"hello": "world"}
        metadata2 = {"foo": "bar"}

        self.store.put("test_table", dd.from_pandas(data, npartitions=2))
        self.store.set_metadata("test_table", metadata1)
        self.store.set_metadata("test_table", metadata2, update=True)
        result = self.store.get_metadata("test_table")
        self.assertDictEqual(result, {**metadata1, **metadata2})

    def test_update_metadata_same_key(self) -> None:
        index = pd.Index(["AAA", "AAC", "AAG"], name="index")
        data = pd.DataFrame({"count": [1, 2, 3]}, index=index)
        metadata1 = {"hello": "world"}
        metadata2 = {"hello": "everyone"}

        self.store.put("test_table", dd.from_pandas(data, npartitions=2))
        self.store.set_metadata("test_table", metadata1)
        self.store.set_metadata("test_table", metadata2, update=True)
        result = self.store.get_metadata("test_table")
        self.assertDictEqual(result, metadata2)

    def test_replace_metadata(self) -> None:
        index = pd.Index(["AAA", "AAC", "AAG"], name="index")
        data = pd.DataFrame({"count": [1, 2, 3]}, index=index)
        metadata1 = {"hello": "world"}
        metadata2 = {"foo": "bar"}

        self.store.put("test_table", dd.from_pandas(data, npartitions=2))
        self.store.set_metadata("test_table", metadata1)
        self.store.set_metadata("test_table", metadata2, update=False)
        result = self.store.get_metadata("test_table")
        self.assertDictEqual(result, metadata2)

    def test_bad_metadata_type(self) -> None:
        index = pd.Index(["AAA", "AAC", "AAG"], name="index")
        data = pd.DataFrame({"count": [1, 2, 3]}, index=index)
        metadata = ["hello", "world"]

        self.store.put("test_table", dd.from_pandas(data, npartitions=2))

        self.assertRaises(TypeError, self.store.set_metadata, "test_table", metadata)

    def test_set_metadata_missing_key(self) -> None:
        index = pd.Index(["AAA", "AAC", "AAG"], name="index")
        data = pd.DataFrame({"count": [1, 2, 3]}, index=index)
        metadata = {"hello": "world"}

        self.store.put("test_table", dd.from_pandas(data, npartitions=2))

        self.assertRaises(KeyError, self.store.set_metadata, "missing_table", metadata)

    def test_get_metadata_missing_key(self) -> None:
        index = pd.Index(["AAA", "AAC", "AAG"], name="index")
        data = pd.DataFrame({"count": [1, 2, 3]}, index=index)

        self.store.put("test_table", dd.from_pandas(data, npartitions=2))

        self.assertRaises(KeyError, self.store.get_metadata, "missing_table")

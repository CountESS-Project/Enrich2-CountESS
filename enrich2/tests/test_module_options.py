from unittest import TestCase

from ..plugins.options import BaseOption, Option
from ..plugins.options import Options, OptionsFile
from ..plugins.options import get_unused_options, get_unused_options_ls
from ..plugins.options import option_varnames_not_in_cfg
from ..plugins.options import option_names_not_in_cfg, apply_cfg_to_options


class TestBaseOption(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_base_option_equal(self):
        option_1 = BaseOption(
            "TestOption",
            "test_option",
            dtype=str,
            default="default string",
            hidden=True,
        )
        option_2 = BaseOption(
            "TestOption",
            "test_option",
            dtype=str,
            default="default string",
            hidden=True,
        )

        self.assertEqual(option_1, option_2)

    def test_base_option_not_equal(self):
        option_1 = BaseOption(
            "TestOption",
            "test_option",
            dtype=str,
            default="default string",
            hidden=True,
        )
        option_2 = BaseOption(
            "TestOption2",
            "test_option2",
            dtype=str,
            default="default string",
            hidden=False,
        )
        self.assertNotEqual(option_1, option_2)

    def test_base_option_init(self):
        option = BaseOption(
            "TestOption",
            "test_option",
            dtype=str,
            default="default string",
            hidden=True,
        )

        self.assertEqual(option.name, "TestOption")
        self.assertEqual(option.varname, "test_option")
        self.assertEqual(option.get_default_value(), "default string")
        self.assertEqual(option.dtype, str)
        self.assertEqual(option.get_value(), "default string")
        self.assertEqual(option.visible(), False)

    def test_base_option_bad_type_name(self):
        with self.assertRaises(TypeError):
            option = BaseOption(
                [], "test_option", dtype=str, default="default string", hidden=True
            )
        with self.assertRaises(ValueError):
            option = BaseOption(
                "", "test_option", dtype=str, default="default string", hidden=True
            )

    def test_base_option_bad_type_varname(self):
        with self.assertRaises(TypeError):
            option = BaseOption(
                "TestOption", 1234, dtype=str, default="default string", hidden=True
            )
        with self.assertRaises(ValueError):
            option = BaseOption(
                "TestOption", "", dtype=str, default="default string", hidden=True
            )

    def test_base_option_bad_type_hidden(self):
        with self.assertRaises(TypeError):
            option = BaseOption(
                "TestOption", 1234, dtype=str, default="default string", hidden={}
            )

    def test_base_option_dtype_mismatch(self):
        with self.assertRaises(TypeError):
            option = BaseOption(
                "TestOption",
                "test_option",
                dtype=int,
                default="default string",
                hidden=True,
            )
        with self.assertRaises(TypeError):
            option = BaseOption(
                "TestOption",
                "test_option",
                dtype=None,
                default="default string",
                hidden=True,
            )

    def test_base_option_set_value_dtype_mismatch(self):
        with self.assertRaises(TypeError):
            option = BaseOption(
                "TestOption",
                "test_option",
                dtype=str,
                default="default string",
                hidden=True,
            )
            option._set_value(1)
        with self.assertRaises(TypeError):
            option = BaseOption(
                "TestOption",
                "test_option",
                dtype=str,
                default="default string",
                hidden=True,
            )
            option._set_value([])
        with self.assertRaises(TypeError):
            option = BaseOption(
                "TestOption",
                "test_option",
                dtype=str,
                default="default string",
                hidden=True,
            )
            option._set_value(b"bytes")

    def test_base_option_set_value_dtype_match(self):
        option = BaseOption(
            "TestOption",
            "test_option",
            dtype=str,
            default="default string",
            hidden=True,
        )
        option._set_value("hello world")
        self.assertEqual(option.get_value(), "hello world")
        self.assertEqual(option.get_default_value(), "default string")


class TestOption(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_option_equal(self):
        option_1 = Option(
            name="Normalization Method",
            varname="logr_method",
            dtype=str,
            default="wt",
            choices={"Wild Type": "wt", "Full": "full", "Complete": "complete"},
            hidden=False,
        )
        option_2 = Option(
            name="Normalization Method",
            varname="logr_method",
            dtype=str,
            default="wt",
            choices={"Wild Type": "wt", "Full": "full", "Complete": "complete"},
            hidden=False,
        )

        self.assertEqual(option_1, option_2)

    def test_option_not_equal(self):
        option_1 = Option(
            name="Normalization Method",
            varname="logr_method",
            dtype=str,
            default="wt",
            choices={"Wild Type": "wt", "Full": "full", "Complete": "complete"},
            hidden=False,
        )
        option_2 = Option(
            name="Normalization Method",
            varname="logr_method",
            dtype=str,
            default="full",
            choices={"Wild Type": "wt", "Full": "full", "Complete": "complete"},
            hidden=False,
        )
        self.assertNotEqual(option_1, option_2)

    def test_option_nondict_choices(self):
        with self.assertRaises(TypeError):
            option = Option(
                "TestOption",
                1234,
                dtype=str,
                default="default string",
                choices=[1, 2, 3],
                hidden=False,
            )

    def test_option_non_unique_values_in_choices(self):
        with self.assertRaises(ValueError):
            opt = Option(
                name="Normalization Method",
                varname="logr_method",
                dtype=str,
                default="Wild Type",
                choices={"Wild Type": "wt", "Full": "wt", "Complete": "wt"},
                hidden=False,
            )

    def test_correct_init_no_choices(self):
        opt = Option(
            name="Normalization Method",
            varname="logr_method",
            dtype=str,
            default="wt",
            choices=None,
            hidden=False,
        )
        self.assertEqual(opt.get_value(), "wt")
        self.assertEqual(opt.set_value("full").get_value(), "full")
        self.assertEqual(opt.set_value("full").get_default_value(), "wt")
        self.assertEqual(opt.choices, {})
        self.assertEqual(opt._rev_choices, {})
        self.assertEqual(opt.get_choice_key(), None)

    def test_correct_init_choices(self):
        opt = Option(
            name="Normalization Method",
            varname="logr_method",
            dtype=str,
            default="Wild Type",
            choices={"Wild Type": "wt", "Full": "full", "Complete": "complete"},
            hidden=False,
        )

        rev = {v: k for (k, v) in opt.choices.items()}
        self.assertEqual(opt._rev_choices, rev)

        self.assertEqual(opt.get_choice_key(), "Wild Type")
        self.assertEqual(opt.get_value(), "wt")
        self.assertEqual(opt.get_default_value(), "wt")

        opt.set_value("Complete")
        self.assertEqual(opt.get_choice_key(), "Complete")
        self.assertEqual(opt.get_value(), "complete")
        self.assertEqual(opt.get_default_value(), "wt")

        opt.set_value("full")
        self.assertEqual(opt.get_choice_key(), "Full")
        self.assertEqual(opt.get_value(), "full")
        self.assertEqual(opt.get_default_value(), "wt")

        opt.set_choice_key("wt")
        self.assertEqual(opt.get_choice_key(), "Wild Type")
        self.assertEqual(opt.get_value(), "wt")
        self.assertEqual(opt.get_default_value(), "wt")

        opt.set_choice_key("Complete")
        self.assertEqual(opt.get_choice_key(), "Complete")
        self.assertEqual(opt.get_value(), "complete")
        self.assertEqual(opt.get_default_value(), "wt")

        with self.assertRaises(ValueError):
            opt.set_choice_key("badkey")

        with self.assertRaises(ValueError):
            opt.keytransform("badkey")

        with self.assertRaises(ValueError):
            opt.set_choice_key(None)

        with self.assertRaises(ValueError):
            opt.validate("badkey")

    def test_correct_init_rev_choices(self):
        opt = Option(
            name="Normalization Method",
            varname="logr_method",
            dtype=str,
            default="wt",
            choices={"Wild Type": "wt", "Full": "full", "Complete": "complete"},
            hidden=False,
        )

        rev = {v: k for (k, v) in opt.choices.items()}
        self.assertEqual(opt._rev_choices, rev)

        self.assertEqual(opt.get_choice_key(), "Wild Type")
        self.assertEqual(opt.get_value(), "wt")
        self.assertEqual(opt.get_default_value(), "wt")

    def test_error_non_string_choice_keys(self):
        with self.assertRaises(TypeError):
            Option(
                name="Normalization Method",
                varname="logr_method",
                dtype=str,
                default="wt",
                choices={1: "wt", 2: "full", 3: "complete"},
                hidden=False,
            )

    def test_error_non_dtype_choice_values(self):
        with self.assertRaises(TypeError):
            Option(
                name="Normalization Method",
                varname="logr_method",
                dtype=str,
                default="wt",
                choices={"Wild Type": 1, "Full": 2, "Complete": 3},
                hidden=False,
            )

    def test_keytransform_no_choices(self):
        opt = Option(
            name="Normalization Method",
            varname="logr_method",
            dtype=str,
            default="wt",
            choices=None,
            hidden=False,
        )

        self.assertEqual(opt.keytransform("123"), "123")
        with self.assertRaises(TypeError):
            opt.keytransform(123)

    def test_keytransform_choices(self):
        opt = Option(
            name="Normalization Method",
            varname="logr_method",
            dtype=str,
            default="Wild Type",
            choices={"Wild Type": "wt", "Full": "full", "Complete": "complete"},
            hidden=False,
        )

        self.assertEqual(opt.keytransform("full"), "Full")
        self.assertEqual(opt.keytransform("Full"), "Full")

        with self.assertRaises(ValueError):
            opt.keytransform("123")
        with self.assertRaises(ValueError):
            opt.keytransform(123)

    def test_validate_no_choices(self):
        opt = Option(
            name="Normalization Method",
            varname="logr_method",
            dtype=str,
            default="wt",
            choices=None,
            hidden=False,
        )

        opt.validate("same dtype")
        with self.assertRaises(TypeError):
            opt.validate(123)

    def test_validate_choices(self):
        opt = Option(
            name="Normalization Method",
            varname="logr_method",
            dtype=str,
            default="Wild Type",
            choices={"Wild Type": "wt", "Full": "full", "Complete": "complete"},
            hidden=False,
        )
        with self.assertRaises(TypeError):
            opt.validate(123)
        with self.assertRaises(ValueError):
            opt.validate("badkey")


class TestOptions(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_add_two_items(self):
        options = Options()
        options.add_option(
            name="Normalization Method",
            varname="logr_method",
            dtype=str,
            default="Wild Type",
            choices={"Wild Type": "wt"},
            hidden=False,
        )
        options.add_option(
            name="Weighted",
            varname="weighted",
            dtype=bool,
            default=True,
            choices=None,
            hidden=False,
        )

    def test_add_two_items_with_same_varname(self):
        with self.assertRaises(ValueError):
            options = Options()
            options.add_option(
                name="Normalization Method",
                varname="logr_method",
                dtype=str,
                default="Wild Type",
                choices={"Wild Type": "wt"},
                hidden=False,
            )
            options.add_option(
                name="Weighted",
                varname="logr_method",
                dtype=bool,
                default=True,
                choices=None,
                hidden=False,
            )

    def test_to_dict(self):
        options = Options()
        options.add_option(
            name="Normalization Method",
            varname="logr_method",
            dtype=str,
            default="Wild Type",
            choices={"Wild Type": "wt"},
            hidden=False,
        )
        options.add_option(
            name="Weighted",
            varname="weighted",
            dtype=bool,
            default=True,
            choices=None,
            hidden=False,
        )
        expected = {"logr_method": "wt", "weighted": True}
        self.assertEqual(options.to_dict(), expected)

    def test_has_options(self):
        options = Options()
        self.assertFalse(options.has_options())

        options = Options()
        options.add_option(
            name="Normalization Method",
            varname="logr_method",
            dtype=str,
            default="Wild Type",
            choices={"Wild Type": "wt"},
            hidden=True,
        )
        self.assertTrue(options.has_options())

        options = Options()
        options.add_option(
            name="Normalization Method",
            varname="logr_method",
            dtype=str,
            default="Wild Type",
            choices={"Wild Type": "wt"},
            hidden=False,
        )
        self.assertTrue(options.has_options())

    def test_option_names(self):
        options = Options()
        options.add_option(
            name="Normalization Method",
            varname="logr_method",
            dtype=str,
            default="Wild Type",
            choices={"Wild Type": "wt"},
            hidden=False,
        )
        options.add_option(
            name="Weighted",
            varname="weighted",
            dtype=bool,
            default=True,
            choices=None,
            hidden=False,
        )
        expected = sorted(["Normalization Method", "Weighted"])
        result = list(sorted(options.option_names()))
        self.assertEqual(expected, result)

    def test_option_varnames(self):
        options = Options()
        options.add_option(
            name="Normalization Method",
            varname="logr_method",
            dtype=str,
            default="Wild Type",
            choices={"Wild Type": "wt"},
            hidden=False,
        )
        options.add_option(
            name="Weighted",
            varname="weighted",
            dtype=bool,
            default=True,
            choices=None,
            hidden=False,
        )
        expected = sorted(["logr_method", "weighted"])
        result = list(sorted(options.option_varnames()))
        self.assertEqual(expected, result)

    def test_set_option_by_varname(self):
        options = Options()
        options.add_option(
            name="Normalization Method",
            varname="logr_method",
            dtype=str,
            default="Wild Type",
            choices={"Wild Type": "wt", "Full": "full"},
            hidden=False,
        )

        options.set_option_by_varname("logr_method", "full")
        result = options.get_option_by_varname("logr_method").get_value()
        self.assertEqual(result, "full")

        with self.assertRaises(TypeError):
            options.set_option_by_varname("logr_method", 123)

        with self.assertRaises(ValueError):
            options.set_option_by_varname("logr_method", "badkey")

    def test_validate_option_by_varname(self):
        options = Options()
        options.add_option(
            name="Normalization Method",
            varname="logr_method",
            dtype=str,
            default="Wild Type",
            choices={"Wild Type": "wt", "Full": "full"},
            hidden=False,
        )
        options.validate_option_by_varname("logr_method", "full")

        with self.assertRaises(TypeError):
            options.validate_option_by_varname("logr_method", 123)

        with self.assertRaises(ValueError):
            options.validate_option_by_varname("logr_method", "badkey")

    def test_get_visible_options(self):
        options = Options()
        options.add_option(
            name="Weighted",
            varname="weighted",
            dtype=str,
            default="Wild Type",
            choices={"Wild Type": "wt"},
            hidden=True,
        )
        options.add_option(
            name="Normalization Method",
            varname="logr_method",
            dtype=str,
            default="Wild Type",
            choices={"Wild Type": "wt"},
            hidden=False,
        )
        expected = sorted([o.varname for o in options.get_visible_options()])
        result = ["logr_method"]
        self.assertEqual(expected, result)

    def test_get_hidden_options(self):
        options = Options()
        options.add_option(
            name="Weighted",
            varname="weighted",
            dtype=str,
            default="Wild Type",
            choices={"Wild Type": "wt"},
            hidden=True,
        )
        options.add_option(
            name="Normalization Method",
            varname="logr_method",
            dtype=str,
            default="Wild Type",
            choices={"Wild Type": "wt"},
            hidden=False,
        )
        expected = sorted([o.varname for o in options.get_hidden_options()])
        result = ["weighted"]
        self.assertEqual(expected, result)


class TestUtilityFunctions(TestCase):
    def setUp(self):
        self.cfg = {"random_option": 1, "logr_method": "full", "weighted": False}
        self.options_1 = Options()
        self.options_1.add_option(
            name="Weighted",
            varname="weighted",
            dtype=bool,
            default=True,
            choices=None,
            hidden=True,
        )
        self.options_1.add_option(
            name="Normalization Method",
            varname="logr_method",
            dtype=str,
            default="Wild Type",
            choices={"Wild Type": "wt", "Full": "full"},
            hidden=False,
        )

        self.options_2 = Options()
        self.options_2.add_option(
            name="Weighted",
            varname="weighted",
            dtype=bool,
            default=True,
            choices=None,
            hidden=True,
        )
        self.options_2.add_option(
            name="Normalization Method",
            varname="logr_method",
            dtype=str,
            default="Wild Type",
            choices={"Wild Type": "wt"},
            hidden=False,
        )
        self.options_2.add_option(
            name="h int",
            varname="h_int",
            dtype=int,
            default=5,
            choices=None,
            hidden=True,
        )
        self.options_2.add_option(
            name="h list",
            varname="h_list",
            dtype=list,
            default=[1, 2, 3, 4],
            choices=None,
            hidden=True,
        )

        self.options_3 = Options()
        self.options_3.add_option(
            name="Weighted",
            varname="random_option",
            dtype=str,
            default="Wild Type",
            choices={"Wild Type": "wt"},
            hidden=True,
        )

        self.options_4 = Options()
        self.options_4.add_option(
            name="Weighted",
            varname="weighted",
            dtype=bool,
            default=True,
            choices=None,
            hidden=True,
        )
        self.options_4.add_option(
            name="Normalization Method",
            varname="different name",
            dtype=str,
            default="Wild Type",
            choices={"Wild Type": "wt", "Full": "full"},
            hidden=False,
        )

    def tearDown(self):
        pass

    def test_options_equal(self):
        self.assertEqual(self.options_1, self.options_1)

    def test_options_not_equal(self):
        self.assertNotEqual(self.options_1, self.options_2)
        self.assertNotEqual(self.options_1, self.options_4)

    def test_get_unused_options(self):
        expected = set(["random_option"])
        result = get_unused_options(self.cfg, self.options_1)
        self.assertEqual(result, expected)

    def test_get_unused_options_ls(self):
        expected = set(["random_option"])
        result = get_unused_options_ls(self.cfg, [self.options_1, self.options_2])
        self.assertEqual(result, expected)

        expected = set([])
        result = get_unused_options_ls(
            self.cfg, [self.options_1, self.options_2, self.options_3]
        )
        self.assertEqual(result, expected)

    def test_option_varnames_not_in_cfg(self):
        result = sorted(option_varnames_not_in_cfg(self.cfg, self.options_2))
        expected = sorted(set(["h_int", "h_list"]))
        self.assertEqual(result, expected)

    def test_option_names_not_in_cfg(self):
        result = sorted(option_names_not_in_cfg(self.cfg, self.options_2))
        expected = sorted(set(["h int", "h list"]))
        self.assertEqual(result, expected)

    def test_apply_to_options(self):
        apply_cfg_to_options(self.cfg, self.options_1)
        result = self.options_1.to_dict()
        expected = {"weighted": False, "logr_method": "full"}
        self.assertEqual(result, expected)


class TestOptionsFile(TestCase):
    def setUp(self):
        from io import StringIO

        json_full = '{"scorer": {"scorer options": {"weighted": true}}}'
        json_inner = '{"scorer options": {"weighted": true}}'
        json_bad_1 = '{"badkey": {"scorer options": {"weighted": true}}}'
        json_bad_2 = '{"scorer": {"badkey": {"weighted": true}}}'
        json_bad_type = '{"scorer": {"scorer options": []}}'

        self.good_file_full = StringIO(json_full)
        self.good_file_inner = StringIO(json_inner)
        self.file_bad_full = StringIO(json_bad_1)
        self.file_bad_inner = StringIO(json_bad_2)
        self.file_bad_type = StringIO(json_bad_type)

        self.json_opt_file = OptionsFile.default_json_options_file()

    def tearDown(self):
        self.good_file_full.close()
        self.good_file_inner.close()
        self.file_bad_full.close()
        self.file_bad_inner.close()
        self.file_bad_type.close()

    def test_options_file(self):
        expected = {"weighted": True}
        result = self.json_opt_file.parse_to_dict(self.good_file_full)
        self.assertEqual(expected, result)

        result = self.json_opt_file.parse_to_dict(self.good_file_inner)
        self.assertEqual(expected, result)

        with self.assertRaises(ValueError):
            self.json_opt_file.parse_to_dict(self.file_bad_full)

        with self.assertRaises(ValueError):
            self.json_opt_file.parse_to_dict(self.file_bad_inner)

        with self.assertRaises(TypeError):
            result = self.json_opt_file.parse_to_dict(self.file_bad_type)
            self.json_opt_file.validate_cfg(result)

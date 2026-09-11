import unittest

from ..item import item_tables, ItemType


class TestItems(unittest.TestCase):
    def test_grouped_upgrades_number(self) -> None:
        """
        Tests if grouped upgrades have set number correctly
        """
        bundled_items = item_tables.upgrade_bundles.keys()
        bundled_item_data = [item_tables.item_table[item_name] for item_name in bundled_items]
        bundled_item_numbers = [item_data.number for item_data in bundled_item_data]

        check_numbers = [number == -1 for number in bundled_item_numbers]

        self.assertNotIn(False, check_numbers)

    def test_non_grouped_upgrades_number(self) -> None:
        """
        Checks if non-grouped upgrades number is set correctly thus can be sent into the game.
        """
        check_modulo = 4
        bundled_items = item_tables.upgrade_bundles.keys()
        non_bundled_upgrades = [
            item_name for item_name in item_tables.item_table.keys()
            if (item_name not in bundled_items
                and item_tables.item_table[item_name].type in item_tables.upgrade_item_types)
        ]
        non_bundled_upgrade_data = [item_tables.item_table[item_name] for item_name in non_bundled_upgrades]
        non_bundled_upgrade_numbers = [item_data.number for item_data in non_bundled_upgrade_data]

        check_numbers = [number % check_modulo == 0 for number in non_bundled_upgrade_numbers]

        self.assertNotIn(False, check_numbers)

    def test_bundles_contain_only_basic_elements(self) -> None:
        """
        Checks if there are no bundles within bundles.
        """
        bundled_items = item_tables.upgrade_bundles.keys()
        bundle_elements: list[str] = [item_name for values in item_tables.upgrade_bundles.values() for item_name in values]

        for element in bundle_elements:
            self.assertNotIn(element, bundled_items)

    def test_weapon_armor_level(self) -> None:
        """
        Checks if Weapon/Armor upgrade level is correctly set to all Weapon/Armor upgrade items.
        """
        weapon_armor_upgrades = [
            item
            for item, item_data in item_tables.item_table.items()
            if item_data.type in item_tables.upgrade_item_types
        ]

        for weapon_armor_upgrade in weapon_armor_upgrades:
            self.assertEqual(item_tables.item_table[weapon_armor_upgrade].quantity, item_tables.WEAPON_ARMOR_UPGRADE_MAX_LEVEL)

    def test_item_ids_distinct(self) -> None:
        """
        Verifies if there are no duplicates of item ID.
        """
        item_ids: set[int] = {item_tables.item_table[item_name].code for item_name in item_tables.item_table}

        self.assertEqual(len(item_ids), len(item_tables.item_table))

    def test_number_distinct_in_item_type(self) -> None:
        """
        Tests if each item is distinct for sending into the mod.
        """
        item_types: list[ItemType] = [
            *[item for item in item_tables.TerranItemType],
            *[item for item in item_tables.ZergItemType],
            *[item for item in item_tables.ProtossItemType],
            *[item for item in item_tables.FactionlessItemType
                if item is not item_tables.FactionlessItemType.Keys] # all keys use number 0
        ]
        self.assertGreater(len(item_types), 0)

        for item_type in item_types:
            for item_name in item_tables.item_table:
                item_names: list[str] = [
                item_name for item_name in item_tables.item_table
                if item_tables.item_table[item_name].number >= 0  # negative numbers have special meaning
                   and item_tables.item_table[item_name].type == item_type
            ]
            item_numbers = {item_tables.item_table[item_name].number for item_name in item_names}
            self.assertEqual(len(item_names), len(item_numbers))

    def test_progressive_has_quantity(self) -> None:
        """
        :return:
        """
        progressive_groups: list[ItemType] = [
            item_tables.TerranItemType.Progressive,
            item_tables.ProtossItemType.Progressive,
            item_tables.ZergItemType.Progressive
        ]

        quantities: list[int] = [
            item_tables.item_table[item].quantity for item in item_tables.item_table
            if item_tables.item_table[item].type in progressive_groups
        ]

        self.assertNotIn(1, quantities)

    def test_non_progressive_quantity(self) -> None:
        """
        Check if non-progressive items have quantity at most 1.
        """
        non_progressive_single_entity_groups: list[ItemType] = [
            # Terran
            item_tables.TerranItemType.Unit,
            item_tables.TerranItemType.Item,
            # Zerg
            item_tables.ZergItemType.Unit,
            item_tables.ZergItemType.Item,
            # Protoss
            item_tables.ProtossItemType.Unit,
            item_tables.ProtossItemType.Item,
        ]

        quantities: list[int] = [
            item_tables.item_table[item].quantity for item in item_tables.item_table
            if item_tables.item_table[item].type in non_progressive_single_entity_groups
        ]

        for quantity in quantities:
            self.assertLessEqual(quantity, 1)

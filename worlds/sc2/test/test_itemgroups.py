"""
Unit tests for item_groups.py
"""

import unittest
from ..item import item_groups, item_names, item_mod_ids, TerranItemType


class ItemGroupsUnitTests(unittest.TestCase):
    def test_all_production_structure_groups_capture_all_units(self) -> None:
        self.assertCountEqual(
            item_groups.terran_units,
            item_groups.barracks_units
            + item_groups.factory_units
            + item_groups.starport_units
            + item_groups.terran_mercenaries
        )
        self.assertCountEqual(
            item_groups.zerg_units,
            item_groups.zerg_nonmorph_units
            + item_groups.zerg_morphs
        )
        self.assertCountEqual(
            item_groups.protoss_units,
            item_groups.gateway_units
            + item_groups.robo_units
            + item_groups.stargate_units
            + item_groups.nexus_units
        )

    def test_terran_original_progressive_group_fully_contained_in_wol_upgrades(self) -> None:
        for item_name in item_groups.terran_original_progressive_upgrades:
            self.assertEqual(
                item_mod_ids.item_id_table[item_name].item_type,
                TerranItemType.Progressive,
                f"{item_name} is not progressive"
            )
            self.assertIn(item_name, item_groups.wol_upgrades)

    def test_all_items_in_stimpack_group_are_stimpacks(self) -> None:
        for item_name in item_groups.terran_stimpacks:
            self.assertIn("Stimpack", item_name)

    def test_all_item_group_names_have_a_group_defined(self) -> None:
        for display_name in item_groups.ItemGroupNames.get_all_group_names():
            self.assertIn(display_name, item_groups.item_name_groups)

    def test_artanis_weapon_aspect_groups_are_classified_correctly(self) -> None:
        self.assertCountEqual(item_groups.artanis_weapon_aspect_active, [
            item_names.ARTANIS_BLADE_WALTZ,
            item_names.ARTANIS_CLEANSING_SMITE,
            item_names.ARTANIS_EXTERMINATE,
            item_names.ARTANIS_SHADOW_SLICE,
        ])
        self.assertCountEqual(item_groups.artanis_weapon_aspect_passive, [
            item_names.ARTANIS_CLOLARIONS_CONFIDENCE,
            item_names.ARTANIS_MALASHS_MALEVOLENCE,
            item_names.ARTANIS_RASZAGALS_RHYTHM,
            item_names.ARTANIS_TASSADARS_TEACHINGS,
        ])

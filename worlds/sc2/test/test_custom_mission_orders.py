"""
Unit tests for custom mission orders
"""

from .test_base import Sc2SetupTestBase
from .. import MissionFlag
from ..item import item_tables, item_names
from BaseClasses import ItemClassification
from .. import options
from ..mission_tables import SC2Mission, SC2Race
from ..tables import HeroFlag
from ..mission_order import entry_rules


class TestCustomMissionOrders(Sc2SetupTestBase):
    def test_custom_mission_order_can_assign_exact_heroes_to_slots(self):
        world_options = {
            **self.ALL_CAMPAIGNS,
            'mission_order': 'custom',
            'hero_presence': 'anywhere',
            'enabled_heroes': ['Kerrigan', 'Nova', 'Artanis'],
            'custom_mission_order': {
                'Hero Slots': {
                    'type': 'column',
                    'size': 3,
                    'missions': [
                        {
                            'index': 0,
                            'mission_pool': [SC2Mission.LIBERATION_DAY.mission_name],
                            'heroes': ['kerrigan'],
                        },
                        {
                            'index': 1,
                            'mission_pool': [SC2Mission.RENDEZVOUS.mission_name],
                            'heroes': ['nova', 'artanis'],
                        },
                        {
                            'index': 2,
                            'mission_pool': [SC2Mission.FOR_AIUR.mission_name],
                            'heroes': [],
                        },
                    ],
                },
            },
        }

        self.generate_world(world_options)

        self.assertEqual(self.world.hero_presence[SC2Mission.LIBERATION_DAY], HeroFlag.KERRIGAN)
        self.assertEqual(self.world.hero_presence[SC2Mission.RENDEZVOUS], HeroFlag.NOVA | HeroFlag.ARTANIS)
        self.assertEqual(self.world.hero_presence[SC2Mission.FOR_AIUR], HeroFlag.NONE)

    def test_custom_mission_order_heroes_override_disabled_heroes(self):
        world_options = {
            **self.ALL_CAMPAIGNS,
            'mission_order': 'custom',
            'hero_presence': 'vanilla',
            'enabled_heroes': [],
            'custom_mission_order': {
                'Disabled Hero Slot': {
                    'type': 'column',
                    'size': 1,
                    'missions': [
                        {
                            'index': 0,
                            'mission_pool': [SC2Mission.THE_OUTLAWS.mission_name],
                            'heroes': ['Kerrigan', 'Nova', 'Artanis'],
                        },
                    ],
                },
            },
        }

        self.generate_world(world_options)

        self.assertEqual(
            self.world.hero_presence[SC2Mission.THE_OUTLAWS],
            HeroFlag.KERRIGAN | HeroFlag.NOVA | HeroFlag.ARTANIS,
        )
        self.assertNotIn(SC2Mission.THE_OUTLAWS, self.world.logic.grant_hero_items)

    def test_mini_wol_generates(self):
        world_options = {
            **self.ALL_CAMPAIGNS,
            'mission_order': 'custom',
            'custom_mission_order': {
                'Mini Wings of Liberty': {
                    'global': {
                        'type': 'column',
                        'mission_pool': [
                            'terran missions',
                            '^ wol missions'
                        ]
                    },
                    'Mar Sara': {
                        'size': 1
                    },
                    'Colonist': {
                        'size': 2,
                        'entry_rules': [{
                            'scope': '../Mar Sara'
                        }]
                    },
                    'Artifact': {
                        'size': 3,
                        'entry_rules': [{
                            'scope': '../Mar Sara'
                        }],
                        'missions': [
                            {
                                'index': 1,
                                'entry_rules': [{
                                'scope': 'Mini Wings of Liberty',
                                'amount': 4
                                }]
                            },
                            {
                                'index': 2,
                                'entry_rules': [{
                                'scope': 'Mini Wings of Liberty',
                                'amount': 8
                                }]
                            }
                        ]
                    },
                    'Prophecy': {
                        'size': 2,
                        'entry_rules': [{
                            'scope': '../Artifact/1'
                            }],
                        'mission_pool': [
                            'protoss missions',
                            '^ prophecy missions'
                        ]
                    },
                    'Covert': {
                        'size': 2,
                        'entry_rules': [{
                            'scope': 'Mini Wings of Liberty',
                            'amount': 2
                        }]
                    },
                    'Rebellion': {
                        'size': 2,
                        'entry_rules': [{
                            'scope': 'Mini Wings of Liberty',
                            'amount': 3
                        }]
                    },
                    'Char': {
                        'size': 3,
                        'entry_rules': [{
                            'scope': '../Artifact/2'
                        }],
                        'missions': [
                            {
                                'index': 0,
                                'next': [2]
                            },
                            {
                                'index': 1,
                                'entrance': True
                            }
                        ]
                    }
                }
            }
        }

        self.generate_world(world_options)
        flags = self.world.custom_mission_order.get_used_flags()
        self.assertEqual(flags[MissionFlag.Terran], 13)
        self.assertEqual(flags[MissionFlag.Protoss], 2)
        self.assertEqual(flags.get(MissionFlag.Zerg, 0), 0)
        sc2_regions = set(self.multiworld.regions.region_cache[self.player]) - {"Menu"}
        self.assertEqual(len(self.world.custom_mission_order.get_used_missions()), len(sc2_regions))

    def test_entry_rule_indexing(self) -> None:
        world_options = {
            options.OPTION_NAME[options.MissionOrder]: 'custom',
            options.OPTION_NAME[options.SelectedRaces]: [SC2Race.TERRAN.get_title()],
            options.OPTION_NAME[options.CustomMissionOrder]: {
                'campaign': {
                    'layout': {
                        'type': 'grid',
                        'size': 9,
                        'missions': [
                            {'index': 'all', 'entrance': True},
                            {'index': 'point(1, 1)', 'empty': True},
                            {'index': 1, 'entry_rules': {'scope': '../0'}},
                            {'index': 2, 'entry_rules': {'scope': './-8+1-1'}},
                            {'index': 6, 'entry_rules': {'scope': './rect(x, y-1, 5, 1)'}},
                            {'index': [3, 7], 'entry_rules': {'scope': './point(x+1, y-1)'}},
                            {'index': -1, 'entry_rules': {'scope': './(1+2)*2 + 1'}},  # == 7
                        ],
                    }
                },
                'campaign2': {
                    'goal': True,
                    'layout2': {
                        'type': 'canvas',
                        'canvas': ['ab', 'cd'],
                        'missions': [
                            {'index': 'rect(0, 0, 2, 1)', 'entrance': True},
                            {'index': 'group(a)', 'entry_rules': {'scope': '../../../campaign/layout/-1'}},
                            {'index': 'group(b)', 'entry_rules': {'scope': '../../../campaign/layout/point(y, x)'}},
                        ]
                    }
                }
            },
        }
        self.generate_world(world_options)
        missions = self.world.custom_mission_order.mission_order_node.campaigns[0].layouts[0].missions
        final_missions = self.world.custom_mission_order.mission_order_node.campaigns[1].layouts[0].missions
        # check mission scope ./0 == first mission
        self.assertEqual(len(missions[1].entry_rule.rules_to_check), 1)
        assert isinstance(missions[1].entry_rule.rules_to_check[0], entry_rules.CountMissionsEntryRule)
        self.assertEqual(missions[1].entry_rule.rules_to_check[0].missions_to_count[0], missions[0])
        # check mission scope ./-8 == second mission
        self.assertEqual(len(missions[2].entry_rule.rules_to_check), 1)
        assert isinstance(missions[2].entry_rule.rules_to_check[0], entry_rules.CountMissionsEntryRule)
        self.assertEqual(missions[2].entry_rule.rules_to_check[0].missions_to_count[0], missions[1])
        # check mission scope ./(1+2)*2+1 == 7
        self.assertEqual(len(missions[-1].entry_rule.rules_to_check), 1)
        assert isinstance(missions[-1].entry_rule.rules_to_check[0], entry_rules.CountMissionsEntryRule)
        self.assertEqual(missions[-1].entry_rule.rules_to_check[0].missions_to_count[0], missions[7])
        # check middle mission, point(1, 1) is empty
        self.assertTrue(missions[4].option_empty)
        # check mission scope ./rect(x, y-1, 5, 1) from mission 6=(0, 2) is the middle row (indices 3,-,5)
        self.assertEqual(len(missions[6].entry_rule.rules_to_check), 1)
        assert isinstance(missions[6].entry_rule.rules_to_check[0], entry_rules.CountMissionsEntryRule)
        self.assertIn(missions[3], missions[6].entry_rule.rules_to_check[0].missions_to_count)
        self.assertIn(missions[5], missions[6].entry_rule.rules_to_check[0].missions_to_count)
        # check mission scope ./point(x+1, y-1) from mission 3=(0, 1) is mission 1=(1, 0)
        self.assertEqual(len(missions[3].entry_rule.rules_to_check), 1)
        assert isinstance(missions[3].entry_rule.rules_to_check[0], entry_rules.CountMissionsEntryRule)
        self.assertEqual(missions[3].entry_rule.rules_to_check[0].missions_to_count[0], missions[1])
        # check mission scope ./point(x+1, y-1) from mission 7=(1, 2) is mission 5=(2, 1)
        self.assertEqual(len(missions[7].entry_rule.rules_to_check), 1)
        assert isinstance(missions[7].entry_rule.rules_to_check[0], entry_rules.CountMissionsEntryRule)
        self.assertEqual(missions[7].entry_rule.rules_to_check[0].missions_to_count[0], missions[5])
        # check mission scope ../../../campaign/layout/-1 points to missions[-1]
        self.assertEqual(len(final_missions[0].entry_rule.rules_to_check), 1)
        assert isinstance(final_missions[0].entry_rule.rules_to_check[0], entry_rules.CountMissionsEntryRule)
        self.assertEqual(final_missions[0].entry_rule.rules_to_check[0].missions_to_count[0], missions[-1])
        # check mission scope ../../../campaign/layout/point(y, x) from final missions (1, 0) points to missions[3]
        self.assertEqual(len(final_missions[1].entry_rule.rules_to_check), 1)
        assert isinstance(final_missions[1].entry_rule.rules_to_check[0], entry_rules.CountMissionsEntryRule)
        self.assertEqual(final_missions[1].entry_rule.rules_to_check[0].missions_to_count[0], missions[3])

    def test_locked_and_necessary_item_appears_once(self):
        # This is a filler upgrade with a parent
        test_item = item_names.MARINE_OPTIMIZED_LOGISTICS
        world_options = {
            'mission_order': 'custom',
            'locked_items': { test_item: 1 },
            'custom_mission_order': {
                'test': {
                    'type': 'column',
                    'size': 5, # Give the generator some space to place the key
                    'max_difficulty': 'easy',
                    'missions': [{
                        'index': 4,
                        'entry_rules': [{
                            'items': { test_item: 1 }
                        }]
                    }]
                }
            }
        }

        self.assertNotEqual(item_tables.item_table[test_item].apclass, ItemClassification.progression, f"Test item {test_item} won't change classification")

        self.generate_world(world_options)
        test_items_in_pool = [item for item in self.multiworld.itempool if item.name == test_item]
        test_items_in_pool += [item for item in self.multiworld.precollected_items[self.player] if item.name == test_item]
        self.assertEqual(len(test_items_in_pool), 1)
        self.assertEqual(test_items_in_pool[0].classification, ItemClassification.progression)

    def test_start_inventory_and_necessary_item_appears_once(self):
        # This is a filler upgrade with a parent
        test_item = item_names.ZERGLING_METABOLIC_BOOST
        world_options = {
            'mission_order': 'custom',
            'enabled_campaigns': set(options.EnabledCampaigns.valid_keys),
            'start_inventory': { test_item: 1 },
            'custom_mission_order': {
                'test': {
                    'type': 'column',
                    'size': 5, # Give the generator some space to place the key
                    'max_difficulty': 'easy',
                    'missions': [{
                        'index': 4,
                        'entry_rules': [{
                            'items': { test_item: 1 }
                        }]
                    }]
                }
            }
        }

        self.generate_world(world_options)
        test_items_in_pool = [item for item in self.multiworld.itempool if item.name == test_item]
        self.assertEqual(len(test_items_in_pool), 0)
        test_items_in_start_inventory = [item for item in self.multiworld.precollected_items[self.player] if item.name == test_item]
        self.assertEqual(len(test_items_in_start_inventory), 1)

    def test_start_inventory_and_locked_and_necessary_item_appears_once(self):
        # This is a filler upgrade with a parent
        test_item = item_names.ZERGLING_METABOLIC_BOOST
        world_options = {
            'mission_order': 'custom',
            'enabled_campaigns': set(options.EnabledCampaigns.valid_keys),
            'start_inventory': { test_item: 1 },
            'locked_items': { test_item: 1 },
            'custom_mission_order': {
                'test': {
                    'type': 'column',
                    'size': 5, # Give the generator some space to place the key
                    'max_difficulty': 'easy',
                    'missions': [{
                        'index': 4,
                        'entry_rules': [{
                            'items': { test_item: 1 }
                        }]
                    }]
                }
            }
        }

        self.generate_world(world_options)
        test_items_in_pool = [item for item in self.multiworld.itempool if item.name == test_item]
        self.assertEqual(len(test_items_in_pool), 0)
        test_items_in_start_inventory = [item for item in self.multiworld.precollected_items[self.player] if item.name == test_item]
        self.assertEqual(len(test_items_in_start_inventory), 1)

    def test_key_item_rule_creates_correct_item_amount(self):
        # This is an item that normally only exists once
        test_item = item_names.ZERGLING
        test_amount = 3
        world_options = {
            **self.ALL_CAMPAIGNS,
            'mission_order': 'custom',
            'locked_items': { test_item: 1 }, # Make sure it is generated as normal
            'custom_mission_order': {
                'test': {
                    'type': 'column',
                    'size': 12, # Give the generator some space to place the keys
                    'max_difficulty': 'easy',
                    'mission_pool': ['zerg missions'], # Make sure the item isn't excluded by race selection
                    'missions': [{
                        'index': 10,
                        'entry_rules': [{
                            'items': { test_item: test_amount } # Require more than the usual item amount
                        }]
                    }]
                }
            }
        }

        self.generate_world(world_options)
        test_items_in_pool = [item for item in self.multiworld.itempool if item.name == test_item]
        test_items_in_start_inventory = [item for item in self.multiworld.precollected_items[self.player] if item.name == test_item]
        self.assertEqual(len(test_items_in_pool + test_items_in_start_inventory), test_amount)

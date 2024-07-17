from __future__ import annotations
from typing import Set, Callable, Dict, List, Union, TYPE_CHECKING, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass

from ..mission_tables import SC2Mission
from BaseClasses import CollectionState

if TYPE_CHECKING:
    from .structs import SC2MOGenMission

class EntryRule(ABC):
    def is_always_fulfilled(self) -> bool:
        return self.is_fulfilled(set())

    @abstractmethod
    def is_fulfilled(self, beaten_missions: Set[SC2MOGenMission]) -> bool:
        """Used during region creation to ensure a beatable mission order."""
        return False
    
    @abstractmethod
    def to_lambda(self, player: int) -> Callable[[CollectionState], bool]:
        """Passed to Archipelago for use during item placement."""
        return lambda _: False
    
    @abstractmethod
    def to_slot_data(self) -> RuleData:
        """Used in the client to determine accessibility while playing and to populate tooltips."""
        return {}

@dataclass
class RuleData(ABC):
    @abstractmethod
    def is_fulfilled(self, beaten_missions: Set[int]) -> bool:
        return False
    
    @abstractmethod
    def tooltip(self, indents: int, missions: Dict[int, SC2Mission]) -> str:
        return ""

class BeatMissionsEntryRule(EntryRule):
    missions_to_beat: Set[SC2MOGenMission]
    visual_reqs: List[Union[str, SC2MOGenMission]]

    def __init__(self, missions_to_beat: Set[SC2MOGenMission], visual_reqs: List[Union[str, SC2MOGenMission]]):
        self.missions_to_beat = missions_to_beat
        self.visual_reqs = visual_reqs
    
    def is_fulfilled(self, beaten_missions: Set[SC2MOGenMission]) -> bool:
        return beaten_missions.issuperset(self.missions_to_beat)
    
    def to_lambda(self, player: int) -> Callable[[CollectionState], bool]:
        return lambda state: state.has_all([mission.beat_item() for mission in self.missions_to_beat], player)
    
    def to_slot_data(self) -> RuleData:
        resolved_reqs: List[Union[str, int]] = [req if type(req) == str else req.mission.id for req in self.visual_reqs]
        mission_ids = {mission.mission.id for mission in self.missions_to_beat}
        return BeatMissionsRuleData(
            mission_ids,
            resolved_reqs
        )

@dataclass
class BeatMissionsRuleData(RuleData):
    mission_ids: Set[int]
    visual_reqs: List[Union[str, int]]

    def is_fulfilled(self, beaten_missions: Set[int]) -> bool:
        return beaten_missions.issuperset(self.mission_ids)
    
    def tooltip(self, indents: int, missions: Dict[int, SC2Mission]) -> str:
        indent = " ".join("" for _ in range(indents))
        if len(self.visual_reqs) == 1:
            req = self.visual_reqs[0]
            return f"Beat {missions[req].mission_name if type(req) == int else req}"
        tooltip = f"Beat all of these:\n{indent}- "
        reqs = [missions[req].mission_name if type(req) == int else req for req in self.visual_reqs]
        tooltip += f"\n{indent}- ".join(req for req in reqs)
        return tooltip
    
class CountMissionsEntryRule(EntryRule):
    missions_to_count: Set[SC2MOGenMission]
    target_amount: int
    visual_reqs: List[Union[str, SC2MOGenMission]]

    def __init__(self, missions_to_count: Set[SC2MOGenMission], target_amount: int, visual_reqs: List[Union[str, SC2MOGenMission]]):
        self.missions_to_count = missions_to_count
        if target_amount == -1 or target_amount > len(missions_to_count):
            self.target_amount = len(missions_to_count)
        else:
            self.target_amount = target_amount
        self.visual_reqs = visual_reqs

    def is_fulfilled(self, beaten_missions: Set[SC2MOGenMission]) -> bool:
        return self.target_amount <= len(beaten_missions.intersection(self.missions_to_count))
    
    def to_lambda(self, player: int) -> Callable[[CollectionState], bool]:
        return lambda state: self.target_amount <= sum(state.has(mission.beat_item(), player) for mission in self.missions_to_count)
    
    def to_slot_data(self) -> RuleData:
        resolved_reqs: List[Union[str, int]] = [req if type(req) == str else req.mission.id for req in self.visual_reqs]
        mission_ids = {mission.mission.id for mission in self.missions_to_count}
        return CountMissionsRuleData(
            mission_ids,
            self.target_amount,
            resolved_reqs
        )

@dataclass
class CountMissionsRuleData(RuleData):
    mission_ids: Set[int]
    amount: int
    visual_reqs: List[Union[str, int]]

    def is_fulfilled(self, beaten_missions: Set[int]) -> bool:
        return self.amount <= len(beaten_missions.intersection(self.mission_ids))
    
    def tooltip(self, indents: int, missions: Dict[int, SC2Mission]) -> str:
        indent = " ".join("" for _ in range(indents))
        if self.amount == len(self.mission_ids):
            amount = "all"
        else:
            amount = str(self.amount)
        if len(self.visual_reqs) == 1:
            req = self.visual_reqs[0]
            req_str = missions[req].mission_name if type(req) == int else req
            if self.amount == 1:
                return f"Beat {req_str}"
            return f"Beat {amount} missions from {req_str}"
        if self.amount == 1:
            tooltip = f"Beat {amount} mission from:\n{indent}- "
        else:
            tooltip = f"Beat {amount} missions from:\n{indent}- "
        reqs = [missions[req].mission_name if type(req) == int else req for req in self.visual_reqs]
        tooltip += f"\n{indent}- ".join(req for req in reqs)
        return tooltip
    
class SubRuleEntryRule(EntryRule):
    rules_to_check: List[EntryRule]
    target_amount: int

    def __init__(self, rules_to_check: List[EntryRule], target_amount: int):
        self.rules_to_check = rules_to_check
        if target_amount == -1 or target_amount > len(rules_to_check):
            self.target_amount = len(rules_to_check)
        else:
            self.target_amount = target_amount

    def is_fulfilled(self, beaten_missions: Set[SC2MOGenMission]) -> bool:
        return self.target_amount <= sum(rule.is_fulfilled(beaten_missions) for rule in self.rules_to_check)
    
    def to_lambda(self, player: int) -> Callable[[CollectionState], bool]:
        sub_lambdas = [rule.to_lambda(player) for rule in self.rules_to_check]
        return lambda state, sub_lambdas=sub_lambdas: self.target_amount <= sum(sub_lambda(state) for sub_lambda in sub_lambdas)
    
    def to_slot_data(self) -> RuleData:
        sub_rules = [rule.to_slot_data() for rule in self.rules_to_check]
        return SubRuleRuleData(
            sub_rules,
            self.target_amount
        )

@dataclass
class SubRuleRuleData(RuleData):
    sub_rules: List[RuleData]
    amount: int

    def is_fulfilled(self, beaten_missions: Set[int]) -> bool:
        return self.amount <= sum(rule.is_fulfilled(beaten_missions) for rule in self.sub_rules)
    
    @staticmethod
    def parse_from_dict(data: Dict[str, Any]) -> SubRuleRuleData:
        amount = data["amount"]
        sub_rules: List[RuleData] = []
        for rule_data in data["sub_rules"]:
            if "sub_rules" in rule_data:
                rule = SubRuleRuleData.parse_from_dict(rule_data)
            elif "amount" in rule_data:
                rule = CountMissionsRuleData(
                    **{field: value for field, value in rule_data.items()}
                )
            else:
                rule = BeatMissionsRuleData(
                    **{field: value for field, value in rule_data.items()}
                )
            sub_rules.append(rule)
        return SubRuleRuleData(
            sub_rules,
            amount
        )
    
    @staticmethod
    def empty() -> SubRuleRuleData:
        return SubRuleRuleData([], 0)
    
    def tooltip(self, indents: int, missions: Dict[int, SC2Mission]) -> str:
        indent = " ".join("" for _ in range(indents))
        if self.amount == len(self.sub_rules):
            if self.amount == 1:
                return self.sub_rules[0].tooltip(indents, missions)
            amount = "all"
        else:
            amount = str(self.amount)
        tooltip = f"Fulfill {amount} of these conditions:\n{indent}- "
        tooltip += f"\n{indent}- ".join(rule.tooltip(indents + 2, missions) for rule in self.sub_rules)
        return tooltip

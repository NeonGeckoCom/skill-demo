# NEON AI (TM) SOFTWARE, Software Development Kit & Application Development System
#
# Copyright 2008-2021 Neongecko.com Inc. | All Rights Reserved
#
# Notice of License - Duplicating this Notice of License near the start of any file containing
# a derivative of this software is a condition of license for this software.
# Friendly Licensing:
# No charge, open source royalty free use of the Neon AI software source and object is offered for
# educational users, noncommercial enthusiasts, Public Benefit Corporations (and LLCs) and
# Social Purpose Corporations (and LLCs). Developers can contact developers@neon.ai
# For commercial licensing, distribution of derivative works or redistribution please contact licenses@neon.ai
# Distributed on an "AS IS” basis without warranties or conditions of any kind, either express or implied.
# Trademarks of Neongecko: Neon AI(TM), Neon Assist (TM), Neon Communicator(TM), Klat(TM)
# Authors: Guy Daniels, Daniel McKnight, Regina Bloomstine, Elon Gasper, Richard Leeds
#
# Specialized conversational reconveyance options from Conversation Processing Intelligence Corp.
# US Patents 2008-2021: US7424516, US20140161250, US20140177813, US8638908, US8068604, US8553852, US10530923, US10530924
# China Patent: CN102017585  -  Europe Patent: EU2156652  -  Patents Pending
import os
import shutil
import unittest
from os import mkdir

import pytest

from time import sleep
from copy import deepcopy
from os.path import dirname, join, exists
from mock import Mock
from mycroft_bus_client import Message
from ovos_utils.messagebus import FakeBus


class TestSkill(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        from mycroft.skills.skill_loader import SkillLoader

        bus = FakeBus()
        bus.run_in_thread()
        skill_loader = SkillLoader(bus, dirname(dirname(__file__)))
        skill_loader.load()
        cls.skill = skill_loader.instance
        cls.test_fs = join(dirname(__file__), "skill_fs")
        if not exists(cls.test_fs):
            mkdir(cls.test_fs)
        cls.skill.settings_write_path = cls.test_fs
        cls.skill.file_system.path = cls.test_fs
        cls.skill._init_settings()
        cls.skill.initialize()
        # Override speak and speak_dialog to test passed arguments
        cls.skill.speak = Mock()
        cls.skill.speak_dialog = Mock()

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.test_fs)

    def test_00_skill_init(self):
        # Test any parameters expected to be set in init or initialize methods
        from neon_utils.skills import NeonSkill

        self.assertIsInstance(self.skill, NeonSkill)
        self.assertTrue(self.skill.settings["prompt_on_start"])

    def test_skill_show_demo_prompt_no_response(self):
        def ask_yesno(dialog):
            if dialog == "ask_demo":
                return ""
            if dialog == "ask_demo_next_time":
                return ""

        default_ask_yesno = self.skill.ask_yesno
        self.skill.ask_yesno = ask_yesno

        self.skill._show_demo_prompt(Message("mycroft.ready"))
        self.skill.speak_dialog.assert_called_with("confirm_demo_disabled")
        self.assertFalse(self.skill.settings["prompt_on_start"])

        self.skill.ask_yesno = default_ask_yesno

    def test_skill_show_demo_prompt_no_demo_no_response(self):
        def ask_yesno(dialog):
            if dialog == "ask_demo":
                return "no"
            if dialog == "ask_demo_next_time":
                return ""

        default_ask_yesno = self.skill.ask_yesno
        self.skill.ask_yesno = ask_yesno

        self.skill._show_demo_prompt(Message("mycroft.ready"))
        self.skill.speak_dialog.assert_called_with("confirm_demo_disabled")
        self.assertFalse(self.skill.settings["prompt_on_start"])

        self.skill.ask_yesno = default_ask_yesno

    def test_skill_show_demo_prompt_no_demo_no_next_time(self):
        def ask_yesno(dialog):
            if dialog == "ask_demo":
                return "no"
            if dialog == "ask_demo_next_time":
                return "no"

        default_ask_yesno = self.skill.ask_yesno
        self.skill.ask_yesno = ask_yesno

        self.skill._show_demo_prompt(Message("mycroft.ready"))
        self.skill.speak_dialog.assert_called_with("confirm_demo_disabled")
        self.assertFalse(self.skill.settings["prompt_on_start"])

        self.skill.ask_yesno = default_ask_yesno

    def test_skill_show_demo_prompt_no_demo_yes_next_time(self):
        def ask_yesno(dialog):
            if dialog == "ask_demo":
                return "no"
            if dialog == "ask_demo_next_time":
                return "yes"

        default_ask_yesno = self.skill.ask_yesno
        self.skill.ask_yesno = ask_yesno

        self.skill._show_demo_prompt(Message("mycroft.ready"))
        self.skill.speak_dialog.assert_called_with("confirm_demo_enabled")
        self.assertTrue(self.skill.settings["prompt_on_start"])

        self.skill.ask_yesno = default_ask_yesno

    def test_skill_show_demo_prompt_yes_demo(self):
        def ask_yesno(dialog):
            if dialog == "ask_demo":
                return "yes"
            if dialog == "ask_demo_next_time":
                return "yes"

        default_ask_yesno = self.skill.ask_yesno
        self.skill.ask_yesno = ask_yesno

        default_handle_show_demo = self.skill.handle_show_demo
        self.skill.handle_show_demo = Mock()

        message = Message("mycroft.ready", context={"neon_should_respond": True})
        self.skill._show_demo_prompt(message)
        self.skill.handle_show_demo.assert_called_with(message)
        self.assertFalse(self.skill.settings["prompt_on_start"])

        self.skill.ask_yesno = default_ask_yesno
        self.skill.handle_show_demo = default_handle_show_demo

    def test_show_demo_valid(self):
        self.skill.handle_show_demo(Message("recognizer_loop:utterance", context={"neon_should_respond": True}))
        self.skill.speak_dialog.assert_called_with("starting_demo")


if __name__ == '__main__':
    pytest.main()

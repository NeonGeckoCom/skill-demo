# NEON AI (TM) SOFTWARE, Software Development Kit & Application Framework
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2022 Neongecko.com Inc.
# Contributors: Daniel McKnight, Guy Daniels, Elon Gasper, Richard Leeds,
# Regina Bloomstine, Casimiro Ferreira, Andrii Pernatii, Kirill Hrymailo
# BSD-3 License
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS  BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS;  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE,  EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import pytest

from mock import Mock
from ovos_bus_client import Message
from neon_minerva.tests.skill_unit_test_base import SkillTestCase


class TestSkill(SkillTestCase):
    def test_00_skill_init(self):
        # Test any parameters expected to be set in init or initialize methods
        from neon_utils.skills import NeonSkill

        self.assertIsInstance(self.skill, NeonSkill)
        self.assertTrue(self.skill.prompt_on_start)

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
        self.assertFalse(self.skill.prompt_on_start)
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
        self.assertFalse(self.skill.prompt_on_start)
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
        self.assertFalse(self.skill.prompt_on_start)
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
        self.assertTrue(self.skill.prompt_on_start)
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

        message = Message("mycroft.ready",
                          context={"neon_should_respond": True})
        self.skill._show_demo_prompt(message)
        self.skill.handle_show_demo.assert_called_with(message)
        self.assertFalse(self.skill.prompt_on_start)
        self.assertFalse(self.skill.settings["prompt_on_start"])

        self.skill.ask_yesno = default_ask_yesno
        self.skill.handle_show_demo = default_handle_show_demo

    def test_show_demo_valid(self):
        self.skill._speak_prompt = Mock()
        self.skill._send_prompt = Mock()
        msg = Message("recognizer_loop:utterance",
                      context={"neon_should_respond": True})
        self.skill.handle_show_demo(msg)
        self.skill.speak_dialog.assert_any_call("starting_demo")
        args = self.skill.speak_dialog.call_args
        self.assertEqual(args[0][0], "finished_demo")

    # TODO: Implement tests for _get_demo_tts, _send_prompt, and _speak_prompt


if __name__ == '__main__':
    pytest.main()

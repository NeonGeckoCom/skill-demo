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


# class TestSkill(unittest.TestCase):

#     @classmethod
#     def setUpClass(cls) -> None:
#         from mycroft.skills.skill_loader import SkillLoader

#         bus = FakeBus()
#         bus.run_in_thread()
#         skill_loader = SkillLoader(bus, dirname(dirname(__file__)))
#         skill_loader.load()
#         cls.skill = skill_loader.instance
#         cls.test_fs = join(dirname(__file__), "skill_fs")
#         if not exists(cls.test_fs):
#             mkdir(cls.test_fs)
#         cls.skill.settings_write_path = cls.test_fs
#         cls.skill.file_system.path = cls.test_fs
#         cls.skill._init_settings()
#         cls.skill.initialize()
#         # Override speak and speak_dialog to test passed arguments
#         cls.skill.speak = Mock()
#         cls.skill.speak_dialog = Mock()

#     @classmethod
#     def tearDownClass(cls) -> None:
#         shutil.rmtree(cls.test_fs)

#     def test_00_skill_init(self):
#         # Test any parameters expected to be set in init or initialize methods
#         from neon_utils.skills import NeonSkill

#         self.assertIsInstance(self.skill, NeonSkill)
#         self.assertTrue(self.skill.settings["prompt_on_start"])

#     def test_skill_show_demo_prompt_no_response(self):
#         def ask_yesno(dialog):
#             if dialog == "ask_demo":
#                 return ""
#             if dialog == "ask_demo_next_time":
#                 return ""

#         default_ask_yesno = self.skill.ask_yesno
#         self.skill.ask_yesno = ask_yesno

#         self.skill._show_demo_prompt(Message("mycroft.ready"))
#         self.skill.speak_dialog.assert_called_with("confirm_demo_disabled")
#         self.assertFalse(self.skill.settings["prompt_on_start"])

#         self.skill.ask_yesno = default_ask_yesno

#     def test_skill_show_demo_prompt_no_demo_no_response(self):
#         def ask_yesno(dialog):
#             if dialog == "ask_demo":
#                 return "no"
#             if dialog == "ask_demo_next_time":
#                 return ""

#         default_ask_yesno = self.skill.ask_yesno
#         self.skill.ask_yesno = ask_yesno

#         self.skill._show_demo_prompt(Message("mycroft.ready"))
#         self.skill.speak_dialog.assert_called_with("confirm_demo_disabled")
#         self.assertFalse(self.skill.settings["prompt_on_start"])

#         self.skill.ask_yesno = default_ask_yesno

#     def test_skill_show_demo_prompt_no_demo_no_next_time(self):
#         def ask_yesno(dialog):
#             if dialog == "ask_demo":
#                 return "no"
#             if dialog == "ask_demo_next_time":
#                 return "no"

#         default_ask_yesno = self.skill.ask_yesno
#         self.skill.ask_yesno = ask_yesno

#         self.skill._show_demo_prompt(Message("mycroft.ready"))
#         self.skill.speak_dialog.assert_called_with("confirm_demo_disabled")
#         self.assertFalse(self.skill.settings["prompt_on_start"])

#         self.skill.ask_yesno = default_ask_yesno

#     def test_skill_show_demo_prompt_no_demo_yes_next_time(self):
#         def ask_yesno(dialog):
#             if dialog == "ask_demo":
#                 return "no"
#             if dialog == "ask_demo_next_time":
#                 return "yes"

#         default_ask_yesno = self.skill.ask_yesno
#         self.skill.ask_yesno = ask_yesno

#         self.skill._show_demo_prompt(Message("mycroft.ready"))
#         self.skill.speak_dialog.assert_called_with("confirm_demo_enabled")
#         self.assertTrue(self.skill.settings["prompt_on_start"])

#         self.skill.ask_yesno = default_ask_yesno

#     def test_skill_show_demo_prompt_yes_demo(self):
#         def ask_yesno(dialog):
#             if dialog == "ask_demo":
#                 return "yes"
#             if dialog == "ask_demo_next_time":
#                 return "yes"

#         default_ask_yesno = self.skill.ask_yesno
#         self.skill.ask_yesno = ask_yesno

#         default_handle_show_demo = self.skill.handle_show_demo
#         self.skill.handle_show_demo = Mock()

#         message = Message("mycroft.ready",
#                           context={"neon_should_respond": True})
#         self.skill._show_demo_prompt(message)
#         self.skill.handle_show_demo.assert_called_with(message)
#         self.assertFalse(self.skill.settings["prompt_on_start"])

#         self.skill.ask_yesno = default_ask_yesno
#         self.skill.handle_show_demo = default_handle_show_demo

#     def test_show_demo_valid(self):
#         self.skill._speak_prompt = Mock()
#         self.skill._send_prompt = Mock()
#         msg = Message("recognizer_loop:utterance",
#                       context={"neon_should_respond": True})
#         self.skill.handle_show_demo(msg)
#         self.skill.speak_dialog.assert_any_call("starting_demo")
#         args = self.skill.speak_dialog.call_args
#         self.assertEqual(args[0][0], "finished_demo")

#     # TODO: Implement tests for _get_demo_tts, _send_prompt, and _speak_prompt

class TestSkillIntentMatching(unittest.TestCase):
    # Import and initialize installed skill
    from skill_demo import DemoSkill
    skill = DemoSkill()
    import yaml
    test_intents = join(dirname(__file__), 'test_intents.yaml')
    with open(test_intents) as f:
        valid_intents = yaml.safe_load(f)

    from mycroft.skills.intent_service import IntentService
    bus = FakeBus()
    intent_service = IntentService(bus)
    test_skill_id = 'test_skill.test'

    @classmethod
    def setUpClass(cls) -> None:
        cls.skill.config_core["secondary_langs"] = list(cls.valid_intents.keys())
        cls.skill._startup(cls.bus, cls.test_skill_id)

    def test_intents(self):
        for lang in self.valid_intents.keys():
            for intent, examples in self.valid_intents[lang].items():
                intent_event = f'{self.test_skill_id}:{intent}'
                self.skill.events.remove(intent_event)
                intent_handler = Mock()
                self.skill.events.add(intent_event, intent_handler)
                for utt in examples:
                    if isinstance(utt, dict):
                        data = list(utt.values())[0]
                        utt = list(utt.keys())[0]
                    else:
                        data = list()
                    message = Message('test_utterance',
                                      {"utterances": [utt], "lang": lang})
                    self.intent_service.handle_utterance(message)
                    intent_handler.assert_called_once()
                    intent_message = intent_handler.call_args[0][0]
                    self.assertIsInstance(intent_message, Message)
                    self.assertEqual(intent_message.msg_type, intent_event)
                    for datum in data:
                        if isinstance(datum, dict):
                            name = list(datum.keys())[0]
                            value = list(datum.values())[0]
                        else:
                            name = datum
                            value = None
                        if name in intent_message.data:
                            # This is an entity
                            voc_id = name
                        else:
                            # We mocked the handler, data is munged
                            voc_id = f'{self.test_skill_id.replace(".", "_")}' \
                                     f'{name}'
                        self.assertIsInstance(intent_message.data.get(voc_id),
                                              str, intent_message.data)
                        if value:
                            self.assertEqual(intent_message.data.get(voc_id),
                                             value)
                    intent_handler.reset_mock()
                    
if __name__ == '__main__':
    pytest.main()

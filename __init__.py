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

from neon_utils import LOG
from neon_utils.message_utils import request_from_mobile
from neon_utils.skills import NeonSkill


class DemoSkill(NeonSkill):
    def __init__(self):
        super(DemoSkill, self).__init__(name="DemoSkill")

    def initialize(self):
        self.register_intent_file("show_demo.intent", self.handle_show_demo)

        # When first run or demo prompt not dismissed, wait for load and prompt user
        if self.settings["prompt_on_start"] and not self.server:
            self.bus.once('mycroft.ready', self._show_demo_prompt)

    def _show_demo_prompt(self, message):
        """
        Handles first run demo prompt
        :param message: message object associated with loaded emit
        """
        LOG.debug("Prompting Demo!")
        self.make_active()
        show_demo = self.ask_yesno("ask_demo")
        if show_demo == "yes":
            self.handle_show_demo(message)
            return
        elif show_demo == "no":
            ask_next_time = self.ask_yesno("ask_demo_next_time")
            if ask_next_time == "yes":
                self.speak_dialog("confirm_demo_enabled")
                self.update_skill_settings({"prompt_on_start": True})
                return
            self.speak_dialog("confirm_demo_disabled")
        else:
            self.speak_dialog("confirm_demo_disabled")
        self.update_skill_settings({"prompt_on_start": False})

    def handle_show_demo(self, message):
        """
        Starts the demoNeon shell script
        :param message: message object associated with request
        """
        if self.neon_in_request(message):
            if request_from_mobile(message):
                pass
            elif self.server:
                pass
            else:
                self.speak_dialog("starting_demo")
                # TODO: Make a new demo or find the old one DM


def create_skill():
    return DemoSkill()

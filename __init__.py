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

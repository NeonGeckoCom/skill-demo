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

from copy import deepcopy
from tempfile import mkstemp
from threading import Event
from time import sleep
from typing import Optional
from mycroft_bus_client import Message
from neon_utils import LOG
from neon_utils.message_utils import get_message_user, dig_for_message
from neon_utils.signal_utils import wait_for_signal_clear
from neon_utils.skills import NeonSkill
from neon_utils.user_utils import get_user_prefs
from ovos_plugin_manager.templates import TTS
from ovos_utils.sound import play_wav

from mycroft.skills import intent_file_handler


class DemoSkill(NeonSkill):
    def __init__(self):
        super(DemoSkill, self).__init__(name="DemoSkill")
        self._active_demos = dict()
        self._speak_timeout = 15
        self._handler_timeout = 10
        self._audio_output_done = Event()

    @property
    def demo_tts_plugin(self) -> str:
        """
        Get the TTS engine spec to use for the demo user
        """
        return self.settings.get("demo_tts_engine") or \
            self.config_core["tts"].get("fallback_module") or \
            "ovos-tts-plugin-mimic"

    def initialize(self):
        # When demo prompt enabled, wait for load and prompt user
        if self.settings["prompt_on_start"]:
            self.bus.once('mycroft.ready', self._show_demo_prompt)
        self.add_event("recognizer_loop:audio_output_start", self._audio_started)
        self.add_event("recognizer_loop:audio_output_end", self._audio_stopped)

    def _audio_started(self, _):
        self._audio_output_done.clear()

    def _audio_stopped(self, _):
        self._audio_output_done.set()

    def _show_demo_prompt(self, message):
        """
        Handles first run demo prompt
        :param message: message object associated with loaded emit
        """
        LOG.debug("Prompting Demo!")
        self.make_active()
        show_demo = self.ask_yesno("ask_demo")
        if show_demo == "yes":
            message.context['neon_should_respond'] = True
            message.context['username'] = 'local'
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

    @intent_file_handler("show_demo.intent")
    def handle_show_demo(self, message):
        """
        Starts a brief demo
        :param message: message object associated with request
        """
        if not self.neon_in_request(message):
            return
        # TODO: Parse demo language from request
        lang = self.lang
        # Track demo state for the user
        user = get_message_user(message)
        self._active_demos[user] = Event()
        # Define a demo profile so user profile isn't modified
        profile = deepcopy(get_user_prefs(message))
        profile['user']['username'] = 'demo'
        profile['units']['measure'] = 'imperial'
        # Confirm demo is starting
        self._audio_output_done.clear()  # Clear signal to wait for intro speak
        self.speak_dialog("starting_demo")
        # Read the demo prompts
        demo_file = self.find_resource("demo.txt")
        with open(demo_file) as f:
            demo_prompts = f.read().split('\n')
        # Define message context for the 'demo' user
        message_context = {
            "neon_should_respond": True,
            "username": "demo",
            "user_profiles": [profile],
            "source": ["demo"]
        }
        # Define a message that will be updated with any profile changes
        message = Message("recognizer_loop:utterance", context=message_context)
        prompter = {"name": "Demo",
                    "language": lang,
                    "gender": "female" if profile['speech'].get('tts_gender')
                            == "male" else "female"}
        # Initialize the demo TTS
        tts = self._get_demo_tts()
        # Iterate over demo prompts until done or user says 'stop'
        for prompt in demo_prompts:
            if self._active_demos[user].is_set():
                # Check to stop before speaking the prompt
                break
            self._speak_prompt(prompt, prompter, tts)
            if self._active_demos[user].is_set():
                # Check to stop before executing the prompt
                break
            LOG.info(message.context['user_profiles'][0]['units']['measure'])
            message.data = {"lang": lang,
                            "utterances": [prompt.lower()]}
            self._send_prompt(message)

        self.speak_dialog("finished_demo")
        self._active_demos.pop(user)

    def _send_prompt(self, message: Message):
        """
        Send a message to skill processing and wait for it to be handled
        :param message: Message to emit to skills
        """
        self._audio_output_done.clear()  # Clear to wait for this response
        resp = self.bus.wait_for_response(message,
                                          "mycroft.skill.handler.complete",
                                          self._handler_timeout)
        if not resp:
            LOG.error(f"Handler not completed for: "
                      f"{message.data.get('utterances')}")
        else:
            message.context['user_profiles'] = resp.context['user_profiles']
        if not self._audio_output_done.wait(self._speak_timeout):
            LOG.error(f"Timed out waiting")
        else:
            sleep(0.5)
            # Wait for anything not yet in the audio queue
            wait_for_signal_clear("isSpeaking", self._speak_timeout)

    def _speak_prompt(self, prompt: str, prompter: dict, tts: Optional[TTS]):
        """
        Speak the prompt in a user's voice and wait for playback to end
        :param prompt: User request to speak that will be emitted to skills
        :param prompter: Speaker config to use for spoken prompts
        """
        self._audio_output_done.wait(self._speak_timeout)
        if tts:
            # If available, use skill-managed TTS
            _, output_file = mkstemp()
            wav_file, _ = tts.get_tts(prompt, output_file)
            # TODO: If server, self.send_with_audio
            play_wav(wav_file,
                     self.config_core.get("play_wav_cmdline")).wait(
                self._speak_timeout)
        else:
            # Else fallback to audio module (probably same voice
            self.speak(prompt, speaker=prompter)
            self._audio_output_done.wait(self._speak_timeout)

    def _get_demo_tts(self, lang: str = None) -> Optional[TTS]:
        """
        Create a TTS plugin instance to
        """
        from ovos_plugin_manager.tts import OVOSTTSFactory
        engine = self.demo_tts_plugin
        lang = lang or self.lang
        config = {"module": engine,
                  "lang": lang}
        try:
            return OVOSTTSFactory.create(config)
        except Exception as e:
            LOG.error(f"Failed to load TTS Plugin: {self.demo_tts_plugin}")
            LOG.error(e)
        try:
            LOG.info("Trying with configured fallback_module")
            config['module'] = self.config_core["tts"].get("fallback_module")
            return OVOSTTSFactory.create(config)
        except Exception as e:
            LOG.error(f"Failed to load TTS Plugin: {self.demo_tts_plugin}")
            LOG.error(e)
        return None

    def stop(self):
        user = get_message_user(dig_for_message())
        if user in self._active_demos:
            LOG.info(f"{user} requested stop")
            self._active_demos[user].set()


def create_skill():
    return DemoSkill()

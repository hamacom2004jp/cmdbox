.. -*- coding: utf-8 -*-

****************************************************
Text-to-Speech (TTS)
****************************************************

This document explains how to use the Text-to-Speech (TTS) functionality in `cmdbox`. The TTS feature allows you to convert text into speech using various configurations.

Overview
========

The TTS functionality is implemented using the following modules:

- `cmdbox.app.features.cli.cmdbox_tts_install`: Install required TTS dependencies.
- `cmdbox.app.features.cli.cmdbox_tts_say`: Convert text into speech and play it.
- `cmdbox.app.features.cli.cmdbox_tts_start`: Start the TTS service.
- `cmdbox.app.features.cli.cmdbox_tts_stop`: Stop the TTS service.

Each command is executed using the `cmdbox` CLI with the `-m tts` mode and the corresponding `-c` command.

Commands
========

1. **Install TTS Dependencies**

   Use the `install` command to set up the required dependencies for TTS functionality.

   Example:
   ```
   cmdbox -m tts -c install --client_only --tts_engine voicevox --voicevox_ver 0.16.0 --voicevox_os linux --voicevox_arc x86 --voicevox_device cpu --voicevox_whl voicevox_core-0.16.0-cp310-abi3-manylinux_2_34_x86_64.whl
   ```

   This command ensures that all necessary libraries and tools for TTS are installed.

2. **Start TTS Service**

   Use the `start` command to start the TTS service. This is useful for applications that require continuous TTS processing.

   Example:
   ```
   cmdbox -m tts -c start --tts_engine voicevox --voicevox_model ずんだもんノーマル
   ```

3. **Convert Text to Speech**

   Use the `say` command to convert text into speech and play it immediately.

   Example:
   ```
   cmdbox -m tts -c say --tts_engine voicevox --voicevox_model ずんだもんノーマル --tts_text "Hello, world!"
   ```

4. **Stop TTS Service**

   Use the `stop` command to stop the TTS service.

   Example:
   ```
   cmdbox -m tts -c stop --tts_engine voicevox --voicevox_model ずんだもんノーマル
   ```

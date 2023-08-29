# Cortana

 It is a fun project to be able to interact with ChatGPT with audio, and it allows programmers to have the response in their favourite markdown editor.

## Installing

```
$ pip install -r requirements.txt
```

## Features

Here are the cool features I implemented:

- Markdown reader (by default, it's Mark text, you can change it for whatever you want)
- Multi-discussion (select any file you want)
- Voice and text (you can activate an inline discussion as if you were discussing with Cortana, ... however it's slow!)
- Prompt Image (using the command `Prompt image` and then asking for whatever you want is going to create images)

## Language

By default, the language is English, but you can use French as well. To do so, you have to add the extension of Sphinx for [french](https://github.com/Uberi/speech_recognition/blob/master/reference/pocketsphinx.rst) into the appropriate folder: `speech_recognition\pocketsphinx-data\fr-FR`

## API key

You need to create a file `api_key.py` inside which you have `secret_key` with the API provided in your openIA account. 

## Video presentation

Check my amateur [video presentation](https://youtu.be/IIm2TONVlyU), presenting the app's last update!

## News

**Done:**

- [x] Simplification of app launching
- [x] Adding preprompt options (persona, text, voice, role)
- [x] Adding API key manager + encryption

**In the future:**

- [ ] Adding more option for speech-to-text and text-to-speech.
- [ ] Adding pre-defined persona and roles in selection directly in the app
- [ ] Adding a light icon when Cortana is listening in the active mode
- [ ] Adding a shutdown button when in active mode
- [ ] Adding a voice and record button to use with the passive mode

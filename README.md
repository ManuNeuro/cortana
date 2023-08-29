# Cortana

 It is a project to interact with ChatGPT4 with audio, and it allows programmers to have the response in their favourite markdown editor.

## Installing

```
$ pip install -r requirements.txt
```

## Features

Here are the cool features I implemented:

- Markdown reader (by default, it's Mark text, you can change it for whatever you want)
- Multi-discussion (select any file you want)
- Voice and text (you can activate the active mode, an audio discussion as if you were discussing with Cortana... however, it's slow!)
- Prompt Image (using the command `Prompt image` and then asking for whatever you want is going to create images)

## Language

By default, the language is English, but you can use French as well. To do so, you have to add the extension of Sphinx for [french](https://github.com/Uberi/speech_recognition/blob/master/reference/pocketsphinx.rst) into the appropriate folder: `speech_recognition\pocketsphinx-data\fr-FR`

## API key

You need to provide the API key delivered in your openIA account. You will be prompted to do so directly in the interface of the app, and then the key is going to be encrypted before it's saved.

## Video presentation

Check my amateur [video presentation](https://youtu.be/IIm2TONVlyU), presenting the app's previous update! <br>
Once I updated the STT and TTS, I will be recording one of **the first podcasts showcasing the capabilities of an AI!**

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

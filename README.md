# Cortana

 It is a project to interact with ChatGPT4 with audio, and it allows programmers to have the response in their favourite markdown editor.

## Installing

```
$ pip install -r requirements.txt
```

## Features

Here are the cool features I implemented:

- Markdown reader (by default, it's Mark text, you can change it for whatever you want)

![image](https://github.com/ManuNeuro/cortana/assets/11985689/61a514eb-a85d-4ab3-9ea4-80001123d346)

- Multi-discussion (select any file you want)
- Voice and text (you can activate the active mode, an audio discussion as if you were discussing with Cortana... however, it's slow!)

![image](https://github.com/ManuNeuro/cortana/assets/11985689/6b23afe8-4a08-43af-b1b3-f63bdf3f05dd)


- Prompt Image (using the command `Prompt image` and then asking for whatever you want is going to create images)

## Language

By default, the language is English, but you can use French as well. To do so, you have to add the extension of Sphinx for [french](https://github.com/Uberi/speech_recognition/blob/master/reference/pocketsphinx.rst) into the appropriate folder: `speech_recognition\pocketsphinx-data\fr-FR`

## API key

You need to provide the API key delivered in your openIA account. You will be prompted to do so directly in the interface of the app, and then the key is going to be encrypted before it's saved.

## Video presentation

Check my amateur [video presentation](https://youtu.be/IIm2TONVlyU), presenting the app's previous update! 

Once I updated the STT and TTS, I will be recording one of **the first podcasts showcasing the capabilities of an AI!**

## News

**Done:**

- [x] Simplification of app launching for users
- [x] Adding preprompt options (persona, text, voice, role)
- [x] Adding API key manager + encryption
- [x] Adding a light icon when Cortana is in the active mode
- [x] Adding a shutdown button when in active mode
- [x] Adding more option for speech-to-text and text-to-speech.
- [x] Adding model and roles selection directly in the app.
- [x] Transfering the app towards CustomTk.
- [x] Adding an external window for active mode.
- [x] Cleaning and factoring the codes
- [x] Speeding up active mode

**In the future:**

- [ ] Test and debug functionalities
- [ ] Adding markdown display in active mode
- [ ] Adding a voice and recording button in passive mode
- [ ] Adding langchain: internet access
- [ ] Adding langchain: python REPL to run code
- [ ] Adding Local open-source LLM models

# Known bugs
- In active mode, the commands "Deactivate" and "ShutDown" do not work.
- In active idle mode, the command activate does not work.
- While using double screens, moving the app from one to another messes up with the layout.
- API Key button is not working anymore

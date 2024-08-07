# pet_project_voice_assistant
A voice assistant empowered with the fine-tuned version of BERT transformer model for the better user experience.

### This project created for Windowns could implement several actions:
- Recognise speech
- Synthesize speech using two different voices (depends on the settings of the assistant)
- Play greetings/farewells to user
- Inform user about the current state of weather
- Perform a weather forecast
- Inform user about current time
- Find term on wikipedia
- Serach for a song and open it on Spotify
- Tell a joke to user

### For a quick installement of the required libraries use command
`pip install requirements.txt`

### Natural Language Understanding
The BERT model fron the Hugging Face was fine tuned for a single lable text classification. I created the dataset `voiceassistant_dataset.json` to train and test the model.
The code for the fine-tuning the model is in the `BERT_fine_tuning_for_voice_assistant.ipynb` file.

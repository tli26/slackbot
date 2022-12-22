from dotenv import dotenv_values
import openai

config = dotenv_values(".env")
openai.organization = config['ORGANIZATION']
openai.api_key = config['OPENAI_API_KEY']

default_config = {
    'model': "text-davinci-003",
    'temperature': 0.85,
    'top_p': 1,
    'max_tokens': 256,
    'frequency_penalty': 0,
    'presence_penalty': 0.7,
    'best_of': 1
}


class OpenaiManager:
    def __init__(self):
        self.config = default_config

    def get_config(self):
        return self.config

    def set_config(self, key, value):
        if key not in self.config:
            return None
        if key == 'model':
            self.config[key] = value
        else:
            self.config[key] = int(value)
        return key

    def generate_code(self, prompt):
        print('Generating code ...')
        openai_response = openai.Completion.create(
            prompt=prompt,
            **self.config
        )
        return openai_response, openai_response['choices'][0]['text']


if __name__ == '__main__':
    test_prompt = "write a firebase query using typescript that retrieves all of the documents from the “score” collection where the field gameUid is equal to “soccer” and the dateAdded field is no older than 2 days"
    openai_manager = OpenaiManager()
    response, text = openai_manager.generate_code(test_prompt)
    print(text)

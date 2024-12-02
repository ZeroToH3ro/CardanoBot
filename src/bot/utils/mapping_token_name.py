import json

class FormatTokenName:
    @staticmethod
    def load_token_name():
        """Load tokens data from the JSON file and create a mapping dictionary."""
        try:
            with open("src/bot/tokens.json", "r") as tokens_file:
                tokens_data = json.load(tokens_file)
            # Create a mapping dictionary: {token_id: token_ascii}
            tokens_mapping = {
                token["token_id"]: token["token_ascii"] for token in tokens_data
            }

            return tokens_mapping
        except Exception as e:
            print(e)

        return {}

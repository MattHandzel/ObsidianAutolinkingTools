from bert_topic_modeling import *
import ollama

MODEL_NAME = "llama3.2"

system_message = """
The topic is described by the following keywords: [KEYWORDS]

Based on the information above, extract a short but highly descriptive topic label of at most 5 words. Make sure it is in the following format:
topic: <topic label>
"""


def query_ollama(user_message):

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            # {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ],
        options={"num_thread": 12},
    )
    return response["message"]["content"].strip().lower()


def load_bert_topic_model(path):
    # Load the BERT model
    model = BERTopic.load(path)
    return model


# Convert topics into a dictionary
topic_number_dictionary = {
    -1: "UNKNOWN",
}


# topic_model.get_document_info(docs) -> DataFrame
def convert_topics_to_labels(topics):
    return [topic_number_dictionary[str(topic)] for topic in topics]


def get_topics_for_every_note(note_path, meta_data, content, root_directory):

    if detect_language(content) != "en":
        return None, None, False
    topics = run_inference_on_bert_topic_model(bert_topic_model, content)
    topics = convert_topics_to_labels(topics)
    print(f"Topics for {note_path}: {topics}")

    return None, None, False


def manually_review_topics(topics):
    for key, topic_word_distribution in topics.items():
        result = input(
            "Please give a high level topic label for the following keywords:\t"
            + ", ".join([z[0] for z in topic_word_distribution])
            + "\n"
        )
        topic_number_dictionary[str(key)] = result


def populate_topic_number_dictionary(raw_topics):
    manual_review_topics = {}
    raw_topics.pop(-1)
    for key, topic_word_distribution in raw_topics.items():
        print(f"Reviewing {key}", ", ".join([z[0] for z in topic_word_distribution]))

        try:
            result = query_ollama(
                f"""Your task is to provide high level topic labels for a variety of key words. You need to extract the underlying theme, do not focus on details. There is noise in the keywords because they were extracted from a topic modeling method.
    The topic will be described a set of key words.

    Based on keywords, extract a short, high level topic label of at most 3 words. Make sure it is in the following format:
    topic: <topic label>

    Ex:
    ```
    Input:
    [arcade game, mario bros, arcade, super mario, wii, video game, sega, game boy, nintendo, wargames]
    Response:
    topic: video games
    ```

    Input:
    [{', '.join([z[0] for z in topic_word_distribution])}]
    """,
            ).split("topic: ")[1]

            topic_number_dictionary[key] = result
        except Exception as e:
            print("Unable to label this topic, adding to manual review")
            manual_review_topics[key] = topic_word_distribution

    if len(manual_review_topics) > 0:
        manually_review_topics(manual_review_topics)


if __name__ == "__main__":
    bert_topic_model = load_bert_topic_model("bert_topic_model_150k.pkl")
    # dictionary = populate_topic_number_dictionary(bert_topic_model.get_topics())
    #
    # # Save dictionary

    #
    # with open("topic_number_dictionary.json", "w") as f:
    #     json.dump(topic_number_dictionary, f)

    # load dictionary
    with open("topic_number_dictionary.json", "r") as f:
        topic_number_dictionary = json.load(f)

    parser = argparse.ArgumentParser()
    parser.add_argument("root_directory", type=str)
    args = parser.parse_args()
    root_directory = args.root_directory
    loop_through_notes(root_directory, [get_topics_for_every_note])

    print(bert_topic_model.get_topics())

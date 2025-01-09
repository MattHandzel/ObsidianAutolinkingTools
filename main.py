"""
This code will add links to your notes based off the folder directories they are in
"""

from utils import *
from PARA_linking import link_folders_into_notes
from semantic_clustering import generate_embedding, find_similar_notes


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("root_directory", type=str)

    args = parser.parse_args()
    root_directory = args.root_directory

    loop_through_notes(root_directory, [link_folders_into_notes])  #

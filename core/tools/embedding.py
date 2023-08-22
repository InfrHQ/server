"""
:dev This page includes function & elements that deal with text vectorization
"""
from typing import List
import numpy as np  # noqa
from core.connectors.model import embedding_model


def get_text_list_as_vectors(text_list: List[str]):

    list_of_vectors = embedding_model.encode(text_list)
    list_of_vectors = [embedding.tolist() for embedding in list_of_vectors]
    return list_of_vectors

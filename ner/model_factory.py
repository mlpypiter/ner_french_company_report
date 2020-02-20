#  Licensed to the Apache Software Foundation (ASF) under one
#  or more contributor license agreements.  See the NOTICE file
#  distributed with this work for additional information
#  regarding copyright ownership.  The ASF licenses this file
#  to you under the Apache License, Version 2.0 (the
#  "License"); you may not use this file except in compliance
#  with the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing,
#  software distributed under the License is distributed on an
#  "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
#  KIND, either express or implied.  See the License for the
#  specific language governing permissions and limitations
#  under the License.

import spacy

# Managed type of tokens
from spacy.lang.fr import French
from spacy.tokenizer import Tokenizer

# entity_types = ["PERS", "PHONE_NUMBER", "LICENCE_PLATE",
#                 # "SOCIAL_SECURITY_NUMBER",
#                 "ORGANIZATION", "LAWYER", "JUDGE_CLERK",
#                 "ADDRESS", "COURT", "DATE", "RG",
#                 "BAR", "UNKNOWN"]
entity_types = ["nom", "PHONE_NUMBER", "LICENCE_PLATE",
                # "SOCIAL_SECURITY_NUMBER",
                "ORGANIZATION", "LAWYER", "JUDGE_CLERK",
                "ADDRESS", "COURT", "DATE", "RG",
                "BAR", "UNKNOWN", "nom", "dateDecision", "codePostal"]


def prevent_sentence_boundary_detection(doc):
    """
    Disable the sentence splitting done by Spacy
    More info: https://github.com/explosion/spaCy/issues/1032
    :param doc: a Spacy doc
    :return: a disable sentence splitting Spacy doc
    """
    for token in doc:
        # This will entirely disable spaCy's sentence detection
        token.is_sent_start = False
    return doc


def get_tokenizer(model: French) -> Tokenizer:
    split_char = r"[ ,\\.()-/\\|:;'\"+=!’?_+#“’']"
    extended_infix = [r'[:\\(\\)-\./#"“’\'—'] + model.Defaults.infixes
    infix_re = spacy.util.compile_infix_regex(extended_infix)
    prefix_re = spacy.util.compile_prefix_regex(tuple(list(model.Defaults.prefixes) + [split_char]))
    suffix_re = spacy.util.compile_suffix_regex(tuple(list(model.Defaults.suffixes) + [split_char]))

    tok = Tokenizer(model.vocab,
                    prefix_search=prefix_re.search,
                    suffix_search=suffix_re.search,
                    infix_finditer=infix_re.finditer,
                    token_match=None)
    return tok


def get_empty_model(load_labels_for_training: bool) -> French:
    """
    Generate an empty NER model
    :rtype: object
    """
    # Important to setup the right language because it impacts the tokenizer, sentences split, ...
    nlp = spacy.blank('fr')

    nlp.tokenizer = get_tokenizer(nlp)

    nlp.add_pipe(prevent_sentence_boundary_detection, name='prevent-sbd', first=True)
    ner = nlp.create_pipe('ner')
    # add labels
    if load_labels_for_training:
        for token_type in entity_types:
            ner.add_label(token_type)

    nlp.add_pipe(ner, last=True)

    return nlp
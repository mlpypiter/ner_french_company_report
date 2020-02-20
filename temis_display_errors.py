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
from spacy.tokens import Doc, Span
from spacy import displacy
from pathlib import Path
import pandas as pd
import csv
import os

from xml_extractions.extract_node_values import get_paragraph_from_file
from ner.model_factory import get_empty_model
from resources.config_provider import get_config_default

config_training = get_config_default()
model_dir_path = config_training["model_dir_path"]
xml_dev_path = config_training["xml_dev_path"]
nlp = get_empty_model(load_labels_for_training=False)
nlp = nlp.from_disk(model_dir_path)
######################## added by piter ################
def to_html(doc, output="/tmp", style="dep"):
    """Doc method extension for saving the current state as a displaCy
    visualization.
    """
    # generate filename from first six non-punct tokens
    file_name = "test_extract.html"
    html = displacy.render(doc, style=style, page=True)  # render markup
    if output is not None:
        output_path = Path(output)
        if not output_path.exists():
            output_path.mkdir()
        output_file = Path(output) / file_name
        output_file.open("a", encoding="utf-8").write(html)  # save to file
        print("Saved HTML to {}".format(output_file))
    else:
        print(html)

report_data_dir = config_training["html_out_put_dir"]
# for filename in os.listdir(report_data_dir):
#
#     if filename.endswith(".csv"):
#         current_path = os.path.join(report_data_dir, filename)
#     else:
#         continue
read_data = list()
with open("test_report.csv","r",encoding='utf-8') as file:
    data =  csv.reader(file)
    for row in  data:
        read_data.append(row)


Doc.set_extension("to_html", method=to_html)
str = " "
for line in read_data:
    doc = nlp(line[0])
#doc = nlp("12134651W - LE PUBLICATEUR LEGAL Aux termes d’un acte SSP en date à PA­ LAISEAU du 17/12/2018 a été constituée  une SAS U nommée : MRBISOL Objet : Bâtiment, rénovation, aménage­ ment ext/int, ravalement, peinture, isola­ tions. Capital : 4.000 € Siège social : 2 avenue  du 1er mai, 91120 Palaiseau Durée: 99  ans Président : M. MOUNIR MSALLEM,  14 Allée de Narbonne, 91300 Massy. La société sera immatriculée au Registre  du commerce et des sociétés de Évry.")
# for ent in doc.ents:
#     print(ent.label_, ent.text)
# add entity manually for demo purposes, to make it work without a model
    doc._.to_html(output=report_data_dir, style="ent")
######################## end piter ####################

#
# DEV_DATA = get_paragraph_from_file(xml_dev_path,
#                                    keep_paragraph_without_annotation=True)
#
# for case_id, texts, xml_extracted_text, annotations in DEV_DATA:
#     doc = nlp(texts)
#
#     spacy_extracted_text_ad_pp = [ent.text for ent in doc.ents if ent.label_ in ["ADDRESS", "PERS"]]
#
#     spacy_extracted_text = [ent.text for ent in doc.ents]
#     str_rep_spacy = ' '.join(spacy_extracted_text)
#     match = [span_xml in str_rep_spacy for span_xml in xml_extracted_text]
#
#     if sum(match) < len(xml_extracted_text):
#         print("XML")
#         print('Entities X', xml_extracted_text)
#         print('Entities S', [(ent.text, ent.label_) for ent in doc.ents])
#         print('Tokens', [(t.text, t.ent_type_, t.ent_iob) for t in doc])
#     elif len(xml_extracted_text) < len(spacy_extracted_text_ad_pp):
#         print("SPACY")
#         print('Entities X', xml_extracted_text)
#         print('Entities S', [(ent.text, ent.label_) for ent in doc.ents])
#         print('Tokens', [(t.text, t.ent_type_, t.ent_iob) for t in doc])

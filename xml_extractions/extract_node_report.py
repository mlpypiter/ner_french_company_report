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
#set PYTHONPATH=C:\path\to\dirWithScripts\;%PYTHONPATH%
# from typing import List, Tuple, Optional
# from attr import dataclass
# from lxml.etree import Element  # type: ignore
#
# from xml_extractions.common_xml_parser_function import replace_none, read_xml
import os
import sys
sys.path.append('.')
sys.path.append('../anonymisation-master/xml_extractions')
from typing import List, Tuple, Optional
from common_xml_parser_function import replace_none, read_xml

from attr import dataclass
from lxml.etree import Element  # type: ignore

@dataclass
class Offset:
    start: int
    end: int
    type: str

    def to_tuple(self) -> Tuple[int, int, str]:
        return self.start, self.end, self.type


@dataclass
class Paragraph:
    case_id: str
    text: str
    extracted_text: List[str]
    offsets: List[Offset]


Case = List[Paragraph]


def get_person_name(node: Element) -> Optional[Tuple[str, str]]:
    """
    Extract value of node <Personne>
    :param node: <Personne> from Lxml
    :return: a tuple with the content inside the node, and the tail content
    """
    assert node.tag == "Personne"
    for t in node.iterchildren(tag="Texte"):
        return replace_none(t.text), replace_none(node.tail)
    return None

def get_paragraph_with_entities(parent_node: Element) -> Tuple[str, List[str], List[Offset]]:
    """
    Extract the entities from paragraph nodes
    :param parent_node: the one containing the others
    :return: a tupple with (paragraph text, the value of the children nodes, the offset of the values from children)
    """
    contents: List[Tuple[str, str]] = list()
    iters = parent_node.iter()
    #for node in parent_node.iter():
    for node in iters:
        contents.append(node)
        # if node.tag == "Personne":
        #     person_name = get_person_name(node)
        #     if person_name is not None:
        #         name, after = person_name
        #         contents.append((name, "PERS"))
        #         contents.append((after, "after"))
        # elif node.tag == "P":
        #     text = replace_none(node.text)
        #     contents.append((text, node.tag))
        # elif node.tag == "Adresse":
        #     text = replace_none(node.text)
        #     tail = replace_none(node.tail)
        #     contents.append((text, "ADDRESS"))
        #     contents.append((tail, "after"))
        # elif node.tag in ["Texte", "TexteAnonymise", "President", "Conseiller", "Greffier", "AvocatGeneral"]:
        #     pass
        # else:
        #     raise NotImplementedError(f"Unexpected type of node: [{node.tag}], node content is [{node.text}] and is "
        #                               f"part of [{node.getparent().text}]")
    clean_content = list()
    extracted_text = list()
    offsets: List[Offset] = list()
    text_current_size = 0
    for content in contents:
        current_text_item = content[0]
        current_tag_item = content[1]
        current_item_text_size = len(current_text_item)

        clean_content.append(current_text_item)
        if current_tag_item in ["PERS", "ADDRESS"]:
            offsets.append(Offset(start=text_current_size,
                                  end=text_current_size + current_item_text_size,
                                  type=current_tag_item))
            extracted_text.append(current_text_item)
        text_current_size += current_item_text_size + 1

    paragraph_text = ' '.join(clean_content)
    return paragraph_text, extracted_text, offsets

def get_entity_values(node: Element):
    contents : List[Tuple[str, str]] = list()
    nodes = node.xpath('./evenements/evenement/personnes/personne/identite/nom | ./evenements/evenement/dateDecision |'
                       './evenements/personnes/personne/identite/etablissements/etablissement/adresse/codePostal')

    for node in nodes:
        if node.tag == "nom":
            contents.append(("nom", node.text))
        if node.tag == "dateDecision":
            contents.append(("dateDecision", node.text))
        if node.tag == "codePostal":
            contents.append(("codePostal", node.text))
    return contents

def get_paragraph_from_report(ad_id: str, report_node: Element, keep_paragraph_without_annotation: bool) -> List[Paragraph]:
    entities = get_entity_values(report_node)
    result = list()
    nodes = report_node.xpath('./annonceInfo/texte')
    for node in nodes:
        offsets = list()
        extracted_text = list()
        for entity in entities:
            node_text = node.text
            ent_start_pos = node_text.find(entity[1])
            if ent_start_pos == -1:
                continue
            offsets.append(Offset(start=ent_start_pos,
                                  end=ent_start_pos + len(entity[1]),
                                  type=entity[0]))
            extracted_text.append(entity[1])
        paragraph_text = node.text
        extracted_cnt = len(extracted_text)
        if extracted_cnt > 0:
            result.append(Paragraph(ad_id, paragraph_text, extracted_text, offsets))
            # paragraph_text, extracted_text, offset = get_paragraph_with_entities(node)
            # has_some_annotation = len(extracted_text) > 0
            # if has_some_annotation:
            #     # TODO replace by unit test
            #     item_text = extracted_text[0]
            #     current_attribute = offset[0]
            #     start = current_attribute.start
            #     end = current_attribute.end
            #     assert item_text == paragraph_text[start:end]
            # else:
            #     offset = list()
            #     extracted_text = list()
            # if has_some_annotation | keep_paragraph_without_annotation:
            #     result.append(Paragraph(ad_id, paragraph_text, extracted_text, offset))

    return result


def get_paragraph_from_file(path: str,
                            keep_paragraph_without_annotation: bool) -> List[Paragraph]:
    """
    Read paragraph from a file
    :param path: path to the XML file
    :param keep_paragraph_without_annotation: keep paragraph which doesn't include annotation according to Temis
    :return: a list of tupple (or a list of list of tuple) of (paragraph text, value inside node, offset)
    """
    result: List[Paragraph] = list()
    tree = read_xml(path)
    nodes = tree.xpath('//annonce')
    for node in nodes:
        idddd = node.xpath('./annonceInfo/adID')
        ad_id = idddd[0].text
        result.extend(get_paragraph_from_report(ad_id, node, keep_paragraph_without_annotation))

    return result
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
import sys
sys.path.append('../xml_extractions')
from typing import List

import regex

from extract_node_values import Offset

phone_regex = regex.compile(pattern=r"(?<!\d[[:punct:] ]*)"
                                    r"\b"
                                    r"(\()?0[1-9][\- \)\.]*"
                                    r"(\d\d[\- \(\)\.]*){4}"
                                    r"\b"
                                    r"(?![[:punct:] ]*\d)",
                            flags=regex.VERSION1)


def get_phone_number(text: str) -> List[Offset]:
    """
    Find phone number.
    Pattern catch numbers in one block or separated per block of 2 numbers
    :param text: original text
    :return: list of offsets
    """
    patterns = phone_regex.finditer(text)
    result = list()
    for pattern in patterns:
        if pattern is not None and ("compte" not in text):
            result.append(Offset(pattern.start(), pattern.end(), "PHONE_NUMBER"))
    return result
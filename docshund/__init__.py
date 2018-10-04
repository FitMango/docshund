#!/usr/bin/env python3
from typing import List

import re

_HEADER = r"\b(\w+):$"
_ARGUMENT = r"\b(\S+)(?:\s\((\S+)(?:\:\s(\S+))?\))?:\s+(.*)"
_DOCUMENTED_ENTITY = re.compile(
    r'''(class|def) (.+)\:\n\s+"""((?:.*\n)+?\s*)"""$''',
    re.MULTILINE
)


class Section:

    def __init__(self, title: str = None, contents = None) -> None:
        """
        """
        self.title = title
        self.contents = contents

    def to_markdown(self) -> str:
        md = ""

        if self.title:
            md += f"# {self.title}"

        if self.contents:
            md += self.contents

        return md


class Report:

    def __init__(self, sections: List[Section] = None) -> None:
        """
        """
        if sections is None:
            sections = []
        self.sections = sections


    def to_markdown(self) -> str:
        return "\n".join([s.to_markdown() for s in self.sections])

    def add_section(self, section: Section, pos: int = -1) -> None:
        if pos:
            self.sections.insert(pos, section)
        else:
            self.sections.append(section)


class Docshund:

    def __init__(self, **kwargs) -> None:
        """
        Create a new Docshund documentation engine.

        """

        self._language = kwargs.get("language", None)

        if self._language is None:
            pass
            # self._infer_language()

        self._indent_string = (" " * 4)

    def _get_indent_level(self, line: str) -> int:
        """
        Return the indent level, based upon the left spacing.
        """
        return len(line) - len(line.lstrip(self._indent_string))

    def _clean_docstring(self, docstring: str) -> List[str]:
        doclines = docstring.split("\n")
        base_indentation = self._get_indent_level(doclines[0]) if self._get_indent_level(doclines[0]) else self._get_indent_level(doclines[1])
        doclines = [d[base_indentation:] for d in doclines]

        reflowed: List[str] = []
        last_indentation = base_indentation
        for line in doclines:
            if line != "" and self._get_indent_level(line) == last_indentation:
                reflowed[-1] += " " + line
            else:
                reflowed.append(line)
                if line == "":
                    last_indentation = -1
                else:
                    last_indentation = self._get_indent_level(line)
        return reflowed

    def parse_docstring(self, docstring: str) -> str:
        """
        Renders a single docstring.

        """
        report = []
        description = None

        doclines = self._clean_docstring(docstring)

        for line in doclines:
            is_header = list(re.finditer(_HEADER, line))
            is_arg = list(re.finditer(_ARGUMENT, line))
            if len(is_header):
                report.append("## " + is_header[0].groups()[0])
            elif len(is_arg):
                varname, type, default, description = is_arg[0].groups()
                report.append(f"> - **{varname}** (`{type}`: `{default}`): {description}")

            else:
                report.append(line)

        return "\n".join([r.rstrip() for r in report])

    def parse_document(self, document: str) -> str:
        """
        Parse a full document, and generate markdown.

        Arguments:
            document (str): The document to parse; i.e. contents of src file

        Returns:
            str: The documentation, in markdown form

        """
        documentation = []
        entities = list(re.finditer(_DOCUMENTED_ENTITY, document))
        for e in entities:
            type, signature, doc = e.groups()
            type = {
                "def": "Function",
                "class": "Class"
            }[type]
            documentation.append("\n".join([
                f"# *{type}* `{signature}`",
                "",
                self.parse_docstring(doc)
            ]))
        return "\n-----\n".join(documentation)


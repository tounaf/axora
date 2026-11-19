import re
from pathlib import Path

from axora.extensions.bdd.introspector.interface import (
    ColumnInfo,
    DatabaseSchema,
    ForeignKeyInfo,
    SchemaIntrospectorInterface,
    TableInfo,
)

_IDENTIFIER = r'(?:`(?:``|[^`])*`|"(?:""|[^"])*"|\[(?:\]\]|[^\]])*\]|[A-Za-z_][\w$]*)'
_CREATE_TABLE = re.compile(
    rf"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?"
    rf"((?:{_IDENTIFIER}\s*\.\s*)?{_IDENTIFIER})\s*\(",
    re.IGNORECASE,
)
_ALTER_TABLE = re.compile(
    rf"ALTER\s+TABLE\s+((?:{_IDENTIFIER}\s*\.\s*)?{_IDENTIFIER})\s+(.*?);",
    re.IGNORECASE | re.DOTALL,
)


class SQLDumpParser(SchemaIntrospectorInterface):
    """Extracts tables, columns and relationships from common SQL DDL dumps."""

    def __init__(self, sql_source: str | Path, schema_name: str = "imported_db") -> None:
        if isinstance(sql_source, Path):
            path = sql_source
        elif "\n" not in sql_source and not re.search(r"\bCREATE\s+TABLE\b", sql_source, re.IGNORECASE):
            path = Path(sql_source)
        else:
            path = None

        if path is not None:
            if not path.is_file():
                raise FileNotFoundError(f"SQL dump file not found: {path.absolute()}")
            self.sql_content = path.read_text(encoding="utf-8", errors="replace")
            self.schema_name = path.stem
        else:
            self.sql_content = str(sql_source)
            self.schema_name = schema_name

    def introspect(self) -> DatabaseSchema:
        tables: dict[str, TableInfo] = {}

        for match in _CREATE_TABLE.finditer(self.sql_content):
            opening_paren = match.end() - 1
            closing_paren = self._find_matching_paren(self.sql_content, opening_paren)
            if closing_paren is None:
                continue

            table_name = self._unquote_identifier(match.group(1).split(".")[-1].strip())
            table_info = TableInfo(name=table_name)
            definition = self.sql_content[opening_paren + 1:closing_paren]
            self._parse_table_definition(definition, table_info)
            for primary_key_column in table_info.primary_key:
                if primary_key_column in table_info.columns:
                    table_info.columns[primary_key_column].is_primary_key = True
            tables[table_name] = table_info

        self._parse_alter_table_constraints(tables)

        for table in tables.values():
            if len(table.foreign_keys) >= 2:
                fk_columns = {fk.constrained_column for fk in table.foreign_keys}
                if set(table.primary_key) == fk_columns or len(table.columns) <= len(fk_columns) + 2:
                    table.is_junction = True

        return DatabaseSchema(name=self.schema_name, tables=tables)

    def _parse_table_definition(self, definition: str, table: TableInfo) -> None:
        for raw_item in self._split_top_level(definition, ","):
            item = self._strip_comments(raw_item).strip()
            if not item:
                continue

            constraint_name = None
            constraint_match = re.match(
                rf"CONSTRAINT\s+({_IDENTIFIER})\s+(.*)$",
                item,
                re.IGNORECASE | re.DOTALL,
            )
            if constraint_match:
                constraint_name = self._unquote_identifier(constraint_match.group(1))
                item = constraint_match.group(2).strip()

            primary_key = re.match(rf"PRIMARY\s+KEY\s*\((.*?)\)", item, re.IGNORECASE | re.DOTALL)
            if primary_key:
                table.primary_key = self._parse_identifier_list(primary_key.group(1))
                continue

            foreign_key = re.match(
                rf"FOREIGN\s+KEY\s*\((.*?)\)\s*REFERENCES\s+"
                rf"((?:{_IDENTIFIER}\s*\.\s*)?{_IDENTIFIER})\s*\((.*?)\)",
                item,
                re.IGNORECASE | re.DOTALL,
            )
            if foreign_key:
                self._add_foreign_keys(
                    table,
                    self._parse_identifier_list(foreign_key.group(1)),
                    foreign_key.group(2),
                    self._parse_identifier_list(foreign_key.group(3)),
                    constraint_name,
                )
                continue

            if re.match(r"^(?:UNIQUE|KEY|INDEX|CHECK)\b", item, re.IGNORECASE):
                continue

            column_match = re.match(rf"^\s*({_IDENTIFIER})\s+(.+)$", item, re.DOTALL)
            if not column_match:
                continue

            column_name = self._unquote_identifier(column_match.group(1))
            remainder = column_match.group(2).strip()
            type_match = re.match(
                r"^(character\s+varying|national\s+character\s+varying|double\s+precision|"
                r"timestamp\s+(?:with|without)\s+time\s+zone|time\s+(?:with|without)\s+time\s+zone|"
                r"[A-Za-z_]\w*)(?:\s*\([^)]*\))?",
                remainder,
                re.IGNORECASE,
            )
            if not type_match:
                continue

            sql_type = type_match.group(0).lower()
            constraints = remainder[type_match.end():]
            column = ColumnInfo(
                name=column_name,
                sql_type=sql_type,
                semantic_type=self._map_sql_type_to_semantic(sql_type, column_name, constraints),
                is_nullable=not bool(re.search(r"\bNOT\s+NULL\b", constraints, re.IGNORECASE)),
            )
            table.columns[column_name] = column

            if re.search(r"\bPRIMARY\s+KEY\b", constraints, re.IGNORECASE):
                table.primary_key.append(column_name)
                column.is_primary_key = True

            inline_reference = re.search(
                rf"\bREFERENCES\s+((?:{_IDENTIFIER}\s*\.\s*)?{_IDENTIFIER})\s*\(({_IDENTIFIER})\)",
                constraints,
                re.IGNORECASE,
            )
            if inline_reference:
                self._add_foreign_keys(
                    table,
                    [column_name],
                    inline_reference.group(1),
                    [inline_reference.group(2)],
                    constraint_name,
                )

    def _parse_alter_table_constraints(self, tables: dict[str, TableInfo]) -> None:
        for match in _ALTER_TABLE.finditer(self.sql_content):
            table_name = self._unquote_identifier(match.group(1).split(".")[-1].strip())
            table = tables.get(table_name)
            if table is None:
                continue

            body = match.group(2)
            for primary_key in re.finditer(r"\bADD\s+(?:CONSTRAINT\s+`?[\w$]+`?\s+)?PRIMARY\s+KEY\s*\((.*?)\)", body, re.IGNORECASE | re.DOTALL):
                table.primary_key = self._parse_identifier_list(primary_key.group(1))
                for column_name in table.primary_key:
                    if column_name in table.columns:
                        table.columns[column_name].is_primary_key = True

            for foreign_key in re.finditer(
                rf"\bADD\s+(?:CONSTRAINT\s+({_IDENTIFIER})\s+)?FOREIGN\s+KEY\s*"
                rf"\((.*?)\)\s*REFERENCES\s+((?:{_IDENTIFIER}\s*\.\s*)?{_IDENTIFIER})\s*\((.*?)\)",
                body,
                re.IGNORECASE | re.DOTALL,
            ):
                constraint_name = (
                    self._unquote_identifier(foreign_key.group(1))
                    if foreign_key.group(1)
                    else None
                )
                self._add_foreign_keys(
                    table,
                    self._parse_identifier_list(foreign_key.group(2)),
                    foreign_key.group(3),
                    self._parse_identifier_list(foreign_key.group(4)),
                    constraint_name,
                )

    def _add_foreign_keys(
        self,
        table: TableInfo,
        constrained_columns: list[str],
        referred_table: str,
        referred_columns: list[str],
        constraint_name: str | None,
    ) -> None:
        target_table = self._unquote_identifier(referred_table.split(".")[-1].strip())
        for constrained, referred in zip(constrained_columns, referred_columns):
            foreign_key = ForeignKeyInfo(
                constrained_column=self._unquote_identifier(constrained),
                referred_table=target_table,
                referred_column=self._unquote_identifier(referred),
                constraint_name=constraint_name,
            )
            if foreign_key not in table.foreign_keys:
                table.foreign_keys.append(foreign_key)

    def _map_sql_type_to_semantic(self, sql_type: str, column_name: str, constraints: str) -> str:
        normalized_type = sql_type.lower()
        base_type = normalized_type.split("(")[0].strip()
        if base_type in ("bool", "boolean") or (
            base_type == "tinyint" and ("(1)" in normalized_type or "bool" in column_name.lower())
        ):
            return "boolean"
        if any(value in base_type for value in ("int", "decimal", "numeric", "float", "double", "real", "serial")):
            return "number"
        if any(value in base_type for value in ("date", "time", "timestamp", "year")):
            return "date"
        if any(value in base_type for value in ("text", "clob")):
            return "text"
        if base_type == "json" or "dc2type:json" in constraints.lower() or "json" in column_name.lower():
            return "string"
        return "string"

    @staticmethod
    def _parse_identifier_list(value: str) -> list[str]:
        identifiers = []
        for item in SQLDumpParser._split_top_level(value, ","):
            identifier = re.match(rf"\s*({_IDENTIFIER})", item)
            if identifier:
                identifiers.append(SQLDumpParser._unquote_identifier(identifier.group(1)))
        return identifiers

    @staticmethod
    def _unquote_identifier(identifier: str) -> str:
        identifier = identifier.strip()
        if len(identifier) >= 2 and identifier[0] == "`" and identifier[-1] == "`":
            return identifier[1:-1].replace("``", "`")
        if len(identifier) >= 2 and identifier[0] == '"' and identifier[-1] == '"':
            return identifier[1:-1].replace('""', '"')
        if len(identifier) >= 2 and identifier[0] == "[" and identifier[-1] == "]":
            return identifier[1:-1].replace("]]", "]")
        return identifier

    @staticmethod
    def _split_top_level(value: str, delimiter: str) -> list[str]:
        parts: list[str] = []
        start = 0
        depth = 0
        quote: str | None = None
        index = 0
        while index < len(value):
            char = value[index]
            if quote:
                if char == quote:
                    if index + 1 < len(value) and value[index + 1] == quote:
                        index += 2
                        continue
                    quote = None
            elif char in ("'", '"', "`"):
                quote = char
            elif char == "[":
                quote = "]"
            elif char == "(":
                depth += 1
            elif char == ")":
                depth = max(0, depth - 1)
            elif value.startswith("--", index):
                line_end = value.find("\n", index)
                index = len(value) if line_end == -1 else line_end
                continue
            elif value.startswith("/*", index):
                comment_end = value.find("*/", index + 2)
                index = len(value) if comment_end == -1 else comment_end + 2
                continue
            elif char == delimiter and depth == 0:
                parts.append(value[start:index])
                start = index + 1
            index += 1
        parts.append(value[start:])
        return parts

    @staticmethod
    def _find_matching_paren(value: str, opening_index: int) -> int | None:
        depth = 0
        quote: str | None = None
        index = opening_index
        while index < len(value):
            char = value[index]
            if quote:
                if char == quote:
                    if index + 1 < len(value) and value[index + 1] == quote:
                        index += 2
                        continue
                    quote = None
            elif char in ("'", '"', "`"):
                quote = char
            elif char == "[":
                quote = "]"
            elif value.startswith("--", index):
                line_end = value.find("\n", index)
                index = len(value) if line_end == -1 else line_end
                continue
            elif value.startswith("/*", index):
                comment_end = value.find("*/", index + 2)
                index = len(value) if comment_end == -1 else comment_end + 2
                continue
            elif char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0:
                    return index
            index += 1
        return None

    @staticmethod
    def _strip_comments(value: str) -> str:
        value = re.sub(r"/\*.*?\*/", " ", value, flags=re.DOTALL)
        return re.sub(r"(?m)--.*$", " ", value)

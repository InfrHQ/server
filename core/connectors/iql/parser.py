class IQLParser:
    """
    IQL Parser is a class that converts string statements into valid SQL queries specific to the Infr platform.
    """

    def __init__(self, IQL_query):
        self.query = IQL_query
        self.version = "1.0.0"
        self.steps = []

        # Make flags
        self._make__include_screenshot = False
        self._make__include_bounding_box = False
        self._make__include_vector = False

        # Fields flags
        self._fields__keys = []
        self._fields__jsonb_fields = []

        # Return flags
        self._return__unique = False

    def parse(self):
        lines = self.query.split("\n")
        for line in lines:
            line = line.strip().lower()
            if line.startswith('use '):
                continue
            elif line.startswith('filter '):
                self._parse_filter(line)
            elif line.startswith('make '):
                self._parse_make(line)
            elif line.startswith('order by '):
                self._parse_order(line)
            elif line.startswith('limit '):
                self._parse_limit(line)
            elif line.startswith('offset '):
                self._parse_offset(line)
            elif line.startswith('fields '):
                self._parse_fields(line)
            elif line.startswith('geobox '):
                self._parse_geobox(line)
            elif line.startswith('vector search '):
                self._parse_vector_search(line)
            elif line.startswith('return '):
                self._parse_return(line)

        self._parse_final()

        return self.steps

    def _filter_test_split_fixed(self, op_val):
        list_of_valid_operators = ['equal to', 'not equal to', 'greater than', 'less than', 'greater than or equal to',
                                   'less than or equal to', 'includes', 'contains']

        split_result = []
        for operator in list_of_valid_operators:
            if operator in op_val:
                split_result = op_val.split(operator, 1)
                split_result[0] += " " + operator

                # Remove any double spaces
                split_result[0] = split_result[0].replace('  ', ' ')
                for i in range(len(split_result)):
                    split_result[i] = split_result[i].strip()
                break

        if len(split_result) == 2:
            operator, value = split_result
            return operator.strip(), self._filter_clean_value(value.strip())
        elif len(split_result) == 1:
            raise Exception("Operator not found or incorrect spacing.")
        else:
            raise Exception("Unexpected number of split results.")

    def _filter_clean_value(self, value):
        # Convert the value to the correct type
        if (value.startswith("'") or value.startswith('"')) and (value.endswith("'") or value.endswith('"')):
            value = self._filter_fix_string(value)
        elif value.startswith('[') and value.endswith(']'):
            value = self._filter_fix_list(value)
        else:
            value = self._filter_fix_string(value)
            value = self._filter_fix_number(value)

        return value

    def _filter_fix_string(self, value):
        if not isinstance(value, str):
            return value
        if value.startswith("'") and value.endswith("'"):
            value = value[1:-1]
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        return value

    def _filter_fix_number(self, value):
        if not isinstance(value, str):
            return value
        if value.isdigit():
            value = int(value)
        elif value.replace('.', '', 1).isdigit():
            value = float(value)
        return value

    def _filter_fix_list(self, value):
        if not isinstance(value, str):
            return value
        if value.startswith('[') and value.endswith(']'):
            value = value[1:-1]
            value = value.split(',')
            value = [self._filter_fix_string(item) for item in value]
            value = [self._filter_fix_number(item) for item in value]
        return value

    def _parse_filter(self, line):
        # Parse the filters from the IQL line
        filter_line = line.replace('filter ', '').strip()
        key, op_val = filter_line.split(' ', 1)
        operator, value = self._filter_test_split_fixed(op_val)

        # Detect additional qualifiers
        is_lowercase = 'lowercase' in op_val.lower()
        is_any = 'any' in op_val.lower()
        is_all = 'all' in op_val.lower()

        # If any of these qualifiers are present, add them to the operator
        if is_lowercase:
            operator += " lowercase"
        if is_any:
            operator += " any"
        if is_all:
            operator += " all"

        self.steps.append({
            "type": "filter",
            "args": {
                "key": key.strip(),
                "operator": operator.strip(),
                "value": value
            }
        })

    def _parse_make(self, line):
        # Parse the includes from the IQL line
        include_line = line.replace('make ', '')
        items = include_line.split(',')
        self.steps.append({
            "type": "make",
            "args": {
                "items": [item.strip() for item in items]
            }
        })

    def _parse_order(self, line):
        # Parse the order from the IQL line
        order_line = line.replace('order by ', '')
        key, direction = order_line.split(' ')
        self.steps.append({
            "type": "order",
            "args": {
                "key": key.strip(),
                "direction": direction.strip()
            }
        })

    def _parse_limit(self, line):
        # Parse the limit from the IQL line
        limit = line.replace('limit ', '')
        self.steps.append({
            "type": "limit",
            "args": {
                "limit": int(limit.strip())
            }
        })

    def _parse_offset(self, line):
        # Parse the offset from the IQL line
        offset = line.replace('offset ', '')
        self.steps.append({
            "type": "offset",
            "args": {
                "offset": int(offset.strip())
            }
        })

    def _parse_fields(self, line):
        # Parse the return fields from the IQL line
        fields = line.replace('fields ', '')
        self.steps.append({
            "type": "fields",
            "args": {
                "fields": [field.strip() for field in fields.split(',')]
            }
        })

    def _parse_geobox(self, line):
        # Parse the geobox from the IQL line
        lat, lng, width = line.replace('geobox ', '').split(',')
        self.steps.append({
            "type": "geobox",
            "args": {
                "lat": float(lat.strip()),
                "lng": float(lng.strip()),
                "width": float(width.strip())
            }
        })

    def _parse_vector_search(self, line):
        # Parse the vector search from the IQL line
        text, limit = line.replace('vector search ', '').split(',')
        if not limit:
            limit = 10
        else:
            limit = int(limit.strip())
        limit = int(limit)

        # Get the text vector
        self.steps.append({
            "type": "vector_search",
            "args": {
                "text": text.strip(),
                "limit": limit,
            }
        })

    def _parse_return(self, line):
        # Parse the unique logic if in return
        unique = line.replace('return ', '')
        is_unique = False
        if unique:
            if unique.strip() == 'unique':
                is_unique = True
        self._return__unique = is_unique
        self.steps.append({
            "type": "return",
            "args": {
                "unique": is_unique
            }
        })
        pass

    def _parse_final(self):
        """
        The final checks for the list of dicts parsed
        """

        # Ensure there is a limit obj
        # If not exists, create one with default 100 before return
        limit_exists = len([step for step in self.steps if step['type'] == 'limit']) > 0
        if not limit_exists:
            self._parse_limit('limit 100')

        # If there is a return obj, make sure its at the end
        return_exists = len([step for step in self.steps if step['type'] == 'return']) > 0
        if return_exists:
            return_step = [step for step in self.steps if step['type'] == 'return'][0]
            self.steps.remove(return_step)
            self.steps.append(return_step)

        return self.steps

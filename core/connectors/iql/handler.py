from core.schemas import Segment
from core.tools.embedding import get_text_list_as_vectors
from sqlalchemy import and_, desc, asc, func, or_
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from core.connectors.iql.parser import IQLParser


class IQLHandler(IQLParser):

    def _handle_filter(self, step, query):
        """
        Handle filtering steps to apply on a SQLAlchemy Query object.

        :param step: A dictionary containing the filtering step.
                    Example: {'args': {'key': 'name', 'operator': 'like', 'value': 'John'}}
        :param query: SQLAlchemy Query object on which to apply the filters.

        :return: Modified SQLAlchemy Query object.

        :dev: When adding new operators, ensure they are correctly mapped to SQLAlchemy methods.

        """

        # Extract filter arguments from the step
        key = step['args']['key']
        operator = step['args']['operator']
        value = step['args']['value']
        is_any = 'any' in operator
        is_all = 'all' in operator
        is_lowercase = 'lowercase' in operator

        # Check if the key indicates JSONB attributes
        is_jsonb = key.startswith("attributes.")
        if is_jsonb:
            key = key.replace("attributes.", "")
            segment_key = Segment.attributes.op('->>')(key)
        else:
            segment_key = getattr(Segment, key)

        # Convert UNIX timestamps to datetime objects if applicable
        if isinstance(value, int) or isinstance(value, float):
            try:
                value = datetime.utcfromtimestamp(value)
            except ValueError:
                pass

        # Handle different filter operators
        if is_lowercase:
            if isinstance(value, str):
                value = value.lower()
            elif isinstance(value, list):
                value = [v.lower() for v in value]
            segment_key = func.lower(segment_key)

        # Handle the basic operators
        if 'equal to' in operator:
            query = query.filter(segment_key == value)
        elif 'not equal to' in operator:
            query = query.filter(segment_key != value)
        elif 'greater than' in operator:
            query = query.filter(segment_key > value)
        elif 'less than' in operator:
            query = query.filter(segment_key < value)
        elif 'greater than or equal to' in operator:
            query = query.filter(segment_key >= value)
        elif 'less than or equal to' in operator:
            query = query.filter(segment_key <= value)

        # Handle the text & list operators
        conditions = []
        if 'includes' in operator:
            if not isinstance(value, list):
                raise ValueError(f'Invalid value for "includes" operator: {value}')
            for v in value:
                conditions.append(segment_key.in_([v]))

            if is_any:
                query = query.filter(or_(*conditions))
            elif is_all:
                query = query.filter(and_(*conditions))

        elif 'contains' in operator:
            if not isinstance(value, str):
                raise ValueError(f'Invalid value for "contains" operator: {value}')

            if is_lowercase:
                query = query.filter(segment_key.ilike(f'%{value}%'))
            else:
                query = query.filter(segment_key.contains(value))

        return query

    def _handle_make(self, step, query):
        """
        This function doesn't modify the query but could be used to set flags to include
        additional data such as screenshots or bounding boxes in the result set.

        :param step: A dictionary containing the "make" step.
        :param query: SQLAlchemy Query object (not modified in this function).

        :return: The query remains unmodified.
        """
        # The "make" logic could be implemented outside of SQL query,
        # for example, making additional data based on the query result.
        items = step['args']['items']
        if 'screenshot' in items:
            self._make__include_screenshot = True
        if 'bounding_box' in items:
            self._make__include_bounding_box = True
        if 'vector' in items:
            self._make__include_vector = True
        return query

    def _handle_order(self, step, query):
        """
        Handles ordering steps to sort the SQL query.

        :param step: A dictionary containing the "order" step.
        :param query: SQLAlchemy Query object.

        :return: Modified SQLAlchemy Query object with ordering.
        """
        key = step['args']['key']
        direction = step['args']['direction']

        if direction.lower() == 'desc':
            query = query.order_by(desc(getattr(Segment, key)))
        else:
            query = query.order_by(asc(getattr(Segment, key)))

        return query

    def _handle_limit(self, step, query):
        """
        Handles limit steps to limit the number of results in the SQL query.

        :param step: A dictionary containing the "limit" step.
        :param query: SQLAlchemy Query object.

        :return: Modified SQLAlchemy Query object with limit applied.
        """
        limit = int(step['args']['limit'])
        return query.limit(limit)

    def _handle_offset(self, step, query):
        """
        Handles offset steps to skip a number of results in the SQL query.

        :param step: A dictionary containing the "offset" step.
        :param query: SQLAlchemy Query object.

        :return: Modified SQLAlchemy Query object with offset applied.
        """
        offset = int(step['args']['offset'])
        return query.offset(offset)

    def _handle_fields(self, step, query):
        """
        Modifies the query to only fetch the specified fields.

        :param step: A dictionary containing the "fields" step.
        :param query: SQLAlchemy Query object.

        :return: Modified SQLAlchemy Query object with only the specified fields.
        """
        fields = step['args']['fields']
        # Prepare list to hold SQLAlchemy column objects
        sqlalchemy_fields = []

        for key in fields:
            is_jsonb = key.startswith("attributes.")

            if is_jsonb:
                self._fields__jsonb_fields.append(key.replace("attributes.", ""))
                key = key.replace("attributes.", "")
                # If it is a JSONB field, use the op method to fetch it
                sqlalchemy_fields.append(Segment.attributes.op('->>')(key).label(key))
            else:
                # Otherwise, it's a regular field, so just use getattr
                sqlalchemy_fields.append(getattr(Segment, key))

        # Modify the query to only include the specified fields
        query = query.with_entities(*sqlalchemy_fields)

        return query

    def _handle_geobox(self, step, query):
        """
        Handles geobox steps to filter results based on geographical coordinates.

        :param step: A dictionary containing the "geobox" step.
        :param query: SQLAlchemy Query object.

        :return: Modified SQLAlchemy Query object with geobox filter applied.
        """
        lat = step['args']['lat']
        lng = step['args']['lng']
        width = step['args']['width']

        lat_br = lat - width  # bottom right latitude
        lng_br = lng + width  # bottom right longitude

        query = query.filter(
            and_(Segment.lat >= lat_br, Segment.lat <= lat,
                 Segment.lng >= lng, Segment.lng <= lng_br)
        )
        return query

    def _handle_vector_search(self, step, query):
        """
        Handles vector search steps to filter and sort results based on vector similarity.

        :param step: A dictionary containing the "vector_search" step.
        :param query: SQLAlchemy Query object.

        :return: Modified SQLAlchemy Query object with vector search applied.
        """
        text = step['args']['text']
        limit = step['args']['limit']
        vector = get_text_list_as_vectors([text])[0]

        # Assuming you have set up an index on the `vector` column with pgvector
        query = query.order_by(Segment.vector.l2_distance(vector)).limit(limit)
        return query

    def _handle_return(self, query):
        """
        This function returns the segment objects as JSON.

        :param query: SQLAlchemy Query object

        :return:
            - If unique false:
                - A LIST of SEGMENT DICT (to_json) objects.
            - If unique true:
                - A DICT of UNIQUE SEGMENT KEY objects.
                    eg. {'id': ['123', '234'], 'name': ['John', 'Jane']}
        """
        is_unique = self._return__unique

        # Execute the query and convert segments to JSON representation
        segments = query.all()  # type: ignore
        with ThreadPoolExecutor() as executor:
            results = list(executor.map(self._fetch_json, segments))

        if is_unique:
            # Initialize an empty dictionary to hold unique values
            unique_values = {}
            for segment in results:
                for key, value in segment.items():
                    if key not in unique_values:
                        unique_values[key] = []
                    if value not in unique_values[key]:
                        unique_values[key].append(value)
            return unique_values
        else:
            return results

    def _fetch_json(self, segment):
        """
        Convert a Segment object or SQLAlchemy Row to JSON representation.
        :param segment: Segment object or SQLAlchemy Row.
        :return: JSON representation of the Segment object.
        """

        if isinstance(segment, Segment):
            return segment.to_json(
                get_vector=self._make__include_vector,
                get_screenshot=self._make__include_screenshot,
                get_bounding_box=self._make__include_bounding_box
            )
        else:
            # If it's a SQLAlchemy Row, convert it to a dictionary
            row_dict = segment._asdict()

            # Check if we have any JSONB fields
            if self._fields__jsonb_fields:
                attributes_dict = {}
                for field in self._fields__jsonb_fields:
                    if field in row_dict:
                        attributes_dict[field] = row_dict.pop(field)

                row_dict['attributes'] = attributes_dict

            return row_dict

    def handle(self, query):
        if not query:
            query = Segment.query

        # Add filters based on provided arguments
        for step in self.steps:
            if step['type'] == 'filter':
                query = self._handle_filter(step, query)
            elif step['type'] == 'make':
                query = self._handle_make(step, query)
            elif step['type'] == 'order':
                query = self._handle_order(step, query)
            elif step['type'] == 'limit':
                query = self._handle_limit(step, query)
            elif step['type'] == 'offset':
                query = self._handle_offset(step, query)
            elif step['type'] == 'fields':
                query = self._handle_fields(step, query)
            elif step['type'] == 'geobox':
                query = self._handle_geobox(step, query)
            elif step['type'] == 'vector_search':
                query = self._handle_vector_search(step, query)

        results = self._handle_return(query)

        return results

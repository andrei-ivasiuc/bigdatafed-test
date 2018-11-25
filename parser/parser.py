import urllib.request
import urllib.error
import lxml.html as lh
import pandas as pd

from parser.model import RowModel, DateField, FloatField
from parser.errors import *

class Parser:

    def __init__(self, schema):
        """
        Parser class.

        Takes schema and fetches all described sources.
        Fetched data is stored inside parser instance and
        can then be pickled and stored to filesystem.

        :param schema:
        """
        self.schema = schema
        self.models = {}
        self.df = {}
        self._init_models()
        self._init_dataframes()

    def fetch_all(self):
        """
        Start fetch process
        :return: None
        """
        self._fetch_all()
        self._save()

    def _save(self):
        """
        Pickle and save pandas DataFrames to files.
        :return: None
        """
        for source in self.schema.keys():
            self.df[source].to_pickle("data/{}.pd".format(source))

    def _init_models(self):
        """
        Create and instantiate model class with attributes specified by schema
        :return: None
        """
        for source, source_schema in self.schema.items():
            field_names, fields = self._schema_get_fields(source_schema)
            model_attrs = self._field_factory(fields)
            model_class = self._model_factory("{}Model".format(source), {}, RowModel, model_attrs)
            self.models[source] = model_class()

    def _init_dataframes(self):
        """
        Create empty pandas DataFrames with specified schema for every source type
        :param source:
        :param source_schema:
        :return: None
        """
        for source, source_schema in self.schema.items():
            field_names, fields = self._schema_get_fields(source_schema)
            self.df[source] = pd.DataFrame(columns=field_names)
            if 'index_field' in source_schema:
                self.df[source].set_index([source_schema['index_field']])

    def _field_factory(self, fields):
        """
        Instantiate field classes with arguments provided by schema.
        :param fields:
        :return: dict(field_name: FieldObject)
        """
        fields_dict = {}
        for field in fields:
            # Find filed class by name in global scope
            field_class = globals()[field['type']]
            # Instantiate filed class with params and add it to a dict
            # Class params are described in field schema
            fields_dict[field['name']] = field_class(**field['params'])
        return fields_dict

    def _model_factory(self, name, arg_names, base_class, attrs):
        """
        Generate a model class with specified attributes described in schema.
        Is inherited from base model class.
        :param name: Class name
        :param arg_names: Class argument names
        :param base_class: Base class to inherit from
        :param attrs: Class attributes
        :return: Class()
        """
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                # here, the arg_names variable is the one passed to the
                # ClassFactory call
                if key not in arg_names:
                    raise TypeError("Argument %s not valid for %s"
                                    % (key, self.__class__.__name__))
                setattr(self, key, value)
            base_class.__init__(self)
        class_attrs = {**attrs, **{"__init__": __init__}}
        new_class = type(name, (base_class,), class_attrs)
        return new_class

    def _schema_get_fields(self, source_schema):
        """
        Get all model fields described in schema
        :param source_schema:
        :return: list(str())
        :return: list(dict()
        """
        field_names = [f['name'] for f in source_schema['fields']]
        return field_names, source_schema['fields']

    def _fetch_all(self):
        """
        Fetch all sources described in schema
        :return: None
        """
        for source, source_schema in self.schema.items():
            rows = self._extract_document_rows(source_schema)
            for row in rows:
                self._process_row(source, row)

    def _extract_document_rows(self, source_schema):
        """
        Extract table rows by applying xpath to html document
        :param source_schema:
        :return: list(lxml Elements)
        """
        document = self._fetch_document(
            source_schema['url'],
            source_schema['headers']
        )
        return document.xpath(source_schema['row_xpath'])

    def _fetch_document(self, url, headers):
        """
        Fetch contents of html document via url
        :param url:
        :param headers:
        :return: str(HTML)
        """
        req = urllib.request.Request(url, headers=headers)
        document = None
        try:
            document = lh.parse(urllib.request.urlopen(req))
        except urllib.error.HTTPError as err:
            if err.code == 404:
                raise ParserErrorURLNotFound("HTTP Error 404: URL {} was not found ".format(url))
        return document

    def _process_row(self, source, row):
        """
        Extract row data by applying a model to it
        :param source:
        :param row:
        :return: None
        """
        row_data = self.models[source](row)
        self._add_row_to_dataframe(source, row_data)

    def _add_row_to_dataframe(self, source, row_data):
        """
        Save row data to source's pandas DataFrame
        :param source:
        :param row_data:
        :return: None
        """
        self.df[source] = self.df[source].append(row_data, ignore_index=True)

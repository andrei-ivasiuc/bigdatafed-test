import locale
from datetime import datetime
from abc import abstractmethod

# Setting locale for string to float conversions
locale.setlocale(locale.LC_NUMERIC, 'en_US')


class RowModel:
    def __init__(self):
        """
        Model describes row structure

        When being instantiated by model factory inside parser class,
        subclass of model class is populated with fields described in parser schema.
        :return: None
        """
        (self.field_names, self.fields) = self._get_fields()

    def __call__(self, row):
        """
        Extract row data by applying field class instances to a row
        :param row: lxml Element
        :return: dict()
        """
        row_values = [field(row) for field in self.fields]
        return dict(zip(self.field_names, row_values))

    def _get_fields(self):
        """
        Return fields of a model instance.

        Fields are added dynamically to a model subclass by model factory
        :return: list(field_names)
        :return: list(fields)
        """
        field_names = []
        fields = []
        # Iterate over class attributes
        for (attr_name, attr) in self.__class__.__dict__.items():
            # And if they're a subclass of RowField, add them to fields list
            if issubclass(attr.__class__, RowField):
                field_names.append(attr_name)
                fields.append(attr)
        return field_names, fields


class RowField:
    def __init__(self, selector):
        """
        Abstract class describes row field to be extracted.

        Class instance takes xpath selector and other params
        required to extract and convert field value.

        To extract a value, class instance is called with
        lxml row element as only param.

        :param selector: xpath selector
        """
        self.selector = selector
        self.value = None

    def __call__(self, row):
        """
        Extract row value
        :param row: lxml Element
        :return: mixed
        """
        value = row.xpath(self.selector)[0]
        return self._convert(value)

    @abstractmethod
    def _convert(self, value):
        """
        Abstract method, converts field value
        :param value: str()
        :return: None
        """
        pass


class DateField(RowField):
    def __init__(self, selector, date_format):
        """
        Describe date fields
        :param selector: str(): xpath selector
        :param date_format: str()
        """
        super(DateField, self).__init__(selector)
        self.date_format = date_format

    def _convert(self, value):
        """
        Convert string value to DateTime object
        :param value: str()
        :return: DateTime()
        """
        return datetime.strptime(value, self.date_format)


class FloatField(RowField):
    def _convert(self, value):
        """
        Convert string value to a float applying locale settings
        :param value: str()
        :return: float()
        """
        return locale.atof(value)

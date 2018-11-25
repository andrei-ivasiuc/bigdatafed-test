Structure
=========

```
/data - where pickled data is stored
/parser - python package with parser files
/parser.py - runs the parser from cmd
/view.py - shows commodity data from cmd
/schema.json - schema of data sources and data structure
/requirements.txt - python package requirements
```

Installation
============

`pip install -r requirements.txt`

How to use
==========

####Running parser

`python parser.py`

####Getting commodity info

`python view.py (commodity) --date-from=(date) --date-to=(date)`

commodity = commodity type(gold, silver, copper)

date-from, date-to = optional date range, if absent shows data for entire dataset(date format: 2018-11-25)


======================
Tavily Python Wrapper
======================

This Python wrapper allows for easy interaction with the Tavily API, providing both basic and advanced search functionalities directly from your Python programs. Easily integrate smart search capabilities into your applications, utilizing Tavily's powerful search features.

Installing
==========

.. code-block:: bash

    pip install tavily-python

Usage
=====

.. code-block:: python

    from tavily import Client
    search = Client(api_key="YOUR_API_KEY")
    search.basic_search(query="Should I invest in Apple in 2024?", include_raw_content=True)

API Methods
===========

Client
------

The ``Client`` class is the entry point to interacting with the Tavily API. Instantiate it with your API key to get started.

Methods
-------

- ``basic_search(query, **kwargs)``: Performs a basic, smart search optimized for performance (quick response time) the specified query and additional parameters as keyword arguments.
  
- ``advanced_search(query, **kwargs)``: Performs an advanced, in-depth search optimized for quality (factual and unbiased) with the specified query and additional parameters as keyword arguments.

Keyword Arguments
-----------------

- ``search_depth`` (str): The depth of the search. It can be "basic" or "advanced". Default is "basic" for `basic_search` and "advanced" for `advanced_search`.
  
- ``num_results`` (int): The number of search results to return. Default is 5.

- ``include_domains`` (list): A list of domains to specifically include in the search results. Default is None, which includes all domains.
  
- ``exclude_domains`` (list): A list of domains to specifically exclude from the search results. Default is None, which does not exclude any domains.
  
- ``include_answer`` (bool): Whether or not to include answers in the search results. Default is False.

- ``include_raw_content`` (bool): Whether or not to include raw content in the search results. Default is False.

Both methods internally use the ``_search`` method to communicate with the API.

Error Handling
==============

In case of an unsuccessful HTTP request, a ``HTTPError`` will be raised.

License
=======

This project is licensed under the terms of the MIT license.

Contact
=======

For questions, support, or to learn more, please visit `Tavily <http://tavily.com>`_.

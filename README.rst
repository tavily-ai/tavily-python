=======================
Tavily Python Wrapper
=======================

This Python wrapper allows for easy interaction with the Tavily API, offering both basic and advanced search functionalities directly from your Python programs. Easily integrate smart search capabilities into your applications, harnessing Tavily's powerful search features.

Installing
----------

.. code-block:: bash

    pip install tavily-python

Usage
-----

.. code-block:: python

    from tavily import Client
    tavily = Client(api_key="YOUR_API_KEY")
    # For basic search:
    tavily.search(query="Should I invest in Apple in 2024?")
    # For advanced search:
    tavily.search(query="Should I invest in Apple in 2024?", search_depth="advanced")

API Methods
-----------

Client
~~~~~~

The ``Client`` class is the entry point to interacting with the Tavily API. Kickstart your journey by instantiating it with your API key.

Methods
~~~~~~~

- ``search(query, search_depth="basic", **kwargs)``: Performs a search using the specified query. The depth of the search can be controlled by the `search_depth` parameter.

Keyword Arguments
~~~~~~~~~~~~~~~~~

- ``search_depth`` (str): The depth of the search. It can be "basic" or "advanced". Default is "basic".
- ``max_results`` (int): The number of search results to return. Default is 10.
- ``include_domains`` (list): A list of domains to specifically include in the search results. Default is None, which includes all domains.
- ``exclude_domains`` (list): A list of domains to specifically exclude from the search results. Default is None, which doesn't exclude any domains.
- ``include_answer`` (bool): Whether or not to include answers in the search results. Default is False.
- ``include_raw_content`` (bool): Whether or not to include raw content in the search results. Default is False.

Both methods internally call the ``_search`` method to communicate with the API.

Error Handling
--------------

In case of an unsuccessful HTTP request, a ``HTTPError`` will be raised.

License
-------

This project is licensed under the terms of the MIT license.

Contact
-------

For questions, support, or to learn more, please visit `Tavily <http://tavily.com>`_.

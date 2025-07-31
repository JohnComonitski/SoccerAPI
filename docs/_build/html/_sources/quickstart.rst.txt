Quickstart
==========

Install
-------

There are two ways to perform the installation. It is always recommended to
work inside a Python virtual environment. Here are some resources that explain
how to do it:

- `Official Python docs <https://docs.python.org/3/library/venv.html>`_
- `Python Virtual Environments: A Primer (Real Python) <https://realpython.com/python-virtual-environments-a-primer/>`_
- `How to Set Up a Virtual Environment in Python – And Why It's Useful - Freecodecamp <https://www.freecodecamp.org/news/how-to-setup-virtual-environments-in-python/>`_

In any case all the necessary dependencies are installed automatically along
with the program.

Before starting you need to clone the project with Git:

.. code-block:: shell

   git clone https://github.com/JohnComonitski/SoccerAPI.git
   cd SoccerAPI

Install directly via pip
````````````````````````

.. code-block:: shell

   pip install .

Install manually
````````````````

.. code-block:: shell

   pip install -r requirements.txt

If you want to contribute to this project, such as by improving the
documentation, install the development dependencies as well:

.. code-block:: shell

   pip install -r requirements.txt -r requirements-dev.txt

Install without cloning the repository
``````````````````````````````````````

As an alternative you can install the project directly without having to clone
it:

.. code-block:: shell

   pip install git+https://github.com/JohnComonitski/SoccerAPI.git

API keys
--------

An API key is required for data interactions. Before using SoccerAPI you need
to sign up on `API Football <https://dashboard.api-football.com/register>`_.
You must use the ``API-SPORTS`` endpoint. A Detailed explanation can be found
in the
`official documentation <https://www.api-football.com/documentation-v3>`_.

The free tier will grant you 100 daily requests.

Full example
------------

Here is a full Python program you can try:

.. code-block:: python

   import soccerapi.soccerapi

   config = {
       'fapi_host' : 'API-FOOTBALL HOST',
       'fapi_key' : 'API-FOOTBALL API KEY',
   }
   api = soccerapi.soccerapi.SoccerAPI(config)

   haaland = api.db.get("players", "82155")
   stat = haaland.statistic("shots")
   print(stat)

You should get something similar to this:

.. code-block:: python

   92.0

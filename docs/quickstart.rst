Quickstart
==========

Install
-------

There are two ways to perform the installation. It is always recommended to
work inside a Python virtual environment. In both cases all the necessary
dependencies are installed automatically along with the program.

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

API keys
--------

Full example
------------

Here is a full Python program you can try:

.. code-block:: python

   import soccerapi.soccerapi

   config = {
       'fapi_host' : 'v3.football.api-sports.io',
       'fapi_key' : 'API-FOOTBALL API KEY',
   }
   api = soccerapi.soccerapi.SoccerAPI(config)

   haaland = api.db.get("players", "82172")
   stat = haaland.statistic("shots")
   print(stat)

You should get something similar to this:

.. code-block:: python

   92.0

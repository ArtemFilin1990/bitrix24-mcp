Quick Start
===========

Configuration
============

The server requires your Bitrix24 webhook URL via environment variable:

.. code-block:: bash

   export BITRIX_WEBHOOK_URL="https://your-domain.bitrix24.ru/rest/1/yoursecretcode/"

You can read Bitrix24 REST API docs here: https://apidocs.bitrix24.ru/

Running the Server
================

After installation and configuration, start the MCP server:

.. code-block:: bash

   uvx bitrix24-mcp
   # or if installed as a script
   bitrix24-mcp

Testing the Installation
=====================

To verify basic Bitrix24 API integration, run the test script:

.. code-block:: bash

   python -m tests.services

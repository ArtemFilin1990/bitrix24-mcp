Quick Start
===========

Configuration
============

The server requires your Bitrix24 webhook URL. Set it via an environment variable before startup:

1. Environment variable:

.. code-block:: bash

   export BITRIX_WEBHOOK_URL="https://your-domain.bitrix24.ru/rest/1/yoursecretcode/"

Running the Server
================

After installation and configuration, start the MCP server:

.. code-block:: bash

   uv run bitrix24-mcp

Testing the Installation
=====================

To verify basic Bitrix24 API integration, run the test script:

.. code-block:: bash

   uv run python tests/services.py

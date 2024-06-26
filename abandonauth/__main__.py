"""
Entrypoint when running as a module, useful for development.

It is recommended that if this is deployed in production to use the uvicorn
command line rather than running as a Python module.

https://www.uvicorn.org/deployment/
https://www.uvicorn.org/deployment/#gunicorn.
"""
import uvicorn

uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)  # noqa: S104

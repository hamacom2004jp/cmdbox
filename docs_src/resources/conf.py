import datetime
import os
import sphinx_rtd_theme
import sphinx_fontawesome
import sys
sys.path.insert(0, os.path.abspath('..'))

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

dt_now = datetime.datetime.now()
project = f'cmdbox'
copyright = f'Copyright (c) 2023-{dt_now.strftime("%Y")} hamacom2004jp All Rights Reserved.'
author = 'hamacom2004jp'
release = dt_now.strftime("%Y/%m/%d")

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.todo',
    'sphinx.ext.napoleon',
    'sphinx_rtd_theme',
    'sphinx.ext.githubpages']

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
language = 'jp'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_theme_options = {}
html_css_files = [
    'custom.css',
]
html_static_path = ['static']

# -- Options for todo extension ----------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/todo.html#configuration

todo_include_todos = True

# -- Suppress autodoc warnings and mock problematic imports ---
# google.adk has compatibility issues with Pydantic v2, mock it to avoid import errors
autodoc_mock_imports = ['google.adk', 'google.adk.agents', 'google.adk.plugins']

# Ignore warnings from modules with Pydantic compatibility issues
suppress_warnings = ['autodoc.import_object', 'autodoc.import_error']

# Configure autodoc to continue on import errors
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
}

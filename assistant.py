import re
import os
import uuid
import json
from dataclasses import dataclass
from typing import List, Dict, Tuple

import streamlit as st
import chromadb
from chromadb.config import Settings
from markdown_it import MarkdownIt
import ollama
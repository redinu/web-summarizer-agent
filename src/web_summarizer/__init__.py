"""
Web Summarizer Agent for MeshCore

Turn any webpage into structured, summarized information that other agents can use instantly.
"""

__version__ = "1.0.0"
__author__ = "Rediet Dagnew"

from web_summarizer.agent import WebSummarizerAgent
from web_summarizer.models import SummaryRequest, SummaryResponse

__all__ = ["WebSummarizerAgent", "SummaryRequest", "SummaryResponse"]

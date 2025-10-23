"""
Simple text rendering library for LED matrices.

This module provides BDF font loading and text rendering that works
with any Canvas-compatible driver (hardware or simulated).
"""

from .font import BDFFont

__all__ = ['BDFFont']

"""Tests for AI modules (style analysis, subject processing, icon generation)."""

import os
import tempfile
import pytest

from PySide6.QtGui import QImage
from PySide6.QtCore import Qt


class TestStyleAnalyzer:
    """Tests for style analysis functionality."""
    
    def test_analyzer_initialization(self):
        """Test StyleAnalyzer initialization."""
        from pixelsmart.style_analysis import StyleAnalyzer
        
        analyzer = StyleAnalyzer()
        assert analyzer is not None
    
    def test_heuristic_color_extraction(self):
        """Test color extraction using heuristic methods."""
        from pixelsmart.style_analysis import StyleAnalyzer
        
        # Create a simple test image with known colors
        image = QImage(64, 64, QImage.Format_ARGB32)
        image.fill(Qt.white)
        
        # Add some colored regions
        from PySide6.QtGui import QPainter
        painter = QPainter(image)
        painter.fillRect(0, 0, 32, 32, Qt.red)
        painter.fillRect(32, 0, 32, 32, Qt.blue)
        painter.fillRect(0, 32, 32, 32, Qt.green)
        painter.fillRect(32, 32, 32, 32, Qt.yellow)
        painter.end()
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            temp_path = f.name
        
        try:
            image.save(temp_path)
            
            analyzer = StyleAnalyzer()
            result = analyzer._analyze_heuristic(temp_path)
            
            assert "palette" in result
            assert len(result["palette"]) > 0
            assert "characteristics" in result
            assert "color_count" in result["characteristics"]
        finally:
            os.unlink(temp_path)
    
    def test_analyze_style_with_ai_disabled(self):
        """Test style analysis with AI disabled (heuristic mode)."""
        from pixelsmart.style_analysis import StyleAnalyzer
        
        # Create a simple test image
        image = QImage(128, 128, QImage.Format_ARGB32)
        image.fill(Qt.cyan)
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            temp_path = f.name
        
        try:
            image.save(temp_path)
            
            analyzer = StyleAnalyzer()
            result = analyzer.analyze_style(temp_path, use_ai=False)
            
            assert "description" in result
            assert "palette" in result
            assert "characteristics" in result
            assert isinstance(result["palette"], list)
        finally:
            os.unlink(temp_path)


class TestSubjectProcessor:
    """Tests for subject processing functionality."""
    
    def test_processor_initialization(self):
        """Test SubjectProcessor initialization."""
        from pixelsmart.subject_processor import SubjectProcessor
        
        processor = SubjectProcessor()
        assert processor is not None
    
    def test_sample_subject_with_padding(self):
        """Test subject sampling with aspect ratio preservation."""
        from pixelsmart.subject_processor import SubjectProcessor
        
        # Create a test image
        source = QImage(200, 100, QImage.Format_ARGB32)
        source.fill(Qt.magenta)
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            temp_path = f.name
        
        try:
            source.save(temp_path)
            
            processor = SubjectProcessor()
            result = processor.sample_subject(temp_path, (64, 64), preserve_aspect_ratio=True)
            
            assert result.width() == 64
            assert result.height() == 64
            # Check that aspect ratio was preserved (height should be less than width due to padding)
        finally:
            os.unlink(temp_path)
    
    def test_sample_subject_stretch(self):
        """Test subject sampling with stretching."""
        from pixelsmart.subject_processor import SubjectProcessor
        
        source = QImage(100, 200, QImage.Format_ARGB32)
        source.fill(Qt.yellow)
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            temp_path = f.name
        
        try:
            source.save(temp_path)
            
            processor = SubjectProcessor()
            result = processor.sample_subject(temp_path, (64, 64), preserve_aspect_ratio=False)
            
            assert result.width() == 64
            assert result.height() == 64
        finally:
            os.unlink(temp_path)


class TestIconGenerator:
    """Tests for icon generation functionality."""
    
    def test_generator_initialization(self):
        """Test IconGenerator initialization."""
        from pixelsmart.icon_generator import IconGenerator
        
        generator = IconGenerator()
        assert generator is not None
    
    def test_generate_icon_basic(self):
        """Test basic icon generation."""
        from pixelsmart.icon_generator import IconGenerator
        
        generator = IconGenerator()
        
        # Mock the AI client to avoid actual API calls
        class MockAIClient:
            def encode_image_to_base64(self, path):
                return ""
        
        generator._ai_client = MockAIClient()
        
        result = generator.generate_icon("test prompt", None, (32, 32))
        
        assert result.width() == 32
        assert result.height() == 32
    
    def test_constrain_to_palette(self):
        """Test color palette constraint."""
        from pixelsmart.icon_generator import IconGenerator
        
        generator = IconGenerator()
        
        # Create a test image with various colors
        source = QImage(16, 16, QImage.Format_ARGB32)
        source.fill(Qt.white)
        
        # Define a simple palette
        palette = ["#FF0000", "#00FF00", "#0000FF"]
        
        result = generator.constrain_to_palette(source, palette)
        
        assert result.width() == 16
        assert result.height() == 16


class TestBackgroundRemover:
    """Tests for background removal functionality."""
    
    def test_remover_initialization(self):
        """Test BackgroundRemover initialization."""
        from pixelsmart.background_remover import BackgroundRemover
        
        remover = BackgroundRemover()
        assert remover is not None
    
    def test_remove_background_heuristic(self):
        """Test background removal using heuristic methods."""
        from pixelsmart.background_remover import BackgroundRemover
        
        # Create a test image
        source = QImage(64, 64, QImage.Format_ARGB32)
        source.fill(Qt.green)
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            temp_path = f.name
        
        try:
            source.save(temp_path)
            
            remover = BackgroundRemover()
            result = remover.remove_background(temp_path, confidence_threshold=0.5)
            
            # Result should have alpha channel
            assert result.width() == 64
            assert result.height() == 64
        finally:
            os.unlink(temp_path)

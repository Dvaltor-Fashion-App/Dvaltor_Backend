"""
Image Processing Utility Module using FFmpeg
This module provides FFmpeg-based image processing capabilities for the Dvaltor Fashion API.
"""

import ffmpeg
import tempfile
import os
import io
from typing import Tuple, Optional
import numpy as np

# FFmpeg quality constants
# qscale values: 1-31 for JPEG (lower is better quality, 2-3 is high quality)
FFMPEG_HIGH_QUALITY = 2
FFMPEG_MEDIUM_QUALITY = 3
# Height value -2 maintains aspect ratio with even pixel dimensions (required by some codecs)
ASPECT_RATIO_EVEN = -2


class ImageProcessor:
    """
    FFmpeg-based image processor for normalizing, optimizing, and transforming images
    """
    
    def __init__(self, max_width: int = 1920, max_height: int = 1080, quality: int = 85):
        """
        Initialize the image processor with default settings
        
        Args:
            max_width: Maximum width for resized images
            max_height: Maximum height for resized images
            quality: JPEG quality (1-100)
        """
        self.max_width = max_width
        self.max_height = max_height
        self.quality = quality
    
    def normalize_image(self, input_bytes: bytes, output_format: str = 'png') -> bytes:
        """
        Normalize an image using FFmpeg - convert format, resize if needed
        
        Args:
            input_bytes: Raw image bytes from upload
            output_format: Desired output format (png, jpg, etc.)
            
        Returns:
            Normalized image as bytes
        """
        # Create temporary files for FFmpeg processing
        with tempfile.NamedTemporaryFile(suffix='.bin', delete=False) as input_temp:
            input_temp.write(input_bytes)
            input_path = input_temp.name
        
        output_temp = tempfile.NamedTemporaryFile(suffix=f'.{output_format}', delete=False)
        output_path = output_temp.name
        output_temp.close()
        
        try:
            
            # Get image dimensions first
            probe = ffmpeg.probe(input_path)
            video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
            width = int(video_info['width'])
            height = int(video_info['height'])
            
            # Calculate new dimensions maintaining aspect ratio
            scale_filter = self._calculate_scale(width, height)
            
            # Process image with FFmpeg
            stream = ffmpeg.input(input_path)
            
            if scale_filter:
                stream = ffmpeg.filter(stream, 'scale', scale_filter)
            
            # Set quality and format
            stream = ffmpeg.output(
                stream, 
                output_path,
                **{'qscale:v': FFMPEG_HIGH_QUALITY} if output_format == 'jpg' else {}
            )
            
            # Run FFmpeg
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            # Read processed image
            with open(output_path, 'rb') as f:
                processed_bytes = f.read()
            
            return processed_bytes
            
        finally:
            # Cleanup temporary files
            if os.path.exists(input_path):
                os.remove(input_path)
            if 'output_path' in locals() and os.path.exists(output_path):
                os.remove(output_path)
    
    def optimize_image(self, input_bytes: bytes) -> bytes:
        """
        Optimize image size and quality for faster processing
        
        Args:
            input_bytes: Raw image bytes
            
        Returns:
            Optimized image bytes
        """
        with tempfile.NamedTemporaryFile(suffix='.bin', delete=False) as input_temp:
            input_temp.write(input_bytes)
            input_path = input_temp.name
        
        output_temp = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        output_path = output_temp.name
        output_temp.close()
        
        try:
            
            # Optimize with compression
            stream = ffmpeg.input(input_path)
            stream = ffmpeg.output(
                stream,
                output_path,
                **{
                    'qscale:v': FFMPEG_MEDIUM_QUALITY,  # Medium quality for optimization
                    'vf': f'scale=w=min(iw\\,{self.max_width}):h={ASPECT_RATIO_EVEN}'  # Limit width, maintain aspect
                }
            )
            
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            with open(output_path, 'rb') as f:
                optimized_bytes = f.read()
            
            return optimized_bytes
            
        finally:
            if os.path.exists(input_path):
                os.remove(input_path)
            if 'output_path' in locals() and os.path.exists(output_path):
                os.remove(output_path)
    
    def convert_format(self, input_bytes: bytes, target_format: str) -> bytes:
        """
        Convert image to a specific format
        
        Args:
            input_bytes: Raw image bytes
            target_format: Target format (jpg, png, webp, etc.)
            
        Returns:
            Converted image bytes
        """
        with tempfile.NamedTemporaryFile(suffix='.bin', delete=False) as input_temp:
            input_temp.write(input_bytes)
            input_path = input_temp.name
        
        output_temp = tempfile.NamedTemporaryFile(suffix=f'.{target_format}', delete=False)
        output_path = output_temp.name
        output_temp.close()
        
        try:
            
            stream = ffmpeg.input(input_path)
            stream = ffmpeg.output(stream, output_path)
            
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            with open(output_path, 'rb') as f:
                converted_bytes = f.read()
            
            return converted_bytes
            
        finally:
            if os.path.exists(input_path):
                os.remove(input_path)
            if 'output_path' in locals() and os.path.exists(output_path):
                os.remove(output_path)
    
    def extract_thumbnail(self, input_bytes: bytes, width: int = 300, height: int = 300) -> bytes:
        """
        Extract a thumbnail from the image
        
        Args:
            input_bytes: Raw image bytes
            width: Thumbnail width
            height: Thumbnail height
            
        Returns:
            Thumbnail image bytes
        """
        with tempfile.NamedTemporaryFile(suffix='.bin', delete=False) as input_temp:
            input_temp.write(input_bytes)
            input_path = input_temp.name
        
        output_temp = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        output_path = output_temp.name
        output_temp.close()
        
        try:
            
            stream = ffmpeg.input(input_path)
            # Use scale filter with force_original_aspect_ratio for better thumbnail generation
            stream = ffmpeg.filter(stream, 'scale', width, height, force_original_aspect_ratio='decrease')
            stream = ffmpeg.filter(stream, 'pad', width, height, -1, -1, 'black')
            stream = ffmpeg.output(stream, output_path, **{'qscale:v': FFMPEG_HIGH_QUALITY})
            
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            with open(output_path, 'rb') as f:
                thumbnail_bytes = f.read()
            
            return thumbnail_bytes
            
        finally:
            if os.path.exists(input_path):
                os.remove(input_path)
            if 'output_path' in locals() and os.path.exists(output_path):
                os.remove(output_path)
    
    def _calculate_scale(self, width: int, height: int) -> Optional[str]:
        """
        Calculate scale filter if image exceeds max dimensions
        
        Args:
            width: Current image width
            height: Current image height
            
        Returns:
            FFmpeg scale filter string or None if no scaling needed
        """
        if width <= self.max_width and height <= self.max_height:
            return None
        
        # Calculate scaling maintaining aspect ratio
        width_ratio = self.max_width / width
        height_ratio = self.max_height / height
        ratio = min(width_ratio, height_ratio)
        
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        
        # Ensure dimensions are even (required by some codecs)
        new_width = new_width - (new_width % 2)
        new_height = new_height - (new_height % 2)
        
        return f'{new_width}:{new_height}'
    
    def get_image_info(self, input_bytes: bytes) -> dict:
        """
        Get image metadata using FFmpeg probe
        
        Args:
            input_bytes: Raw image bytes
            
        Returns:
            Dictionary with image information
        """
        with tempfile.NamedTemporaryFile(suffix='.bin', delete=False) as input_temp:
            input_temp.write(input_bytes)
            input_path = input_temp.name
        
        try:
            probe = ffmpeg.probe(input_path)
            video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
            
            return {
                'width': int(video_info['width']),
                'height': int(video_info['height']),
                'format': video_info.get('codec_name', 'unknown'),
                'pixel_format': video_info.get('pix_fmt', 'unknown'),
                'size_bytes': int(probe['format'].get('size', 0))
            }
        finally:
            if os.path.exists(input_path):
                os.remove(input_path)

import re
import os
import chardet
import logging

class SubtitleParser:
    def parse_srt(self, subtitle_path: str) -> str:
        """Parse SRT subtitle file and return plain text."""
        # Detect encoding
        with open(subtitle_path, 'rb') as file:
            raw_content = file.read()
            encoding_result = chardet.detect(raw_content)
            encoding = encoding_result['encoding']
        
        # Read the file with the detected encoding
        with open(subtitle_path, 'r', encoding=encoding, errors='replace') as file:
            content = file.read()
        
        # Extract text from SRT format
        # Remove timestamps and subtitle numbers
        lines = content.split('\n')
        text_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip empty lines
            if not line:
                i += 1
                continue
            
            # Check if this is a subtitle number
            if re.match(r'^\d+$', line):
                i += 1
                # Skip timestamp line
                if i < len(lines):
                    i += 1
                continue
            
            # Skip timestamp lines
            if re.match(r'^\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}$', line):
                i += 1
                continue
            
            # Add text lines
            text_lines.append(line)
            i += 1
        
        # Join lines and clean up
        text = ' '.join(text_lines)
        
        # Clean up common subtitle artifacts
        text = re.sub(r'<[^>]+>', '', text)  # Remove HTML tags
        text = re.sub(r'\{[^}]+\}', '', text)  # Remove curly braces content
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
        
        return text.strip()

import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  CircularProgress,
  Alert,
  Button
} from '@mui/material';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import DownloadIcon from '@mui/icons-material/Download';
import axios from 'axios';
import { API_BASE_URL } from '../config';

function TranscriptionResult({ jobId, loading, onTranscriptionComplete }) {
  const [text, setText] = useState('');
  const [error, setError] = useState('');
  const [status, setStatus] = useState('processing');
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    let intervalId = null;

    const checkStatus = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/status/${jobId}`);
        const { status, text: resultText, error: resultError } = response.data;

        setStatus(status);

        if (status === 'completed') {
          setText(resultText);
          if (onTranscriptionComplete) onTranscriptionComplete();
          clearInterval(intervalId);
        } else if (status === 'error') {
          setError(resultError || 'An error occurred during transcription');
          if (onTranscriptionComplete) onTranscriptionComplete();
          clearInterval(intervalId);
        }
      } catch (err) {
        setError('Failed to check transcription status');
        setStatus('error');
        if (onTranscriptionComplete) onTranscriptionComplete();
        clearInterval(intervalId);
      }
    };

    // Start polling if we have a job ID
    if (jobId && status === 'processing') {
      intervalId = setInterval(checkStatus, 3000); // Check every 3 seconds
      checkStatus(); // Check immediately
    }

    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [jobId, onTranscriptionComplete, status]);

  const handleCopyText = () => {
    navigator.clipboard.writeText(text).then(
      () => {
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      },
      () => {
        setError('Failed to copy text to clipboard');
      }
    );
  };

  const handleDownloadText = () => {
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `transcription-${jobId}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  if (status === 'processing' || loading) {
    return (
      <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', py: 4 }}>
        <CircularProgress size={40} sx={{ mb: 2 }} />
        <Typography variant="body1">Processing your video...</Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          This may take a few minutes depending on the video length
        </Typography>
      </Box>
    );
  }

  if (status === 'error') {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        {error || 'An error occurred while processing the video'}
      </Alert>
    );
  }

  return (
    <Box>
      {text ? (
        <>
          <Paper 
            variant="outlined" 
            sx={{ 
              p: 2, 
              maxHeight: '400px', 
              overflowY: 'auto',
              backgroundColor: '#fafafa',
              mb: 2
            }}
          >
            <Typography variant="body1" component="div" sx={{ whiteSpace: 'pre-line' }}>
              {text}
            </Typography>
          </Paper>
          
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
            <Button
              variant="outlined"
              startIcon={<ContentCopyIcon />}
              onClick={handleCopyText}
            >
              {copied ? 'Copied!' : 'Copy Text'}
            </Button>
            
            <Button
              variant="contained"
              startIcon={<DownloadIcon />}
              onClick={handleDownloadText}
            >
              Download
            </Button>
          </Box>
        </>
      ) : (
        <Typography>No transcription result available</Typography>
      )}
    </Box>
  );
}

export default TranscriptionResult;

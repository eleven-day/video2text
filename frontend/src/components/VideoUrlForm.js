import React, { useState } from 'react';
import { 
  Button, 
  Box, 
  FormControlLabel, 
  Switch, 
  TextField,
  CircularProgress,
  Alert
} from '@mui/material';
import LinkIcon from '@mui/icons-material/Link';
import axios from 'axios';
import { API_BASE_URL } from '../config';

function VideoUrlForm({ onJobStarted }) {
  const [url, setUrl] = useState('');
  const [useOpenAI, setUseOpenAI] = useState(false);
  const [language, setLanguage] = useState('auto');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!url) {
      setError('Please enter a video URL');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await axios.post(`${API_BASE_URL}/upload/url`, {
        url: url,
        settings: {
          use_openai_api: useOpenAI,
          language: language
        }
      });

      if (response.data && response.data.job_id) {
        onJobStarted(response.data.job_id);
        setUrl('');
      } else {
        throw new Error('Invalid response from server');
      }
    } catch (error) {
      console.error('Error processing URL:', error);
      setError(error.response?.data?.detail || 'Error processing URL');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box component="form" onSubmit={handleSubmit}>
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      
      <Box sx={{ mb: 3 }}>
        <TextField
          label="Video URL"
          variant="outlined"
          fullWidth
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://example.com/video.mp4"
          InputProps={{
            startAdornment: <LinkIcon sx={{ color: 'text.secondary', mr: 1 }} />,
          }}
        />
      </Box>
      
      <Box sx={{ mb: 3 }}>
        <TextField
          label="Language (leave as 'auto' for automatic detection)"
          variant="outlined"
          fullWidth
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
          helperText="Specify language code (e.g., 'en', 'zh', 'es') or leave as 'auto'"
        />
      </Box>
      
      <FormControlLabel
        control={
          <Switch
            checked={useOpenAI}
            onChange={(e) => setUseOpenAI(e.target.checked)}
            color="primary"
          />
        }
        label="Use OpenAI API (more accurate, but costs credits)"
      />
      
      <Box sx={{ mt: 3, textAlign: 'right' }}>
        <Button
          variant="contained"
          color="primary"
          type="submit"
          disabled={loading}
          startIcon={loading ? <CircularProgress size={20} /> : null}
        >
          {loading ? 'Processing...' : 'Process Video'}
        </Button>
      </Box>
    </Box>
  );
}

export default VideoUrlForm;

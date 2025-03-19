import React, { useState } from 'react';
import { 
  Button, 
  Box, 
  FormControlLabel, 
  Switch, 
  TextField, 
  Typography,
  CircularProgress,
  Alert
} from '@mui/material';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import axios from 'axios';
import { API_BASE_URL } from '../config';

function VideoUploadForm({ onJobStarted }) {
  const [file, setFile] = useState(null);
  const [fileName, setFileName] = useState('');
  const [useOpenAI, setUseOpenAI] = useState(false);
  const [language, setLanguage] = useState('auto');
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setFileName(selectedFile.name);
      setError('');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a video file');
      return;
    }

    setUploading(true);
    setError('');

    const formData = new FormData();
    formData.append('file', file);
    formData.append('use_openai_api', useOpenAI);
    formData.append('language', language);

    try {
      const response = await axios.post(`${API_BASE_URL}/upload/file`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data && response.data.job_id) {
        onJobStarted(response.data.job_id);
        setFile(null);
        setFileName('');
      } else {
        throw new Error('Invalid response from server');
      }
    } catch (error) {
      console.error('Error uploading file:', error);
      setError(error.response?.data?.detail || 'Error uploading file');
    } finally {
      setUploading(false);
    }
  };

  return (
    <Box component="form" onSubmit={handleSubmit}>
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      
      <Box 
        sx={{ 
          border: '2px dashed #ccc', 
          borderRadius: 2, 
          p: 3, 
          textAlign: 'center',
          mb: 3,
          cursor: 'pointer',
          '&:hover': {
            backgroundColor: '#f8f8f8'
          }
        }}
        onClick={() => document.getElementById('file-input').click()}
      >
        <input
          type="file"
          id="file-input"
          accept="video/*"
          onChange={handleFileChange}
          style={{ display: 'none' }}
        />
        <UploadFileIcon sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
        <Typography variant="h6" gutterBottom>
          Upload Video File
        </Typography>
        <Typography variant="body2" color="textSecondary">
          {fileName || 'Click to browse or drag and drop video file'}
        </Typography>
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
          disabled={uploading}
          startIcon={uploading ? <CircularProgress size={20} /> : null}
        >
          {uploading ? 'Uploading...' : 'Upload and Process'}
        </Button>
      </Box>
    </Box>
  );
}

export default VideoUploadForm;

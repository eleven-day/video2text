import React, { useState } from 'react';
import { Container, Paper, Typography, Box } from '@mui/material';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import VideoUploadForm from './components/VideoUploadForm';
import VideoUrlForm from './components/VideoUrlForm';
import TranscriptionResult from './components/TranscriptionResult';
import Header from './components/Header';
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
});

function App() {
  const [activeTab, setActiveTab] = useState(0);
  const [jobId, setJobId] = useState(null);
  const [loading, setLoading] = useState(false);
  
  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };
  
  const handleJobStarted = (id) => {
    setJobId(id);
    setLoading(true);
  };
  
  const handleTranscriptionComplete = () => {
    setLoading(false);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Header />
      <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
        <Paper elevation={3} sx={{ p: 3 }}>
          <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
            <Tabs value={activeTab} onChange={handleTabChange} aria-label="video input tabs">
              <Tab label="Upload Video File" />
              <Tab label="Provide Video URL" />
            </Tabs>
          </Box>
          
          {activeTab === 0 && (
            <VideoUploadForm onJobStarted={handleJobStarted} />
          )}
          
          {activeTab === 1 && (
            <VideoUrlForm onJobStarted={handleJobStarted} />
          )}
          
          {jobId && (
            <Box sx={{ mt: 4 }}>
              <Typography variant="h6" gutterBottom>
                Transcription Result
              </Typography>
              <TranscriptionResult 
                jobId={jobId} 
                loading={loading}
                onTranscriptionComplete={handleTranscriptionComplete}
              />
            </Box>
          )}
        </Paper>
      </Container>
    </ThemeProvider>
  );
}

export default App;

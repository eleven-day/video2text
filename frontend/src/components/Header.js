import React from 'react';
import { AppBar, Toolbar, Typography, Box } from '@mui/material';
import TextFieldsIcon from '@mui/icons-material/TextFields';

function Header() {
  return (
    <AppBar position="static">
      <Toolbar>
        <TextFieldsIcon sx={{ mr: 2 }} />
        <Typography variant="h6" component="div">
          Video2Text
        </Typography>
        <Box sx={{ flexGrow: 1 }} />
        <Typography variant="body2" color="inherit">
          Convert videos to text with ease
        </Typography>
      </Toolbar>
    </AppBar>
  );
}

export default Header;

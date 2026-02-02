import { BrowserRouter, Routes, Route } from 'react-router-dom';
// import {Button, Container, Typography, Stack} from '@mui/material';
// import DeleteIcon from '@mui/icons-material/Delete';
import './App.css'
import Home from "./pages/Home.tsx";
import About from "./pages/About.tsx";
import PATHS from "./utils/paths.ts";



function App() {
    return (
        <BrowserRouter>
      <Routes>
        <Route path={PATHS.HOME} element={<Home />} />
        <Route path={PATHS.ABOUT} element={<About />} />
      </Routes>
    </BrowserRouter>
    );
}

export default App;
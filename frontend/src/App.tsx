import {BrowserRouter, Routes, Route} from 'react-router-dom';
// import {Button, Container, Typography, Stack} from '@mui/material';
// import DeleteIcon from '@mui/icons-material/Delete';
import './App.css'
import HomePage from "./pages/HomePage.tsx";
import AboutPage from "./pages/AboutPage.tsx";
import PATHS from "./constants/paths.ts";
import MonthlyGroceryAppBar from "./components/common/MonthlyGroceryAppBar.tsx";
import AddGroceryPage from "./pages/AddGroceryPage.tsx";


function App() {
    return (
        <BrowserRouter>
            <MonthlyGroceryAppBar></MonthlyGroceryAppBar>
            <Routes>
                <Route path={PATHS.HOME} element={<HomePage/>}/>
                <Route path={PATHS.ADD_GROCERY} element={<AddGroceryPage/>}/>
                <Route path={PATHS.ABOUT} element={<AboutPage/>}/>
            </Routes>
        </BrowserRouter>
    );
}

export default App;
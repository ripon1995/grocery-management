import {BrowserRouter, Routes, Route} from 'react-router-dom';
import './App.css'
import HomePage from "./pages/HomePage.tsx";
import AboutPage from "./pages/AboutPage.tsx";
import PATHS from "./constants/paths.ts";
import MonthlyGroceryAppBar from "./components/common/MonthlyGroceryAppBar.tsx";
import AddGroceryPage from "./pages/AddGroceryPage.tsx";
import GroceryEditPage from "./pages/EdtiGroceryPage.tsx";
import GroceryDetailPage from "./pages/DetailGroceryPage.tsx";


function App() {
    return (
        <BrowserRouter>
            <MonthlyGroceryAppBar></MonthlyGroceryAppBar>
            <Routes>
                <Route path={PATHS.HOME} element={<HomePage/>}/>
                <Route path={PATHS.ADD_GROCERY} element={<AddGroceryPage/>}/>
                <Route path={PATHS.DETAIL_GROCERY} element={<GroceryDetailPage/>}/>
                <Route path={PATHS.EDIT_GROCERY} element={<GroceryEditPage/>}/>
                <Route path={PATHS.ABOUT} element={<AboutPage/>}/>
            </Routes>
        </BrowserRouter>
    );
}

export default App;
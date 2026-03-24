import {BrowserRouter, Routes, Route} from 'react-router-dom';
import {ToastContainer} from 'react-toastify'; // 1. Import the container
import 'react-toastify/dist/ReactToastify.css';  // 2. Import the CSS
import './App.css'
import HomePage from "./pages/HomePage.tsx";
import AboutPage from "./pages/AboutPage.tsx";
import PATHS from "./constants/paths.ts";
import MonthlyGroceryAppBar from "./components/common/MonthlyGroceryAppBar.tsx";
import AddGroceryPage from "./pages/AddGroceryPage.tsx";
import UpdateGroceryPage from "./pages/UpdateGroceryPage.tsx";
import GroceryDetailPage from "./pages/DetailGroceryPage.tsx";
import LoginPage from "./pages/LoginPage.tsx";


function App() {
    return (
        <BrowserRouter>
            <MonthlyGroceryAppBar></MonthlyGroceryAppBar>

            <ToastContainer
                position="bottom-right"
                autoClose={5000}
                hideProgressBar={false}
                newestOnTop={false}
                closeOnClick
                rtl={false}
                pauseOnFocusLoss
                draggable
                pauseOnHover
                theme="colored" // Or "light"/"dark" based on your MUI theme
            />

            <Routes>
                <Route path={PATHS.HOME} element={<HomePage/>}/>
                <Route path={PATHS.ADD_GROCERY} element={<AddGroceryPage/>}/>
                <Route path={PATHS.DETAIL_GROCERY} element={<GroceryDetailPage/>}/>
                <Route path={PATHS.EDIT_GROCERY} element={<UpdateGroceryPage/>}/>
                <Route path={PATHS.ABOUT} element={<AboutPage/>}/>
                <Route path={PATHS.LOGIN} element={<LoginPage/>}/>
            </Routes>
        </BrowserRouter>
    );
}

export default App;
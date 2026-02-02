import {Container, Typography} from '@mui/material';
import Sample from "../components/Sample.tsx";

export const homeRoute='/';

function Home() {
    return (
        <Container>
            <Typography variant="h2">Welcome to the Home Page</Typography>
            <Sample/>

        </Container>
    );
}

export default Home;
import {Box, CircularProgress, Typography, Paper} from "@mui/material";

interface LoadingStateProps {
    message?: string;
    minHeight?: string | number;
}

const MonthlyGroceryAppLoader = ({
                                     message = "Fetching Groceries...",
                                     minHeight = "400px"
                                 }: LoadingStateProps) => {
    return (
        <Paper
            elevation={0}
            sx={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                minHeight: minHeight,
                width: '100%',
                backgroundColor: 'rgba(255, 255, 255, 0.05)',
                gap: 3,
                borderRadius: 0
            }}
        >
            <Box sx={{position: 'relative', display: 'inline-flex'}}>
                <CircularProgress
                    size={60}
                    color="secondary"
                    thickness={4}
                />
            </Box>
            <Typography
                variant="h6"
                color="textSecondary"
                sx={{fontWeight: 300, letterSpacing: '0.5px'}}
            >
                {message}
            </Typography>
        </Paper>
    );
};

export default MonthlyGroceryAppLoader;
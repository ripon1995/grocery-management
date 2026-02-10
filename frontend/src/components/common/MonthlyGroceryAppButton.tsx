import Button from '@mui/material/Button';
import Stack from '@mui/material/Stack';

interface IButtonProps {
    onClick: () => void;
}

export function MonthlyGroceryAppSaveButton({onClick}: IButtonProps) {
    return (
        <Stack direction="row" spacing={2}>
            <Button
                variant="outlined"
                onClick={onClick}
                sx={{
                    color: 'success.main',          // Uses MUI's theme green
                    borderColor: 'success.main',    // Matches the border to the text
                    borderWidth: '2px',
                    fontWeight: 'bold',             // Makes text bold
                    padding: '10px 30px',           // Increases the size (vertical/horizontal)
                    fontSize: '1.1rem',             // Makes the text slightly larger
                    borderRadius: '4px',
                    '&:hover': {
                        borderColor: 'success.dark',
                        backgroundColor: 'rgba(46, 125, 50, 0.04)',
                        borderWidth: '2px'
                    }
                }}
            >
                Save
            </Button>
        </Stack>
    );
}


export function MonthlyGroceryAppCancelButton({onClick}: IButtonProps) {
    return (
        <Button
            variant="outlined"
            onClick={onClick}
            sx={{
                color: 'error.main',          // MUI Theme Red
                borderColor: 'error.main',    // Matching border
                fontWeight: 'bold',           // Bold text as requested
                padding: '10px 30px',         // Large size matching your Save button
                borderWidth: '2px',
                fontSize: '1.1rem',
                borderRadius: '4px',          // Matching your input field radius
                '&:hover': {
                    borderColor: 'error.dark',
                    backgroundColor: 'rgba(211, 47, 47, 0.04)', // Subtle red hover
                    borderWidth: '2px'
                }
            }}
        >
            Cancel
        </Button>
    );
}

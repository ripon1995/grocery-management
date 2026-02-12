import Typography from "@mui/material/Typography";
import TextField from "@mui/material/TextField";
import Box from "@mui/material/Box";


interface MonthlyGroceryAppFieldProps {
    label: string;
    value: string | number;
}

function MonthlyGroceryAppDisplayField({label, value}: MonthlyGroceryAppFieldProps) {
    return (
        <Box
            sx={{
                display: 'flex',
                alignItems: 'center', // Centers label vertically with the box
                mb: 2,
                width: '80%',
            }}
        >
            {/* Label Section */}
            <Typography
                sx={{
                    fontWeight: 600,
                    color: 'text.secondary',
                    width: '20%', // Adjust this to give more or less space to the label
                    minWidth: '80px',
                    pr: 2, // Padding between label and box
                }}
            >
                {label}
            </Typography>

            {/* Display Box Section */}
            <TextField
                value={value}
                variant="outlined"
                fullWidth // Fills the remaining 70% of the row
                slotProps={{
                    input: {
                        readOnly: true,
                    },
                }}
                sx={{
                    '& .MuiOutlinedInput-root': {
                        borderRadius: '4px',
                        backgroundColor: '#f9f9f9', // Subtle background to distinguish from input
                        '& fieldset': {
                            borderColor: 'rgba(0, 0, 0, 0.2)',
                        },
                    },
                    '& .MuiOutlinedInput-input': {
                        padding: '10px 14px', // Slimmer height for a more "data" feel
                    }
                }}
            />
        </Box>
    );
}

export default MonthlyGroceryAppDisplayField;
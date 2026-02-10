import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';


interface ITextInputProps {
    label: string;
}

function MonthlyGroceryAppInputField({label}: ITextInputProps) {
    return (
        <Box
            component="form"
            sx={{'& > :not(style)': {m: 1, width: '40%'}}}
            noValidate
            autoComplete="off"
        >
            <TextField id="outlined-basic" label={label} variant="outlined" sx={{
                '& .MuiOutlinedInput-root': {
                    borderRadius: '4px',
                }
            }}/>

        </Box>
    );
}

export default MonthlyGroceryAppInputField;
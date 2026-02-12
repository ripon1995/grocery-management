import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select, {type SelectChangeEvent} from '@mui/material/Select';


interface ISelectProps {
    label: string;
    value: string;
    onChange: (val: string) => void;
    options: string[];
}


function MonthlyGroceryAppSelectField({label, value, onChange, options}: ISelectProps) {

    const handleChange = (event: SelectChangeEvent) => {
        onChange(event.target.value);
    };

    return (
        <FormControl fullWidth sx={{mb: 2}}>
            <InputLabel id={`select-label-${label}`}>{label}</InputLabel>
            <Select
                labelId={`select-label-${label}`}
                value={value}
                label={label}
                onChange={handleChange}
                sx={{
                    textAlign: 'left',
                    '& .MuiOutlinedInput-notchedOutline': {
                        borderRadius: '4px',
                    }
                }}
            >
                {options.map((opt) => (
                    <MenuItem key={opt} value={opt}>
                        {opt.toUpperCase()}
                    </MenuItem>
                ))}
            </Select>
        </FormControl>
    );
}

export default MonthlyGroceryAppSelectField;
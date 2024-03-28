import Chip from '@mui/material/Chip';
import Paper from '@mui/material/Paper';
import ListItem from '@mui/material/ListItem';
import { ChipData } from './ChipData';

// Pulled from the example found at: https://mui.com/material-ui/react-chip/#chip-array


interface ChipsArrayProps {
    chipData: readonly ChipData[];
    handleClick: (clickedChip: ChipData) => void;
}

export default function ChipsArray({ chipData, handleClick }: ChipsArrayProps) {
    return (
        <Paper
            sx={{
                display: 'flex',
                flexWrap: 'wrap',
                listStyle: 'none',
                p: 0.5,
                m: 0,
                height: '9rem',
                position: 'absolute',
                right: '0',
                top: '-172px',
                bottom: '0',
                backgroundColor: 'transparent !important'
            }}
            component="ul"
            elevation={0}
        >
            {chipData.map((data) => {
                return (
                    <ListItem key={data.key}>
                        <Chip
                            label={data.label}
                            onClick={() => handleClick(data)}
                            sx={{
                                ml: 'auto'
                            }}
                        />
                    </ListItem>
                );
            })}
        </Paper>
    );
}

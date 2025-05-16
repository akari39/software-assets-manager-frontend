import * as React from 'react';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import { Button, InputAdornment, OutlinedInput, Stack, TextField } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';

export default function FilterSearchBar(props) {
    return <Stack
        direction="row"
        flexWrap="wrap"
        sx={{
            marginLeft: "32px",
            marginRight: "32px",
            marginTop: "8px",
            marginBottom: "8px",
            alignItems: "end",
        }}>
        <FormControl sx={{ m: 1, minWidth: 100 }} size="small">
            <TextField
                select
                defaultValue={props.default.value}
                label="搜索选项"
                placeholder='请选择...'
                variant='standard'
                onChange={props.onSortChange ?? (() => { })}
            >
                {props.options.map((option) => <MenuItem value={option.value}>{option.name}</MenuItem>)}
            </TextField>
        </FormControl>
        <Stack direction="row" alignItems="center" sx={{ flexGrow: 1 }}>
            <FormControl sx={{ m: 1 }} variant="outlined" fullWidth>
                <OutlinedInput
                    startAdornment={<InputAdornment position="start"><SearchIcon /></InputAdornment>}
                    placeholder={props.placeholder}
                    size='small'
                    onChange={props.onSearchChange ?? (() => { })}
                />
            </FormControl>
            <Button variant="contained" disableElevation onClick={props.onSearch}>搜索</Button>
        </Stack>
    </Stack>
}
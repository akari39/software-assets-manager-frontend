import { Chip, Stack } from "@mui/material";

export default function SingleChoiceChipFilter(props) {
    return <Stack
        direction="row"
        spacing="8px"
        sx={{
            marginLeft: "32px",
            marginRight: "32px",
            marginTop: "8px",
            marginBottom: "8px",
        }}>
        {
            Object.keys(props.choices).map((key, index) =>
                <Chip
                    key={key}
                    label={key}
                    variant={props.choices[key]['selected'] ? 'filled' : 'outlined'}
                    onClick={props.choices[key]['onClick']}
                />
            )
        }
    </Stack>
}
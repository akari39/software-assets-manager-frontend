import { Chip, Stack } from "@mui/material";
import { useState } from "react";

export default function SingleChoiceChipFilter(props) {
    const [choices, setChoices] = useState(props.choices);

    function setSelected(choiceName) {
        setChoices((prevState) => Object.fromEntries(
            Object.entries(prevState).map(([key, value]) => [
                key,
                { ...value, selected: key === choiceName }
            ])
        ));
    }

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
            Object.keys(choices).map((key, index) => {
                const choice = choices[key];
                return <Chip
                    key={key}
                    label={key}
                    variant={choice['selected'] ? 'filled' : 'outlined'}
                    color={'primary'}
                    onClick={() => {
                        setSelected(key);
                        choice['onClick'];
                    }}
                />;
            }
            )
        }
    </Stack>
}
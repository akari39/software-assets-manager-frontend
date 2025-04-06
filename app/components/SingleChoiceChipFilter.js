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

    console.log(choices);

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
            Object.keys(choices).map((key, index) =>
                <Chip
                    key={key}
                    label={key}
                    variant={choices[key]['selected'] ? 'filled' : 'outlined'}
                    onClick={() => {
                        setSelected(key);
                        choices[key]['onClick'];
                    }}
                />
            )
        }
    </Stack>
}
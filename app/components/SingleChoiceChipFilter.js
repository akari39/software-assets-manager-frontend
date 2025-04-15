import { Chip, Stack } from "@mui/material";
import { useState } from "react";

export default function SingleChoiceChipFilter(props) {
    const [selectedChoice, setSelectedChoice] = useState(
        props.choices.find((choice) => choice.isDefault) ?? null
    );

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
            props.choices.map((choice) => {
                const choiceIndex = props.choices.indexOf(choice);
                return <Chip
                    key={choiceIndex}
                    label={choice.name}
                    variant={selectedChoice == choice ? 'filled' : 'outlined'}
                    color={'primary'}
                    onClick={() => {
                        setSelectedChoice(choice);
                        props.onClick(choice);
                    }}
                />;
            }
            )
        }
    </Stack>
}
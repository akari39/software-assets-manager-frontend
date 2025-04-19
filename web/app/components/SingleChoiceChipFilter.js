import { Chip, Stack } from "@mui/material";
import { useState } from "react";

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
            props.choices.map((choice) => {
                const choiceIndex = props.choices.indexOf(choice);
                return <Chip
                    key={choiceIndex}
                    label={choice.name}
                    variant={props.selectedChoice == choice ? 'filled' : 'outlined'}
                    color={'primary'}
                    onClick={() => {
                        props.onClick(choice);
                    }}
                />;
            }
            )
        }
    </Stack>
}
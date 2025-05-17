// StyledMenu.jsx
import Menu from '@mui/material/Menu';
import { styled } from '@mui/material/styles';

const StyledMenu = styled((props) => (
  <Menu
    elevation={4}
    anchorOrigin={{
      vertical: 'bottom',
      horizontal: 'right',
    }}
    transformOrigin={{
      vertical: 'top',
      horizontal: 'right',
    }}
    {...props}
  />
))(({ theme }) => ({
  '& .MuiPaper-root': {
    borderRadius: 6,
    minWidth: 180,
    color:
      theme.palette.mode === 'light'
        ? 'rgba(0, 0, 0, 0.87)'
        : theme.palette.grey[300],
    boxShadow:
      'rgb(255 255 255 / 10%) 0px 0px 0px 1px, ' +
      'rgb(0 0 0 / 10%) 0px 10px 15px -3px, ' +
      'rgb(0 0 0 / 5%) 0px 4px 6px -2px',
    '& .MuiMenu-list': {
      padding: '4px 0',
    },
    '& .MuiMenuItem-root': {
      '&:hover': {
        backgroundColor: theme.palette.action.hover,
      },
    },
  },
}));

export default StyledMenu;

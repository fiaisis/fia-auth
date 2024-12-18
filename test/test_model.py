"""Model Tests"""

from unittest.mock import patch

from fia_auth.model import Role, User


@patch("fia_auth.model.is_staff_user")
@patch("fia_auth.model.is_instrument_scientist")
def test_role_is_user(mock_is_staff_user, mock_is_instrument_scientist):
    """Test user enum assign"""
    mock_is_staff_user.return_value = False
    mock_is_instrument_scientist.return_value = False

    user = User(user_number=1234)
    assert user.role == Role.USER


@patch("fia_auth.model.is_staff_user")
@patch("fia_auth.model.is_instrument_scientist")
def test_role_is_staff_in_db(mock_is_staff_user, mock_is_instrument_scientist):
    """Test staff enum assign"""
    mock_is_staff_user.return_value = True
    mock_is_instrument_scientist.return_value = False

    user = User(user_number=1234)
    assert user.role == Role.STAFF


@patch("fia_auth.model.is_staff_user")
@patch("fia_auth.model.is_instrument_scientist")
def test_role_is_staff_in_db_and_inst_scientist(mock_is_staff_user, mock_is_instrument_scientist):
    """Test staff enum assign"""
    mock_is_staff_user.return_value = True
    mock_is_instrument_scientist.return_value = True

    user = User(user_number=1234)
    assert user.role == Role.STAFF


@patch("fia_auth.model.is_staff_user")
@patch("fia_auth.model.is_instrument_scientist")
def test_role_is_staff_inst_scientist(mock_is_staff_user, mock_is_instrument_scientist):
    """Test staff enum assign"""
    mock_is_staff_user.return_value = False
    mock_is_instrument_scientist.return_value = True

    user = User(user_number=1234)
    assert user.role == Role.STAFF

"""Model Tests"""

from unittest.mock import patch

from fia_auth.model import Role, User


@patch("fia_auth.model.is_staff_user")
def test_role_is_user(mock_is_staff_user):
    """Test user enum assign"""
    mock_is_staff_user.return_value = False

    user = User(user_number=1234)
    assert user.role == Role.USER


@patch("fia_auth.model.is_staff_user")
def test_role_is_staff(mock_is_staff_user):
    """Test staff enum assign"""
    mock_is_staff_user.return_value = True

    user = User(user_number=1234)
    assert user.role == Role.STAFF

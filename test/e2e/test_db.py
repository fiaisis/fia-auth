"""
Test cases for db module
"""
from fia_auth.db import SESSION, Staff, is_staff_user


def test_is_staff_staff_user_exists():
    """
    test is staff returns true when staff exists
    """
    with SESSION() as session:
        staff = Staff(user_number=54321)
        session.add(staff)
        session.commit()

    assert is_staff_user(54321)


def test_is_staff_user_does_not_exist():
    """
    Test is staff returns false when not staff
    """
    assert not is_staff_user(5678)

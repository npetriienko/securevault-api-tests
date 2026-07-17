"""Auth: login endpoint tests.

Cases to cover:
    - valid credentials return a token
    - invalid password -> 401
    - unknown user -> 401
    - missing fields -> 400
    - locked/disabled account handling
"""

# import pytest
#
# @pytest.mark.auth
# @pytest.mark.smoke
# def test_login_with_valid_credentials():
#     ...

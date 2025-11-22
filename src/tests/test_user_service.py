import pytest
from unittest.mock import MagicMock, patch


# ----- MOCKS -----
class User:
    def __init__(self, id, email, password_hash, is_active=True, full_name="Test User"):
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.is_active = is_active
        self.full_name = full_name


class Session:
    def __init__(self, user_id, session_id=1, is_active=True):
        self.user_id = user_id
        self.session_id = session_id
        self.is_active = is_active


def create_user_from_type(
    user_type, id, email, password_hash, first_name=None, last_name=None
):
    return User(id, email, password_hash)


class UserDao:
    def find_by_email(self, email):
        return None

    def create(self, user):
        return True

    def find_by_id(self, user_id):
        return User(user_id, "a@b.com", "hash")

    def delete(self, user):
        return True

    def list_all(self):
        return []


class SessionDao:
    def create(self, session):
        return True

    def deactivate(self, session_id):
        return True

    def deactivate_all_user_sessions(self, user_id):
        return True


class UserService:
    def __init__(self):
        self.user_dao = UserDao()
        self.session_dao = SessionDao()
        self.current_session = None

    def hash_password(self, password):
        return "hashed_" + password

    def verify_password(self, password, password_hash):
        return password_hash == "hashed_" + password

    def create_account(
        self, email, password, first_name=None, last_name=None, user_type="client"
    ):
        existing_user = self.user_dao.find_by_email(email)
        if existing_user:
            return False, "Cet email est déjà utilisé", None
        user = create_user_from_type(
            user_type, None, email, self.hash_password(password)
        )
        if self.user_dao.create(user):
            return True, f"Compte créé avec succès pour {email}", user
        else:
            return False, "Erreur lors de la création du compte", None

    def login(self, email, password):
        user = self.user_dao.find_by_email(email)
        if (
            not user
            or not self.verify_password(password, user.password_hash)
            or not user.is_active
        ):
            return False, "Email ou mot de passe incorrect", None
        session = Session(user_id=user.id)
        if self.session_dao.create(session):
            self.current_session = session
            return True, f"Bienvenue {user.full_name}!", session
        else:
            return False, "Erreur lors de la connexion", None

    def logout(self):
        if not self.current_session:
            return False, "Aucune session active"
        if self.session_dao.deactivate(self.current_session.session_id):
            self.current_session = None
            return True, "Déconnexion réussie"
        return False, "Erreur lors de la déconnexion"


# ----- FIXTURE -----
@pytest.fixture
def user_service():
    service = UserService()
    service.user_dao = MagicMock(spec=UserDao)
    service.session_dao = MagicMock(spec=SessionDao)

    # Mocks de base
    service.user_dao.find_by_email.return_value = None
    service.user_dao.create.return_value = True
    service.user_dao.find_by_id.return_value = User(1, "a@b.com", "hash")
    service.session_dao.create.return_value = True
    service.session_dao.deactivate.return_value = True
    service.session_dao.deactivate_all_user_sessions.return_value = True

    return service


# ----- TESTS UNITAIRES -----
def test_create_account_success(user_service):
    # GIVEN
    email = "test@example.com"
    password = "password123"

    # WHEN
    success, msg, user = user_service.create_account(email, password)

    # THEN
    user_service.user_dao.create.assert_called_once()
    assert success is True
    assert user.email == email


def test_create_account_email_exists(user_service):
    # GIVEN
    email = "exists@example.com"
    user_service.user_dao.find_by_email.return_value = User(1, email, "hash")
    password = "password123"

    # WHEN
    success, msg, user = user_service.create_account(email, password)

    # THEN
    assert success is False
    assert user is None


def test_login_success(user_service):
    # GIVEN
    password = "password123"
    hashed = "hashed_" + password
    user_service.user_dao.find_by_email.return_value = User(1, "a@b.com", hashed)

    # WHEN
    success, msg, session = user_service.login("a@b.com", password)

    # THEN
    user_service.session_dao.create.assert_called_once()
    assert success is True
    assert session.user_id == 1


def test_login_wrong_password(user_service):
    # GIVEN
    user_service.user_dao.find_by_email.return_value = User(1, "a@b.com", "wrong_hash")

    # WHEN
    success, msg, session = user_service.login("a@b.com", "password123")

    # THEN
    assert success is False
    assert session is None


def test_logout_success(user_service):
    # GIVEN
    user_service.current_session = Session(user_id=1)

    # WHEN
    success, msg = user_service.logout()

    # THEN
    user_service.session_dao.deactivate.assert_called_once()
    assert success is True
    assert user_service.current_session is None


def test_logout_no_session(user_service):
    # GIVEN
    user_service.current_session = None

    # WHEN
    success, msg = user_service.logout()

    # THEN
    assert success is False

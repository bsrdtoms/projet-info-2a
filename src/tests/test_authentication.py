"""
Test script for the JWT authentication system
"""
import requests
import json
from typing import Optional

BASE_URL = "http://localhost:9876"

class TestAuthenticationSystem:
    def __init__(self):
        self.base_url = BASE_URL
        self.admin_token: Optional[str] = None
        self.designer_token: Optional[str] = None
        self.client_token: Optional[str] = None
        self.test_designer_email = "test_designer@example.com"
        self.test_client_email = "test_client@example.com"

    def print_section(self, title: str):
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}\n")

    def test_login_admin(self):
        """Test 1: Login with default admin account"""
        self.print_section("Test 1: Login Admin")

        response = requests.post(
            f"{self.base_url}/user/login",
            params={
                "email": "admin@magicsearch.com",
                "password": "our very secure password"
            }
        )

        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            self.admin_token = data["access_token"]
            print(f"✓ Login succeeded!")
            print(f"  User ID: {data['user_id']}")
            print(f"  Email: {data['email']}")
            print(f"  Role: {data['user_type']}")
            print(f"  Token (first 50 chars): {data['access_token'][:50]}...")
            return True
        else:
            print(f"✗ Login failed: {response.text}")
            return False

    def test_create_game_designer(self):
        """Test 2: Create a game_designer account (as admin)"""
        self.print_section("Test 2: Create a Game Designer account (via admin)")

        if not self.admin_token:
            print("✗ Failed: Admin token required (test 1 must succeed first)")
            return False

        # Create a game_designer account via the admin endpoint
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        response = requests.post(
            f"{self.base_url}/admin/user/",
            headers=headers,
            json={
                "email": self.test_designer_email,
                "password": "designer123",
                "first_name": "Test",
                "last_name": "Designer",
                "user_type": "game_designer"
            }
        )

        print(f"Status: {response.status_code}")
        if response.status_code in [200, 400]:
            if response.status_code == 200:
                print(f"✓ Game_designer account created")
            else:
                print(f"✓ Account already exists")

            # Login with the account
            response = requests.post(
                f"{self.base_url}/user/login",
                params={
                    "email": self.test_designer_email,
                    "password": "designer123"
                }
            )

            if response.status_code == 200:
                data = response.json()
                self.designer_token = data["access_token"]
                print(f"✓ Game_designer login succeeded")
                print(f"  User ID: {data['user_id']}")
                print(f"  Role: {data['user_type']}")

                # Verify the role is correct
                if data['user_type'] != 'game_designer':
                    print(f"✗ ERROR: Expected role 'game_designer', got '{data['user_type']}'")
                    return False

                return True

        print(f"✗ Failed: {response.text}")
        return False

    def test_create_client(self):
        """Test 3: Create a client account (public registration)"""
        self.print_section("Test 3: Create a Client account (public registration)")

        # Public registration - no token needed
        response = requests.post(
            f"{self.base_url}/user/register",
            json={
                "email": self.test_client_email,
                "password": "client123",
                "first_name": "Test",
                "last_name": "Client"
            }
        )

        print(f"Status: {response.status_code}")
        if response.status_code in [200, 400]:
            if response.status_code == 200:
                print(f"✓ Client account created via public registration")
            else:
                print(f"✓ Account already exists")

            # Login with the account
            response = requests.post(
                f"{self.base_url}/user/login",
                params={
                    "email": self.test_client_email,
                    "password": "client123"
                }
            )

            if response.status_code == 200:
                data = response.json()
                self.client_token = data["access_token"]
                print(f"✓ Client login succeeded")
                print(f"  User ID: {data['user_id']}")
                print(f"  Role: {data['user_type']}")

                # Verify the role is client
                if data['user_type'] != 'client':
                    print(f"✗ ERROR: Expected role 'client', got '{data['user_type']}'")
                    return False

                return True

        print(f"✗ Failed: {response.text}")
        return False

    def test_public_endpoint(self):
        """Test 4: Access to a public endpoint (no token required)"""
        self.print_section("Test 4: Public Endpoint (GET /card/random)")

        response = requests.get(f"{self.base_url}/card/random")

        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"✓ Public access succeeded (no token needed)")
            return True
        else:
            print(f"✗ Failed: {response.text}")
            return False

    def test_create_card_as_designer(self):
        """Test 5: Create a card as game_designer"""
        self.print_section("Test 5: Create a card (Game Designer)")

        headers = {"Authorization": f"Bearer {self.designer_token}"}

        response = requests.post(
            f"{self.base_url}/card/Test Card/This is a test card",
            headers=headers
        )

        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"✓ Card successfully created by game_designer")
            print(f"  Response: {response.json()}")
            return True
        else:
            print(f"✗ Failed: {response.text}")
            return False

    def test_create_card_as_client(self):
        """Test 6: Attempt to create a card as client (should fail)"""
        self.print_section("Test 6: Create a card (Client - should fail)")

        headers = {"Authorization": f"Bearer {self.client_token}"}

        response = requests.post(
            f"{self.base_url}/card/Unauthorized Card/This should fail",
            headers=headers
        )

        print(f"Status: {response.status_code}")
        if response.status_code == 403:
            print(f"✓ Access denied as expected (403 Forbidden)")
            print(f"  Message: {response.json()['detail']}")
            return True
        else:
            print(f"✗ Error: should return 403, returned {response.status_code}")
            return False

    def test_create_card_without_token(self):
        """Test 7: Attempt to create a card without token (should fail)"""
        self.print_section("Test 7: Create a card without token (should fail)")

        response = requests.post(
            f"{self.base_url}/card/Unauthenticated Card/This should fail"
        )

        print(f"Status: {response.status_code}")
        if response.status_code == 403:
            print(f"✓ Unauthenticated access denied as expected (403)")
            return True
        else:
            print(f"✗ Error: should return 403, returned {response.status_code}")
            return False

    def test_list_users_as_admin(self):
        """Test 8: List users as admin"""
        self.print_section("Test 8: List users (Admin)")

        headers = {"Authorization": f"Bearer {self.admin_token}"}

        response = requests.get(
            f"{self.base_url}/user/",
            headers=headers
        )

        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            users = response.json()
            print(f"✓ List retrieved successfully")
            print(f"  Number of users: {len(users)}")
            return True
        else:
            print(f"✗ Failed: {response.text}")
            return False

    def test_list_users_as_designer(self):
        """Test 9: Attempt to list users as designer (should fail)"""
        self.print_section("Test 9: List users (Designer - should fail)")

        headers = {"Authorization": f"Bearer {self.designer_token}"}

        response = requests.get(
            f"{self.base_url}/user/",
            headers=headers
        )

        print(f"Status: {response.status_code}")
        if response.status_code == 403:
            print(f"✓ Access denied as expected (403)")
            print(f"  Message: {response.json()['detail']}")
            return True
        else:
            print(f"✗ Error: should return 403, returned {response.status_code}")
            return False

    def test_invalid_token(self):
        """Test 10: Use an invalid token (should fail)"""
        self.print_section("Test 10: Invalid token (should fail)")

        headers = {"Authorization": "Bearer invalid_token_123"}

        response = requests.post(
            f"{self.base_url}/card/Invalid/Should fail",
            headers=headers
        )

        print(f"Status: {response.status_code}")
        if response.status_code == 401:
            print(f"✓ Invalid token rejected as expected (401)")
            print(f"  Message: {response.json()['detail']}")
            return True
        else:
            print(f"✗ Error: should return 401, returned {response.status_code}")
            return False

    def test_public_register_forces_client_role(self):
        """Test 11: Public registration forces client role even if another role is requested"""
        self.print_section("Test 11: Public registration forces 'client' role")

        # Try to register with a game_designer role via the public endpoint
        response = requests.post(
            f"{self.base_url}/user/register",
            json={
                "email": "sneaky_user@example.com",
                "password": "password123",
                "first_name": "Sneaky",
                "last_name": "User",
                "user_type": "game_designer"  # Attempt to get a privileged role
            }
        )

        print(f"Status: {response.status_code}")
        if response.status_code in [200, 400]:
            # Login to verify the actual role
            login_response = requests.post(
                f"{self.base_url}/user/login",
                params={
                    "email": "sneaky_user@example.com",
                    "password": "password123"
                }
            )

            if login_response.status_code == 200:
                user_data = login_response.json()
                if user_data['user_type'] == 'client':
                    print(f"✓ Role correctly forced to 'client' (security OK)")
                    print(f"  User type: {user_data['user_type']}")

                    # Clean up: delete this test account
                    if self.admin_token:
                        requests.delete(
                            f"{self.base_url}/user/{user_data['user_id']}",
                            headers={"Authorization": f"Bearer {self.admin_token}"}
                        )

                    return True
                else:
                    print(f"✗ SECURITY: Role not forced! User type: {user_data['user_type']}")
                    return False

        print(f"✗ Test failed")
        return False

    def test_non_admin_cannot_create_privileged_accounts(self):
        """Test 12: A non-admin cannot create privileged accounts"""
        self.print_section("Test 12: Non-admin cannot create privileged accounts")

        if not self.client_token:
            print("✗ Client token required")
            return False

        # Try to create a game_designer account as a client
        headers = {"Authorization": f"Bearer {self.client_token}"}
        response = requests.post(
            f"{self.base_url}/admin/user/",
            headers=headers,
            json={
                "email": "unauthorized_designer@example.com",
                "password": "password123",
                "first_name": "Unauthorized",
                "last_name": "Designer",
                "user_type": "game_designer"
            }
        )

        print(f"Status: {response.status_code}")
        if response.status_code == 403:
            print(f"✓ Access denied as expected (403)")
            print(f"  Message: {response.json()['detail']}")
            return True
        else:
            print(f"✗ Error: should return 403, returned {response.status_code}")
            return False

    def run_all_tests(self):
        """Execute all tests"""
        print("\n" + "="*60)
        print("  JWT AUTHENTICATION SYSTEM TEST")
        print("="*60)
        print(f"\nBase URL: {self.base_url}")
        print(f"Make sure the API is running before executing the tests!")

        input("\nPress Enter to continue...")

        results = []

        # Tests
        results.append(("Login Admin", self.test_login_admin()))
        results.append(("Create Game Designer (admin)", self.test_create_game_designer()))
        results.append(("Create Client (public)", self.test_create_client()))
        results.append(("Public Endpoint", self.test_public_endpoint()))
        results.append(("Create card (Designer)", self.test_create_card_as_designer()))
        results.append(("Create card (Client - denied)", self.test_create_card_as_client()))
        results.append(("Create card (No token - denied)", self.test_create_card_without_token()))
        results.append(("List users (Admin)", self.test_list_users_as_admin()))
        results.append(("List users (Designer - denied)", self.test_list_users_as_designer()))
        results.append(("Invalid token (denied)", self.test_invalid_token()))
        results.append(("Register forces client role", self.test_public_register_forces_client_role()))
        results.append(("Non-admin creates account - denied", self.test_non_admin_cannot_create_privileged_accounts()))

        # Summary
        self.print_section("TEST SUMMARY")

        passed = sum(1 for _, result in results if result)
        total = len(results)

        for test_name, result in results:
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"{status:10} | {test_name}")

        print(f"\n{'='*60}")
        print(f"Result: {passed}/{total} tests succeeded ({(passed/total)*100:.1f}%)")
        print(f"{'='*60}\n")

        if passed == total:
            print("All tests passed! The authentication system works correctly.")
        else:
            print("Some tests failed. Check the errors above.")


if __name__ == "__main__":
    tester = TestAuthenticationSystem()

    try:
        tester.run_all_tests()
    except requests.exceptions.ConnectionError:
        print("\nERROR: Unable to connect to the API")
        print(f"   Make sure the API is running on {BASE_URL}")
        print("   Launch the API with: python src/app.py")
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()

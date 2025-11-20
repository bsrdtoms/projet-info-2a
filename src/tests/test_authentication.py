"""
Script de test pour le système d'authentification JWT
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
        """Test 1: Login avec le compte admin par défaut"""
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
            print(f"✓ Login réussi!")
            print(f"  User ID: {data['user_id']}")
            print(f"  Email: {data['email']}")
            print(f"  Role: {data['user_type']}")
            print(f"  Token (premiers 50 car): {data['access_token'][:50]}...")
            return True
        else:
            print(f"✗ Échec du login: {response.text}")
            return False

    def test_create_game_designer(self):
        """Test 2: Créer un compte game_designer (en tant qu'admin)"""
        self.print_section("Test 2: Créer un compte Game Designer (via admin)")

        if not self.admin_token:
            print("✗ Échec: Token admin requis (le test 1 doit réussir d'abord)")
            return False

        # Créer un compte game_designer via l'endpoint admin
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
                print(f"✓ Compte game_designer créé")
            else:
                print(f"✓ Compte existe déjà")

            # Login avec le compte
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
                print(f"✓ Login game_designer réussi")
                print(f"  User ID: {data['user_id']}")
                print(f"  Role: {data['user_type']}")

                # Vérifier que le rôle est correct
                if data['user_type'] != 'game_designer':
                    print(f"✗ ERREUR: Rôle attendu 'game_designer', obtenu '{data['user_type']}'")
                    return False

                return True

        print(f"✗ Échec: {response.text}")
        return False

    def test_create_client(self):
        """Test 3: Créer un compte client (inscription publique)"""
        self.print_section("Test 3: Créer un compte Client (inscription publique)")

        # Inscription publique - pas besoin de token
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
                print(f"✓ Compte client créé via inscription publique")
            else:
                print(f"✓ Compte existe déjà")

            # Login avec le compte
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
                print(f"✓ Login client réussi")
                print(f"  User ID: {data['user_id']}")
                print(f"  Role: {data['user_type']}")

                # Vérifier que le rôle est client
                if data['user_type'] != 'client':
                    print(f"✗ ERREUR: Rôle attendu 'client', obtenu '{data['user_type']}'")
                    return False

                return True

        print(f"✗ Échec: {response.text}")
        return False

    def test_public_endpoint(self):
        """Test 4: Accès à un endpoint public (pas de token requis)"""
        self.print_section("Test 4: Endpoint Public (GET /card/random)")

        response = requests.get(f"{self.base_url}/card/random")

        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"✓ Accès public réussi (pas de token nécessaire)")
            return True
        else:
            print(f"✗ Échec: {response.text}")
            return False

    def test_create_card_as_designer(self):
        """Test 5: Créer une carte en tant que game_designer"""
        self.print_section("Test 5: Créer une carte (Game Designer)")

        headers = {"Authorization": f"Bearer {self.designer_token}"}

        response = requests.post(
            f"{self.base_url}/card/Test Card/This is a test card",
            headers=headers
        )

        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"✓ Carte créée avec succès par game_designer")
            print(f"  Response: {response.json()}")
            return True
        else:
            print(f"✗ Échec: {response.text}")
            return False

    def test_create_card_as_client(self):
        """Test 6: Tentative de créer une carte en tant que client (devrait échouer)"""
        self.print_section("Test 6: Créer une carte (Client - devrait échouer)")

        headers = {"Authorization": f"Bearer {self.client_token}"}

        response = requests.post(
            f"{self.base_url}/card/Unauthorized Card/This should fail",
            headers=headers
        )

        print(f"Status: {response.status_code}")
        if response.status_code == 403:
            print(f"✓ Accès refusé comme attendu (403 Forbidden)")
            print(f"  Message: {response.json()['detail']}")
            return True
        else:
            print(f"✗ Erreur: devrait retourner 403, a retourné {response.status_code}")
            return False

    def test_create_card_without_token(self):
        """Test 7: Tentative de créer une carte sans token (devrait échouer)"""
        self.print_section("Test 7: Créer une carte sans token (devrait échouer)")

        response = requests.post(
            f"{self.base_url}/card/Unauthenticated Card/This should fail"
        )

        print(f"Status: {response.status_code}")
        if response.status_code == 403:
            print(f"✓ Non authentifié refusé comme attendu (403)")
            return True
        else:
            print(f"✗ Erreur: devrait retourner 403, a retourné {response.status_code}")
            return False

    def test_list_users_as_admin(self):
        """Test 8: Lister les utilisateurs en tant qu'admin"""
        self.print_section("Test 8: Lister utilisateurs (Admin)")

        headers = {"Authorization": f"Bearer {self.admin_token}"}

        response = requests.get(
            f"{self.base_url}/user/",
            headers=headers
        )

        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            users = response.json()
            print(f"✓ Liste récupérée avec succès")
            print(f"  Nombre d'utilisateurs: {len(users)}")
            return True
        else:
            print(f"✗ Échec: {response.text}")
            return False

    def test_list_users_as_designer(self):
        """Test 9: Tentative de lister les utilisateurs en tant que designer (devrait échouer)"""
        self.print_section("Test 9: Lister utilisateurs (Designer - devrait échouer)")

        headers = {"Authorization": f"Bearer {self.designer_token}"}

        response = requests.get(
            f"{self.base_url}/user/",
            headers=headers
        )

        print(f"Status: {response.status_code}")
        if response.status_code == 403:
            print(f"✓ Accès refusé comme attendu (403)")
            print(f"  Message: {response.json()['detail']}")
            return True
        else:
            print(f"✗ Erreur: devrait retourner 403, a retourné {response.status_code}")
            return False

    def test_invalid_token(self):
        """Test 10: Utiliser un token invalide (devrait échouer)"""
        self.print_section("Test 10: Token invalide (devrait échouer)")

        headers = {"Authorization": "Bearer invalid_token_123"}

        response = requests.post(
            f"{self.base_url}/card/Invalid/Should fail",
            headers=headers
        )

        print(f"Status: {response.status_code}")
        if response.status_code == 401:
            print(f"✓ Token invalide rejeté comme attendu (401)")
            print(f"  Message: {response.json()['detail']}")
            return True
        else:
            print(f"✗ Erreur: devrait retourner 401, a retourné {response.status_code}")
            return False

    def test_public_register_forces_client_role(self):
        """Test 11: Inscription publique force le rôle client même si autre rôle demandé"""
        self.print_section("Test 11: Inscription publique force rôle 'client'")

        # Essayer de s'inscrire avec un rôle game_designer via l'endpoint public
        response = requests.post(
            f"{self.base_url}/user/register",
            json={
                "email": "sneaky_user@example.com",
                "password": "password123",
                "first_name": "Sneaky",
                "last_name": "User",
                "user_type": "game_designer"  # Tenter d'obtenir un rôle privilégié
            }
        )

        print(f"Status: {response.status_code}")
        if response.status_code in [200, 400]:
            # Login pour vérifier le rôle réel
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
                    print(f"✓ Rôle correctement forcé à 'client' (sécurité OK)")
                    print(f"  User type: {user_data['user_type']}")

                    # Nettoyer: supprimer ce compte de test
                    if self.admin_token:
                        requests.delete(
                            f"{self.base_url}/user/{user_data['user_id']}",
                            headers={"Authorization": f"Bearer {self.admin_token}"}
                        )

                    return True
                else:
                    print(f"✗ SÉCURITÉ: Rôle non forcé! User type: {user_data['user_type']}")
                    return False

        print(f"✗ Échec du test")
        return False

    def test_non_admin_cannot_create_privileged_accounts(self):
        """Test 12: Un non-admin ne peut pas créer de comptes privilégiés"""
        self.print_section("Test 12: Non-admin ne peut pas créer comptes privilégiés")

        if not self.client_token:
            print("✗ Token client requis")
            return False

        # Essayer de créer un compte game_designer en tant que client
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
            print(f"✓ Accès refusé comme attendu (403)")
            print(f"  Message: {response.json()['detail']}")
            return True
        else:
            print(f"✗ Erreur: devrait retourner 403, a retourné {response.status_code}")
            return False

    def run_all_tests(self):
        """Exécuter tous les tests"""
        print("\n" + "="*60)
        print("  TEST DU SYSTÈME D'AUTHENTIFICATION JWT")
        print("="*60)
        print(f"\nBase URL: {self.base_url}")
        print(f"Assurez-vous que l'API est lancée avant d'exécuter les tests!")

        input("\nAppuyez sur Entrée pour continuer...")

        results = []

        # Tests
        results.append(("Login Admin", self.test_login_admin()))
        results.append(("Créer Game Designer (admin)", self.test_create_game_designer()))
        results.append(("Créer Client (public)", self.test_create_client()))
        results.append(("Endpoint Public", self.test_public_endpoint()))
        results.append(("Créer carte (Designer)", self.test_create_card_as_designer()))
        results.append(("Créer carte (Client - refus)", self.test_create_card_as_client()))
        results.append(("Créer carte (Sans token - refus)", self.test_create_card_without_token()))
        results.append(("Lister users (Admin)", self.test_list_users_as_admin()))
        results.append(("Lister users (Designer - refus)", self.test_list_users_as_designer()))
        results.append(("Token invalide (refus)", self.test_invalid_token()))
        results.append(("Register force rôle client", self.test_public_register_forces_client_role()))
        results.append(("Non-admin crée compte - refus", self.test_non_admin_cannot_create_privileged_accounts()))

        # Résumé
        self.print_section("RÉSUMÉ DES TESTS")

        passed = sum(1 for _, result in results if result)
        total = len(results)

        for test_name, result in results:
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"{status:10} | {test_name}")

        print(f"\n{'='*60}")
        print(f"Résultat: {passed}/{total} tests réussis ({(passed/total)*100:.1f}%)")
        print(f"{'='*60}\n")

        if passed == total:
            print("🎉 Tous les tests sont passés! Le système d'authentification fonctionne correctement.")
        else:
            print("⚠️  Certains tests ont échoué. Vérifiez les erreurs ci-dessus.")


if __name__ == "__main__":
    tester = TestAuthenticationSystem()

    try:
        tester.run_all_tests()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERREUR: Impossible de se connecter à l'API")
        print(f"   Assurez-vous que l'API tourne sur {BASE_URL}")
        print("   Lancez l'API avec: python src/app.py")
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrompus par l'utilisateur")
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()

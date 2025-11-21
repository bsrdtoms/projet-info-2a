from views.abstract_view import AbstractView
from service.historical_service import HistoricalService
from service.card_service import CardService
from business_object.card import Card
from tabulate import tabulate
from datetime import datetime
import logging


class HistoryView(AbstractView):
    """Vue pour afficher et gérer l'historique des recherches d'un utilisateur"""

    def __init__(self, user):
        """
        Initialise la vue d'historique

        Parameters
        ----------
        user : User
            L'utilisateur actuellement connecté
        """
        self.user = user
        self.history_service = HistoricalService()
        self.card_service = CardService()

    def display(self):
        """Affiche le menu de gestion de l'historique"""
        self.show_title(f"Search History - {self.user.email}")
        print("1. View all searches")
        print("2. View search statistics")
        print("3. Delete a specific search")
        print("4. Clear all history")
        print("5. Repeat a past search")
        print("6. Return to main menu")

    def display_history_table(self, history):
        """
        Affiche l'historique sous forme de tableau

        Parameters
        ----------
        history : list[HistoricalSearch]
            Liste des recherches historiques
        """
        if not history:
            self.show_message("❌ No searches in history yet")
            return

        table_data = []
        for search in history:
            # Formater la date de manière lisible
            date_str = search.created_at.strftime("%d/%m/%Y %H:%M:%S")
            
            # Tronquer le texte de la requête s'il est trop long
            query = search.query_text[:40]
            if len(search.query_text) > 40:
                query += "..."

            table_data.append([
                search.id,
                query,
                search.result_count,
                date_str
            ])

        headers = ["ID", "Query", "Results", "Date"]
        print("\n" + tabulate(table_data, headers=headers, tablefmt="grid"))

    def view_all_searches(self):
        """Affiche toutes les recherches de l'utilisateur"""
        self.show_title("Your Search History")

        # Récupérer l'historique
        try:
            history = self.history_service.get_user_history(self.user.id, limit=100)

            if not history:
                self.show_message("📭 You haven't searched anything yet!")
                input("\nPress Enter to continue...")
                return

            # Afficher le nombre de recherches
            print(f"\n📊 Total searches: {len(history)}\n")

            self.display_history_table(history)

            # Afficher les détails de chaque recherche
            print("\n" + "=" * 70)
            print("DETAILED VIEW")
            print("=" * 70)

            for i, search in enumerate(history[:10], 1):  # Afficher max 10
                print(f"\n#{i} - Search ID: {search.id}")
                print(f"   Query: {search.query_text}")
                print(f"   Results: {search.result_count}")
                print(f"   Date: {search.created_at.strftime('%d/%m/%Y %H:%M:%S')}")

                if search.query_embedding:
                    print(f"   Embedding: {len(search.query_embedding)} dimensions")
                else:
                    print(f"   Embedding: None")

            if len(history) > 10:
                print(f"\n... and {len(history) - 10} more searches")

        except Exception as e:
            self.show_message(f"❌ Error retrieving history: {e}")
            logging.error(f"Error retrieving history: {e}", exc_info=True)

        input("\nPress Enter to continue...")

    def view_statistics(self):
        """Affiche les statistiques de recherche"""
        self.show_title("Search Statistics")

        try:
            stats = self.history_service.get_stats(self.user.id)

            if not stats or stats.get('total_searches', 0) == 0:
                self.show_message("📊 No search statistics available yet")
                input("\nPress Enter to continue...")
                return

            print("\n" + "=" * 70)
            print("YOUR SEARCH STATISTICS")
            print("=" * 70 + "\n")

            stats_table = [
                ["Total Searches", stats['total_searches']],
                ["Total Results Found", stats['total_results']],
                ["Average Results per Search", f"{stats['avg_results']:.2f}"],
                ["Most Recent Search", stats['most_recent'].strftime('%d/%m/%Y %H:%M:%S')],
                ["Oldest Search", stats['oldest'].strftime('%d/%m/%Y %H:%M:%S')],
            ]

            print(tabulate(stats_table, headers=["Metric", "Value"], tablefmt="grid"))

            print(f"\n📈 Analysis:")
            if stats['total_searches'] > 0:
                avg_results = stats['total_results'] / stats['total_searches']
                print(f"   • You average {avg_results:.1f} results per search")
                print(f"   • Your most productive search found {int(max(10, stats['avg_results']))} results")

        except Exception as e:
            self.show_message(f"❌ Error retrieving statistics: {e}")
            logging.error(f"Error retrieving statistics: {e}", exc_info=True)

        input("\nPress Enter to continue...")

    def delete_search(self):
        """Supprime une recherche spécifique"""
        self.show_title("Delete a Search")

        try:
            # Afficher l'historique d'abord
            history = self.history_service.get_user_history(self.user.id, limit=20)

            if not history:
                self.show_message("No searches to delete")
                input("\nPress Enter to continue...")
                return

            self.display_history_table(history)

            # Demander l'ID à supprimer
            search_id_input = self.get_input("\nEnter the search ID to delete (or 0 to cancel): ")

            try:
                search_id = int(search_id_input)
                if search_id == 0:
                    return

                # Vérifier que la recherche appartient à l'utilisateur
                found = any(s.id == search_id for s in history)
                if not found:
                    self.show_message(f"❌ Search ID {search_id} not found in your history")
                    input("\nPress Enter to continue...")
                    return

                # Supprimer
                if self.history_service.delete_search(search_id):
                    self.show_message(f"✅ Search #{search_id} deleted successfully!")
                else:
                    self.show_message(f"❌ Failed to delete search #{search_id}")

            except ValueError:
                self.show_message("❌ Please enter a valid number")

        except Exception as e:
            self.show_message(f"❌ Error: {e}")
            logging.error(f"Error deleting search: {e}", exc_info=True)

        input("\nPress Enter to continue...")

    def clear_history(self):
        """Vide tout l'historique"""
        self.show_title("Clear All History")

        print("\n⚠️  WARNING: This will delete ALL your search history!")
        print("This action cannot be undone.\n")

        confirm = self.get_input("Are you sure? (yes/no): ").strip().lower()

        if confirm == "yes":
            try:
                if self.history_service.clear_user_history(self.user.id):
                    self.show_message("✅ All history cleared successfully!")
                else:
                    self.show_message("❌ Failed to clear history")
            except Exception as e:
                self.show_message(f"❌ Error: {e}")
                logging.error(f"Error clearing history: {e}", exc_info=True)
        else:
            self.show_message("Cancelled")

        input("\nPress Enter to continue...")

    def repeat_search(self):
        """Permet de répéter une recherche passée"""
        self.show_title("Repeat a Past Search")

        try:
            # Afficher l'historique
            history = self.history_service.get_user_history(self.user.id, limit=20)

            if not history:
                self.show_message("No searches to repeat")
                input("\nPress Enter to continue...")
                return

            self.display_history_table(history)

            # Demander laquelle répéter
            search_id_input = self.get_input("\nEnter the search ID to repeat (or 0 to cancel): ")

            try:
                search_id = int(search_id_input)
                if search_id == 0:
                    return

                # Trouver la recherche
                search_to_repeat = None
                for s in history:
                    if s.id == search_id:
                        search_to_repeat = s
                        break

                if not search_to_repeat:
                    self.show_message(f"❌ Search ID {search_id} not found")
                    input("\nPress Enter to continue...")
                    return

                # Effectuer la recherche
                self.show_message(f"🔍 Searching for: '{search_to_repeat.query_text}'...")
                
                results = self.card_service.semantic_search(
                    search_to_repeat.query_text,
                    top_k=5,
                    user_id=self.user.id
                )

                # Afficher les résultats
                print("\n" + "=" * 70)
                print("SEARCH RESULTS")
                print("=" * 70 + "\n")

                if results:
                    for i, (card, similarity) in enumerate(results, 1):
                        print(f"\n{i}. {card.name} (Similarity: {similarity:.4f})")
                        if card.text:
                            text_preview = card.text[:100]
                            if len(card.text) > 100:
                                text_preview += "..."
                            print(f"   {text_preview}")
                else:
                    print("❌ No results found")

            except ValueError:
                self.show_message("❌ Please enter a valid number")

        except Exception as e:
            self.show_message(f"❌ Error: {e}")
            logging.error(f"Error repeating search: {e}", exc_info=True)

        input("\nPress Enter to continue...")

    def menu_choice(self):
        """Gère les choix du menu"""
        while True:
            self.display()
            choice = self.get_input()

            if choice == "1":
                self.view_all_searches()

            elif choice == "2":
                self.view_statistics()

            elif choice == "3":
                self.delete_search()

            elif choice == "4":
                self.clear_history()

            elif choice == "5":
                self.repeat_search()

            elif choice == "6":
                break

            else:
                self.show_message("❌ Invalid choice, please try again")
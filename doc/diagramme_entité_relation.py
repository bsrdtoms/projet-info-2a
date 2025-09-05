from graphviz import Digraph

# Création du diagramme
dot = Digraph('ERD', comment='ER Diagram for MagicSearch')

# Définition des entités
dot.node('Card', 'Card\n- id (PK)\n- name\n- type\n- color\n- text\n- vector_embedding')
dot.node('Set', 'Set\n- id (PK)\n- name\n- release_date')
dot.node('Type', 'Type\n- id (PK)\n- name')

# Relations
# Card appartient à un Set (1:N)
dot.edge('Set', 'Card', label='1:N')

# Card peut avoir plusieurs Types (N:M)
dot.edge('Card', 'Type', label='N:M')

# Génération du fichier
dot.render('magicsearch_erd', format='png', cleanup=True)

print("Diagramme ERD généré : magicsearch_erd.png")


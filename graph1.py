import streamlit as st
import random
import networkx as nx
from streamlit_agraph import agraph, Node, Edge, Config

st.title("Visualisation de graphe interactif")

#methode pour generer un graph aléatoire
def genere_graphe_aleatoire(n, p, seed=None):
    """
    Modèle Erdős–Rényi G(n, p)
    n : nombre de nœuds
    p : probabilité d'existence de chaque arête
    """
    G = nx.Graph()
    random.seed(seed)

    for u in range(n):
        for v in range(u + 1, n):
            r = random.random()        # r ∈ [0, 1[
            if r < p:
                G.add_edge(u, v)
                
    for i in range(n):
        G.add_node(i)

    return G

#methode pour déterminer la clique dans une graph graph
def bron_kerbosch(R, P, X, graph, cliques):
    if not P and not X:
        cliques.append(set(R))
        return
    
    for v in list(P):
        neighbors = set(graph.neighbors(v))  # N(v) via NetworkX
        bron_kerbosch(
            R | {v},
            P & neighbors,
            X & neighbors,
            graph,
            cliques
        )
        P = P - {v}
        X = X | {v}

def find_max_cliques(graph):
    """
    graph : networkx.Graph
    """
    V = set(graph.nodes())
    cliques = []
    bron_kerbosch(set(), V, set(), graph, cliques)
    return cliques

# Palette de couleurs distinctes pour les cliques
COLORS = [
    "#e74c3c", "#3498db", "#2ecc71", "#f39c12", "#9b59b6",
    "#1abc9c", "#e67e22", "#e91e63", "#00bcd4", "#8bc34a",
]

def get_node_color(node, cliques):
    """Retourne la couleur uniquement si le nœud est dans la plus grande clique."""
    if not cliques:
        return "#95a5a6"
    
    max_size = max(len(c) for c in cliques)
    largest_cliques = [c for c in cliques if len(c) == max_size]
    
    for i, clique in enumerate(largest_cliques):
        if node in clique:
            return COLORS[i % len(COLORS)]
    
    return "#95a5a6"  # gris = pas dans une clique maximale


# --- Sidebar : paramètres ---
st.sidebar.header("Paramètres du graphe")
nb_nodes     = st.sidebar.slider("Nombre de nœuds", 5, 50, 10)
prob         = st.sidebar.slider("Probabilité de connexion", 0.0, 1.0, 0.3)
layout_type  = st.sidebar.selectbox("Type de layout", ["spring", "circular", "random"])
show_cliques = st.sidebar.toggle("Colorier les cliques", value=False)

# --- Génération du graphe (persisté en session) ---
if st.sidebar.button("Générer un nouveau graphe"):
    st.session_state.G = genere_graphe_aleatoire(nb_nodes, prob)

if "G" not in st.session_state:
    st.session_state.G = genere_graphe_aleatoire(nb_nodes, prob)

G = st.session_state.G

# --- Calcul des cliques ---
cliques = find_max_cliques(G) if show_cliques else []

# Trier par taille décroissante pour afficher les plus grandes en priorité
cliques_sorted = sorted(cliques, key=len, reverse=True)

# --- Construction des nœuds / arêtes pour agraph ---
if layout_type == "spring":
    pos = nx.spring_layout(G, seed=42)
elif layout_type == "circular":
    pos = nx.circular_layout(G)
else:
    pos = nx.random_layout(G, seed=42)


nodes = []
for n in G.nodes():
    x, y = pos[n]
    color = get_node_color(n, cliques_sorted) if show_cliques else "#3498db"
    nodes.append(Node(
        id=str(n),
        label=str(n),
        size=10,
        color=color,
        x=float(x) * 400,
        y=float(y) * 400,
    ))

edges = [Edge(source=str(u), target=str(v), width=2, directed=False) for u, v in G.edges()]

config = Config(
    width=700,
    height=500,
    directed=False,
    physics=False,
    hierarchical=False,
)

agraph(nodes=nodes, edges=edges, config=config)

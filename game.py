# Šajā daļā tiek importētas nepieciešamās bibliotēkas
# random - lai ģenerētu nejaušus skaitļus 
# time - lai mērītu algoritmu darbības laiku 
# math - matemātiskām funkcijām, ja nepieciešams
# tkinter - grafiskās saskarnes izveidei
# HUMAN un AI ir konstantes, kas apzīmē spēlētāju tipus
# HUMAN = 0 nozīmē cilvēka spēlētājs
# AI = 1 nozīmē mākslīgais intelekts
# Šādi ir ērtāk pārslēgties starp spēlētājiem, neizmantojot tekstuālus nosaukumus

# Importētās bibliotēkas
import random # nejauša skaitļa ģenerēšanai
import time # laika mērīšanai
import math # matemātiskām funkcijām
import tkinter as tk
from tkinter import ttk, messagebox

# Spēlētāju konstantes
HUMAN = 0
AI = 1

# Move klase

class Move:
    def __init__(self, divisor):
        self.divisor = divisor  # 2 or 3

# GameState klase

# Šī klase apraksta visu spēles stāvokli konkrētajā brīdī 
class GameState:
    def __init__(self, n, score_human, score_ai, player_to_move):
        self.n = n
        self.score_human = score_human
        self.score_ai = score_ai
        self.player_to_move = player_to_move  # HUMAN or AI
# Nosaka legālos gājienus
    def legal_moves(self):
        moves = []
        if self.n % 2 == 0:
            moves.append(Move(2))
        if self.n % 3 == 0:
            moves.append(Move(3))
        return moves
# Pārbauda vai spēle ir beigusies
    def is_terminal(self):
        return self.n <= 10 or (len(self.legal_moves()) == 0)
# Nosaka, kāpēc spēle beigusies
    def terminal_reason(self):
        if self.n <= 10:
            return "number_reached"
        if len(self.legal_moves()) == 0:
            return "no_moves"
        return None
 # Pārbauda vai vispār var veikt gājienu
    def can_move(self):
        return len(self.legal_moves()) > 0
# Izpilda gājienu
    def apply(self, move):
        d = move.divisor
        if d not in (2, 3):
            raise ValueError("Invalid move divisor")
        if self.n % d != 0:
            raise ValueError("Illegal move (non-integer division)")

        new_n = self.n // d
        sh = self.score_human
        sa = self.score_ai

        # Scoring rules:
        # divide by 2 -> opponent gets +2
        # divide by 3 -> current player gets +3
        if d == 2:
            if self.player_to_move == HUMAN:
                sa += 2
            else:
                sh += 2
        else:  # d == 3
            if self.player_to_move == HUMAN:
                sh += 3
            else:
                sa += 3

        next_player = AI if self.player_to_move == HUMAN else HUMAN
        return GameState(new_n, sh, sa, next_player)
# Nosaka uzvarētāju
    def winner(self):
        # Return HUMAN / AI / None for draw, only valid when terminal.
        if not self.is_terminal():
            return None
        if self.score_human == self.score_ai:
            return None
        if self.score_human > self.score_ai:
            return HUMAN
        return AI


# -----------------------------
# Node + SearchStats (simple classes)
# -----------------------------
class Node:
    def __init__(self, state, move_from_parent=None, parent=None, depth=0):
        self.state = state
        self.move_from_parent = move_from_parent
        self.parent = parent
        self.depth = depth
        self.value = None
        self.children = []


class SearchStats:
    def __init__(self):
        self.generated_nodes = 0
        self.evaluated_nodes = 0


# -----------------------------
# Heuristic evaluation
# -----------------------------
def heuristic(state):
    """
    Evaluation from AI perspective: higher is better for AI.
    Depth-limited search needs heuristic for non-terminal nodes.

    - base: score difference (AI - human)
    - plus small term based on size of n (bigger n => more future moves possible)
    - plus mobility (number of legal moves for side to move) as a tiny tie-breaker
    """
    score_diff = state.score_ai - state.score_human

    # Estimate remaining "room": if n is large, more moves remain.
    # Use log so it doesn't dominate.
    if state.n <= 10:
        room = 0.0
    else:
        room = math.log(state.n / 10.0)

    mobility = len(state.legal_moves())

    # If it's AI to move, mobility is good; if human to move, mobility is slightly bad for AI
    if state.player_to_move == AI:
        mobility_term = 0.2 * mobility
    else:
        mobility_term = -0.2 * mobility

    return score_diff + 0.3 * room + mobility_term


def terminal_utility(state):
    """Hard utility for terminal positions, from AI perspective."""
    if state.score_ai > state.score_human:
        return 1000000.0 + (state.score_ai - state.score_human)
    if state.score_ai < state.score_human:
        return -1000000.0 - (state.score_human - state.score_ai)
    return 0.0


# -----------------------------
# Minimax (depth-limited)
# Builds Node structure and tracks stats.
# -----------------------------
def minimax_decision(root_state, depth_limit):
    stats = SearchStats()
    root = Node(state=root_state, depth=0)

    def max_value(node, depth):
        stats.generated_nodes += 1

        if node.state.is_terminal():
            stats.evaluated_nodes += 1
            v = terminal_utility(node.state)
            node.value = v
            return v

        if depth == 0:
            stats.evaluated_nodes += 1
            v = heuristic(node.state)
            node.value = v
            return v

        v = -float("inf")
        for mv in node.state.legal_moves():
            child_state = node.state.apply(mv)
            child = Node(state=child_state, move_from_parent=mv, parent=node, depth=node.depth + 1)
            node.children.append(child)

            v = max(v, min_value(child, depth - 1))

        node.value = v
        return v
###########//Martins
    def min_value(node, depth):
        stats.generated_nodes += 1  #katrā iterācijā pieskaita izveidoto node skaitu

        if node.state.is_terminal(): # ja spēle šajā state ir beigusies, pārtrauc un atgriež novērtējumu
            stats.evaluated_nodes += 1 # katrā iterācija pieskatia apskatīto node skaitu
            v = terminal_utility(node.state)
            node.value = v
            return v

        if depth == 0: #ja dziļums ir izsmelts, pārtrauc un atgriež novērtējumu
            stats.evaluated_nodes += 1
            v = heuristic(node.state)
            node.value = v
            return v

        v = float("inf")
        for mv in node.state.legal_moves(): #apskata visus iespējamos gājienus, izveido child states
            child_state = node.state.apply(mv)
            child = Node(state=child_state, move_from_parent=mv, parent=node, depth=node.depth + 1)
            node.children.append(child)

            v = min(v, max_value(child, depth - 1))

        node.value = v
        return v

    # Decide best move for side-to-move:
    # If AI to move -> maximize; if HUMAN -> minimize (from AI perspective).
    best_move = None

    if root_state.player_to_move == AI:
        best_val = -float("inf")  #sākuma novērtējums
        for mv in root_state.legal_moves():
            child_state = root_state.apply(mv)
            child = Node(state=child_state, move_from_parent=mv, parent=root, depth=1)
            root.children.append(child)

            val = min_value(child, depth_limit - 1)
            if val > best_val:
                best_val = val
                best_move = mv
        root.value = best_val
    else:
        best_val = float("inf")
        for mv in root_state.legal_moves():
            child_state = root_state.apply(mv)
            child = Node(state=child_state, move_from_parent=mv, parent=root, depth=1)
            root.children.append(child)

            val = max_value(child, depth_limit - 1)
            if val < best_val:
                best_val = val
                best_move = mv
        root.value = best_val

    if best_move is None:
        # No moves -> terminal anyway; fallback
        best_move = Move(2)

    return best_move, root, stats


# -----------------------------
# Alpha-Beta (depth-limited)
# Builds Node structure and tracks stats.
# -----------------------------
def alphabeta_decision(root_state, depth_limit):
    stats = SearchStats()
    root = Node(state=root_state, depth=0)

    def max_value(node, depth, alpha, beta):
        stats.generated_nodes += 1

        if node.state.is_terminal():
            stats.evaluated_nodes += 1
            v = terminal_utility(node.state)
            node.value = v
            return v

        if depth == 0:
            stats.evaluated_nodes += 1
            v = heuristic(node.state)
            node.value = v
            return v

        v = -float("inf")
        for mv in node.state.legal_moves():
            child_state = node.state.apply(mv)
            child = Node(state=child_state, move_from_parent=mv, parent=node, depth=node.depth + 1)
            node.children.append(child)

            v = max(v, min_value(child, depth - 1, alpha, beta))
            if v >= beta:
                node.value = v
                return v
            alpha = max(alpha, v)

        node.value = v
        return v

    def min_value(node, depth, alpha, beta):
        # Šī funkcija aprēķina minimālo vērtību bērnu mezglam
        # (no AI perspektīvas tas atbilst cilvēka gājienam).
        # Tiek izmantots alfa-bēta griešana, lai attēlotu optimālu spēli un
        # saīsinātu meklēšanu, ja rezultāts jau ir mazāks par alfa.
        stats.generated_nodes += 1  # palielina radīto mezglu skaitu

        # Ja pašreizējā stāvoklī spēle ir beigusies, atgriež terminālo vērtību
        if node.state.is_terminal():
            stats.evaluated_nodes += 1
            v = terminal_utility(node.state)
            node.value = v
            return v

### /Martins
        # Ja sasniegts meklēšanas dziļuma limits, izmanto heuristiku,
        # lai novērtētu pozīciju un atgrieztu “aptuveno” vērtību.
        if depth == 0:
            stats.evaluated_nodes += 1  # palielina novērtēto mezglu skaitu
            v = heuristic(node.state)
            node.value = v
            return v

        # sākotnēji pieņem, ka minimālā vērtība ir bezgalīga
        v = float("inf")
        for mv in node.state.legal_moves():
            # izveido bērna stāvokli un pievieno to kokam
            child_state = node.state.apply(mv)
            child = Node(state=child_state, move_from_parent=mv, parent=node, depth=node.depth + 1)
            node.children.append(child)

            # rekursīvi aprēķina maksimālo vērtību bērnam
            v = min(v, max_value(child, depth - 1, alpha, beta))
            # alfa–beta griešana: ja v jau ir mazāks vai vienāds ar alfa,
            # nav vērts turpināt cilpu, jo ieteikums tiks sagriezts
            if v <= alpha:
                node.value = v
                return v
            # atjauno beta, tas ir, labāko minimālo vērtību redzēto gājienu vidū
            beta = min(beta, v)

        node.value = v
        return v

    best_move = None  # saglabā labāko gājienu

    # izvēlamies gājienu atkarībā no tā, kura spēlētāja kārta ir pienākusi
    if root_state.player_to_move == AI:
        # AI gājiens: AI cenšas maksimizēt kopējo vērtību, tāpēc sākam ar -inf, jo jebkura atrastā vērtība būs labāka par to
        best_val = -float("inf")
        alpha = -float("inf")
        beta = float("inf")

        for mv in root_state.legal_moves(): # AI gājienā pārbaudām katru iespējamo gājienu, izveidojam bērnu mezglu un iegūstam tā vērtību ar min_value funkciju, kas atgriež minimālo vērtību no AI perspektīvas. Ja šī vērtība ir labāka par pašreizējo best_val, atjaunojam best_val un saglabājam šo gājienu kā best_move. Pēc tam atjaunojam alfa vērtību, lai noraidītu sliktus gājienus nākotnē.
            # pārbaudām katru iespējamo gājienu citam spēles n vērtībai
            child_state = root_state.apply(mv) # izveidojam bērna stāvokli, kas rodas pēc gājiena izpildes
            child = Node(state=child_state, move_from_parent=mv, parent=root, depth=1) # izveidojam bērna mezglu kokā ar informāciju par stāvokli, gājienu, vecāku un dziļumu
            root.children.append(child) # pievienojam bērnu mezglu saknes bērniem

            # rekursīvi aprēķinām minimālo vērtību bērnam, jo pēc AI gājiena nāk cilvēka gājiens, kas cenšas samazināt kopējo vērtību
            val = min_value(child, depth_limit - 1, alpha, beta) # izsaucam min_value, jo pēc AI gājiena nāk cilvēka gājiens, kas cenšas samazināt kopējo vērtību. Pārejam uz nākamo dziļuma līmeni, samazinot depth_limit par 1
            if val > best_val:
                best_val = val
                best_move = mv
            # atjaunojam alfa ar jaunāko labāko rezultātu
            alpha = max(alpha, best_val)

        root.value = best_val
    else:
        # Cilvēka gājiens: AI var tikai samazināt kopējo vērtību
        # Inializē labāko vērtību uz bezgalību, jo mēs meklējam minimumu
        best_val = float("inf")
        alpha = -float("inf")  # mazākā vērtība, ko mēs jebkad redzējam
        beta = float("inf")    # lielākā vērtība, ko mēs jebkad redzējam

        # Pārbaudām katru iespējamo gājienu, kuram cilvēks pārvietojas
        for mv in root_state.legal_moves():
            # Izpildām gājienu un izvedojam jaunu spēles stāvokli
            child_state = root_state.apply(mv)
            # Izveidojam mezglu kokā ar informāciju par gājienu un dziļumu
            child = Node(state=child_state, move_from_parent=mv, parent=root, depth=1)
            root.children.append(child)

            # Izsaucam max_value, jo pēc cilvēka gājiena ir AI kārta maksimizēt
            val = max_value(child, depth_limit - 1, alpha, beta)
            # Ja šis gājiens dod sliktāku rezultātu, tas ir labāk cilvēkam
            if val < best_val:
                best_val = val
                best_move = mv
            # Atjaunojam beta, lai noraidietu sliktus gājienus nākotnē
            beta = min(beta, best_val)

        # Saglabāsim labāko vērtību šajā mezglā
        root.value = best_val

    # Drošības pārbaude: ja neparamādi neviens gājiens netika atrasts (neturētos brīdi)
    if best_move is None:
        # Izmantojam noklusējuma gājienu - dalīt ar 2
        best_move = Move(2)  # Fallback

    # Atgriežam labāko gājienu, pilno koku un statistiku par meklēšanu
    return best_move, root, stats


# Funkcija, kas ģenerē sākuma skaitļus eksperimentiem.
# Katrs skaitlis ir 6 daudzkārtnis, jo spēlē var dalīt ar 2 vai 3.
def generate_start_numbers(k=5, low=10000, high=20000, seed=None):
    # Ja sēkla ir norādīta, uzstāda pseudogadījuma ģeneratoru konsekventos rezultātiem
    if seed is not None:
        random.seed(seed)

    nums = set()
    # Ģenerējam k dažādus skaitļus diapazonā no low līdz high
    while len(nums) < k:
        # Izvēlas nejaušu skaitli norādītajā diapazonā
        x = random.randint(low, high)
        # Noapaļo uz leju līdz tuvākajam 6 daudzkārtnim,
        # lai nodrošinātu, ka vismaz viens gājiens vienmēr ir iespējams
        x = x - (x % 6) 
        # Pārbauda, vai noapaļotais skaitlis vēl atrodas pieļautajā diapazonā
        if x < low:
            continue
        nums.add(x)

    # Kārtējam iegūtos skaitļus augošā secībā un atgriežam
    nums = sorted(list(nums))
    return nums



# Šī funkcija simulē veselu spēles partiju starp AI un cilvēku (abi spēlē optimāli).
# Tā ievāc statistiku: uzvarētāju, gājienu skaitu, domas laiku un pārbaudīto mezglu skaitu.
def play_game_simulated(start_n, algo, depth_limit, seed):
    # Izveido pseudogadījuma ģeneratoru ar dotos sēklas, lai reproducējams
    rnd = random.Random(seed)
    # Sākotnējais spēles stāvoklis: skaitlis ir start_n, abi spēlētāji sākumā bez punktiem
    # Cilvēks sāk spēli
    state = GameState(start_n, 0, 0, HUMAN) 

    # Mainīgie statistikas izkopošanai
    total_ai_time = 0.0  # kopējais laiks, ko AI pavada "domāšanā"
    ai_moves = 0  # cik reizes AI padarīja gājienu
    total_generated = 0  # cik kopā mezglu tika ģenerēti meklēšanā
    total_evaluated = 0  # cik kopā mezglu tika novērtēti ar heuristiku/terminālo utilit

    # Spēles cikls turpinās, kamēr spēle nav beigusies
    while not state.is_terminal():
        # Saņem visus pieļautos gājienus pašreizējā pozīcijā
        moves = state.legal_moves()
        # Ja nav pieļauto gājienu, spēle ir beigusies
        if len(moves) == 0:
            break

         #Aleksandrs start
        
        # Human simulācijā dara random legālu gājienu un atjauno state
        if state.player_to_move == HUMAN:
            mv = rnd.choice(moves)
            state = state.apply(mv)

        # AI izvēlas gājienu ar minimax vai alphabeta, izmēra laiku un krāj search statistiku
        else:
            t0 = time.perf_counter()
            if algo == "minimax":
                mv, root, st = minimax_decision(state, depth_limit)
            else:
                mv, root, st = alphabeta_decision(state, depth_limit)
            dt = time.perf_counter() - t0
            
            total_ai_time += dt
            ai_moves += 1

            total_generated += st.generated_nodes
            total_evaluated += st.evaluated_nodes

            state = state.apply(mv)

    # Nosaka uzvarētāju un atgriež rezultātu objektu priekš eksperimentu analīzes
    winner = state.winner()
    if winner is None:
        winner_str = "draw"
    elif winner == HUMAN:
        winner_str = "human"
    else:
        winner_str = "ai"

    # Atgriežam vienu rezultāta objektu priekš eksperimentu tabulas, te ir sākuma skaitlis, algoritms, dziļums, uzvarētājs, gala skaitlis, punkti un performance statistika
    return {
        "start_n": start_n,
        "algo": algo,
        "depth": depth_limit,
        "winner": winner_str,
        "final_n": state.n,
        "human_score": state.score_human,
        "ai_score": state.score_ai,
        "ai_move_time_avg": (total_ai_time / ai_moves) if ai_moves else 0.0,
        "generated_nodes_total": total_generated,
        "evaluated_nodes_total": total_evaluated,
        "ai_moves": ai_moves,
    }


def run_experiments(depth_limit=8, games_per_algo=10):
    results = []
    base_seed = 12345  # fiksēts seed reproducējamībai

    starts = []
    for i in range(games_per_algo):
        starts.append(generate_start_numbers(seed=base_seed + i)[0])  # deterministiski start_n katrai spēlei

    for algo in ("minimax", "alphabeta"):  # salīdzinām abus algoritmus vienādos apstākļos
        for i in range(games_per_algo):
            res = play_game_simulated(
                start_n=starts[i], # vienādi start_n abiem algoritmiem
                algo=algo, # izvēlētais algoritms šajā ciklā
                depth_limit=depth_limit, # vienāds dziļums visiem eksperimentiem
                seed=base_seed + 1000 + i  # atsevišķs seed human random gājieniem
            )
            results.append(res) # res jau satur ai_move_time_avg, nodes, winner utt.

    return results

class GameApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # Uztaisām galveno logu un uzliekam nosaukumu un izmēru
        self.title("Dalīšanas spēle: Minimax / Alpha-Beta")
        self.geometry("760x480")

        # Uzģenerējam sākuma skaitļus un sagatavojam UI mainīgos, kurus var piesaistīt radiobuttoniem un dropdowniem
        self.start_numbers = generate_start_numbers() # Ģenerē iespējamos sākuma skaitļus, ko lietotājs var izvēlētie
        self.selected_start = tk.IntVar(value=self.start_numbers[0]) # Tkinter mainīgais, kas glabā izvēlēto sākuma skaitli
        self.first_player = tk.StringVar(value="human") # Nosaka, kurš sāk spēli (cilvēks vai dators)
        self.algorithm = tk.StringVar(value="alphabeta") # Izvēlētais AI algoritms (minimax vai alphabeta)
        self.depth_limit = tk.IntVar(value=8) # Meklēšanas dziļuma limits AI algoritmam

         # Mainīgie spēles stāvoklim un pēdējā AI search rezultātam, lai varētu rādīt vai debugot
        self.state = None # Pašreizējais spēles stāvoklis
        self.last_tree_root = None
        self.last_stats = None # Saglabā pēdējā AI meklēšanas koka sakni un statistiku (mezglu skaits utt.)

        self._build_ui()
        self._refresh_start_numbers_ui() 
        self._set_status("Izvēlies sākuma skaitli un iestatījumus, tad spied 'Sākt'.")

    def _build_ui(self):
        # Augšējais frame priekš izvēlēm un iestatījumiem, ieliekam to loga augšā un izstiepjam pa X asi
        top = ttk.Frame(self, padding=10)
        top.pack(side=tk.TOP, fill=tk.X) # Novieto augšējo UI bloku loga augšā un izstiepj pa horizontāli
        
        # Teksts, kas paskaidro ko lietotājs izvēlas kreisajā pusē
        ttk.Label(top, text="Sākuma skaitļi (dalās ar 2 un 3):").grid(row=0, column=0, sticky="w")

        # Frame, kurā tiks ielikti konkrētie start number radiobuttoni vai pogas
        self.numbers_frame = ttk.Frame(top)
        self.numbers_frame.grid(row=1, column=0, sticky="w", pady=(6, 10))
        
        # Labais frame ar kontrolēm, piemēram algo izvēle, depth, kurš sāk, un start poga
        controls = ttk.Frame(top)
        controls.grid(row=0, column=1, rowspan=2, sticky="ne", padx=(20, 0)) # Iestatījumu panelis labajā pusē, aizņem 2 rindas, pielīdzināts augšējā labajā stūrī

        #Aleksandrs end

        ttk.Label(controls, text="Kas sāk:").grid(row=0, column=0, sticky="w")
        ttk.Radiobutton(controls, text="Cilvēks", variable=self.first_player, value="human").grid(row=1, column=0, sticky="w")
        ttk.Radiobutton(controls, text="Dators", variable=self.first_player, value="ai").grid(row=2, column=0, sticky="w")

        ttk.Label(controls, text="Algoritms:").grid(row=3, column=0, sticky="w", pady=(10, 0))
        ttk.Radiobutton(controls, text="Minimax", variable=self.algorithm, value="minimax").grid(row=4, column=0, sticky="w")
        ttk.Radiobutton(controls, text="Alpha–Beta", variable=self.algorithm, value="alphabeta").grid(row=5, column=0, sticky="w")

        ttk.Label(controls, text="Dziļuma limits (n):").grid(row=6, column=0, sticky="w", pady=(10, 0))
        ttk.Spinbox(controls, from_=1, to=30, textvariable=self.depth_limit, width=6).grid(row=7, column=0, sticky="w")

        btns = ttk.Frame(controls)
        btns.grid(row=8, column=0, sticky="w", pady=(12, 0))
        ttk.Button(btns, text="Jauni skaitļi", command=self._regen_numbers).pack(side=tk.LEFT)
        ttk.Button(btns, text="Sākt", command=self._start_game).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(btns, text="Eksperimenti (10+10)", command=self._run_experiments_ui).pack(side=tk.LEFT, padx=(8, 0))

        mid = ttk.Frame(self, padding=10)
        mid.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        left = ttk.LabelFrame(mid, text="Spēles stāvoklis", padding=10)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.lbl_n = ttk.Label(left, text="n = -", font=("Segoe UI", 18))
        self.lbl_n.pack(anchor="w")

        self.lbl_scores = ttk.Label(left, text="Cilvēks: 0 | Dators: 0", font=("Segoe UI", 12))
        self.lbl_scores.pack(anchor="w", pady=(8, 0))

        self.lbl_turn = ttk.Label(left, text="Gājiens: -", font=("Segoe UI", 12))
        self.lbl_turn.pack(anchor="w", pady=(8, 0))

        move_frame = ttk.Frame(left)
        move_frame.pack(anchor="w", pady=(16, 0))

        self.btn_div2 = ttk.Button(move_frame, text="Dalīt ar 2", command=lambda: self._human_move(2))
        self.btn_div3 = ttk.Button(move_frame, text="Dalīt ar 3", command=lambda: self._human_move(3))
        self.btn_div2.pack(side=tk.LEFT)
        self.btn_div3.pack(side=tk.LEFT, padx=(10, 0))

        right = ttk.LabelFrame(mid, text="AI informācija", padding=10)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        self.txt_ai = tk.Text(right, height=14, wrap="word")
        self.txt_ai.pack(fill=tk.BOTH, expand=True)

        bottom = ttk.Frame(self, padding=10)
        bottom.pack(side=tk.BOTTOM, fill=tk.X)

        self.lbl_status = ttk.Label(bottom, text="", foreground="#444")
        self.lbl_status.pack(side=tk.LEFT)

    def _refresh_start_numbers_ui(self):
        for w in self.numbers_frame.winfo_children():
            w.destroy()
        for x in self.start_numbers:
            ttk.Radiobutton(self.numbers_frame, text=str(x), variable=self.selected_start, value=x).pack(side=tk.LEFT, padx=6)

    def _regen_numbers(self):
        self.start_numbers = generate_start_numbers()
        self.selected_start.set(self.start_numbers[0])
        self._refresh_start_numbers_ui()
        self._set_status("Saģenerēti jauni sākuma skaitļi.")

    def _start_game(self):
        n0 = int(self.selected_start.get())
        starter = HUMAN if self.first_player.get() == "human" else AI
        self.state = GameState(n0, 0, 0, starter)

        self.last_tree_root = None
        self.last_stats = None

        self._update_ui_from_state()
        self._log_ai("Jauna spēle sākta.\n")

        if self.state.player_to_move == AI:
            self.after(100, self._ai_move)
    # aptjauno speles logu ar speles aktualajiem rezultatiem, kur tiek paradi rezultati, gajiena informacija aun vai gajiens ir atluts
    def _update_ui_from_state(self):
        # parbaude vai ir stavoklis, ja nav, neizpilda funkciju
        if not self.state:
            return
        # atjauno informaciju par skaitli, punktiem, gajiena informaciju un atlautu gajienu pogam
        self.lbl_n.config(text="n = " + str(self.state.n))
        self.lbl_scores.config(text="Cilvēks: {} | Dators: {}".format(self.state.score_human, self.state.score_ai))
        # gajiena informacija tiek atjaunota, ja ir cilveka gajiens, tad parada cilveks un preteji
        who = "Cilvēks" if self.state.player_to_move == HUMAN else "Dators"
        self.lbl_turn.config(text="Gājiens: " + who)
        # vai ir gājiens, kas ir atļauts
        legal = set([mv.divisor for mv in self.state.legal_moves()])
        # ja ir atļauts dalīt ar 2 un ir cilveka gajiens un spele nav beigusies, tad dala ar 2 poga tiek aktivizeta
        if (2 in legal) and (self.state.player_to_move == HUMAN) and (not self.state.is_terminal()):
            self.btn_div2.config(state="normal")
        else:
            self.btn_div2.config(state="disabled")
        # ja ir atļauts dalīt ar 3 un ir cilveka gajiens un spele nav beigusies, tad dala ar 3 poga tiek aktivizeta
        if (3 in legal) and (self.state.player_to_move == HUMAN) and (not self.state.is_terminal()):
            self.btn_div3.config(state="normal")
        else:
            self.btn_div3.config(state="disabled")
        # ja spele ir beigusies, abas gajienu pogas tiek atslēgtas un tiek paraditi rezultati
        if self.state.is_terminal():
            self.btn_div2.config(state="disabled")
            self.btn_div3.config(state="disabled")
            self._announce_result()
        # ja spele nav beigusies, tiek paradits cik gajienu ir atlicis
        if not self.state:
            return
        
        w = self.state.winner()
        reason = self.state.terminal_reason()
        # ja spele ir beigusies, tiek paradits iemesls, uzvarētājs un rezultati
        if reason == "number_reached":
            prefix = "Game over: reached number {} (<= 10).".format(self.state.n)
        else:
            prefix = "Game over: no legal moves remain at {}.".format(self.state.n)
        # ja ir neizšķirts, tiek paradits neizšķirts, ja uzvar cilveks, tiek paradits cilveks uzvar, ja uzvar dators, tiek paradits dators uzvar
        if w is None:
            msg = "{}\nDraw.\nScore: {}:{}".format(prefix, self.state.score_human, self.state.score_ai)
        elif w == HUMAN:
            msg = "{}\nHuman wins.\nScore: {}:{}".format(prefix, self.state.score_human, self.state.score_ai)
        else:
            msg = "{}\nComputer wins.\nScore: {}:{}".format(prefix, self.state.score_human, self.state.score_ai)
        # rezultati tiek paraditi status loga un ar popup logu
        self._set_status(msg)
        messagebox.showinfo("Result", msg)
    # funkcija tiek definets cilveka gajieni, kur ir skatits speles stavoklis ir gajieni/beigusies un vai gajiens ir atlauts 
    def _human_move(self, divisor):
        # parbaude vai ir stavoklis, ja nav, neizpilda funkciju
        if not self.state:
            return
        # parbauda vai ir AI karta
        if self.state.player_to_move != HUMAN:
            self._set_status("It is currently the computer's turn.")
            return
        # parbvauda vai spele ir beigusies
        if self.state.is_terminal():
            self._announce_result()
            return
        # parbauda vai gajiens ir atlauts, ja nav, paradit brīdinājumu un nelauj izpildit gājienu
        if self.state.n % divisor != 0:
            self._set_status("Illegal move: {} is not divisible by {}.".format(self.state.n, divisor))
            messagebox.showwarning("Illegal move", "{} is not divisible by {}.".format(self.state.n, divisor))
            return
        # ja gajiens ir atlauts, tad tiek izpildits gajiens, atjaunots UI un ja spele nav beigusies un ir AI karta, tad tiek izsaukta AI gajiena funkcija
        self.state = self.state.apply(Move(divisor))
        self._update_ui_from_state()
        # ja spele nav beigusies un ir AI karta, tad tiek izsaukta AI gajiena funkcija ar sekundes aizkavi, lai redzētu gājienu izpildi
        if self.state and (not self.state.is_terminal()) and self.state.player_to_move == AI:
            self.after(1000, self._ai_move)
    # ja vairs nav gajienu, spele tiek partraukta un tiek paraditi rezultati
    def _skip_turn_if_no_moves(self):
        if not self.state or self.state.is_terminal():
            return
        # ja nav gajienu, tiek partraukta spele un tiek paraditi rezultati
        if not self.state.can_move():
            self._set_status("No legal moves remain at {}.".format(self.state.n))
            self._update_ui_from_state()
            
    # funkcija AI gajieniem, skatos pec kura algoritma ir izveleta spele, kur ari tas tiek loggots, lai redzetu AI gajienus
    def _ai_move(self):
        if (not self.state) or (self.state.player_to_move != AI) or self.state.is_terminal():
            return
        # ja nav gajienu, tiek partraukta spele un tiek paraditi rezultati
        if not self.state.can_move():
            self._log_ai("AI cannot move at {}: no legal moves remain.\n".format(self.state.n))
            self._skip_turn_if_no_moves()
            return
        # skatas pēc izveleta algoritma un dziluma limita, izsauc attiecīgo funkciju, lai AI izveletos gajienu, un izmera cik ilgi tas aiznem
        algo = self.algorithm.get()
        depth = int(self.depth_limit.get())
        # AI gajiena izvele un laika merisana
        t0 = time.perf_counter()
        if algo == "minimax":
            mv, root, stats = minimax_decision(self.state, depth)
        else:
            mv, root, stats = alphabeta_decision(self.state, depth)
        dt = time.perf_counter() - t0
        # saglaba meklesanas koku un statistiku
        self.last_tree_root = root
        self.last_stats = stats
        # AI darbibu log
        self._log_ai(
            "AI gājiens: dalīt ar {}\n"
            "Algoritms: {}, dziļums: {}\n"
            "Laiks: {:.4f}s\n"
            "Ģenerētās virsotnes: {}\n"
            "Novērtētās virsotnes: {}\n"
            "Saknes vērtība: {}\n"
            "{}\n".format(
                mv.divisor, algo, depth, dt,
                stats.generated_nodes, stats.evaluated_nodes,
                root.value, "-" * 40
            )
        )

        self.state = self.state.apply(mv)
        self._update_ui_from_state()
    # _ai_move paligfunkcija darbibu loggosanai
    def _log_ai(self, text):
        self.txt_ai.insert("end", text)
        self.txt_ai.see("end")
    # funkcija tiek definets rezultatu loga paradisanai, kur tiek paradi rezultati un uzvaretajs
    def _set_status(self, text):
        self.lbl_status.config(text=text)
    # 10 eksperimentus veiksanas funkcija, kas tiek izvadita spele UI un parada eksperimentu rezultatus
    def _run_experiments_ui(self):
        depth = int(self.depth_limit.get())
        results = run_experiments(depth_limit=depth, games_per_algo=10)
        # eksperimantu rezultatu apkopojums, kur tiek saskaitits uzvaras, zaudes, neizšķirti un AI gajienu laiki katram algoritmam
        summary = {
            "minimax": {"ai": 0, "human": 0, "draw": 0, "t": 0.0, "k": 0},
            "alphabeta": {"ai": 0, "human": 0, "draw": 0, "t": 0.0, "k": 0},
        }
        # reultatu apstrade, kur tiek saskaitits uzvaras, zaudejum, neizskirti un AI gajienu laiks
        for r in results:
            s = summary[r["algo"]]
            s[r["winner"]] += 1
            s["t"] += r["ai_move_time_avg"]
            s["k"] += 1
        # eksperimentu rezultatu izvade uz UI
        msg = (
            "Eksperimenti pabeigti (dziļums {}).\n\n"
            "Minimax: AI uzvaras={}, Cilvēks={}, Neizšķirti={}, AI vid. gājiena laiks={:.4f}s\n"
            "Alpha–Beta: AI uzvaras={}, Cilvēks={}, Neizšķirti={}, AI vid. gājiena laiks={:.4f}s\n\n"
            "(Cilvēks eksperimentos ir simulēts ar random legālu gājienu.)"
        ).format(
            depth,
            summary["minimax"]["ai"], summary["minimax"]["human"], summary["minimax"]["draw"],
            (summary["minimax"]["t"] / summary["minimax"]["k"]) if summary["minimax"]["k"] else 0.0,
            summary["alphabeta"]["ai"], summary["alphabeta"]["human"], summary["alphabeta"]["draw"],
            (summary["alphabeta"]["t"] / summary["alphabeta"]["k"]) if summary["alphabeta"]["k"] else 0.0
        )
        # eksperimentu log izveide
        self._log_ai("\n" + msg + "\n" + "=" * 40 + "\n")
        messagebox.showinfo("Eksperimentu kopsavilkums", msg)

# main funkcuija, kas palaiz speles logu
def main():
    app = GameApp()
    app.mainloop()


if __name__ == "__main__":
    main()
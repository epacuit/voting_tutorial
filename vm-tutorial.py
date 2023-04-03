import streamlit as st
import streamlit.components.v1 as components
import string
from  display_profile import *
from itertools import combinations
import pandas as pd
import numpy as np


from pref_voting.profiles import Profile
from pref_voting.generate_profiles import *
from pref_voting.voting_methods import *

def margin_str(prof, c1, c2, cmap): 
    return f"$Margin({cmap[c1]}, {cmap[c2]}) = {prof.margin(c1, c2)}$"

def cand_list_str(cs, cmap): 
    return f"{', '.join([cmap[c] for c in cs])}"

def same_candidate_sets(cs, cnames, cmap): 
    return all([cmap[c] in cnames for c in cs]) and all([cname in [cmap[_c] for _c in cs] for cname in cnames])

condorcet_cycle = Profile([
    (0, 1, 2),
    (1, 2, 0),
    (2, 0, 1)
])

condorcet_cycle_with_winner = Profile([
    (3, 0, 1, 2),
    (3, 1, 2, 0),
    (3, 2, 0, 1)
])

condorcet_cycle_with_loser = Profile([
    (0, 1, 2, 3),
    (1, 2, 0, 3),
    (2, 0, 1, 3)
])

illustrative_ex1 = Profile([
    (0,1,2,3),
    (0,2,1,3), 
    (1,3,2,0), 
    (2,1,3,0)
], 
rcounts=[3, 5, 7, 6])

illustrative_ex2 = Profile([
    (0, 1, 2, 3),
    (1, 2, 3, 0),
    (3, 1, 2, 0),
    (2, 3, 0, 1)
], 
rcounts=[7, 5, 4, 3])

illustrative_ex3 = Profile([
    (2, 1, 3, 0),
    (0, 2, 3, 1), 
    (1, 0, 2, 3), 
    (1, 0, 3, 2), 
    (3, 0, 2, 1)
], 
rcounts=[1, 1, 1, 1, 1])


fixed_profiles = {
    "Condorcet Cycle": condorcet_cycle,
    "Condorcet Cycle with Winner":condorcet_cycle_with_winner,
    "Condorcet Cycle with Loser": condorcet_cycle_with_loser,
    "Illustrative Example 1": illustrative_ex1,
    "Illustrative Example 2": illustrative_ex2,
    "Illustrative Example 3": illustrative_ex3
    }

def generate_mg_dot(profile, cmap):
    candidates = profile.candidates
    nodes = [cmap[_c] for _c in candidates]
    edges = [(cmap[c1], cmap[c2], prof.margin(c1, c2))  
           for c1 in candidates 
           for c2 in candidates if c1 != c2 if profile.majority_prefers(c1, c2)]
    node_strings ="\n".join([f'{n}[ label = "{n}" ];' for n in nodes])
    edge_strings = "\n".join([f'{e[0]} -> {e[1]}[label="{e[2]}",weight="{e[2]}"];' for e in edges])
    dot = '''digraph { \n layout="circo";\n''' + node_strings + "\n" + edge_strings + "}"
    return dot
   
def generate_cycle_dot(cycle, profile, cmap):
    candidates = cycle
    nodes = [cmap[_c] for _c in candidates]
    edges = list()
    for cidx, c1 in enumerate(cycle[0:-1]): 
        edges.append((cmap[c1], cmap[cycle[cidx+1]], profile.margin(c1, cycle[cidx+1])))
    edges.append((cmap[cycle[-1]], cmap[cycle[0]], profile.margin(cycle[-1], cycle[0])))
    node_strings ="\n".join([f'{n}[ label = "{n}" ];' for n in nodes])
    edge_strings = "\n".join([f'{e[0]} -> {e[1]}[label="{e[2]}",weight="{e[2]}"];' for e in edges])
    dot = '''digraph { \n layout="circo";\n''' + node_strings + "\n" + edge_strings + "}"
    return dot

def generate_sc_defeat_dot(sc_defeat, cmap):
    candidates = sc_defeat.nodes
    nodes = [cmap[_c] for _c in candidates]
    edges = [(cmap[e[0]], cmap[e[1]]) for e in sc_defeat.edges]

    node_strings ="\n".join([f'{n}[ label = "{n}" ];' for n in nodes])
    edge_strings = "\n".join([f'{e[0]} -> {e[1]};' for e in edges])
    dot = '''digraph { \n layout="circo";\n''' + node_strings + "\n" + edge_strings + "}"
    return dot

@st.cache_data
def gen_profile(num_cands, num_voters, fixed_profile=None):
    print(fixed_profile)
    if fixed_profile not in fixed_profiles.keys(): 
        return generate_profile(num_cands, num_voters)
    else: 
        return fixed_profiles[fixed_profile]

st.title("Voting Methods Tutorial")

with st.sidebar.form("generate_profile"):
   num_cands = st.slider("Number of candidates", min_value=2, max_value=7, value=3)
   num_voters = st.slider("Number of Voters", min_value=1, max_value=15, value=5)
   
   fixed_profile_str = st.selectbox(
    'Choose a profile',
    tuple([""] + list(fixed_profiles.keys())))
   
   submitted = st.form_submit_button("Generate Profile")
   if submitted:
       if fixed_profile_str == "":
           st.cache_data.clear()
       else:
           num_cands = len(fixed_profiles[fixed_profile_str].candidates)
           num_voters = fixed_profiles[fixed_profile_str].num_voters

st.sidebar.write("Tutorial created by [Eric Pacuit](https://pacuit.org) for the course [PHPE 400](https://phpe400.info): Individual and Group Decision Making")

print("regenerating....")
prof = gen_profile(num_cands, num_voters, fixed_profile=fixed_profile_str)
num_cands, num_voters = len(prof.candidates), prof.num_voters
c1, c2 = None, None
print("prof is ", prof)
#prof.display()
_rs, _cs = prof.rankings_counts

rs = [tuple([int(c) for c in r]) for r in _rs]
cs = [int(nc) for nc in _cs]
cmap =  {c: string.ascii_letters[c] for c in prof.candidates}

col1, col2 = st.columns(2)

with col2: 
    tab1, tab2 = st.tabs(["Margin Graph", "Margin Calculations"])

    with tab1:
        dot=generate_mg_dot(prof, cmap)
        st.graphviz_chart(dot)

    with tab2:
        """The **margin** of a canidate $x$ over a candidate $y$, denoted $Margin(x, y)$, is the number of voters that rank $x$ above $y$ minus the number of voters that rank $y$ above $x$."""
        """Candidate $x$ is  **majority preferred** to $y$ when $Margin(x, y)>0$."""
        print( [(None, None)] + list(combinations(prof.candidates, 2)))
        cands_for_margins = st.selectbox(
            'Which candidates to compare head-to-head?',
            [(None, None)] + list(combinations(prof.candidates, 2)), format_func = lambda cs : f"{cmap[cs[0]]} vs. {cmap[cs[1]]}" if (cs[0] is not None and cs[1] is not None) else "Select two candidates.")
        c1, c2 = cands_for_margins
        if c1 is not None and c2 is not None and prof.majority_prefers(c1, c2):  
            st.markdown(f"${cmap[c1]}$ is majority preferred to ${cmap[c2]}$.") 
            st.markdown(f"$Margin({cmap[c1]}, {cmap[c2]}) = {prof.support(c1, c2)} - {prof.support(c2, c1)} = {prof.margin(c1, c2)}$")
            st.markdown(f"$Margin({cmap[c2]}, {cmap[c1]}) = {prof.support(c2, c1)} - {prof.support(c1, c2)} = {prof.margin(c2, c1)}$")
        elif c1 is not None and c2 is not None and prof.majority_prefers(c2, c1): 
            st.markdown(f"${cmap[c2]}$ is majority preferred to ${cmap[c1]}$.") 
            st.markdown(f"$Margin({cmap[c2]}, {cmap[c1]}) = {prof.support(c2, c1)} - {prof.support(c1, c2)} = {prof.margin(c2, c1)}$")
            st.markdown(f"$Margin({cmap[c1]}, {cmap[c2]}) = {prof.support(c1, c2)} - {prof.support(c2, c1)} = {prof.margin(c1, c2)}$")
        elif c1 is not None and c2 is not None: 
            st.markdown(f"The margin between ${cmap[c1]}$ and ${cmap[c2]}$ is 0. So, ${cmap[c1]}$ is not majority preferred to ${cmap[c2]}$ and ${cmap[c2]}$ is not majority preferred to ${cmap[c1]}$.") 
            st.markdown(f"$Margin({cmap[c2]}, {cmap[c1]}) = {prof.support(c2, c1)} - {prof.support(c1, c2)} = {prof.margin(c2, c1)}$")
            st.markdown(f"$Margin({cmap[c1]}, {cmap[c2]}) = {prof.support(c1, c2)} - {prof.support(c2, c1)} = {prof.margin(c1, c2)}$")

with col1:
    display_profile(rs, cs, int(num_cands), [cmap[c] for c in prof.candidates], c1=c1, c2=c2, key="p1")
    #should_gen_profile = st.button(f"Generate another profile with {num_cands} candidates and {num_voters} voters")


condorcet_winner = prof.condorcet_winner()
condorcet_loser = prof.condorcet_loser()
majority_winner = majority(prof)
cycles = prof.cycles()

if len(majority_winner) == 1: 
    st.write(f"The majority winner is {cmap[majority_winner[0]]}.")
else: 
    st.write(f"There is no majority winner.")
with st.expander("See explanation"):
    st.write(f"""
        The **majority winner** is the candidate with a strict majority of first-place votes.

        There are {prof.num_voters} voters in the election.  A candidate  is a majority winner if at least {prof.strict_maj_size()} voters rank that candidate in first place.""") 
    if len(majority_winner) == 1:
        st.write(f"The number of voters that rank {cmap[majority_winner[0]]} in first place is {prof.plurality_scores()[majority_winner[0]]}.")
    else: 
        st.write(f"No candidate is ranked in first place by at least {prof.strict_maj_size()} voters.")

if condorcet_winner is not None: 
    st.write(f"The Condorcet winner is {cmap[condorcet_winner]}.")
else: 
    st.write(f"There is no Condorcet winner.")
with st.expander("See explanation"):
    st.write("""
        The **Condorcet winner** is the candidate that is majority preferred to every other candidate.
    """)

    if condorcet_winner is None: 
        for cand1 in prof.candidates: 
            st.write(f"${cmap[cand1]}$ is not the Condorcet winner:")
            for cand2 in prof.candidates: 
                if cand1 != cand2: 
                    if not prof.majority_prefers(cand1, cand2): 
                        st.write(f"* Since $Margin({cmap[cand1]}, {cmap[cand2]}) = {prof.margin(cand1, cand2)}$, ${cmap[cand1]}$ is not majority preferred to ${cmap[cand2]}$")
    else: 
        for cand1 in prof.candidates: 
            if condorcet_winner != cand1: 
                st.write(f"* Since $Margin({cmap[condorcet_winner]}, {cmap[cand1]}) = {prof.margin(condorcet_winner, cand1)}$, ${cmap[condorcet_winner]}$ is  majority preferred to ${cmap[cand1]}$")

if condorcet_loser is not None: 
    st.write(f"The Condorcet loser is {cmap[condorcet_loser]}.")
else: 
    st.write(f"There is no Condorcet loser.")
with st.expander("See explanation"):
    st.write("""
        The **Condorcet loser** is the candidate such that every other candidate is majority preferred to that candidate.
    """)

    if condorcet_loser is None: 
        for cand1 in prof.candidates: 
            st.write(f"${cmap[cand1]}$ is not the Condorcet loser:")
            for cand2 in prof.candidates: 
                if cand1 != cand2: 
                    if not prof.majority_prefers(cand2, cand1): 
                        st.write(f"* Since $Margin({cmap[cand2]}, {cmap[cand1]}) = {prof.margin(cand2, cand1)}$, ${cmap[cand2]}$ is not majority preferred to ${cmap[cand1]}$")
    else: 
        for cand1 in prof.candidates: 
            if condorcet_loser != cand1: 
                st.write(f"* Since $Margin({cmap[cand1]}, {cmap[condorcet_loser]}) = {prof.margin(cand1, condorcet_loser)}$, ${cmap[cand1]}$ is  majority preferred to ${cmap[condorcet_loser]}$")

if len(cycles) == 0:
    st.write(f"There are no majority cycles in the profile.")
else: 
    if len(cycles) == 1: 
        st.write(f"There is {len(cycles)} majority cycle in the profile.")
    else: 
        st.write(f"There are {len(cycles)} majority cycles in the profile.")
with st.expander("See explanation"):
    st.write("A **majority cycle** (also called a **Condorcet cycle**) is a list of candidates $x_1, x_2, \ldots, x_k$ such that $x_1$ is majority preferred to $x_2$, $x_2$ is majority preferred to $x_3$, $\ldots$, $x_{k-1}$ is majority preferred to $x_k$, and $x_k$ is majority preferred to $x_1$.")

    if len(cycles) > 0: 
        for cycle in cycles: 
            st.write(f"${', '.join([cmap[c] for c in cycle])}$ is a cycle: ")
            for cidx, c in enumerate(cycle[0:-1]): 
                st.write(f"* Since $Margin({cmap[c]}, {cmap[cycle[cidx+1]]}) = {prof.margin(c, cycle[cidx+1])}$, ${cmap[c]}$ is majority preferred to ${cmap[cycle[cidx+1]]}$")
            st.write(f"* Since $Margin({cmap[cycle[-1]]}, {cmap[cycle[0]]}) = {prof.margin(cycle[-1], cycle[0])}$, ${cmap[cycle[-1]]}$ is majority preferred to ${cmap[cycle[0]]}$")

st.subheader("Voting Methods")

display_profile(rs, cs, int(num_cands), [cmap[c] for c in prof.candidates], c1=None, c2=None, key="p2")

pl_tab, borda_tab, pl_w_roff_tab, irv_tab, coombs_tab, minimax_tab, copeland_tab, sc_tab= st.tabs(["Plurality", "Borda", "Plurality with Runoff", "Instant Runoff", "Coombs", "Minimax", "Copeland", "Split Cycle"])

with pl_tab: 
    vm_string = "Plurality"
    pl_ws = plurality(prof)
    pl_submitted_winning_set = st.multiselect(
        f'Which candidates are the {vm_string} winners?',
        [cmap[c] for c in prof.candidates],
        [])
    if st.button(f"Check {vm_string} winners"):
        if len(pl_submitted_winning_set) > 0: 
            if same_candidate_sets(pl_ws, pl_submitted_winning_set, cmap):
                st.success(f"Correct, the {vm_string} winning set is: {', '.join(pl_submitted_winning_set)}.")
            else: 
                for cname in pl_submitted_winning_set: 
                    if not cname in [cmap[_c] for _c in pl_ws]: 
                        st.error(f"${cname}$ is not a {vm_string} winner.")
                for w in pl_ws: 
                    if cmap[w] not in pl_submitted_winning_set:
                        st.error(f"${cmap[w]}$ is a {vm_string}  winner.")
            st.write()
        else: 
            st.write("You must select some candidates.")
        with st.expander(f"Explain the {vm_string} winners"):
            st.write("The **Plurality score** for a candidate is that rank that candidate in first place.   The candidate(s) with the largest Plurality score is a Plurality winner.")
            plscores = prof.plurality_scores()
            st.write(f"The largest Plurality score is {max(plscores.values())}")
            for c in prof.candidates: 
                st.write(f"* The Plurality score of ${cmap[c]}$ is ${plscores[c]}$ " + ("(winner)" if c in pl_ws else ""))


with borda_tab: 
    borda_ws = borda(prof)
    b_submitted_winning_set = st.multiselect(
        'Which candidates are the Borda winners?',
        [cmap[c] for c in prof.candidates],
        [])
    if st.button("Check Borda winners"):
        if len(b_submitted_winning_set) > 0: 
            if same_candidate_sets(borda_ws, b_submitted_winning_set, cmap):
                st.success(f"Correct, the Borda winning set is: {', '.join(b_submitted_winning_set)}.")
            else: 
                for cname in b_submitted_winning_set: 
                    if not cname in [cmap[_c] for _c in borda_ws]: 
                        st.error(f"${cname}$ is not a Borda winner.")
                for w in borda_ws: 
                    if cmap[w] not in b_submitted_winning_set:
                        st.error(f"${cmap[w]}$ is a Borda winner.")
            st.write()
        else: 
            st.write("You must select some candidates.")

        scores = list(range(len(prof.candidates)-1, -1, -1))
        bscores = prof.borda_scores()
        with st.expander("Explain the Borda winners"):
            st.write("The **Borda score** for a candidate is determined as follows:  Each voter gives 3 points to the candidate ranked in first palce, 2 points to the candidate ranked in 2nd place, $\\ldots$, 0 points to the candidate ranked in last place.  The candidates overall Borda score is the sum of the Borda scores assigned from each voter.   The candidate(s) with the largest Borda score is a Borda winner.")

            st.write(f"The largest Borda score is {max(bscores.values())}")
            for c in prof.candidates: 
                num_ranks = [prof.num_rank(c, l) for l in range(1, len(prof.candidates) + 1)]
                bscore_str = ' + '.join([f"{str(x)} * {str(y)} " for x, y in zip(scores, num_ranks)])
                st.write(f"* The Borda score of ${cmap[c]}$ is ${bscore_str} = {bscores[c]}$ " + ("(winner)" if c in borda_ws else ""))

with pl_w_roff_tab: 
    vm_string = "Plurality with Runoff"
    pl_w_runoff_ws = plurality_with_runoff(prof)
    pl_runoff_submitted_winning_set = st.multiselect(
        f'Which candidates are the {vm_string} winners?',
        [cmap[c] for c in prof.candidates],
        [])
    if st.button(f"Check {vm_string} winners"):
        if len(pl_runoff_submitted_winning_set) > 0: 
            if same_candidate_sets(pl_ws, pl_submitted_winning_set, cmap):
                st.success(f"Correct, the {vm_string} winning set is: {', '.join(pl_runoff_submitted_winning_set)}.")
            else: 
                for cname in pl_runoff_submitted_winning_set: 
                    if not cname in [cmap[_c] for _c in pl_ws]: 
                        st.error(f"${cname}$ is not a {vm_string} winner.")
                for w in pl_ws: 
                    if cmap[w] not in pl_runoff_submitted_winning_set:
                        st.error(f"${cmap[w]}$ is a {vm_string}  winner.")
            st.write()
        else: 
            st.write("You must select some candidates.")
        with st.expander(f"Explain the {vm_string} winners"):
            st.write("The **Plurality with Runoff** winners are determined as follows.  If there is a majority winner then that candidate is the Plurality with Runoff winner. If there is no majority winner, then hold a runoff with  the top two candidates: either two (or more candidates) with the most first place votes or the candidate with the most first place votes and the candidate with the 2nd highest first place votes are ranked first by the fewest number of voters.   A candidate is a Plurality with Runoff winner if it is a winner in a runoff between two pairs of first- or second- ranked candidates. If the candidates are all tied for the most first place votes, then all candidates are winners.")


            maj_winner = majority(prof)
            
            if len(maj_winner) == 1:
                st.write(f"${cmap[maj_winner[0]]}$ is a majority winner.")
            else:
                pl_runoff_ws, plr_exp = plurality_with_runoff_with_explanation(prof)
                st.write(f"The Plurality with Runoff winners: {cand_list_str(pl_runoff_ws, cmap)}.")

                runoffs = list()
                for c1, c2 in plr_exp: 
                    if all([not (runoff[0] == c1 and runoff[1] == c2) and not (runoff[1] == c1 and runoff[0] == c2) for runoff in runoffs]):
                        runoffs.append((c1, c2))
                        if prof.majority_prefers(c1, c2): 
                            st.write(f"* In the runoff between {cmap[c1]} and {cmap[c2]}, the winner is {cmap[c1]} by a margin of {prof.margin(c1, c2)}.")
                        elif prof.majority_prefers(c2, c1): 
                            st.write(f"* In the runoff between {cmap[c1]} and {cmap[c2]}, the winner is {cmap[c2]} by a margin of {prof.margin(c2, c1)}.")
                        else: 
                            st.write(f"* In the runoff between {cmap[c1]} and {cmap[c2]},  {cmap[c1]} and {cmap[c2]} are tied.")
                        

with irv_tab: 
    vm_string = "Instant Runoff Voting"
    irv_ws = instant_runoff(prof)
    irv_submitted_winning_set = st.multiselect(
        f'Which candidates are the {vm_string} winners?',
        [cmap[c] for c in prof.candidates],
        [])
    if st.button(f"Check {vm_string} winners"):
        if len(irv_submitted_winning_set) > 0: 
            if same_candidate_sets(irv_ws, irv_submitted_winning_set, cmap):
                st.success(f"Correct, the {vm_string} winning set is: {', '.join(irv_submitted_winning_set)}.")
            else: 
                for cname in irv_submitted_winning_set: 
                    if not cname in [cmap[_c] for _c in irv_ws]: 
                        st.error(f"${cname}$ is not a {vm_string} winner.")
                for w in irv_ws: 
                    if cmap[w] not in irv_submitted_winning_set:
                        st.error(f"${cmap[w]}$ is a {vm_string}  winner.")
            st.write()
        else: 
            st.write("You must select some candidates.")
        with st.expander(f"Explain the {vm_string} winners"):
            st.write("""The **Instant Runoff Voting** (also known as Ranked Choice Voting) winners are determined as follows.  If there is a candidate that is the majority winner, then that candidate is the Instant Runoff Voting winner.  Otherwise, iteratively remove all candidates with the fewest number of voters who rank them first, until there is a candidate who is a majority  winner.  Then that candidate is the Instant Runoff Voting winner.  If, at some stage of the removal process, all remaining candidates have the same number of  voters who rank them first (so all candidates would be removed), then all remaining candidates  are selected as Instant Runoff Voting winners.""")

            st.write(f"The Instant Runoff Voting winners: {', '.join([cmap[w] for w in irv_ws])}.")
            maj_winner = majority(prof)
            
            if len(maj_winner) == 1:
                st.write(f"${cmap[maj_winner[0]]}$ is a majority winner.")

            _, irv_exp = instant_runoff_with_explanation(prof)
            all_cands_to_remove = list()
            for r, cands_removed in enumerate(irv_exp):
                all_cands_to_remove += cands_removed
                reduced_prof, reduced_prof_cmap = prof.remove_candidates(all_cands_to_remove)
                reduced_prof.display()

                _rs_reduced, _cs_reduced = reduced_prof.rankings_counts
                reduced_rs = [tuple([int(c) for c in _r]) for _r in _rs_reduced]
                reduced_cs = [int(nc) for nc in _cs_reduced]
                updated_cmap = {_c: cmap[reduced_prof_cmap[_c]] for _c in reduced_prof.candidates}
                st.write(f"""*Round {r+1}*: The candidates with the fewest number of first place votes:  {', '.join([cmap[_c] for _c in cands_removed])}.  The profile with these candidates removed: 
                """) 

                display_profile(reduced_rs, reduced_cs, int(len(reduced_prof.candidates)), [updated_cmap[c] for c in reduced_prof.candidates], c1=None, c2=None, key=f"irv_p_{r}")

                reduced_maj_winner = majority(reduced_prof)
                if len(reduced_maj_winner) == 1: 
                    st.write(f"{updated_cmap[reduced_maj_winner[0]]} is the majority winner in the reduced profile.")
                else: 
                    st.write(f"There is no candidate that is ranked in first place by a majority of voters in the reduced profile.")
                st.write("")

with coombs_tab: 
    vm_string = "Coombs"
    coombs_ws = coombs(prof)
    coombs_submitted_winning_set = st.multiselect(
        f'Which candidates are the {vm_string} winners?',
        [cmap[c] for c in prof.candidates],
        [])
    if st.button(f"Check {vm_string} winners"):
        if len(coombs_submitted_winning_set) > 0: 
            if same_candidate_sets(coombs_ws, coombs_submitted_winning_set, cmap):
                st.success(f"Correct, the {vm_string} winning set is: {', '.join(coombs_submitted_winning_set)}.")
            else: 
                for cname in coombs_submitted_winning_set: 
                    if not cname in [cmap[_c] for _c in coombs_ws]: 
                        st.error(f"${cname}$ is not a {vm_string} winner.")
                for w in coombs_ws: 
                    if cmap[w] not in coombs_submitted_winning_set:
                        st.error(f"${cmap[w]}$ is a {vm_string}  winner.")
            st.write()
        else: 
            st.write("You must select some candidates.")
        with st.expander(f"Explain the {vm_string} winners"):
            st.write("""The **Coombs** winners are determined as follows.  If there is a candidate that is the majority winner, then that candidate is the Coombs winner.  Otherwise, iteratively remove all candidates with the largest number of voters who rank them last, until there is a candidate who is a majority  winner.  Then that candidate is the Coombs winner.  If, at some stage of the removal process, all remaining candidates have the same number of  voters who rank them first (so all candidates would be removed), then all remaining candidates  are selected as Coombs winners.""")

            st.write(f"The Coombs winners: {', '.join([cmap[w] for w in coombs_ws])}.")
            maj_winner = majority(prof)

            if len(maj_winner) == 1:
                st.write(f"${cmap[maj_winner[0]]}$ is a majority winner.")
                
            _, coombs_exp = coombs_with_explanation(prof)
            all_cands_to_remove = list()
            for r, cands_removed in enumerate(coombs_exp):
                all_cands_to_remove += cands_removed
                reduced_prof, reduced_prof_cmap = prof.remove_candidates(all_cands_to_remove)
                reduced_prof.display()

                _rs_reduced, _cs_reduced = reduced_prof.rankings_counts
                reduced_rs = [tuple([int(c) for c in _r]) for _r in _rs_reduced]
                reduced_cs = [int(nc) for nc in _cs_reduced]
                updated_cmap = {_c: cmap[reduced_prof_cmap[_c]] for _c in reduced_prof.candidates}
                st.write(f"""* Round {r+1}: The candidates with the largest number of last place votes:  {', '.join([cmap[_c] for _c in cands_removed])}.  The profile with these candidates removed: 
                """) 

                display_profile(reduced_rs, reduced_cs, int(len(reduced_prof.candidates)), [updated_cmap[c] for c in reduced_prof.candidates], c1=None, c2=None, key=f"coombs_p_{r}")

                reduced_maj_winner = majority(reduced_prof)
                if len(reduced_maj_winner) == 1: 
                    st.write(f"{updated_cmap[reduced_maj_winner[0]]} is the majority winner in the reduced profile.")
                else: 
                    st.write(f"There is no candidate that is ranked in first place by a majority of voters in the reduced profile.")
                st.write("")

with minimax_tab: 
    vm_string = "Minimax"
    minimax_ws = minimax(prof)
    minimax_submitted_winning_set = st.multiselect(
        f'Which candidates are the {vm_string} winners?',
        [cmap[c] for c in prof.candidates],
        [])
    if st.button(f"Check {vm_string} winners"):
        if len(minimax_submitted_winning_set) > 0: 
            if same_candidate_sets(minimax_ws, minimax_submitted_winning_set, cmap):
                st.success(f"Correct, the {vm_string} winning set is: {', '.join(minimax_submitted_winning_set)}.")
            else: 
                for cname in minimax_submitted_winning_set: 
                    if not cname in [cmap[_c] for _c in minimax_ws]: 
                        st.error(f"${cname}$ is not a {vm_string} winner.")
                for w in minimax_ws: 
                    if cmap[w] not in minimax_submitted_winning_set:
                        st.error(f"${cmap[w]}$ is a {vm_string}  winner.")
            st.write()
        else: 
            st.write("You must select some candidates.")
        with st.expander(f"Explain the {vm_string} winners"):
            st.write("""The **Minimax** winners are determined as follows. Say that the head-to-head loss of a candidate $x$ with a candidate $y$ is the margin of $y$ over $x$.  For each candidate, find the largest head-to-head loss.  Any candidate  with the smallest head-to-head loss is a winner.""")

            dot = generate_mg_dot(prof, cmap)
            st.graphviz_chart(dot)
            st.write(f"The Minimax winners: {', '.join([cmap[w] for w in minimax_ws])}.")

            minimax_data = {c:None for c in prof.candidates}
            min_max_loss = len(prof.candidates)
            for c in prof.candidates: 
                max_loss = max([prof.margin(other_c, c) for other_c in prof.candidates])
                if max_loss < min_max_loss: 
                    min_max_loss = max_loss
                minimax_data[c] = max_loss
            
            st.write(f"The minimum largest head-to-head loss for any candidate is {min_max_loss}")

            for c in prof.candidates:

                if minimax_data[c] == 0: 
                    st.write(f"* {cmap[c]} has no head-to-head losses, so the maximum loss is 0.")
                else:
                    st.write(f"* The largest head-to-head loss for {cmap[c]} is {minimax_data[c]} (against {', '.join([cmap[_c] for _c in prof.candidates if _c != c and prof.margin(_c, c)==minimax_data[c]])})")


with copeland_tab: 
    vm_string = "Copeland"
    copeland_ws = copeland(prof)
    copeland_submitted_winning_set = st.multiselect(
        f'Which candidates are the {vm_string} winners?',
        [cmap[c] for c in prof.candidates],
        [])
    if st.button(f"Check {vm_string} winners"):
        if len(copeland_submitted_winning_set) > 0: 
            if same_candidate_sets(copeland_ws, copeland_submitted_winning_set, cmap):
                st.success(f"Correct, the {vm_string} winning set is: {', '.join(copeland_submitted_winning_set)}.")
            else: 
                for cname in copeland_submitted_winning_set: 
                    if not cname in [cmap[_c] for _c in copeland_ws]: 
                        st.error(f"${cname}$ is not a {vm_string} winner.")
                for w in copeland_ws: 
                    if cmap[w] not in copeland_submitted_winning_set:
                        st.error(f"${cmap[w]}$ is a {vm_string}  winner.")
            st.write()
        else: 
            st.write("You must select some candidates.")
        with st.expander(f"Explain the {vm_string} winners"):
            st.write("""The **Copeland** winners are determined as follows. Say that the **win-loss record** for a candidate $x$ is the number of candidates that $x$ is majority preferred to minus the number of candidates that is majority preferred to $y$.  Any candidate with the largest win-loss record is a Copeland winner.""")

            dot = generate_mg_dot(prof, cmap)
            st.graphviz_chart(dot)
            st.write(f"The Copeland winners: {', '.join([cmap[w] for w in copeland_ws])}.")

            max_win_loss = -np.infty
            copeland_data = {c: None for c in prof.candidates}
            for c in prof.candidates: 
                cands_c_defeats = [other_c for other_c in prof.candidates if prof.majority_prefers(c, other_c)]
                cands_c_loses = [other_c for other_c in prof.candidates if prof.majority_prefers(other_c, c)]
                copeland_data[c] = (cands_c_defeats, cands_c_loses)
                c_score = len(copeland_data[c][0]) - len(copeland_data[c][1])
                if max_win_loss < c_score: 
                    max_win_loss = c_score
            
            st.write(f"The maximum win-loss record for any candidate is {max_win_loss}")

            for c in prof.candidates:

                st.write(f"""* The win-loss record for {cmap[c]} is calculated as follows: 

    Candidates that {cmap[c]} beats: {cand_list_str(copeland_data[c][0], cmap) if len(copeland_data[c][0]) > 0 else 'none'}. 
    
    Candidates that {cmap[c]} loses to: {cand_list_str(copeland_data[c][1], cmap) if len(copeland_data[c][1]) > 0 else 'none'}. 

    The win-loss record for {cmap[c]} is ${len(copeland_data[c][0])} - {len(copeland_data[c][1])} = {len(copeland_data[c][0]) - len(copeland_data[c][1])}$ {'(winner)' if len(copeland_data[c][0]) - len(copeland_data[c][1]) == max_win_loss else ''}.""")
                

with sc_tab: 
    vm_string = "Split Cycle"
    sc_ws = split_cycle_faster(prof)
    sc_submitted_winning_set = st.multiselect(
        f'Which candidates are the {vm_string} winners?',
        [cmap[c] for c in prof.candidates],
        [])
    if st.button(f"Check {vm_string} winners"):
        if len(sc_submitted_winning_set) > 0: 
            if same_candidate_sets(sc_ws, sc_submitted_winning_set, cmap):
                st.success(f"Correct, the {vm_string} winning set is: {', '.join(sc_submitted_winning_set)}.")
            else: 
                for cname in sc_submitted_winning_set: 
                    if not cname in [cmap[_c] for _c in sc_ws]: 
                        st.error(f"${cname}$ is not a {vm_string} winner.")
                for w in sc_ws: 
                    if cmap[w] not in sc_submitted_winning_set:
                        st.error(f"${cmap[w]}$ is a {vm_string}  winner.")
            st.write()
        else: 
            st.write("You must select some candidates.")
        with st.expander(f"Explain the {vm_string} winners"):
            st.write("""The **Split Cycle** winners are determined as follows. 

1. In each majority cycle (if any), identify the head-to-head win(s) with the smallest margin of victory in that cycle. 
2. After completing step 1 for all cycles, discard the identified wins. All remaining wins count as defeats of the losing candidates.

The candidates with no defeats are the Split Cycle winners.
""")

            dot = generate_mg_dot(prof, cmap)
            st.graphviz_chart(dot)
            st.write(f"The Split Cycle winners: {', '.join([cmap[w] for w in sc_ws])}.")

            sc_defeat = split_cycle_defeat(prof)
            cycles = prof.cycles()

            if len(cycles) == 0: 
                st.write(f"""There are no cycles, so all wins count as defeats.
                
Candidate(s) with no defeats:  {cand_list_str([c1 for c1 in prof.candidates if len([c2 for c2 in prof.candidates if prof.majority_prefers(c2, c1)]) == 0], cmap)}.
                """)

            else: 
                if len(cycles) == 1:
                    st.write(f"There is {len(cycles)} cycle: ")
                else: 
                    st.write(f"There are {len(cycles)} cycles: ")
                for cycle in cycles: 
                    cycle_dot=generate_cycle_dot(cycle, prof, cmap)
                    st.graphviz_chart(cycle_dot)
                    st.write(f"The smallest margin of victory in this cycle is {min([prof.margin(cycle[-1], cycle[0])] + [prof.margin(_c, cycle[_cidx+1]) for _cidx, _c in enumerate(cycle[0:-1])])}.")

                st.write("After discarding the smallest margin of victory in each of the above cycles, the remaining wins count as defeats of the losing candidates.   The Split Cycle defeats: ")

                sc_defeat_dot = generate_sc_defeat_dot(sc_defeat, cmap)
                st.graphviz_chart(sc_defeat_dot)

                st.write(f"The candidates with no defeats: {cand_list_str(sc_ws, cmap)}")


import os
import streamlit.components.v1 as components

num_voters = 3
num_cands = 3
prof = [(0,1,2),(1,2,0),(2,0,1)]
rank_sizes = [1,2,2]
cand_names = ["A", "B", "C"]
margin_matrix = [[0,1,1],[1,0,1],[1,1,0]]

# Create a _RELEASE constant. We'll set this to False while we're developing
# the component, and True when we're ready to package and distribute it.
# (This is, of course, optional - there are innumerable ways to manage your
# release process.)
_RELEASE = True

# Declare a Streamlit component. `declare_component` returns a function
# that is used to create instances of the component. We're naming this
# function "_component_func", with an underscore prefix, because we don't want
# to expose it directly to users. Instead, we will create a custom wrapper
# function, below, that will serve as our component's public API.

# It's worth noting that this call to `declare_component` is the
# *only thing* you need to do to create the binding between Streamlit and
# your component frontend. Everything else we do in this file is simply a
# best practice.

if not _RELEASE:
    _component_func = components.declare_component(
        "display_profile",
        # Pass `url` here to tell Streamlit that the component will be served
        # by the local dev server that you run via `npm run start`.
        # (This is useful while your component is in development.)
        url="http://localhost:3001",
    )
else:
    # When we're distributing a production version of the component, we'll
    # replace the `url` param with `path`, and point it to to the component's
    # build directory:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component("display_profile", path=build_dir)


# Create a wrapper function for the component. This is an optional
# best practice - we could simply expose the component function returned by
# `declare_component` and call it done. The wrapper allows us to customize
# our component's API: we can pre-process its input args, post-process its
# output value, and add a docstring for users.
def display_profile(prof, rank_sizes, num_cands, cand_names, c1=None, c2=None, margin_matrix=None, key=None):
    """Create a new instance of "display_profile".

    Parameters
    ----------
    prof: 2d array of integers
        The profile: an array where each component is a ranking of the candidates.
    rank_sizes: array of integers
        array of the number of voters with each ranking
    num_cands: integer
        number of candidates
    margin_matrix: 2d array of integers
        the margin matrix for the profile
    cand_names: array of strings
        names of the candidates to display (usually, it is better to display letters rather than numbers)
    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.

    Returns
    -------
    none
    """
    # Call through to our private component function. Arguments we pass here
    # will be sent to the frontend, where they'll be available in an "args"
    # dictionary.
    #
    # "default" is a special argument that specifies the initial return
    # value of the component before the user has interacted with it.
    component_value = _component_func(prof=prof, rank_sizes=rank_sizes, num_cands=num_cands, cand_names=cand_names, c1=c1, c2=c2, margin_matrix=margin_matrix, key=key)

    # We could modify the value returned from the component if we wanted.
    # There's no need to do this in our simple example - but it's an option.
    return component_value


# Add some test code to play with the component while it's in development.
# During development, we can run this just as we would any other Streamlit
# app: `$ streamlit run my_component/__init__.py`
if not _RELEASE:
    import streamlit as st

    st.subheader("Diplaying a profile")

    display_profile(prof, rank_sizes, num_cands, cand_names)

    st.markdown("---")

    display_profile(prof, rank_sizes, num_cands, cand_names, margin_matrix= margin_matrix, key='1')

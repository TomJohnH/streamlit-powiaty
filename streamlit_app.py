import streamlit as st
import leafmap.foliumap as leafmap
import pycrs
import geopandas as gpd

st.set_page_config(layout="wide")

# Geopandas use

# https://leafmap.org/notebooks/10_add_vector/
# https://leafmap.org/notebooks/13_geopandas/


# @st.cache(allow_output_mutation=True)
@st.cache_data
def get_data(file):
    geo_df = gpd.read_file(file)  # , rows=100)
    return geo_df


@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode("utf-8")


@st.cache_resource
def expensive_chart(_gdf):
    m = leafmap.Map()
    m.add_gdf(gdf, layer_name="JPT_NAZWA_")
    return m


uploaded_file = st.file_uploader("Choose a file [Powiaty.zip]")
use_example_file = st.checkbox(
    "Use example file", False, help="Use direct download from GIS"
)
st.write(
    "Download Powiaty.zip from here https://www.gis-support.pl/downloads/Powiaty.zip"
)

if use_example_file:
    uploaded_file = "https://www.gis-support.pl/downloads/Powiaty.zip"

if uploaded_file is not None:
    # ----- GEOPANDAS -----

    if "gdf" not in st.session_state:
        gdf = get_data(uploaded_file)
        my_bar = st.progress(0)
        if "gdf" not in st.session_state:
            for i in range(len(gdf.index)):
                print(i)
                current_disjoint = ~gdf.geometry.disjoint(gdf.geometry[i])
                neighbors = gdf[current_disjoint].JPT_NAZWA_.tolist()
                neighbors_JPT_KOD_JE = gdf[current_disjoint].JPT_KOD_JE.tolist()
                gdf.at[i, "NEIGHBORS"] = ", ".join(neighbors)
                gdf.at[i, "NEIGHBORS_JPT_KOD_JE"] = ", ".join(neighbors_JPT_KOD_JE)
                my_bar.progress(i / len(gdf.index))

            gdf = gdf.loc[
                :,
                [
                    "JPT_KOD_JE",
                    "JPT_NAZWA_",
                    "geometry",
                    "NEIGHBORS",
                    "NEIGHBORS_JPT_KOD_JE",
                ],
            ]
            st.session_state["gdf"] = gdf
        st.caption("Rendering map. Please wait...")

    if "gdf_output" not in st.session_state:
        gdf_output = gdf.loc[
            :,
            [
                "JPT_KOD_JE",
                "JPT_NAZWA_",
                "NEIGHBORS",
                "NEIGHBORS_JPT_KOD_JE",
            ],
        ]
        st.session_state["gdf_output"] = gdf_output

    gdf = st.session_state["gdf"]

    # ----- Region Fill -----

    def region_fill():

        st.session_state["r_no_col"] = gdf.loc[
            gdf["JPT_KOD_JE"] == st.session_state["region"]
        ].index[0]

        st.session_state["jpt_table"] = gdf.loc[
            gdf["JPT_KOD_JE"] == st.session_state["region"]
        ]
        # jpt_table.write(gdf.loc[gdf["JPT_KOD_JE"] == st.session_state["region"]].index[0])

    #################
    #
    #   Comment sectiion for geopandas dataframe
    #   st.write(type(gdf))
    #   if you select row by gdf.loc[o,:] the data type changes and code brakes,
    #   therefore use gdf.loc[[1]] instead st.write(type(gdf.loc[[1]]))
    #
    #################

    # m.add_shp(file, layer_name="JPT_NAZWA_", encoding="utf-8")

    # ----- Define map -----

    # m = expensive_chart(gdf)

    # ----- Region Colour -----

    if "r_no_col" not in st.session_state:
        st.session_state["r_no_col"] = 6

    # st.write(st.session_state["r_no_col"])

    expensive_chart(gdf).add_gdf(
        gdf.loc[[st.session_state["r_no_col"]]],
        layer_name="Selected",
        fill_colors=["red"],
    )
    # m.add_gdf(gdf, layer_name="JPT_NAZWA_")

    if "region" not in st.session_state:
        region = "1405"

    expensive_chart(gdf).to_streamlit()

    jpt_code = st.text_input(
        "Kod jednostki", "0510", on_change=region_fill, key="region"
    )

    jpt_table = st.empty()

    if "jpt_table" in st.session_state:
        jpt_table.write(st.session_state["jpt_table"])

    csv = convert_df(st.session_state["gdf_output"])

    st.write("")
    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name="gdf_output.csv",
        mime="text/csv",
    )
# test

# import packages
import streamlit as st
import pandas as pd
from PIL import Image
import requests
from io import BytesIO
import SessionState  # this is a script within the working directory

# Temporary prototype notice
st.markdown("PROTOTYPE UNDER DEVELOPMENT - Last Updated 9th December 2021")


# import NHS logo from repo
img = Image.open("images/nhs_logo.png")
if img.mode != 'RGB':
    img = img.convert('RGB')

# App appearance
st.image(img, width=100)
st.title("ICS Place Based Allocation Tool")
st.markdown(
    "This tool is designed to allow place, for allocation purposes, to be defined by aggregating GP Practices within an ICS. Please refer to the User Guide for instructions.")
st.markdown("The Relative Need Index for ICS (i) and Defined Place (p) is given by the formula:")
st.latex(r''' (WP_p/GP_p)\over (WP_i/GP_i)''')
st.markdown("This tool utilises weighted populations calculated from the 2018/19 GP Registered Practice Populations")
st.markdown("To use the tool please:")
st.markdown("- Select an ICS")
st.markdown("- Select a group of practices")
st.markdown("- Give the group a name in place of 'Group 3'")
st.markdown("- Click Calculate Need Indices.")
st.markdown("- MORE EXPLANATION AROUND SINGLE ICS USE")

# Use file uploaded to read in groups of practices
group_file = st.file_uploader("Upload CSV",type=["csv"])
if group_file is not None:
    df_group = pd.read_csv(group_file)
    st.dataframe(df_group)
    dict_group = df_group.to_dict('dict') 
      
# Load data and cache
@st.cache  # Use Streamlit cache decorator to cache this operation so data doesn't have to be read in everytime script is re-run
def get_data():
    path = "data/gp_practice_weighted_population.xlsx"  # excel file containing the gp practice level data
    return pd.read_excel(path, sheet_name ='GP practice WP by ICS', header = 0, usecols="F,L,M:AC")  # Dataframe with specific columns that will be used

# Store defined places in a list to access them later for place based calculations
@st.cache(allow_output_mutation=True)
def store_data():
    return []

# Download functionality
@st.cache
def convert_df(df):
    return df.to_csv(index=False).encode("utf-8")

# Manipulate loaded dataframe
data = get_data()
data = data.rename(columns={"STP21_42": "ICS", "GP practice name": "practice_name"})  # Rename some columns with more sensible names
data["Practice"] = data["Practice"] + " " + ":" + " " + data["practice_name"]  # Concatenate practice name with practice code to ensure all practices are unique
data = data.drop(["practice_name"], axis=1)  # Remove practice name column which is not needed anymore

# Session state initialisation and variables, this ensures that everytime a user adds a place, the previous places remain.
col_list = list(data.columns.to_list())  # create a list of columns exactly the same as those in the original data for the output df
col_list = col_list.append("Place_Name")  # add a Place Name column which will be used to group practices by defined place
output_df = pd.DataFrame(columns=col_list)  # initialise empty output dataframe with defined column names
session_state = SessionState.get(df=output_df, list=[], places=[])  # initialise session state, empty df that will hold places and empty list that will hold assigned practices
flat_list = [item for sublist in session_state.list for item in sublist]  # session state list is a list of lists so this unpacks them into one single flat list to use later

# Drop downs for user manipulation/selection of data
ics = data['ICS'].drop_duplicates()  # pandas series of unique ICSs for dropdown list
ics = ics.sort_values()  # sort ICSs in alphabetical order
ics_choice = st.sidebar.selectbox("Select your ICS:", ics, help="Select an ICS")  # dropdown for selecting ICS
practices = list(data["Practice"].loc[data["ICS"] == ics_choice])  # dynamic list of practices that changes based on selected ICS
practices = [x for x in practices if x not in flat_list]  # this removes practices that have been assigned to a place from the practices dropdown list
practice_choice = st.sidebar.multiselect("Select practices", practices,
                                         help="Select GP Practices to aggregate into a single defined 'place'")  # Dynamic practice dropdown
place_name = st.text_input("Place Name", "Group 1", help="Give your defined place a name to identify it")


# Buttons that provide functionality 
left, middle, right = st.columns(3)  # set 2 buttons on the same line
with left:
    if st.button("Calculate Need Indices", help="Save the selected practices to the named place", key="output"):
        store_data().append({place_name: practice_choice})  # append a dictionary to the cached list that has the place name as the key and a list of th
        new_place = store_data()[0]  # Extract the dictionary from the list
        session_state.places.append(new_place)  # Append the dictionary to a list that keeps track of practices in each place
        place_practices = list(new_place.values())  # Assign the practices in the newly defined place to a list
        place_practices = place_practices[0]  # place_practices is a list of lists so this turns it into a flat list
        session_state.list.append(place_practices)  # Save the assigned practices to session state to remove them from the practice dropdown list
        place_key = list(new_place.keys())  # Save place name to a list
        place_name = place_key[0]  # Extract place name from the list
        df_1 = data.query("Practice == @place_practices")  # Queries the original data and only returns the selected practices
        df_1["Place Name"] = place_name  # adds the place name to the dataframe to allow it to be used for aggregation
        df_2 = df_1.groupby('Place Name').agg(
            {'GP_pop': 'sum', 'WP_G&A': 'sum', 'WP_CS': 'sum', 'WP_MH': 'sum', 'WP_Mat': 'sum', 'WP_HCHS': 'sum', 'EACA_index' : 'sum', "WP_Presc": 'sum', "WP_AM": 'sum', "WP_Overall": "sum"}) # aggregates the practices to give the aggregated place values
        df_2 = df_2.astype(int)
        session_state.df = session_state.df.append(df_2)  # Add the aggregated place to session state
        store_data().clear()  # clear the data store so that this process can be repeated for next place
        #session_state.df = session_state.df.apply(round)
        df_3 = data.query("ICS == @ics_choice")
        df_3["Place Name"] = ics_choice
        df_4 = df_3.groupby('Place Name').agg(
            {'GP_pop': 'sum', 'WP_G&A': 'sum', 'WP_CS': 'sum', 'WP_MH': 'sum', 'WP_Mat': 'sum', 'WP_HCHS': 'sum', 'EACA_index' : 'sum', "WP_Presc": 'sum', "WP_AM": 'sum', "WP_Overall": "sum"}) # aggregates the practices to give the aggregated place values
        df_4 = df_4.astype(int)
        session_state.df = session_state.df.append(df_4)
        #session_state.df = session_state.df.append(session_state.df.sum().rename('{ics}'.format(ics=ics_choice)))
        session_state.df["G&A_Index"] = (session_state.df["WP_G&A"]/session_state.df["GP_pop"])/((session_state.df.iloc[-1, 1])/(session_state.df.iloc[-1, 0]))
        session_state.df["CS_Index"] = (session_state.df["WP_CS"]/session_state.df["GP_pop"])/((session_state.df.iloc[-1, 2])/(session_state.df.iloc[-1, 0]))
        session_state.df["MH_Index"] = (session_state.df["WP_MH"]/session_state.df["GP_pop"])/((session_state.df.iloc[-1, 3])/(session_state.df.iloc[-1, 0]))
        session_state.df["Mat_Index"] = (session_state.df["WP_Mat"]/session_state.df["GP_pop"])/((session_state.df.iloc[-1, 4])/(session_state.df.iloc[-1, 0]))
        session_state.df["HCHS_Index"] = (session_state.df["WP_HCHS"]/session_state.df["GP_pop"])/((session_state.df.iloc[-1, 5])/(session_state.df.iloc[-1, 0]))
        session_state.df["Presc_Index"] = (session_state.df["WP_Presc"]/session_state.df["GP_pop"])/((session_state.df.iloc[-1, 10])/(session_state.df.iloc[-1, 0]))
        session_state.df["AM_Index"] = (session_state.df["WP_AM"]/session_state.df["GP_pop"])/((session_state.df.iloc[-1, 11])/(session_state.df.iloc[-1, 0]))
        session_state.df["Overall_Index"] = (session_state.df["WP_Overall"]/session_state.df["GP_pop"])/((session_state.df.iloc[-1, 14])/(session_state.df.iloc[-1, 0]))
        
with middle:
    if st.button("Calculate Need Indices of Uploaded", help="Save the selected practices to the named place", key="output_upload"):
        new_place = dict_group
        session_state.places.append(new_place)  # Append the dictionary to a list that keeps track of practices in each place
        place_practices = list(new_place.values())  # Assign the practices in the newly defined place to a list
        place_practices = place_practices[0]  # place_practices is a list of lists so this turns it into a flat list
        session_state.list.append(place_practices)  # Save the assigned practices to session state to remove them from the practice dropdown list
        place_key = list(new_place.keys())  # Save place name to a list
        place_name = place_key[0]  # Extract place name from the list
        df_1 = data.query("Practice == @place_practices")  # Queries the original data and only returns the selected practices
        df_1["Place Name"] = place_name  # adds the place name to the dataframe to allow it to be used for aggregation
        df_2 = df_1.groupby('Place Name').agg(
            {'GP_pop': 'sum', 'WP_G&A': 'sum', 'WP_CS': 'sum', 'WP_MH': 'sum', 'WP_Mat': 'sum', 'WP_HCHS': 'sum', 'EACA_index' : 'sum', "WP_Presc": 'sum', "WP_AM": 'sum', "WP_Overall": "sum"}) # aggregates the practices to give the aggregated place values
        df_2 = df_2.astype(int)
        session_state.df = session_state.df.append(df_2)  # Add the aggregated place to session state
        store_data().clear()  # clear the data store so that this process can be repeated for next place
        #session_state.df = session_state.df.apply(round)
        df_3 = data.query("ICS == @ics_choice")
        df_3["Place Name"] = ics_choice
        df_4 = df_3.groupby('Place Name').agg(
            {'GP_pop': 'sum', 'WP_G&A': 'sum', 'WP_CS': 'sum', 'WP_MH': 'sum', 'WP_Mat': 'sum', 'WP_HCHS': 'sum', 'EACA_index' : 'sum', "WP_Presc": 'sum', "WP_AM": 'sum', "WP_Overall": "sum"}) # aggregates the practices to give the aggregated place values
        df_4 = df_4.astype(int)
        session_state.df = session_state.df.append(df_4)
        #session_state.df = session_state.df.append(session_state.df.sum().rename('{ics}'.format(ics=ics_choice)))
        session_state.df["G&A_Index"] = (session_state.df["WP_G&A"]/session_state.df["GP_pop"])/((session_state.df.iloc[-1, 1])/(session_state.df.iloc[-1, 0]))
        session_state.df["CS_Index"] = (session_state.df["WP_CS"]/session_state.df["GP_pop"])/((session_state.df.iloc[-1, 2])/(session_state.df.iloc[-1, 0]))
        session_state.df["MH_Index"] = (session_state.df["WP_MH"]/session_state.df["GP_pop"])/((session_state.df.iloc[-1, 3])/(session_state.df.iloc[-1, 0]))
        session_state.df["Mat_Index"] = (session_state.df["WP_Mat"]/session_state.df["GP_pop"])/((session_state.df.iloc[-1, 4])/(session_state.df.iloc[-1, 0]))
        session_state.df["HCHS_Index"] = (session_state.df["WP_HCHS"]/session_state.df["GP_pop"])/((session_state.df.iloc[-1, 5])/(session_state.df.iloc[-1, 0]))
        session_state.df["Presc_Index"] = (session_state.df["WP_Presc"]/session_state.df["GP_pop"])/((session_state.df.iloc[-1, 10])/(session_state.df.iloc[-1, 0]))
        session_state.df["AM_Index"] = (session_state.df["WP_AM"]/session_state.df["GP_pop"])/((session_state.df.iloc[-1, 11])/(session_state.df.iloc[-1, 0]))
        session_state.df["Overall_Index"] = (session_state.df["WP_Overall"]/session_state.df["GP_pop"])/((session_state.df.iloc[-1, 14])/(session_state.df.iloc[-1, 0]))     
        
with right:
    if st.button("Reset", help="Reset the place selections and start again. Press a second time to restore Practice dropdown list"):
        session_state.df.drop(session_state.df.index[:], inplace=True)
        session_state.list.clear()
        session_state.places.clear()

# Write out dataframe
st.write(session_state.df.style.format(subset=['GP_pop','WP_G&A', 'WP_CS', 'WP_MH', 'WP_Mat', 'WP_HCHS', 'WP_Presc', 'WP_AM', 'WP_Overall'],formatter="{:,.0f}"))

csv = convert_df(session_state.df)
st.download_button(label="Download Output", data=csv, file_name="{ics} place based allocations.csv".format(ics=ics_choice), mime="text/csv")

# Write out places
df_places = pd.DataFrame.from_dict(session_state.list).transpose()

st.markdown("Below is a table of the defined groups")
st.write(df_places)

csv_places = convert_df(df_places)
st.download_button(label="Download Groups", data=csv_places, file_name="{ics} place based allocations groups.csv".format(ics=ics_choice), mime="text/csv")

# Temporary prototype notice
st.markdown("PROTOTYPE UNDER DEVELOPMENT - Last Updated 9th December 2021")

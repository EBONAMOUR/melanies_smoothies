# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom smoothie!")

name_on_order = st.text_input('Name on smoothie:')
st.write('The name on your smoothie will be!')

cnx = st.connection("snowflake")
session = cnx.session()

# FIX 1: select both columns
my_dataframe = session.table("smoothies.public.fruit_options").select(
    col('FRUIT_NAME'),
    col('SEARCH_ON')
)

pd_df = my_dataframe.to_pandas()

st.dataframe(pd_df)

# FIX 2: use only fruit names
ingredient_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'],
    max_selections=5
)

if ingredient_list:
    ingredients_string = ''

    for fruit_chosen in ingredient_list:
        ingredients_string += fruit_chosen + ' '

        search_on = pd_df.loc[
            pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'
        ].iloc[0]

        st.write('The search value for', fruit_chosen, 'is', search_on)

        st.subheader(fruit_chosen + ' Nutrition Information')

        # FIX 3: correct API call
        response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{search_on}"
        )

        st.dataframe(response.json(), use_container_width=True)

    my_insert_stmt = f"""
        insert into smoothies.public.orders(ingredients, name_on_order)
        values ('{ingredients_string}','{name_on_order}')
    """

    if st.button('Submit order'):
        session.sql(my_insert_stmt).collect()
        st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")


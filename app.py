
#streamlit run "/Users/linking/My Python Stuff/TDI-python/capstone/app.py"
#for pathname with spaces need to put in quotes


import pandas as pd
import streamlit as st
import datetime
from datetime import date, time
import time
import folium
#from streamlit_folium import folium_static, st_folium
from get_recs import get_distance, filter_by_restrictions, top_reviews, reviews, reviews_all_text, open_now, get_map, print_open_hours, detailed_info, reviews_all_text, create_graph
import pgeocode
from PIL import Image
import altair as alt

#import dataframe
    #only open restaurants (remove permanently closed restaurants)
    #remove all restauranst with less than 4 stars
    #only restaurants in Philadelphia
    #add hours
#df0 = pd.read_csv("My Python Stuff/TDI-python/capstone/df_br_reduced_restaurant_philly_19107_10min_4stars_2019.csv")

df0 = pd.read_csv("My Python Stuff/TDI-python/capstone/df_philly_restaurants_with_four_stars.csv")

pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)   
pd.set_option('display.max_row', None)
pd.set_option('display.max_seq_item', None)

def app():
    st.set_page_config(layout = 'wide')
    
    with st.sidebar:
        options = st.multiselect(
        'Select your dietary restrictions',
        ['low-carb', 'lactose-free', 'gluten-free', 'vegetarian', 'pescatarian', 'vegan', 'kosher', 'halal'])

        col1, col2 = st.columns(2)

        with col1:
            zip_code = st.text_input('Enter zip code', '19107')
                                    
        with col2:
            within_x_mi = st.selectbox('Within',
        ('20 miles', '5 miles', '1 mile', '.3 miles'))
            
        col1, col2 = st.columns(2)
        with col1:
            d = st.date_input(
            "Open on",
            date.today())  #current date 
            #st.write(d)
        with col2:
            t = st.time_input("", datetime.time(18,30))
        
            #t = st.time_input("", datetime.time(6, 30))

        string_all = []
        for dietary_restriction in options:
            string = f'best for {dietary_restriction}'
            string_all.append(string)

        rank_options = ['most reviewed']
        rank_options.extend(string_all)
        rank_options.append('distance')    

        rank = st.selectbox('Sort restaurants by', (rank_options))

        with st.form("Get restaurant recs!"):

       # Every form must have a submit button.
            submitted = st.form_submit_button("Submit")
    
    if not submitted:
        tab3, tab4 = st.tabs(["why", "how"])
        
        tab3.header("FoodieWith")
        with tab3:     
            st.write("finds restaurants for your dietary restriction(s)")

            st.subheader("Difficult to find tasty restaurants for everyone")

            image1 = Image.open("My Python Stuff/TDI-python/capstone/230213_diagram0.png")

            st.image(image1, caption="40% of Americans have dietary restrictions due to preference, religious, or health conditions (Statistica, 2021).")
            
        tab4.header("FoodieWith")
        with tab4:
            st.write("finds best restaurants for your dietary restriction(s)")            

            st.subheader("FoodieWith pipeline")   

            image2 = Image.open("My Python Stuff/TDI-python/capstone/230213_diagram3.png")

            st.image(image2, caption="FoodieWith recommends only tasty restaurants (at least 4 star average) that accommodate your dietary restriction(s) (at least 4 star average).")

    
    
            st.subheader("FoodieWith searches Yelp reviews")   

            image4 = Image.open("My Python Stuff/TDI-python/capstone/230214-diagram.png")

            st.image(image4, caption='For example, FoodWith searches for "gluten-free" and "celiac" to identify reviews from gluten-free diners.')
            
            st.subheader("FoodieWith analyzes reviews and recommends restaurants")  
            
            image5 = Image.open("My Python Stuff/TDI-python/capstone/230214-diagram1.png")

            st.image(image5, caption="For example, FoodieWith counts the total number of reviews from gluten-free diners and averages the star rating of these reviews. Only restaurants with at least a 4 star average rating for your dietary restriction(s) are recommended.")
            
            st.subheader("FoodieWith shares detailed reviews") 
            
            image6 = Image.open("My Python Stuff/TDI-python/capstone/230214-diagram2.png")
            
            st.image(image6, caption="For example, FoodWith displays the most recent and useful reviews that mention your dietary restriction(s).")
            


        
        
        
    if submitted:
        
        #need to remove
        #st.write(time.ctime())        
        #st.write('submitted')
        
        nomi = pgeocode.Nominatim('us')
        current_location = nomi.query_postal_code(zip_code)
        current_location_lat = current_location['latitude']
        current_location_long = current_location['longitude']
        user_location = (current_location_lat, current_location_long)
        
        
        
        if int(zip_code) in pd.unique(df0['postal_code']): 
            #need to remove
            #st.write(time.ctime())
            #st.write('before filtered by distance')
                    
            df2 = get_distance(df0, within_x_mi, user_location)
            #need to remove
            #st.write(time.ctime())
            #st.write('after filtered by distance')            
            
            
            result1 = filter_by_restrictions(options, df2)
            #result1 gets altered
            #result10 = result1
            #need to remove
            #st.write(time.ctime())
            #st.write('filter by restriction')
            
            
            result2 = top_reviews(options, result1, rank)
            #need to remove
            #st.write(time.ctime())
            #st.write('find top reviews')            
            
            
            
            
            if len(result2) == 0:
                st.write("Oh no! You're in a foodie desert.")
                st.write("Please search again with a different location and/or expand the distance you're willing to travel.")
            else:
                result4 = open_now(result2, df2, d, t)
                #need to remove
                #st.write(time.ctime())
                #st.write('find open now')   
                
                result8 = reviews_all_text(options, result4, result1)
                #need to remove
                #st.write(time.ctime())
                #st.write('get result8')   
                
                
                
                result3 = reviews(options, result4, result1)
                #need to remove
                #st.write(time.ctime())
                #st.write('get result3')  
                
                
                
                result5 = print_open_hours(result4)
                
                
                
                
                result6 = detailed_info(result4, df2)

            #df for location and hours
                df_review_info = result6[['rank', 'categories', 'hours', 'address', 'city', 'state', 'postal_code']]
                df_review_info = df_review_info.sort_values(['rank']).drop_duplicates()
                df_review_info.dropna(how = 'any', inplace = True)
                df_review_info.reset_index(drop=True, inplace=True)
                df_review_info.index = df_review_info.index + 1

                #df for reviews
                df_review_details = result3[['rank', 'cat', 'review_stars', 'text', 'date']]
                df_review_details = df_review_details.sort_values(['rank', 'cat'])
                df_review_details = df_review_details.drop_duplicates(subset = 'text')

                tab1, tab2, tab3, tab4, tab5 = st.tabs(["map", "top 10", "why", "how", "about"])

                tab1.header("FoodieWith map")
                with tab1:
                    #need to remove
                    #st.write(time.ctime())
                    #st.write('before map')
                    
                    m = get_map(result4, df2, rank, within_x_mi, current_location_lat, current_location_long)
                    #folium_static(m)

                tab2.header("FoodieWith restaurants")
                with tab2:
                    #need to remove
                    #st.write(time.ctime())
                    #st.write('after map')
                    
                    for i in range(1,(len(result4) + 1),1):
                        string_title = (str(i) + '. ' + result4.loc[i]['name'] + '\n')
                        container = st.container()
                        container.subheader(string_title)            
                        string = ('overall: ' + str(result4.loc[i]['stars']))
                        expander_title = df_review_info.loc[i]['categories']
                        with st.expander(expander_title):
                            st.subheader('location and hours')
                            distance_away =('(' + str(round(result4.loc[i]['distance_to_restaurant'], 1)) + ' miles)')
                            
                            address_line1 = (df_review_info.loc[i]['address'] + '\n'
                            + df_review_info.loc[i]['city'] + ', ' + df_review_info.loc[i]['state'] + ' ' + str(int(df_review_info.loc[i]['postal_code'])))
                            col1, col2 = st.columns(2)
                            with col1:    
                                
                                st.text(address_line1)                   

                                st.text(distance_away)
                                
                            with col2:
                                st.text(result5['Mon'][i-1] +'\n' 
                                        + result5['Tue'][i-1] +'\n' 
                                        + result5['Wed'][i-1] +'\n' 
                                        + result5['Thu'][i-1] +'\n' 
                                        + result5['Fri'][i-1] +'\n' 
                                        + result5['Sat'][i-1] +'\n' 
                                        + result5['Sun'][i-1] +'\n'                                 
                                       )


                            st.subheader('ratings')
                            
                            df_ratings = result4.drop(['rank', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'], axis = 1)
                            
                            string = ('overall: ' + str(df_ratings.loc[i]['stars']))
                            for j in range(5, (len(df_ratings.columns)-1), 2):
                                string = (string + ' | '+ df_ratings.columns[j] + ': ' + str(df_ratings.loc[i][df_ratings.columns[j]]))

                            st.write(string)
                            
                            
                            score = i
                            for k in range(len(options)):
                                dietary_restriction = options[k]
                                chart_title = f'Rating distribution for {dietary_restriction} reviews'
                                df_graph = create_graph(result8, score, dietary_restriction)

                                bar = (alt.Chart(df_graph).mark_bar()
                                    .encode(x=alt.X('count', axis = alt.Axis(title = 'number of reviews')),
                                            y=alt.Y('review_label', axis=alt.Axis(title='', tickSize = 0),
                                                    sort=['5 stars', '4 stars', '3 stars', '2 stars', '1 star'])#sort = '-y'
                                ).properties(title = chart_title)
                                )

                                bar.mark_text(
                                    align='left',
                                    baseline='middle',
                                    dx=3  # Nudges text to right so it doesn't appear on top of the bar
                                ).encode(
                                    text='count:Q'
                                )

                                #text does not show up

                                st.altair_chart(bar, use_container_width=True)

                            st.subheader('')

                            review_string = df_review_details[df_review_details['rank'] == i].drop(['rank'], axis = 1)
                            
                            review_string = review_string[['cat', 'review_stars', 'text', 'date']]

                            review_string.columns = ['dietary restriction', 'stars', 'text', 'date']
                            review_string['date'] = pd.to_datetime(review_string['date']).dt.date
                            review_string['stars'] = review_string['stars'].apply(str)
                            
                            
                            
                            review_string.reset_index(drop=True, inplace=True)
                
                            st.subheader('recent and useful reviews')

                            # CSS to inject contained in a string
                            hide_table_row_index = """
                                    <style>
                                    thead tr th:first-child {display:none}
                                    tbody th {display:none}
                                    </style>
                                    """

                            # Inject CSS with Markdown
                            st.markdown(hide_table_row_index, unsafe_allow_html=True)


                            st.table(review_string)



                tab3.header("FoodieWith")
                with tab3:     
                    #need to remove
                    #st.write(time.ctime())
                    
                    
                    st.write("finds best restaurants for your dietary restriction(s)")

                    st.subheader("Difficult to find tasty restaurants for everyone")

                    image1 = Image.open("My Python Stuff/TDI-python/capstone/230213_diagram0.png")

                    st.image(image1, caption="40% of Americans have dietary restrictions due to preference, religious, or health conditions (Statistica, 2021).")

                tab4.header("FoodieWith")
                with tab4:
                    st.write("finds best restaurants for your dietary restriction(s)")
                    st.subheader("FoodieWith pipeline")   

                    image2 = Image.open("My Python Stuff/TDI-python/capstone/230213_diagram3.png")

                    st.image(image2, caption="FoodieWith recommends only tasty restaurants (at least 4 star average) that accommodate your dietary restriction(s) (at least 4 star average).")

                    
                    
                    #st.write("finds best restaurants for your dietary restriction(s)")            

                    st.subheader("FoodieWith searches Yelp reviews")   

                    image4 = Image.open("My Python Stuff/TDI-python/capstone/230214-diagram.png")

                    st.image(image4, caption='For example, FoodWith searches for "gluten-free" and "celiac" to identify reviews from gluten-free diners.')

                    st.subheader("FoodieWith analyzes reviews and recommends restaurants")  

                    image5 = Image.open("My Python Stuff/TDI-python/capstone/230214-diagram1.png")

                    st.image(image5, caption="For example, FoodieWith counts the total number of reviews from gluten-free diners and averages the star rating of these reviews. Only restaurants with at least a 4 star average rating for your dietary restriction(s) are recommended.")

                    st.subheader("FoodieWith shares detailed reviews") 

                    image6 = Image.open("My Python Stuff/TDI-python/capstone/230214-diagram2.png")

                    st.image(image6, caption="For example, FoodWith displays the most recent and useful reviews that mention your dietary restriction(s).")

                tab5.header("about")        
                with tab5:
                    col1, col2 = st.columns(2)

                    with col1:
                        #st.write('My name is Yuan-Hung Lin King. I have a PhD in Neuroscience from the University of California, San Francisco. I love exploring new restaurants with my friends and family!')
                        st.write('Yuan-Hung Lin King (PhD)')
                        
                        st.write('email: yuan.hung.lin.king@mg.thedataincubator.com')
                        
                        st.write('LinkedIn: www.linkedin.com/in/yuan-hung-lin-king')

                        #need to remove
                        #st.write(time.ctime())
                        
                        
                        #st.write('Thank you for visiting FoodieWith!')

                        #txt = st.text_area('Please leave your comments and/or questions below:', placeholder ='Thank you for visiting FoodieWith!')


                    #with col2:
                        #image3 = Image.open("My Python Stuff/TDI-python/capstone/230213_pigs.jpeg")

                        #st.image(image3, caption="") #, width = 400)
        else:
            st.write('Oh no! FoodieWith has not expanded to your location yet!')
            st.write('Please enter a zip code in Philadelphia!')

if __name__ == '__main__':
    app()


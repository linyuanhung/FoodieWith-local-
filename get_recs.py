def get_distance(df0, within_x_mi, user_location):
    import pandas as pd
    from geopy import distance
    from geopy.distance import great_circle
    
    distance_dict = {'20 miles': 20, '5 miles' : 5, '1 mile' : 1, '.3 miles': .3}
    
    df1 = df0[['business_id', 'latitude', 'longitude']]
    df1 = df1.drop_duplicates().reset_index(drop = True)
    
    list = []
    for i in range(len(df1)):
        restaurant_location = (df1['latitude'][i], df1['longitude'][i])
        list.append(distance.great_circle(user_location, restaurant_location).miles)
    df1['distance_to_restaurant'] = list
   
    df1 = df1[(df1['distance_to_restaurant'] <= distance_dict[within_x_mi])]

    df2 = pd.merge(df0, df1, left_on = ['business_id', 'latitude', 'longitude'], right_on = ['business_id', 'latitude', 'longitude'], how = 'inner')
    
    return df2






#function to filter by dietary restriction
def filter_by_restrictions(dietary_restriction_list, df0):
#arguments: 
    #dietary_restriction: list with key (string) that correspond to key in the keyword_dict
    #df: pandas df
    
#returns a list of df
    
#first pull relevant columns from dataset
    df = df0[['business_id', 'name', 'stars', 'review_count', 'review_stars', 'useful', 'text', 'date', 'distance_to_restaurant']]
#first filter dataset and keep restuarants (that does not taste bad) for overall food tastiness with 'stars' >3   
    #dataset = dataset[(dataset['stars'] >= 4)]
#create a dictionary of {dietary_restriction: keyword_lsit}

    #low-carb, kosher, keto, diabetes, 
    #lactose, diary, allergies
    
    #do not use 'gf'--also stands for girlfriend
    #keyword_dict = {'gluten-free' : ['gluten-free', 'gluten free', 'celiac', 'coeliac'],
    #                'pescatarian': ['pescatarian', 'vegetarian', 'vegan'],
    #               'vegetarian' : ['vegetarian', 'vegan'],
    #                'vegan' : ['vegan'],
    #               'halal' : ['halal'],
    #               'kosher' : ['kosher', 'hechsher', 'kashrut'],
    #               'lactose-free' : ['lactose-free','lactose free', 'dairy-free', 'dairy free', 'milk free', 'milk-free', 'vegan'],
    #               'low-carb' : ['low carb', 'low-carb', 'keto', 'diabet']}
    
    
    keyword_dict = {'gluten-free' : 'gluten-free|gluten free|celiac|coeliac',
        'pescatarian' :' pescatarian|vegetarian|vegan',
        'vegetarian' : 'vegetarian|vegan',
        'halal' : 'halal',
        'kosher' : 'kosher|hechsher|kashrut',
        'lactose-free' : 'lactose-free|lactose free|dairy-free|dairy free|milk free|milk-free|vegan',
        'low-carb' : 'low carb|low-carb|keto|diabet'}                   
    
#pull out restaurant reviews corresponding to dietary restriction--any reviews containing a keyword in keyword_list 
    import pandas as pd
    
    review_list = []
    for dietary_restriction in dietary_restriction_list:
        keyword_list = keyword_dict[dietary_restriction]
        reviews = pd.DataFrame()
        keyword_review = df.loc[df['text'].str.contains(keyword_list, case = False, regex=True)]
        keyword_review = keyword_review.drop_duplicates()
        reviews = pd.concat([reviews, keyword_review]).drop_duplicates()
        
        #for keyword in keyword_list:
        #    keyword_review = df.loc[df['text'].str.contains(keyword, case = False)]
        #    keyword_review = keyword_review.drop_duplicates()
        #    reviews = pd.concat([reviews, keyword_review]).drop_duplicates() 

        #add new columns with number of reviews for keyword and avg of review_stars for keyword
        #avg of 'review_stars' for keyword
        avg_review_stars_column_name = f'stars for {dietary_restriction}'
        reviews[avg_review_stars_column_name] = round(reviews.groupby(['business_id'])['review_stars'].transform('mean'), 2)
        
        #count number of reviews
        count_review_stars_column_name = f'{dietary_restriction} reviews'
        reviews[count_review_stars_column_name] = reviews.groupby(['business_id'])['review_stars'].transform('count')

        review_list.append(reviews)
            
    return review_list 
            
    return review_list 
        
#function to return a list of restaurants
def top_reviews(dietary_restriction_list, review_list, rank):
    import pandas as pd
    
    business_list = []
    for i in range(len(review_list)):
        dietary_restriction = dietary_restriction_list[i]

        #avg of 'review_stars' for keyword
        avg_review_stars_column_name = f'stars for {dietary_restriction}'
        
        #count number of reviews
        count_review_stars_column_name = f'{dietary_restriction} reviews'
        
        reviews = review_list[i]
        #keep only top rated restuarants for dietary restriction with 'avg_review_stars' >4
        reviews = reviews[(reviews[avg_review_stars_column_name] >= 4)]
        
        #keep only top rated restaurants with more than 1 review per dietary retriction
        reviews = reviews[(reviews[count_review_stars_column_name] > 2)]
    
        #keep more than 5 reviews or 5 star rating (restaurants with less than 5 reviews need a 5 star rating)
        reviews = reviews[(reviews[count_review_stars_column_name] > 5) | (reviews[avg_review_stars_column_name] == 5)]

        #remove restaurants without reviews after 2019 since Covid caused disruptions
        reviews = reviews[(reviews['date'] >= "2019-01-01 00:00:00")]
        
        #drop columns
        df = reviews.drop(['review_stars', 'useful', 'text','date'], axis = 1)
        #remove duplicates
        business_list.append(df.drop_duplicates(subset = ['business_id']))
        
    #merge together        
    if len(business_list) == 2:
        df_recommend = pd.merge(business_list[0], business_list[1], left_on = ['business_id', 'name', 'stars', 'review_count', 'distance_to_restaurant'], right_on = ['business_id', 'name', 'stars', 'review_count', 'distance_to_restaurant'], how = 'inner')
    
    elif len(business_list) > 2:
        i = 2
        df_recommend = pd.merge(business_list[0], business_list[1], left_on = ['business_id', 'name', 'stars', 'review_count', 'distance_to_restaurant'], right_on = ['business_id', 'name', 'stars', 'review_count', 'distance_to_restaurant'], how = 'inner')
        while i < len(business_list):
            df_recommend = pd.merge(df_recommend, business_list[i], left_on = ['business_id', 'name', 'stars', 'review_count', 'distance_to_restaurant'], right_on = ['business_id', 'name', 'stars', 'review_count', 'distance_to_restaurant'], how = 'inner')
            i = i + 1
    
    elif len(business_list) == 1:
        df_recommend = business_list[0]
    
    else:
        df_recommend = pd.DataFrame()
    
        
    #sort and reset index
    if rank == 'most reviewed':
        df_recommend = df_recommend.sort_values(['review_count', 'stars'], ascending = False)
        df_recommend = df_recommend.reset_index(drop=True)
        df_recommend.index = df_recommend.index + 1
        
    if rank == 'best for low-carb':
        df_recommend = df_recommend.sort_values(['low-carb reviews', 'stars for low-carb'], ascending = False)
        df_recommend = df_recommend.reset_index(drop=True)
        df_recommend.index = df_recommend.index + 1
    
    if rank == 'best for lactose-free':
        df_recommend = df_recommend.sort_values(['lactose-free reviews', 'stars for lactose-free'], ascending = False)
        df_recommend = df_recommend.reset_index(drop=True)
        df_recommend.index = df_recommend.index + 1
    
    if rank == 'best for vegetarian':
        df_recommend = df_recommend.sort_values(['vegetarian reviews', 'stars for vegetarian'], ascending = False)
        df_recommend = df_recommend.reset_index(drop=True)
        df_recommend.index = df_recommend.index + 1    
    
    if rank == 'best for gluten-free':
        df_recommend = df_recommend.sort_values(['gluten-free reviews', 'stars for gluten-free'], ascending = False)
        df_recommend = df_recommend.reset_index(drop=True)
        df_recommend.index = df_recommend.index + 1
    
    if rank == 'best for pescatarian':
        df_recommend = df_recommend.sort_values(['pescatarian reviews', 'stars for pescatarian'], ascending = False)
        df_recommend = df_recommend.reset_index(drop=True)
        df_recommend.index = df_recommend.index + 1
    
    if rank == 'best for vegan':
        df_recommend = df_recommend.sort_values(['vegan reviews', 'stars for vegan'], ascending = False)
        df_recommend = df_recommend.reset_index(drop=True)
        df_recommend.index = df_recommend.index + 1
    
    if rank == 'best for kosher':
        df_recommend = df_recommend.sort_values(['kosher reviews', 'stars for kosher'], ascending = False)
        df_recommend = df_recommend.reset_index(drop=True)
        df_recommend.index = df_recommend.index + 1
    
    if rank == 'best for halal':
        df_recommend = df_recommend.sort_values(['halal reviews', 'stars for halal'], ascending = False)
        df_recommend = df_recommend.reset_index(drop=True)
        df_recommend.index = df_recommend.index + 1
    
    
    if rank == 'distance':
        df_recommend = df_recommend.sort_values(['distance_to_restaurant', 'review_count'])
        df_recommend = df_recommend.reset_index(drop=True)
        df_recommend.index = df_recommend.index + 1

    
    #make index into a new column in df_recommend
    df_recommend['rank'] = df_recommend.index

                        
    return df_recommend

#need to filter by open hours before returning a top 10 list

#write a function to determine if restaurant is currently open

def open_now(result2, df2, d, t):
    
    #returns only business_id of currently open restaurants
    import pandas as pd
    import datetime
    from datetime import datetime
        
    #current_datetime = datetime.now()
    #current_time = current_datetime.time()
        
    df3 = df2[['business_id', 'hours']].drop_duplicates()
    df_hours = df3[df3['business_id'].isin(result2['business_id'])]
    df_hours['hours_dict'] = df_hours['hours'].transform(eval)
    df_hours = pd.concat([df_hours, df_hours['hours_dict'].apply(pd.Series)], axis = 1)
    #df_hours = df_hours.drop(columns = ['hours_dict', 'hours'])
    
    
    
    #split into open and closed times
    df_hours['Monday'] = df_hours['Monday'].str.split('-')
    df_hours['Tuesday'] = df_hours['Tuesday'].str.split('-')
    df_hours['Wednesday'] = df_hours['Wednesday'].str.split('-')
    df_hours['Thursday'] = df_hours['Thursday'].str.split('-')
    df_hours['Friday'] = df_hours['Friday'].str.split('-')
    df_hours['Saturday'] = df_hours['Saturday'].str.split('-')
    df_hours['Sunday'] = df_hours['Sunday'].str.split('-')
    
    
    weekday_index = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekday = weekday_index[d.weekday()] #index starts at 0 for Monday
    
    df_hours = df_hours.fillna(0)
    df_hours = df_hours.reset_index()
    
    
    open_restaurants = []
    for i in range(len(df_hours)):
        if df_hours[weekday][i] == 0:
            continue
        else:
            open_hours = df_hours[weekday][i][0]
            close_hours = df_hours[weekday][i][1]
            if ((datetime.strptime(open_hours, '%H:%M').time()) < t) or ((datetime.strptime(close_hours, '%H:%M').time()) > t):
                open_restaurants.append(df_hours['business_id'][i])
                
    #return df of result2 with only currently open restaurants
    result3 = result2.loc[result2['business_id'].isin(open_restaurants)]

    result4 = pd.merge(result3, df_hours, left_on = ['business_id'], right_on = ['business_id'], how = 'inner')

    result4 = result4.drop(['index','hours', 'hours_dict'], axis = 1)
    
    result4 = result4.sort_values(['rank'], ascending = True)
    result4 = result4.reset_index(drop=True)
    result4.index = result4.index + 1
    
    result4['rank'] = result4.index
    
    return result4[:10]




#function to return a detailed restaurant review
def reviews(dietary_restriction_list, df_recommend, review_list):
    #argument: dietary_restriction
            #need to make sure in the same order as in filter_by_dietary_restrction func
            #df containing restaurants
            #df containing reviews per dietary restriction
            #df containging all reviews

    #return a dataframe containing most useful reviews of the restaurant
    
    import pandas as pd
    

        
    df_recommend = df_recommend[['rank', 'business_id']]
        
    df_reviews = pd.DataFrame()
    
    for i in range(len(review_list)):   
        #remove restaurants without reviews after 2019 since Covid caused disruptions
        df = review_list[i][(review_list[i]['date'] >= "2019-01-01 00:00:00")]
        
        #merge with original df containing text per dietary restriction
        df_merge = pd.merge(df_recommend, df, left_on = ['business_id'], right_on = ['business_id'], how = 'inner')
        #pull most useful review per dietary restriction
        df_useful = df_merge.groupby(['business_id'])['useful'].transform('max')
        df_useful_text = df_merge[df_merge['useful'] == df_useful]

        #add review category
        dietary_restriction = dietary_restriction_list[i]
        cat_column_name = f'{dietary_restriction}'
        df_useful_text.loc[:,'cat'] = cat_column_name
        
        df_reviews = pd.concat([df_reviews, df_useful_text]) 

        #pull most recent review per dietary restriction
        df_date = df_merge.groupby(['business_id'])['date'].transform('max')
        df_date_text = df_merge[df_merge['date'] == df_date]

        #add review category
        dietary_restriction = dietary_restriction_list[i]
        cat_column_name = f'{dietary_restriction}'
        #df['cat'] = cat_column_name
        df_date_text.loc[:,'cat'] = cat_column_name
        
        df_reviews = pd.concat([df_reviews, df_date_text])
    
    
    #merge with orignal df containing text of all reviews
#    df = df[(df['date'] >= "2019-01-01 00:00:00")]
#    df_merge = pd.merge(df_recommend, df0, left_on = ['business_id'], right_on = ['business_id'], how = 'inner')
    #pull most useful review per dietary restriction
#    df_all_useful = df_merge.groupby(['business_id'])['useful'].transform('max')
#   df_all_useful_text = df_merge[df_merge['useful'] == df_all_useful]   
#    df_all_useful_text.loc[:,'cat'] = 'all'   
#    df_reviews = pd.concat([df_reviews, df_all_useful_text])

    
    
    return df_reviews

#rating graph

def reviews_all_text(dietary_restriction_list, df_recommend, review_list):
    import pandas as pd
    import seaborn as sns
    
    df_recommend = df_recommend[['business_id', 'rank']].drop_duplicates()
    df_reviews = pd.DataFrame()
    for i in range(len(review_list)):        
        #merge with original df containing text per dietary restriction
        #review_list[i]['business'].isin(df_recommend['business_id'])
        
        df_merge = pd.merge(df_recommend, review_list[i], left_on = ['business_id'], right_on = ['business_id'], how = 'inner')
        print(len(df_merge))
        #add review category
        dietary_restriction = dietary_restriction_list[i]
        cat_column_name = f'{dietary_restriction}'
        #df['cat'] = cat_column_name
        df_merge.loc[:,'cat'] = cat_column_name
        df_reviews = pd.concat([df_reviews, df_merge])
    df_graph = df_reviews[['business_id', 'rank', 'cat', 'review_stars']]
    df_graph['count'] = df_graph.groupby(['business_id', 'rank', 'cat', 'review_stars'])['review_stars'].transform('count')
    df_graph.drop_duplicates(inplace = True)
    df_graph = df_graph.sort_values(['rank', 'cat', 'review_stars']).reset_index()

    return df_graph
        
    
def get_map(result4, df2, rank, within_x_mi, current_location_lat, current_location_long):
    import pandas as pd
    
    import folium
    import folium.plugins as plugins

    from streamlit_folium import folium_static, st_folium

    result5 = result4[['business_id', 'name','rank']]
    df3 = df2[['business_id','latitude','longitude']].drop_duplicates()
    df_map = pd.merge(df3, result5, left_on = ['business_id'], right_on = ['business_id'], how = 'inner')
    df_map = df_map.sort_values(['rank']).reset_index(drop = True)



    zoom_dict = {'20 miles' : 13, '5 miles': 15, '1 mile': 16, '.3 miles': 16}

    if rank == 'distance':
        zoom_x = 15
    else:
        zoom_x = zoom_dict[within_x_mi]

    m = folium.Map(location = [current_location_lat, current_location_long], min_zoom=13, max_zoom=16.5) #zoom_start = zoom_dict[within_x_mi])

    #tooltip = "Click me!"

    #for current location
    folium.Marker(
        [current_location_lat, current_location_long], popup="<i>Current location</i>", icon=folium.Icon(color='red', prefix='fa', icon = 'fa-solid fa-user')
    ).add_to(m)


    icon_list = ['fa-solid fa-1', 'fa-solid fa-2', 'fa-solid fa-3', 'fa-solid fa-4', 'fa-solid fa-5', 'fa-solid fa-6', 'fa-solid fa-7', 'fa-solid fa-8', 'fa-solid fa-9', 'fa-solid fa-10']

    for i in range(len(df_map)):
        latitude = df_map['latitude'][i]
        longitude = df_map['longitude'][i]
        name = df_map['name'][i]
        rank_icon = icon_list[i]
        #folium.Icon(color='blue', prefix='fa', icon = 'fa-solid fa-utensils')).add_to(m)    

        #folium.Marker([latitude, longitude], popup = name, tooltip=tooltip, icon= folium.Icon(color='blue', prefix='fa', icon = rank_icon)).add_to(m)    

        folium.Marker(
            [latitude, longitude], popup = name, 
            icon=plugins.BeautifyIcon(
                             icon="arrow-down", icon_shape="marker",
                             number=i+1, border_color= '#0096FF', background_color = '#0096FF', text_color = 'white'
                         )
        ).add_to(m)


    df_map_all = df_map[['latitude', 'longitude']]
    df_map_all.loc[len(df_map_all)] = [current_location_lat, current_location_long]


    sw = df_map_all[['latitude', 'longitude']].min().values.tolist()
    ne = df_map_all[['latitude', 'longitude']].max().values.tolist()

    m.fit_bounds([sw, ne]) 
    folium_static(m)
    #st_folium(m, width = 725)

    m
    
    
    
def print_open_hours(result4):
    import pandas as pd
    weekday = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekday_short = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    df_print_open_hours = pd.DataFrame(columns = weekday_short)

    for i in range(1, len(result4)+1,1):
        open_hours = []
        for j in range(len(weekday)):            
            label_short = weekday_short[j]
            label_long = weekday[j]
            if (result4.loc[i][label_long] == 0):
                open_hours.append(f'{label_short}: closed')
            elif (((result4.loc[i][label_long][0]) == '0:0') and ((result4.loc[i][label_long][1]) == '0:0')):
                open_hours.append(f'{label_short}: closed')
            else:
                open_hours.append((f'{label_short}: ' + str(result4.loc[i][label_long][0]) + '0 - ' + str(result4.loc[i][label_long][1]) + '0'))
        df_print_open_hours.loc[len(df_print_open_hours)] = open_hours
    return df_print_open_hours



def detailed_info(result4, df2):
    import pandas as pd
    df3 = df2.drop(['useful','name','text','date','stars','review_count','distance_to_restaurant'], axis = 1)
    result4 = result4.drop(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'], axis = 1)
    result6 = pd.merge(result4, df3, left_on = ['business_id'], right_on = ['business_id'], how = 'inner')
    return result6


#rating graph

def reviews_all_text(dietary_restriction_list, df_recommend, review_list):
    import pandas as pd
    
    df_recommend = df_recommend[['business_id', 'rank']].drop_duplicates()
    df_reviews = pd.DataFrame()
    for i in range(len(review_list)):        
        #merge with original df containing text per dietary restriction
        #review_list[i]['business'].isin(df_reccomend['business_id'])
        
        df_merge = pd.merge(df_recommend, review_list[i], left_on = ['business_id'], right_on = ['business_id'], how = 'inner')

        #add review category
        dietary_restriction = dietary_restriction_list[i]
        cat_column_name = f'{dietary_restriction}'
        #df['cat'] = cat_column_name
        df_merge.loc[:,'cat'] = cat_column_name
        df_reviews = pd.concat([df_reviews, df_merge])
    
    df_graph = df_reviews[['business_id', 'rank', 'cat', 'review_stars']]
    #df_graph = df_graph.sort_values(['rank', 'cat', 'review_stars'])

    df_graph['count'] = df_graph.groupby(['business_id', 'rank', 'cat', 'review_stars'])['review_stars'].transform('count')
    df_graph.drop_duplicates(inplace = True)
    df_graph = df_graph.sort_values(['rank', 'cat', 'review_stars']).reset_index(drop = True)

    return df_graph

def create_graph(df_graph, score, dietary_restriction):
    import pandas as pd
    df_graph_list = []
    df_graph = df_graph[df_graph['rank'] == score]
    df_graph = df_graph[df_graph['cat'] == dietary_restriction]
    df_graph = df_graph[['review_stars', 'count']].sort_values(['review_stars'])
    df_graph = df_graph.reset_index(drop = True)
    for i in [1 , 2 , 3 , 4 , 5]:
        if i not in df_graph['review_stars'].values:
            #new_row = {'review_stars' : i, 'count': 0}
            df_graph.loc[len(df_graph.index)] = [i, 0]     
            
    df_graph = df_graph.sort_values(['review_stars'])
    
    new_label = ['1 star', '2 stars', '3 stars', '4 stars', '5 stars']
    df_graph['review_label'] = new_label

    df_graph = df_graph.reset_index(drop = True)
    df_graph = df_graph.drop(['review_stars'], axis = 1)
    return df_graph
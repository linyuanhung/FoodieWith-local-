#function to map out reccomendations

def make_map(df_reccomend, df, current_location = [39.955505, -75.155564]):
    
    import folium
    
    import pandas as pd
    
    df_reccomend = df_reccomend[['business_id','name']]
    df = df[['business_id', 'name', 'latitude', 'longitude','address','city','state']]
    
    df_map = pd.merge(df_reccomend, df, left_on = ['business_id', 'name'], right_on = ['business_id', 'name'], how = 'inner')

    
    
    m = folium.Map(location = current_location, zoom_start = 12)

    tooltip = "Click me!"

    #for current location
    folium.Marker(
        [39.955505, -75.155564], popup="<i>Current location</i>", tooltip=tooltip, icon=folium.Icon(color='red')
).add_to(m)

    #need to figure out how to add longitude and latitude that actually corresponds to address vs zipcode
    for i in range(len(df_map)):
        latitude = df_map['latitude'][i]
        longitude = df_map['longitude'][i]
        
        #want to add address to pop up
        name = df_map['name'][i]
        folium.Marker([latitude, longitude], popup = name, tooltip=tooltip).add_to(m)    

        
        
        

        
        
        
    return m
import pandas as pd
import streamlit as st
import plotly.express as px
from sklearn.model_selection import train_test_split
# from sklearn.ensemble import RandomForestClassifier 
from sklearn.linear_model import LinearRegression
from sklearn.metrics import accuracy_score 
import pickle 

@st.cache
def get_airbnb_data():
    return pd.read_csv("http://data.insideairbnb.com/united-states/ca/los-angeles/2020-09-09/visualisations/listings.csv")

df = get_airbnb_data()
df['number_of_reviews'] = df['number_of_reviews'].astype('int64')
st.title("IDS HW3")
st.header("Dataset")
st.subheader("Airbnb LA Dataset Overview")
st.markdown("In this project, we are going to use the Airbnb dataset containing information of LA listings from .")
st.markdown("Let's first take a look at the first few records of the dataset to get an overview.")
st.dataframe(df.head())

if st.checkbox('Show the whole dataset (There are 31536 rows, so it may take a while to run)'):
    st.dataframe(df)
    
st.subheader("Selecting the most useful features")
st.write(f"Out of all 16 features, the following ones are the most informative and useful features for our exploration tasks. Users could also add/delete features according to their needs. We will display the first 10 rows in our dataset.")
cols_ofinterest = ["neighbourhood", "neighbourhood_group", "room_type", "price", "number_of_reviews", "availability_365", "reviews_per_month", "minimum_nights", 'calculated_host_listings_count', 'latitude', 'longitude']
cols = st.multiselect("Columns", df.columns.tolist(), default=cols_ofinterest)
st.dataframe(df[cols].head(10))
df = df[cols]

st.header("Discoveries and Insights")
st.subheader("What is the distribution of price?")
st.write("Let's first take a look at the distribution of the main variable of our interest -- price. By looking at the distribution of price, one could gain a sense of the general price level of the LA listings. Users could also select a custom range using the sidebar ('Price range') on the left to adjust the histogram below. The default range we set is from $0 to $200. ")
price_range = st.sidebar.slider("Price range", float(df.price.min()), float(df.price.clip(upper=1000.).max()), (0., 200.))
min_hist_value_price = price_range[0]
max_hist_value_price = price_range[1]
f = px.histogram(df.query('price <= @max_hist_value_price and price >= @min_hist_value_price'), x="price", nbins=15, title="Price distribution")
f.update_xaxes(title="Price")
f.update_yaxes(title="# of listings")
st.plotly_chart(f)


st.subheader("What is the distribution of number of reviews?")
st.write("Then let's take a look at the distribution of the number_of_reviews variable. Usually the more reviews a listing has, the more legit/popular is the listing. Users could also select a custom range using the sidebar ('Number of reviews range') on the left to adjust the histogram below. The default range we set is from 0 to 40. ")
review_range = st.sidebar.slider("Number of reviews range", int(df.number_of_reviews.min()), int(df.number_of_reviews.clip(upper=100).max()), (0, 40))
min_hist_value_numreviews = review_range[0]
max_hist_value_numreviews = review_range[1]
f = px.histogram(df.query('number_of_reviews <= @max_hist_value_numreviews and number_of_reviews >= @min_hist_value_numreviews'), x="number_of_reviews", nbins=15, title="Number of reviews distribution")
f.update_xaxes(title="Number of reviews")
f.update_yaxes(title="# of listings")
st.plotly_chart(f)

st.subheader("What is the distribution of room type?")
st.write("Then let's take a look at the distribution of room types using a pie chart.")
df_room = df.groupby('room_type').count().reset_index()
f = px.pie(df, values=df_room['price'], names= df_room['room_type'], title="Pie Chart of Room Type", color = df_room['room_type'])
f.update_xaxes(title="Room Type")
f.update_yaxes(title="#. of listings")
st.plotly_chart(f)
st.markdown("We can see that entire home/apt and private room constitute the majority of all the listings.")

st.subheader("Filter properties using number of reviews")
st.write("We added an interative table below to enable users to set a range using the sideboxs to view the properties whose number of reviews fall in that range. The table below shows the top 100 properties and you can click the checkbox below to get all properties in that number of reviews range. The default values we set for the lower bound and the upper bound are 10 and 15 respectively. The listings displayed are sorted in descending order by number of reviews. ")
numreview_min = st.sidebar.number_input("number of reviews lower bound", min_value=0, value = 10)
numreview_max = st.sidebar.number_input("number of reviews upper bound", min_value=0, value = 15)
if numreview_min > numreview_max:
    st.error("This is not a valid range")
else:
    df.query("@numreview_min<=number_of_reviews<=@numreview_max").sort_values("number_of_reviews", ascending=False)\
        .head(100)[["neighbourhood", "neighbourhood_group", "room_type", "price", "number_of_reviews", "availability_365", "reviews_per_month", "minimum_nights", 'calculated_host_listings_count']]
    if st.checkbox('Click to show the whole list of properties with number of reviews in that range'):
        df.query("@numreview_min<=number_of_reviews<=@numreview_max").sort_values("number_of_reviews", ascending=False)[["neighbourhood", "neighbourhood_group", "room_type", "price", "number_of_reviews", "availability_365", "reviews_per_month", "minimum_nights", 'calculated_host_listings_count']]

st.subheader("Filter properties using price")
st.write("We added an interative table below to enable users to set a range using the sideboxs to view the properties whose prices fall in that range. The table below shows the top 100 properties and you can click the checkbox below to get all properties in that price range. The default values we set for the lower bound and the upper bound are $50 and $200 respectively. The listings displayed are sorted in ascending order by price.")
price_min = st.sidebar.number_input("price lower bound", min_value=0, value = 50)
price_max = st.sidebar.number_input("price upper bound", min_value=0, value = 200)
if price_min > price_max:
    st.error("This is not a valid range")
else:
    df.query("@price_min<=price<=@price_max").sort_values("price", ascending=True)\
        .head(100)[["neighbourhood", "neighbourhood_group", "room_type", "price", "number_of_reviews", "availability_365", "reviews_per_month", "minimum_nights", 'calculated_host_listings_count']]
    if st.checkbox('Click to show the whole list of properties with price in that range'):
        df.query("@price_min<=price<=@price_max").sort_values("price", ascending=True)\
        [["neighbourhood", "neighbourhood_group", "room_type", "price", "number_of_reviews", "availability_365", "reviews_per_month", "minimum_nights", 'calculated_host_listings_count']]


st.subheader("What is the average listing price of each neighbourhood?")
st.markdown("If users would like to get a sense of the average listing prices by neighborhood, they could check the checkbox below.")
if st.checkbox('Show the whole list of average listing prices by neighbourhood'):
    st.table(df.groupby("neighbourhood").price.mean().reset_index()\
        .round(2).sort_values("price", ascending=False)\
        .assign(avg_price=lambda x: x.pop("price").apply(lambda y: "%.2f" % y)))

st.markdown("The following table displays the average prices of the top 5 most expensive neighbourhoods")
st.table(df.groupby("neighbourhood").price.mean().reset_index()\
        .round(2).sort_values("price", ascending=False).head(5))

st.markdown("Following are the average prices of the top 5 cheapest neighbourhoods")
st.table(df.groupby("neighbourhood").price.mean().reset_index()\
        .round(2).sort_values("price", ascending = True).head(5))

st.subheader("what is the average listing price for each room type?")
st.table(df.groupby("room_type").price.mean().reset_index()\
    .round(2).sort_values("price", ascending=False)\
    .assign(avg_price=lambda x: x.pop("price").apply(lambda y: "%.2f" % y)))

f = px.bar(df.groupby(["room_type"]).price.mean().reset_index(), x="room_type", y='price', title="Price of each room type for Airbnb listings in LA", color = 'room_type')
f.update_xaxes(title="Room Type")
f.update_yaxes(title="Price")
st.plotly_chart(f)

st.markdown("We can see from the table and bar plot above that entire home/apt has the highest average price and shared room has the lowest average price.")

st.subheader("Where are the most expensive properties located in LA?")
st.markdown("The following map shows the most expensive Airbnbs with prices at $800 and above.")
st.map(df.query("price>=800")[["latitude", "longitude"]].dropna(how="any"),)
st.markdown("From the map, we can see that expensive properties are mainly concentrated at West Hollywood and Beverly Hills while some of them are scattered around the coastline.")
st.markdown("Following are the top five most expensive Airbnb listings in LA.")
st.write(df.query("price>=800").sort_values("price", ascending=False).head())
st.markdown("We can notice that the top 5 most expensive listings are all entire home/apartment, which is the room type with the highest average price (shown previously).")

st.subheader("Where are the cheapest properties located in LA?")
st.markdown("The following map shows the cheapest Airbnbs priced at $50 and below.")
st.map(df.query("price<=50")[["latitude", "longitude"]].dropna(how="any"))
st.markdown("From the map, we can see that cheap properties are roughly evenly distributed in all locations in LA, while some of them belong to Santa Clarita and Palmdale.")
st.markdown("Following are the top five cheapest Airbnb listings in LA.")
st.write(df.query("price<=50").sort_values("price", ascending=True).head())
st.markdown("From the table above, an interesting thing to notice is that all of the five listings are priced at $0 and they all don't have any reviews, indicating that either the data displayed above are inaccurate or those properties are not very legit.")

st.subheader("Where are the most popular properties located in LA?")
st.markdown("The following map shows the most popular Airbnbs with number of reviews at 100 and above.")
st.map(df.query("number_of_reviews>=100")[["latitude", "longitude"]].dropna(how="any"),)
st.markdown("Following are the top five most popular Airbnb listings in LA.")
st.write(df.query("number_of_reviews>=100").sort_values("price", ascending=False).head())

st.subheader("Where are the least popular properties located in LA?")
st.markdown("The following map shows the most least popular Airbnbs with number of reviews at 5 and below.")
st.map(df.query("number_of_reviews<=5")[["latitude", "longitude"]].dropna(how="any"),)
st.markdown("Following are the top five least popular Airbnb listings in LA.")
st.write(df.query("number_of_reviews<=5").sort_values("price", ascending=False).head())

st.markdown("From the two maps above, we can see that the distribution of the most popular properties on map is similar to that of the most expensive properties. Also, the distribution of the least popular properties on map is similar to that of the cheapest properties. This indicates that it is likely that price is positively associated with number of reviews.")

df = df.dropna()
X = df[['number_of_reviews', 'availability_365', 'minimum_nights', 'calculated_host_listings_count']]
X = X.apply(pd.to_numeric)
y = df['price']
y = y.apply(pd.to_numeric)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.3, random_state = 0) 
classifier = LinearRegression() 
classifier.fit(X_train, y_train) 
y_pred = classifier.predict(X_test)

def prediction(number_of_reviews, availability_365, minimum_nights, calculated_host_listings_count):      
    prediction = classifier.predict( 
        [[number_of_reviews, availability_365, minimum_nights, calculated_host_listings_count]]) 
    print(prediction) 
    return prediction[0]

st.header("Listing Price Estimation")   
st.markdown("What's shown below is the coolest part of our project! Users could get an estimation of the price after they specify the values for the following numerical features: number of reviews, availability, minimum_nights and host listings count. We leveraged the linear regression model to do the prediction.") 
number_of_reviews = st.text_input("number_of_reviews (number of reviews for this property): ", "Type Here") 
availability_365 = st.text_input("availability_365 (number of available days of this property in one year): ", "Type Here") 
minimum_nights = st.text_input("minimum_nights (minimum number of nights required): ", "Type Here") 
calculated_host_listings_count = st.text_input("calculated_host_listings_count (number of properties this host have on airbnb): ", "Type Here") 
result ="" 

if st.button("Show estimated price"): 
    result = prediction(int(number_of_reviews), int(availability_365), int(minimum_nights), int(calculated_host_listings_count))
    st.success('Based on given information, the estimated price is ${:.2f}.'.format(result))

st.markdown("Now we've reached the end of our project. If you decide to visit LA some day and need information on selecting airbnbs, hopefully our project can be a great help!")
btn = st.button("Thank you:)")
if btn:
    st.balloons()
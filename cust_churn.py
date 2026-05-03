#EDA
import pandas as pd
df = pd.read_csv("customer_shopping_behavior.csv")
#print(df.head)


# Data Cleaning
df['Item Purchased'].unique()
df['Category'].unique()

pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_row', None)

df.groupby('Category')['Item Purchased'].unique()
#mismatch - item purchased in wrong categories
correct_mapping = {
    # Clothing
    "T-shirt": "Clothing", "Shirt": "Clothing", "Shorts": "Clothing",
    "Hoodie": "Clothing", "Pants": "Clothing", "Socks": "Clothing",
    "Jeans": "Clothing", "Blouse": "Clothing", "Skirt": "Clothing",
    "Sweater": "Clothing", "Dress": "Clothing",
    # Accessories
    "Sunglasses": "Accessories", "Gloves": "Accessories",
    "Jewelry": "Accessories", "Hat": "Accessories",
    "Handbag": "Accessories", "Backpack": "Accessories",
    "Belt": "Accessories", "Scarf": "Accessories",
    "Bag": "Accessories",
    # Electronics
    "Laptop": "Electronics", "Phone": "Electronics",
    "Headphones": "Electronics", "Watch": "Electronics",
    # Footwear
    "Shoes": "Footwear", "Sandals": "Footwear",
    "Sneakers": "Footwear", "Boots": "Footwear",
    # Outerwear
    "Coat": "Outerwear", "Jacket": "Outerwear"
}
df['Category'] = df["Item Purchased"].map(correct_mapping)
df.groupby('Category')['Item Purchased'].unique()

## Treating null values
#size
df['Size'].unique()
df.groupby('Category')['Size'].unique()

df.loc[df['Category']=='Electronics', 'Size'] = "Not Applicable"
df.loc[df['Category']=='Accessories', 'Size'] = "Free Size"
df.loc[df['Category']=='Footwear', 'Size'] = "Not Available"
df.loc[(df["Category"]=='Clothing') & (df['Size'].isnull()), "Size"] = df[df["Category"]== "Clothing"]["Size"].mode()[0] 

df.groupby('Category')['Size'].unique()

#Review Ratings
df['Review Rating'].mean() #3.668195100022477
df['Review Rating'].median() #3.7
df['Review Rating'].mode() #4.0
df.groupby("Item Purchased")["Review Rating"].mean()

#Filling the null values of Review Rating with the m mean of each items

df["Review Rating"] = df["Review Rating"].fillna(df.groupby("Item Purchased")["Review Rating"].transform('mean'))
df.groupby('Category')['Review Rating'].unique()
df['Review Rating'] = df["Review Rating"].round(2)
df.groupby('Category')['Review Rating'].unique()

# Previous Purchase
#replace na of this col with 0 as the customer would have not purchased anything prior to this purchase
df['Previous Purchases'] = df['Previous Purchases'].fillna(0)
df.isnull().sum()

#Purchase Amount (USD)
#replace null val with mean
df.groupby("Item Purchased")["Purchase Amount (USD)"].mean()
df['Purchase Amount (USD)'] = df['Purchase Amount (USD)'].fillna(df.groupby('Item Purchased')['Purchase Amount (USD)'].transform("mean"))
df.isnull().sum()

## CHECKIG DUPLICATES
df.duplicated().sum() #50
len(df)
df = df.drop_duplicates(subset=['Customer ID'], keep='first')
len(df)
df.duplicated().sum()

## Renaming Headers
df.columns = df.columns.str.replace(" ", "_")
df.columns = df.columns.str.lower()
df = df.rename(columns={"purchase_amount_(usd)" : "purchased_amount"})
#print(df.columns)


## Connecting with MYSQL
import mysql.connector
from mysql.connector import Error

username = "root"          
password = "root123" 
host = "localhost"         
port = "3306"              
database = "data_analysis_project"

try:
    connection = mysql.connector.connect(
        host=host,
        user=username,
        password=password,
        database=database,
        port=port
    )
    
    if connection.is_connected():
        print("Successfully connected to MySQL!")
        
        create_table_query = """
        CREATE TABLE IF NOT EXISTS customer_churn (
            customer_id INT PRIMARY KEY,
            age INT,
            gender VARCHAR(10),
            item_purchased VARCHAR(255),
            category VARCHAR(255),
            purchased_amount DECIMAL(10,2),
            location VARCHAR(255),
            size VARCHAR(50),
            color VARCHAR(50),
            season VARCHAR(50),
            review_rating DECIMAL(3,2),
            subscription_status VARCHAR(20),
            shipping_type VARCHAR(50),
            discount_applied VARCHAR(10),
            previous_purchases INT,
            payment_method VARCHAR(50),
            frequency_of_purchases VARCHAR(50)
        )
        """
        
        cursor = connection.cursor()
        cursor.execute(create_table_query)
        cursor.execute("DELETE FROM customer_churn")
        # Insert data
        for index, row in df.iterrows():
            insert_query = """
            INSERT INTO customer_churn 
            (customer_id, age, gender, item_purchased, category, purchased_amount, location, size, color, season, review_rating, subscription_status, shipping_type, discount_applied, previous_purchases, payment_method, frequency_of_purchases) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, tuple(row))
        
        connection.commit()
        print("Data inserted successfully!")
        query = "SELECT * FROM customer_churn LIMIT 5"
        df_sql = pd.read_sql("SELECT * FROM customer_churn LIMIT 5", connection)
        print(df_sql)
        
except Error as e:
    print(f"Error: {e}")
finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("MySQL connection closed.")


import sys
import pandas as pd
from sqlalchemy import create_engine

def load_data(messages_filepath, categories_filepath):
    """
    Load and merge the messages and categories datasets.
    
    Args:
        messages_filepath (str): Filepath for the messages dataset.
        categories_filepath (str): Filepath for the categories dataset.
    
    Returns:
        df (DataFrame): Merged dataframe of messages and categories.
    """
    messages = pd.read_csv(messages_filepath)
    categories = pd.read_csv(categories_filepath)
    
    # Merge datasets
    df = messages.merge(categories, how="inner", on="id")
    return df


def clean_data(df):
    """
    Clean and preprocess the data by splitting categories into separate columns,
    converting values to numeric, and concatenating the cleaned categories with 
    the original dataframe.

    Args:
    df (pandas.DataFrame): The input dataframe containing the merged df from load_data
                            function with 'categories' column.

    Returns:
    pandas.DataFrame: The cleaned dataframe with separate category columns with
                        respective values.

    """
    # Split categories into separate category columns
    categories = df["categories"].str.split(";", expand=True)
    row = categories.iloc[0]
    category_colnames = row.apply(lambda x: x.split("-")[0])
    
    # Rename the columns of `categories`
    categories.columns = category_colnames

    for column in categories:
        # Set each value to be the last character of the string
        categories[column] = categories[column].str[-1]
    
        # Convert column from string to numeric
        categories[column] = categories[column].astype("int")

    # Drop the original categories column from `df`
    df.drop(['categories'], axis=1, inplace=True)
    
    # Concatenate the original dataframe with the new `categories` dataframe
    df = pd.concat([df, categories], axis=1, join="inner")

    # Drop duplicates
    df.drop_duplicates(inplace=True)

    return df

def save_data(df, database_filename):
    """
    Save the clean dataset into an sqlite database.

    Inputs:
        - df : DataFrame to write
        - database_filename: InsertDatabaseName.db
    
    Output: 
        - SQL Database file based on given database_filename parameter 
    """
    engine = create_engine(f'sqlite:///{database_filename}.db')
    df.to_sql("Message", 
          engine, 
          index=False, 
          if_exists='replace')

def main():
    if len(sys.argv) == 4:

        messages_filepath, categories_filepath, database_filepath = sys.argv[1:]

        print('Loading data...\n    MESSAGES: {}\n    CATEGORIES: {}'
              .format(messages_filepath, categories_filepath))
        df = load_data(messages_filepath, categories_filepath)

        print('Cleaning data...')
        df = clean_data(df)
        
        print('Saving data...\n    DATABASE: {}'.format(database_filepath))
        save_data(df, database_filepath)
        
        print('Cleaned data saved to database!')
    
    else:
        print('Please provide the filepaths of the messages and categories '\
              'datasets as the first and second argument respectively, as '\
              'well as the filepath of the database to save the cleaned data '\
              'to as the third argument. \n\nExample: python process_data.py '\
              'disaster_messages.csv disaster_categories.csv '\
              'DisasterResponse.db')


if __name__ == '__main__':
    main()
"""
Analyses whether C40 cities have peaked their emissions. 
"""

__author__ = 'Oliver Wills'
__contact__ = 'owills@c40.org'
__year__ = '2019'
__application__ = 'Peaking Analysis'

#Python libararies
import pandas as pd
import numpy as np
import simplejson
from datetime import date
import os

#Set display options
pd.options.mode.chained_assignment = None  # default='warn'
pd.options.display.float_format = '{:.1f}'.format

def read_in_data_from_master_emissions_tracker(path,former_c40_cities):
    """
    Reads in data from 2017 peaking analysis and reshapes for use in programme.
    INPUT: Excel file (.xlsx)
    OUTPUT: Pandas DataFrame
    """
    #Read in data
    df = pd.read_excel(path, sheet_name='All raw GHG_(excl.C40 GPC data)',header = 1) 
    #Tidy column names
    df = df[['City name tidy up','Source_Protocol','Inventory\n_year.1', 'Emissions\n_mtCO2e','Use in peaking (Yes or No)']] #***
    df.rename(columns={'City name tidy up':'City', 
                       'Source_Protocol':'Data source',
                       'Inventory\n_year.1':'Year',
                       'Emissions\n_mtCO2e':'Emissions',
                       'Use in peaking (Yes or No)':'Use in dashboard (Yes or No)'},inplace = True) #***
    #Filter dataframe for valid rows
    df['Emissions'].fillna(0, inplace = True) #Fill rows with missing emissions data
    df = df[['City','Data source','Year','Emissions','Use in dashboard (Yes or No)']]
    df = df[(~df.iloc[:,0].isin(former_c40_cities)) & (df.iloc[:,2]!= 0) & (df.iloc[:,4].isin(['Yes','yes','Y','y']))]

    def map_data_sources_to_data_quality_scores(x):
        '''Maps data to data quality scores. Returns 100 if no match found'''
        d = {'C40_GPC':1,'City_GPC':2,'CDP_GPC':3,'Target_Other':5,'City_Other':6,'CDP_Other':7}
        try:
            return d[x]
        except:
            return 100
        
    df['Data quality'] = df['Data source'].apply(map_data_sources_to_data_quality_scores)
    df = df[df['Data quality']!=100]
    df = df[['City','Data source','Data quality','Year','Emissions']]
    df = df.sort_values(['City','Year']).reset_index(drop=True)
    return df 

def combine_gpc_and_non_gpc_data_sources(df,base_year,current_year):
    """
    Calculates All GPC Considered and All non-GPC considered rows by combining data sources for each city. Function 
    constructs All GPC Considered rows by backfilling data gaps in C40 GPC data sources with CDP GPC and City GPC data.
    Function constructuct All Non GPC Considered rows by backfilling data gaps in C40 Target Baseline Other data sources
    with CDP Other and City Other. 
    INPUT: Master DataFrame with GPC Tracker and Master GHG data
    OUTPUT: DataFrame with additional All GPC Considered and All non-GPC considered rows
    """
    def reshape_data(df):
        """
        Reshapes DataFrame so that each city and datasource has a unique row with years as a column header. Also 
        adds in empty columsn for missing years to be modelled. 
        INPUT: DataFrame
        OUTPUT: Reshaped DataFrame
        """
        df = df.pivot_table(values='Emissions', index=['City','Data source','Data quality'], columns='Year', aggfunc='first').reset_index() #***
        
        for year in range(base_year,current_year + 1,1):
            if year not in df.columns:
                df[float(year)] = np.nan
        
        df.columns.name = None #set column index name to none 
        return df
        
    def calculate_gpc_and_non_gpc_combinations(df):

        df = df.sort_values(['City','Data source'], ascending = [True, True]).reset_index(drop=True)
    
        #Create 3 dataframes for GPC, non-GPC data and all GPC data
        df1 = df[df['Data quality'] <= 3]
        df2 = df[df['Data quality'] >= 4]
        
        #Create variable for columns with emissions data 
        cols = df.columns.difference(['City','Data source','Data quality'])
        
        def combine_rows_for_each_city(df, cols, rows):
            #Select rows where there is at least 1 city
            df = df.groupby('City').filter(lambda x: len(x) > 1) 
            
            for col in cols:
                df[col] = df.groupby(['City'], sort=False)[col].apply(lambda x: x.fillna(method='bfill'))
            df = df.drop_duplicates(subset='City', keep="first")

            if rows == 'all_gpc':
                df['Data quality'] = 4
                df['Data source'] = 'All GPC considered'
            if rows == 'all_non_gpc':
                df['Data quality'] = 8
                df['Data source'] = 'All non GPC considered'
            if rows == 'all_non_gpc_and_all_gpc':
                df['Data quality'] = 9
                df['Data source'] = 'All GPC and non GPC considered'
            return df

        df_all_gpc_considered = combine_rows_for_each_city(df1,cols,'all_gpc')
        df_all_non_gpc_considered = combine_rows_for_each_city(df2,cols,'all_non_gpc')

        #Combine dataframes into a master dataset
        df = df.append([df_all_gpc_considered,
                        df_all_non_gpc_considered]).reset_index(drop=True)
                        #df_all_non_gpc_and_gpc_considered]).reset_index(drop=True)
        
        df = df.sort_values(['City','Data quality'], ascending = [True,True])
        df.fillna(0, inplace=True) 
        return df
    
    df = reshape_data(df)
    df = calculate_gpc_and_non_gpc_combinations(df)    
    return df

def calculate_peak_emissions(df, current_year):
    """
    Analyses city GHG emissions to determine if they have peaked
    INPUT: DataFrame containing peaking analysis and GPC Tracker GHG emissions
    OUTPUT: DataFrame with assessment of whether each city has peaked
    """
    def calculate_peaking_parameters(df):
        """
        Caclulate parameters used to assess whether city has peaked emissions
        INPUT: DataFrame
        OUTPUT: DataFrame with peakign parameters as 4 additional columns
        """
        #***cols = df.columns.difference(['City','Data Source','Protocol','Verified by city'])
        cols = df.columns.difference(['City','Data source','Data quality'])
        df['Num data points'] = df[cols].gt(0).sum(axis=1)
        df['Max emissions'] = df[cols].max(axis =1)
        df['Max emissions year'] = df[cols].idxmax(axis =1)
        df['Recent emissions'] = df[cols].apply(lambda x: x.iloc[x.to_numpy().nonzero()].iloc[-1], axis=1)
        df['Recent emissions year'] = df[cols].apply(lambda x: x.iloc[x.to_numpy().nonzero()].index[-1], axis=1)
        df['Earliest emissions'] = df[cols].apply(lambda x: x.iloc[x.to_numpy().nonzero()].iloc[0], axis=1)
        df['Earliest emissions year'] = df[cols].apply(lambda x: x.iloc[x.to_numpy().nonzero()].index[0], axis=1)
        
        for col in ['Max emissions year','Recent emissions year','Earliest emissions year']:
            df[col] = pd.to_numeric(df[col],downcast='float',errors="coerce") 
            
        return df
    
    def apply_peaking_criteria(df, current_year):
        """
        Calculates peaking criteria using peaking parameters
        INPUT: DataFrame
        OUTPUT: DataFrame with Boolean assessment for each peaking criteria
        """
        #Peaking Criteria 1: At least 3 years of data available?
        df['PC1'] = (df['Num data points'] >= 3)
        #Peaking Criteria 2: Max emissions >5 years before recent inventory?
        df['PC2'] = (df['Recent emissions year'] - df['Max emissions year'] >= 5)
        #Peaking Criteria 3: Recent inventory < 5 years old
        df['PC3'] = (current_year - df['Recent emissions year'] <= 5)
        #Peaking Criteria 4: Max emissions >10% higher than recent inventory
        df['PC4'] = ((df['Max emissions']-df['Recent emissions'])/df['Max emissions']) >= 0.1        
        #Percentage change since peak
        df['Percentage change since peak (%)'] = ((df['Recent emissions']-df['Max emissions'])/df['Max emissions'])*100
        return df
    
    def calculate_peak_emissions_status(df):
        """
        Analyses peaking criteria to assess whether city has peaked
        INPUT: DataFrame
        OUTPUT: DataFrame with peaking assessment as additional columne
        """
        
        def evaluate_peaking_criteria(x):
            
            if x['PC1'] & x['PC2'] & x['PC3'] & x['PC4']: #If all peaking criteria are TRUE returns 'PEAKED'
                return 'Peaked'
            elif x['PC1'] & x['PC3'] & (not x['PC4']): #If first 3 peaking critiera are TRUE and PC4 are FALSE return 'NOT PEAKED'
                return 'Not Peaked'
            else: #Otherwise returns 'Unkown'
                return 'Unknown'
            
        #Calculates columns by applying above function across rows 
        df['Peak Status'] = df.apply(evaluate_peaking_criteria, axis = 1)
        return df 
    
    def rename_columns(df):
        """
        Rename columns for ease of understanding
        """
        df.rename(columns ={
            'PC1':'PC1: At least 3 year of data available',
            'PC2':'PC2: Max emissions >5 years before recent inventory',
            'PC3':'PC3: Recent inventory <5 years old',
            'PC4':'PC4: Max emissions <10% higher than recent inventory'},
            inplace = True)
        return df 
  
    df = calculate_peaking_parameters(df)
    df = apply_peaking_criteria(df, current_year)
    df = calculate_peak_emissions_status(df)
    df = rename_columns(df)
    return df
    
def select_cities_to_use_in_dashboard(df):
    """
    Selects data sources to use in dashboard for each city
    INPUT: DataFrame 
    OUTPUT: DataFrame with sorted cities containing NO duplicates for use in peaking analysis dashboard 
    """    
    def select_cities(df):
        """
        Selects initial datasources by ordering Fataframe by City, Verfiedy by City and Data Source columns and 
        selecting the first instance of PEAKED, NOT PEAKED or UNKNOWN depending on  conditions which count the 
        number of peak statuses for each city.
        INPUT: DataFrame
        OUTPUT: DataFrame with additional column identifying which record to use for each city 
        """
        #Create copy of dataframe and order by city and num data points 

        df = df.sort_values(['City','Data quality']).reset_index(drop=True)
        df1 = df.copy()
            
        for city, group in df1.groupby('City'):
            
            try: n_peaked = group['Peak Status'].value_counts()['Peaked']
            except: n_peaked = 0
                
            try: n_not_peaked = group['Peak Status'].value_counts()['Not Peaked']
            except: n_not_peaked = 0
                
            try: unknown = group['Peak Status'].value_counts()['Unknown']
            except: unknown = 0
                
            if n_peaked > 0 and n_peaked >= n_not_peaked:
                selected_index = group[group['Peak Status']=='Peaked'].index[0]

            elif n_not_peaked > 0 and n_not_peaked > n_peaked:
                selected_index = group[group['Peak Status']=='Not Peaked'].index[0]

            else:
                selected_index = group[group['Peak Status']=='Unknown'].sort_values('Num data points',ascending=False).index[0]
                
            df.loc[selected_index,'Use for dashboard?'] = 'yes'

        df['Use for dashboard?'].fillna('no', inplace = True)
        return df
    
    def read_in_cities_that_have_peaked():
        df_temp = pd.read_sql_table(table_name='city_peak_emissions',schema='city_data',con=database.connect_to_database())
        cities = dict(zip(list(df_temp['c40_city_name']),list(df_temp['data_source'])))
        n = len(cities.keys())
        return cities, n
    
    def check_emissions_status_of_cities_that_have_peaked(cities, df):
        """
        Checks whether cities that have previously peaked are shown as having peaked. If not, and if PC4 is still
        True, the emissions status is set to PEAKED. 
        INPUT: Dictionary of cities and data sources
        OUTPUT: DataFrame
        """
        for city, data_source in cities.items():
            try:
                current_status = df[(df['City']==city) & (df['Use for dashboard?']=='yes')]['Peak Status'].values[0]
                current_index = df[(df['City']==city) & (df['Use for dashboard?']=='yes')]['Peak Status'].index[0]
                if current_status != 'Peaked':
                    peak_index = df[(df['City']==city) & (df['Data source'] == data_source)].index[0]
                    if df.loc[peak_index, 'Percentage change since peak (%)']<=5.0:
                        df.loc[peak_index, 'Peak Status'] = 'Peaked'
                        if peak_index != current_index:
                            df.loc[peak_index, 'Use for dashboard?'] = 'yes'
                            df.loc[current_index, 'Use for dashboard?'] = 'no'
                    else:
                        df.loc[peak_index, 'Peak Status'] = 'Peak Reversed'
                        
            except:
                continue
        return df
    
    def count_cities_that_have_peaked(df, cities,n): # removed cities that have already peaked
        """
        Updates text file with dictionary of cities and data sources that have peaked
        INPUT: DataFrame
        OUTPUT: Dictionary written to text file
        """
        df = df[(df['Use for dashboard?'] == 'yes')&(df['Peak Status']=='Peaked')]
        if len(df) > n:
            print('New cities have peaked!')
            for city in list(df['City'].unique()):
                if city not in cities.keys():
                    print(city)
        else:
            print('No new cities have peaked')

    df = select_cities(df)
    cities, n = read_in_cities_that_have_peaked()
    df = check_emissions_status_of_cities_that_have_peaked(cities, df)
    count_cities_that_have_peaked(df, cities,n)
    return df

def reshape_data_for_dashboard(df):
    """
    Reshapes data for use in dashboard
    INPUT: DataFrame (Years as rows)
    OUTPUT: DataFrame (Years as column)
    """
    cols = df.columns.difference(['Verified by city','Num data points', 'Max emissions', 'Recent emissions',
                                  'Earliest emissions', 'Earliest emissions year',
                                  'Recent emissions year', 'PC1: At least 3 year of data available', 
                                  'PC2: Max emissions >5 years before recent inventory', 
                                  'PC3: Recent inventory <5 years old', 
                                  'PC4: Max emissions <10% higher than recent inventory',
                                  'Percentage change since peak (%)',
                                  'Kaya identity used?','Num modelled data points'])
    df = df[cols] 
    df = pd.melt(df, id_vars=["City", "Data source", "Data quality","Peak Status", "Max emissions year","Use for dashboard?"], var_name="Year", value_name="Emissions").sort_values(['City', 'Year']).reset_index(drop=True)
    df['Peak year'] = df.apply(lambda x : 1 if x['Max emissions year'] == x['Year'] and x['Peak Status'] == 'Peaked' else 0, axis=1)
    df.drop('Max emissions year', axis = 1, inplace = True)
    
    df1 = df.copy()
    df2 = df.copy()
    
    df1 = df1[df1['Use for dashboard?'] == 'yes']
    df1 = df1.drop('Use for dashboard?',axis=1)
    
    return df1, df2


def run_etl_pipeline(path, current_year, base_year, former_c40_cities):
    """
    Generates DataFrames used in the programme by calling above functions
    INPUT: File paths to 2017 Peaking Analysis and GPC Tracker
    OUTPUT: Tuple of 6 DataFrames
    """
    print('F1')
    df1 = read_in_data_from_master_emissions_tracker(path, former_c40_cities)
    print('F2')
    df2 = combine_gpc_and_non_gpc_data_sources(df1,base_year,current_year)
    print('F3')
    df3 = calculate_peak_emissions(df2,current_year)
    print('F4')
    df4 = select_cities_to_use_in_dashboard(df3)
    print('F5')
    df5, df6 = reshape_data_for_dashboard(df4)
    return (df1, df2, df3, df4, df5, df6) 

def write_to_excel(results,target_path):
    """
    Writes dataframes to Excel
    INPUT: Tuple of 6 DataFrames
    OUTPUT: None
    """
    #Create a Pandas Excel writer using XlsxWriter as the engine
    writer = pd.ExcelWriter(target_path, engine='xlsxwriter')
    results[3].to_excel(writer, sheet_name='MASTER_Emissions', index = False)
    results[5].to_excel(writer, sheet_name='PEAKING_Emissions', index = False)
    writer.save()

def main():
    current_year = date.today().year
    base_year = 1990
    path = '~/Box/C40 (internal)/M&P (internal)/04_Analytics/00_Raw data/01_Emissions/Live tracker/01_GHG Master Tracker.xlsx'
    date_string = str(date.today().day) + '_' + str(date.today().month) + '_' + str(date.today().year)
    target_path = os.path.join('/data/peaking_analysis/peaking_analysis_{}.xlsx'.format(date_string))
    former_c40_cities = ['Basel','Caracas']
    results = run_etl_pipeline(path, current_year, base_year, former_c40_cities)
    write_to_excel(results, target_path)
    print('Check output file')

if __name__ == "__main__":
    main()
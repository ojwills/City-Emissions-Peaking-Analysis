#!/Users/oliverwills/anaconda3/bin/python3
import pandas as pd
import numpy as np
import datetime
pd.options.display.float_format = '{:.2f}'.format
pd.set_option('display.max_columns', 500)
pd.options.mode.chained_assignment = None  

def read_in_data_from_gpc_tracker(path, regions):
    df = pd.read_excel(path, sheet_name = 'GPC data_Live', header = 2)
    df = df[['Use for GPC Dashboard?', 'City', 'Year_calendar', 'Population','BASIC', 'BASIC Stationary', 'BASIC Transport', 'BASIC Waste']].sort_values(['City','Year_calendar'])
    df = df[df['Use for GPC Dashboard?'] == 'Yes'].reset_index(drop=True)
    df.rename(columns={'Year_calendar': 'Year', 'BASIC':'Total', 'BASIC Stationary':'Stationary', 'BASIC Transport':'Transport', 'BASIC Waste': 'Waste'}, inplace=True)
    df.drop('Use for GPC Dashboard?', axis = 1, inplace = True)
    df = map_gpc_regions_to_funder_regions(df, regions)
    return df

def read_in_d2020_targets(path, regions):
    df = pd.read_excel(path)
    df = df[['City Name', 'Region', 'D2020_2030 target emissions (tCO2e)','D2020_2030 target emissions (tCO2e per capita)']]
    df = df.rename(columns = {'City Name':'City'})
    df.dropna(inplace = True) #drop cities that don't yet have targets
    df = map_gpc_regions_to_funder_regions(df, regions)
    return df

def map_gpc_regions_to_funder_regions(df, regions):
    
    def categorise_regions(x):
        for key, value in regions.items():
            for city in value:
                if city == x:
                    return key

    df['Region'] = df['City'].apply(categorise_regions)
    
    return df

def calculate_recent_emissions(df):
    year_maxes = df.groupby(['City']).Year.transform(max)
    df = df.loc[df.Year == year_maxes].reset_index(drop=True)
    return df

def calculate_baseline_emissions(df, baseline_year):
    df = df[df['Year']<= baseline_year] 
    year_maxes = df.groupby(['City']).Year.transform(max) 
    df = df.loc[df.Year == year_maxes] 
    df['Baseline'] = baseline_year
    return df

def calculate_percentage_change_in_emissions(df1, df2, baseline_year):
    
    #Merge dataframes and exclude years where no datapoints since baseline
    df = pd.merge(df1, df2, on=['City'], suffixes = ['_' + str(baseline_year), '_recent']) #merge recent and baseline emissions
    df = df[df['Year_recent'] > baseline_year] 
    base = str(baseline_year) 
    
    #Calculate percentage changes
    df['Stationary_Percentage_Change'] = (df['Stationary_recent'] - df['Stationary_'+ base])/df['Stationary_' + base]
    df['Transport_Percentage_Change'] = (df['Transport_recent'] - df['Transport_'+ base])/df['Transport_'+ base]
    df['Waste_Percentage_Change'] = (df['Waste_recent'] - df['Waste_' + base])/df['Waste_' + base]
    df['Total_Percentage_Change'] = (df['Total_recent'] - df['Total_' + base])/df['Total_' + base]
    
    #Rename and reshape dataframe for presentatiom purposes
    df = df.rename(columns={'Year_recent':'Recent inventory year','Stationary_Percentage_Change': 'Stationary', 'Transport_Percentage_Change': 'Transport', 'Waste_Percentage_Change':'Waste', 'Total_Percentage_Change':'Total', ('Region_' + base):'Region'})
    df = pd.melt(df[['City', 'Region', 'Baseline','Recent inventory year','Stationary','Transport','Waste','Total']], id_vars=["City", "Region", "Baseline",'Recent inventory year'], var_name="Sector", value_name="Percentage change in emissions since baseline")
    df = df.sort_values(by = 'City', ascending = True).reset_index(drop=True)
    
    return df  

def calculate_emissions_variance_with_d2020_targets(df1, df2):
    df = pd.merge(df1, df2, on=['City'], suffixes = ['_recent', '_D2020']) #join with recent_emissions
    df['Emissions per capita (tCO2e per capita)'] = df['Total']/df['Population']
    df['Variance 2030 target (tCO2e per capita)'] = df['Emissions per capita (tCO2e per capita)'] - df['D2020_2030 target emissions (tCO2e per capita)']
    df['Variance 2050 target (tCO2e per capita)'] = df['Emissions per capita (tCO2e per capita)']
    df = df[['City','Region_D2020','Year', 'Stationary', 'Transport', 'Waste', 'Total','Emissions per capita (tCO2e per capita)','D2020_2030 target emissions (tCO2e)','D2020_2030 target emissions (tCO2e per capita)', 'Variance 2030 target (tCO2e per capita)', 'Variance 2050 target (tCO2e per capita)']]
    df = df.rename(columns={'Region_D2020':'Region'})
    return df

def reshape_emissions_data_for_dashboard(df, baseline_year):
    df = df.pivot_table(index = ['City', 'Region', 'Baseline', 'Recent inventory year'],columns = 'Sector', values = 'Percentage change in emissions since baseline')
    df['Num cities'] = 1 #add helper column
    df = df.rename(columns={'Stationary': 'Stationary (%)', 'Transport': 'Transport (%)', 'Waste':'Waste (%)', 'Total':'Total (%)'})
    df = df.groupby('Region').agg({'Num cities':'sum','Stationary (%)':'mean', 'Transport (%)':'mean', 'Waste (%)':'mean', 'Total (%)':'mean'})
    df['Baseline'] = baseline_year
    df = df[['Num cities', 'Baseline', 'Stationary (%)', 'Transport (%)', 'Waste (%)', 'Total (%)']]
    df = df.sort_values('Region', ascending = True)
    return df

def reshape_emissions_variance_data_for_dashboard(df):
    df['Num cities'] = 1 #add helper columns
    df = df.groupby('Region').agg({'Num cities':'sum', 'Emissions per capita (tCO2e per capita)':lambda x: np.mean(x),'D2020_2030 target emissions (tCO2e per capita)':lambda x: np.mean(x), 'Variance 2030 target (tCO2e per capita)':lambda x: np.mean(x), 'Variance 2050 target (tCO2e per capita)':lambda x: np.mean(x)})
    df = df.sort_values('Region', ascending = True)
    return df

def generate_dataframes(path_1, path_2, regions, baseline_year_1, baseline_year_2):
    df1 = read_in_data_from_gpc_tracker(path_1, regions)
    df2 = read_in_d2020_targets(path_2, regions)
    df3 = calculate_recent_emissions(df1)
    df4 = calculate_baseline_emissions(df1, baseline_year_1)
    df5 = calculate_baseline_emissions(df1, baseline_year_2)
    df6 = calculate_percentage_change_in_emissions(df4, df3, baseline_year_1)
    df7 = calculate_percentage_change_in_emissions(df5, df3, baseline_year_2)
    df8 = df6.append(df7) #create master dataframe
    df9 = calculate_emissions_variance_with_d2020_targets(df3, df2)
    df10 = reshape_emissions_data_for_dashboard(df6, baseline_year_1)
    df11 = reshape_emissions_data_for_dashboard(df7, baseline_year_2)
    df12 = reshape_emissions_variance_data_for_dashboard(df9)
    return (df3, df8, df9, df10, df11, df12)

def write_to_excel(results):
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter('/Users/oliverwills/desktop/funder_ghg_emissions_dashboard.xlsx', engine='xlsxwriter')
    # Write each dataframe to a different worksheet.
    results[0].to_excel(writer, sheet_name='MASTER_recent_emissions', index = False) 
    results[1].to_excel(writer, sheet_name='MASTER_change_since_baselines', index = False)
    results[2].to_excel(writer, sheet_name='MASTER_variance_against_d2020', index = False)
    results[3].to_excel(writer, sheet_name='SUMMARY_emissions_change_2010')
    results[4].to_excel(writer, sheet_name='SUMMARY_emissions_change_2015')
    results[5].to_excel(writer, sheet_name='SUMMARY_variance_against_d2020')
    #close the Pandas Excel writer and output the Excel file.
    writer.save()

def run_programme(path_1, path_2, regions):
    results = list(generate_dataframes(path_1, path_2, regions, 2010, 2015))
    results[0] = pd.melt(results[0], id_vars = ['City', 'Region', 'Year', 'Population'], var_name = 'Sector',value_name = 'Emissions').drop('Population',axis=1)
    write_to_excel(results)
    return results

#Parameters for use in programme
path_1 = '/Users/oliverwills/Box/C40 (internal)/Regions and Cities (internal)/M&P/04_Analytics/00_Raw data/01_Emissions/Live tracker/01_GPC Inventory Tracker.xlsx'
path_2 = '/Users/oliverwills/Box/C40 (internal)/Regions and Cities (internal)/M&P/04_Analytics/03_Other analytics/02_D2020 targets vs city own targets/D2020 proposed emissions levels for 2030_20180516.xlsx'
regions =  {'Africa':['Tschwane', 'Durban', 'Cape Town', 'Johannesburg', 'Lagos', 'Dar es Salaam', 'Accra'],
      'East, Southeast Asia & Oceania':['Melbourne', 'Sydney', 'Bangkok', 'Yokohama', 'Jakarta', 'Hong Kong', 'Tokyo', 'Auckland', 'Seoul', 'Ho Chi Minh City', 'Hanoi'],
      'Europe':['Venice', 'Heidelberg', 'Amsterdam', 'Warsaw', 'Athens', 'Milan', 'Basel', 'London', 'Rome', 'Madrid', 'Copenhagen', 'Paris', 'Oslo', 'Stockholm', 'Barcelona'],
      'Latin America':['Buenos Aires', 'Mexico City', 'Rio de Janeiro', 'Curitiba', 'Quito', 'Lima', 'Bogota', 'Medellin', 'Salvador', 'Ciudad de México'],
      'North America':['Houston', 'Chicago', 'Philadelphia', 'Washington, DC', 'Austin', 'New Orlans', 'Boston', 'Portland', 'Los Angeles', 'Seattle', 'Toronto', 'San Francisco', 'New York City', 'Montreal', 'Vancouver'],
      'South and West Asia':['Dubai', 'Istanbul', 'Chennai', 'Amman']}

run_programme(path_1, path_2, regions)
datetime.datetime.now()


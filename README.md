# City Emissions Analysis 

### 1) Background
This repository documents the methods and code used by C40 Cities Climate Leadership Group (C40) to determine whether its cities have peaked their greenhouse gas (GHG) emissions. A city is considered to have peaked when there is sufficient evidence to show that its emissions have decreased from a maximum level. This is a critical milestone for cities on the road to achieveing the goals of the Paris Climate Agreement. This repository includes the data collection, analysis and vizualisation methodlogies and scripts as well as links to press releases which announced the results during the 2019 World Mayors Summit.

### 2) Data Collection 
Time series GHG emissions data was collected for each C40 city for the period 1990-2019 by reviewing publicly available emissiosn data. Data sources were ranked using the data quality hierarchy below.

**Table 1: Data Source Hierarchy**

<table style="width:80%">
  <tr>
    <th colspan="2" style="text-align:center">Data source</th>
    <th colspan="1" style="text-align:center">Data quality</th> 
    <th colspan="5" style="text-align:center">Description</th>
  </tr>
  <tr>
    <td colspan="2">C40_GPC</td>
    <td colspan="1" style="text-align:center">1</td>
    <td colspan="5">Global Protocol for Community-Scale (GPC) GHG emissions data reported through CIRIS Inventories reviewed 			  and approved as compliant by C40.</td> 
  </tr>
    <tr>
    <td colspan="2">CDP_GPC</td>
    <td colspan="1" style="text-align:center">2</td>
    <td colspan="5">GPC emissions data submitted by cities through Carbon Disclosure Project (CDP) questionnaires, but not 		        reviewed by C40.</td> 
  </tr> 
  <tr>
    <td colspan="2">City_GPC</td>
    <td colspan="1" style="text-align:center">3</td>
    <td colspan="5">GPC emissions inventories published by cities through their website or elsewhere, for example in climate 			action progress reports, inventory reports or other publications, but not reviewed by CDP or C40.</td> 
  </tr>
  <tr>
    <td colspan="2">All_GPC_considered</td>
    <td colspan="1" style="text-align:center">4</td>
    <td colspan="5">GPC emissions data combined from C40_GPC, CDP_GPC and City_GPC data sources.  Where there were multiple 			data points for the same year priority was given to the GPC record with the highest data quality.</td> 
  </tr>
  <tr>
    <td colspan="2">Target_Other</td>
    <td colspan="1" style="text-align:center">5</td>
    <td colspan="5">Non-GPC emissions reported for city baseline year reduction targets.</td> 
  </tr>
  <tr>
    <td colspan="2">CDP_Other</td>
    <td colspan="1" style="text-align:center">6</td>
    <td colspan="5">Non-GPC emissions reported through CDP (not reviewed by C40).</td> 
  </tr>
  <tr>
    <td colspan="2">City_Other</td>
    <td colspan="1" style="text-align:center">7</td>
    <td colspan="5">Non-GPC emissions data published by cities through their website or elsewhere, for example in climate 		      action progress reports, inventory reports or other publications. </td> 
  </tr>
  <tr>
    <td colspan="2">All_non_GPC_Considered</td>
    <td colspan="1" style="text-align:center">8</td>
    <td>Non-GPC emissions data combined from Target_Other, CDP_Other and City_Other data sources.  Where there were multiple 	     data points for the same year priority was given to the non-GPC record with the highest data quality.</td> 
  </tr>
</table>

### 3) Data Analysis
The following criteria were used to determine if each city had peaked emissions. If all criteria were TRUE it was concluded that the city had not PEAKED. If criteria 1 and 3 are TRUE and criteria 2 and 4 were FALSE it was concluded that the city had NOT PEAKED. Otherwise, it was concluded that it was UNKNOWN if the city has peaked.

**Table 2: Peaking Criteria**

<table style="width:80%">

<tr>
  <th>Criteria</th>
  <th>Rationale</th>
</tr>

<tr>
  <td>1) At least 3 years of emissions data available?</td>
  <td>At least 3 data points required to determine the direction of the trend in city GHG emissions.</td>
</tr>

<tr>
  <td>2) Peak emissions occurred more than 5 years before most recent emissions data point?</td>
  <td>Require long term trends to control for natural annual variations such as weather and economic activity. </td>
</tr>

<tr>
  <td>3) Latest emission data point is no more than 5 years old?</td>
  <td>Require recent data point within the last 5 years to ensure that peak has not been reversed. </td>
</tr>

<tr>
  <td> 4) Peak emission is more than 10% higher than latest emissions data point? </td>
  <td>Require significant decrease to be confident that emission reduction is not being driven by natural variation which will cause the peak to be reversed in future. </td>
</tr>

</table>

For cities with more than one data source the decision tree below was used to select a single data source as the best available time series data. 

**Figure 1: Decision tree used to select data sources for inclusion in the peaking analysis**

![Alt text](images/peaking_methodology.png?raw=true "Decision tree for dealing with multiple data sources")

In a small number of cases exceptions were made as there were compelling reasons to assume that a city had peaked.These cases are documented in the table below. One way in which these edge cases were identified was by using the Kaya Identity to model emissions in future years. The Kaya Identity is exprsssed in the form:

Kaya identity is expressed in the form:

F = P * G/P * E/G * F/E

Where:

 - F is city CO2 emissions from human sources
 - P is city population
 - G is city GDP
 - E is city energy consumption

**Table 3: Criteria to determine if C40 cities have peaked**

<table style="width:80%">

<tr>
  <th>City</th>
  <th>Peaking criteria</th>
  <th>Peak status</th>
  <th>Rationale</th>
</tr>

<tr>
  <td>New Orleands</td>
  <td>1, 2 and 4</td>
  <td>PEAKED</td>
  <td>Exception made as city confirmed C40 estimate for 2016 data using IPCC Kaya Identity</td>
</tr>


<tr>
  <td>Rome</td>
  <td>1,2 and 4</td>
  <td>PEAKED</td>
  <td>Exception made as city confirmed C40 estimate for 2015 data from draft 2015 GPC</td>
</tr>


<tr>
  <td>Oslo</td>
  <td>1,3 and 4</td>
  <td>PEAKED</td>
  <td>Exception made on basis of the scale of reduction and climate actions taken in recent years</td>
</tr>

</table>

### 4) Data Automation/Visualisation
The results of the peaking analysis are visualised using dashboards developed using Dash and Tableau. On an annual basis C40 repeats the data collection exercise in section 2 to update the source data. In between times the results of the peaking analysis are likely to change as C40 collects city GPC and non-GPC data on a rolling basis. To ensure that these changes are reflected a Python script repeats the analysis on a daily basis ensuring the dashboard is up-to-date. 

**Figure 2: Dashboard developed in Dash**

![Alt text](images/city_emission_tracker.png?raw=true "Front end developed in Dash")


### 5) Directions on use

**Running the code**<br>
The backend script is designed to work with C40's internal GHG emissions database. However, the script could be adapted to use another database and would succesfullu apply peaking critieria helping the user to choose the best time series data for their analysis. 

**Prerequisites**<br>
The code requires python 3 libraries which can be installed from the requirements.txt file. 

### 6) Press releases
The results of this analysis were announced at the World Mayor's Summit in 2019. Here are links to press releases:
 1. https://www.weforum.org/agenda/2019/10/carbon-emissions-climate-change-global-warming/
 2. https://www.outlookindia.com/newsscroll/worlds-30-largest-cities-peaked-emissions/1636075
 3. https://www.businessgreen.com/news/3082404/c40-30-major-cities-have-already-peaked-their-emissions
 4. https://www.smartcitiesworld.net/news/news/30-cities-say-their-greenhouse-gas-emissions-have-peaked--4662
 5. https://www.edie.net/news/9/C40--30-cities-have-reach-peak-emissions/

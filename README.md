# City Green House Gas Emissions Tracker

### 1) Background

A city is considered to have “peaked emissions” when there is sufficient evidence to show that its greenhouse gas (GHG) emissions have decreased from a maximum level. This document explains the method used by C40 to determine whether its cities have peaked. The first section explains how C40 collects GHG emissions data for its cities. The second section explains how C40 analyses this data to conclude whether cities have peaked. And the final section, explains how this analysis is automated and visualised using an interactive dashboard built in Dash and hosted using Heroku. 

### 2) Data Collection 
C40 collects time series GHG emissions data for each of its 93 cities on an annual basis by reviewing publicly available emissions data. Data sources are ranked using the data quality hierarchy in the table below.

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
The following criteria are used to determine if each city has peaked. If all criteria are TRUE it is concluded that the city has PEAKED. If criteria 1 and 3 are TRUE and criteria 2 and 4 are FALSE it is concluded that the city had NOT PEAKED. Otherwise, it is concluded that it is UNKNOWN if the city has peaked.

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

For cities with more than one data source the decision tree below is used to select a single data source for inclusion in the results presented by the dashboard.

**Figure 1: Decision tree used to select data sources for inclusion in the peaking analysis**

![Alt text](./peaking_methodology.png?raw=true "Decision tree for dealing with multiple data sources")

In a small number of cases exceptions may be made to the above rule where there are compelling reasons to assume that a city has peaked. These cases are documented in the table below. These cities are handled using the same logic for cities that have already peaked (see above).

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

## 4) Data Automation/Visualisation
The results of the peaking analysis are visualised using a dashboard developed using Dash (see here). On an annual basis C40 repeats the data collection exercise in section 2 to update the source data. In between times the results of the peaking analysis are likely to change as C40 collects city GPC and non-GPC data on a rolling basis. To ensure that these changes are reflected a Python script repeats the analysis on a daily basis ensuring the dashboard is up-to-date. 

**Figure 2: Dashboard developed in Dash**

![Alt text](./city_emission_tracker.png?raw=true "Front end developed in Dash")



###### Cell 1 ######

### Import Libraries ###

import streamlit as st
import plotly.express as px
import pandas as pd

###### Cell 1 ######



###### Cell 2 ######

### Read in data and clean data up ###

initial_df = pd.read_csv("tech_employment_2000_2025.csv")

# convert data columns to numeric values to transform and compare them
initial_df["year"] = pd.to_numeric(initial_df["year"], errors = "coerce")
initial_df["employees_start"] = pd.to_numeric(initial_df["employees_start"], errors = "coerce")
initial_df["employees_end"] = pd.to_numeric(initial_df["employees_end"], errors = "coerce")
initial_df["new_hires"] = pd.to_numeric(initial_df["new_hires"], errors = "coerce")
initial_df["layoffs"] = pd.to_numeric(initial_df["layoffs"], errors = "coerce")
initial_df["net_change"] = pd.to_numeric(initial_df["net_change"], errors = "coerce")
initial_df["hiring_rate_pct"] = pd.to_numeric(initial_df["hiring_rate_pct"], errors = "coerce")
initial_df["attrition_rate_pct"] = pd.to_numeric(initial_df["attrition_rate_pct"], errors = "coerce")
initial_df["revenue_billions_usd"] = pd.to_numeric(initial_df["revenue_billions_usd"], errors = "coerce")
initial_df["stock_price_change_pct"] = pd.to_numeric(initial_df["stock_price_change_pct"], errors = "coerce")
initial_df["gdp_growth_us_pct"] = pd.to_numeric(initial_df["gdp_growth_us_pct"], errors = "coerce")
initial_df["unemployment_rate_us_pct"] = pd.to_numeric(initial_df["unemployment_rate_us_pct"], errors = "coerce")

# remove rows with empty company and year data
initial_df = initial_df.dropna(subset = ["company", "year"])

# normalize net_change metric since some companies are much bigger than others
# and we want to be able to compare that value at scale between companies
initial_df["net_change_pct"] = (initial_df["net_change"] / initial_df["employees_start"]) * 100

###### Cell 2 ######



###### Cell 3 ######

st.title("Visualizing Tech Workforce Data from 2000 - 2025")

### Filtering Displayable Data ###

# add interactive filters
list_of_years = sorted(initial_df["year"].unique())
list_of_companies = sorted(initial_df["company"].unique())

year_selector = st.selectbox(
    "Select a year",
    list_of_years
)

company_selector = st.multiselect(
    "Select a company",
    options = list_of_companies,
    default = list_of_companies,
)

# include only selected company data
chart_data_df = initial_df[initial_df["company"].isin(company_selector)]

###### Cell 3 ######



###### Cell 4 ######

# Initial chart to describe the state of the US economy over the last 2 decades
# Historical chart to provide context

gdp_line_df = chart_data_df[["year", "gdp_growth_us_pct"]]

gdp_line_df = gdp_line_df.groupby(["year"])["gdp_growth_us_pct"].mean().reset_index()

gdp_line_fig = px.line(
    gdp_line_df, 
    x = "year",
    y = "gdp_growth_us_pct",
    title = "US GDP Growth Rate Over Time (Figure 1)",
    labels = {
        "year": "Year",
        "gdp_growth_us_pct": "Annual US GDP Growth Rate (%)"
    },
    markers = True
)

gdp_line_fig.add_hline(
    y = 0,
    line = {"color": "white"}
)

gdp_line_fig.add_vline(
    x = 2000,
    line = {"color": "white"}
)

st.plotly_chart(gdp_line_fig)

###### Cell 4 ######



###### Cell 5 ######

# Chart 1
# Purpose: To show historical trend of employee headcount changes from 2000-2025

heatmap_data = chart_data_df.pivot_table(index = "company", columns = "year", values = "net_change_pct", aggfunc = "mean")

granular_steps = [
        [0.0, "#b2182b"],
        [0.05, "#f4a582"],
        [0.2, "#ffffff"],
        [0.35, "#a6d96a"],
        [1.0, "#1a9850"]
    ]

heatmap_fig = px.imshow(
    heatmap_data,
    labels = {
        "x": "Year",
        "y": "Company",
        "color": "Net Change (%)"
    },
    color_continuous_scale=granular_steps,
    title = "Which Companies Experienced The Biggest Growth / Reduction from 2000 - 2025? (Figure 2)"
)

heatmap_fig.update_layout(height=500)

st.plotly_chart(heatmap_fig, use_container_width=True)

###### Cell 5 ######



###### Cell 6 ######

# Chart 2
# Purpose: To show relationship between companies' hiring and layoff relationship in a given year

# find the order of companies with most layoffs -> least layoffs
# we want to preserve this order to make the layoff and hiring rate comparisons easier
layoff_company_order = chart_data_df[chart_data_df["year"] == year_selector].sort_values("layoffs", ascending = False)["company"].drop_duplicates().tolist()

# create layoff bar chart
layoff_bardata_df = chart_data_df[chart_data_df["year"] == year_selector]

layoff_bardata_df = layoff_bardata_df.groupby(["company", "year"], as_index = False)["layoffs"].sum().sort_values("layoffs", ascending = False)

layoff_bardata_fig = px.bar(
    layoff_bardata_df,
    x = "company",
    y = "layoffs",
    category_orders = {"company": layoff_company_order},
    title = f"Which Companies Had The Most Layoffs in {year_selector}?  (Figure 3)",
    labels = {
        "company": "Company",
        "layoffs": "Number of employees laid off"
    }
)

st.plotly_chart(layoff_bardata_fig, use_container_width=True)

# create hiring bar chart
hiring_bardata_df = chart_data_df

hiring_bardata_df = hiring_bardata_df[hiring_bardata_df["year"] == year_selector]

hiring_bardata_df = hiring_bardata_df.groupby(["company", "year"], as_index = False)["hiring_rate_pct"].mean().sort_values("hiring_rate_pct", ascending = False)

hiring_bardata_fig = px.bar(
    hiring_bardata_df,
    x = "company",
    y = "hiring_rate_pct",
    category_orders = {"company": layoff_company_order},
    title = f"Which Companies Had The Highest Hiring Rate in {year_selector}?  (Figure 4)",
    labels = {
        "company": "Company",
        "hiring_rate_pct": "Hiring Rate (%)"
    }
)

st.plotly_chart(hiring_bardata_fig, use_container_width=True)

###### Cell 6 ######



###### Cell 7 ######

# Chart 3
# Purpose: To show the relationship of how a company's stock performance influences
# their headcount
metric_scatterplot_df = chart_data_df

metric_scatterplot_fig = px.scatter(
    metric_scatterplot_df,
    x = "stock_price_change_pct",
    y = "net_change_pct",
    color = "company",
    hover_data = [
        "year",
        "new_hires",
        "layoffs",
        "attrition_rate_pct"
    ],
    title = "Company Stock Performance vs Workforce Growth?  (Figure 5)",
    labels = {
        "stock_price_change_pct": "Year over Year Stock Price Change (%)",
        "net_change_pct": "Net Change in Employee Headcount (%)"
    }
)

metric_scatterplot_fig.add_hline(
    y = 0,
    line = {"color": "white"}
)

metric_scatterplot_fig.add_vline(
    x = 0,
    line = {"color": "white"}
)

st.plotly_chart(metric_scatterplot_fig, use_container_width=True)

###### Cell 7 ######



###### Cell 8 ######

# Chart 4
# Purpose: To show how companies stack up against each other when it comes to attrition
hiring_bardata_df = chart_data_df

boxplot_fig = px.box(
    hiring_bardata_df,
    x = "company",
    y = "attrition_rate_pct",
    title = "Which Companies Had The Most Unstable Attrition Rates  (Figure 6)",
    labels = {
        "company": "Company",
        "attrition_rate_pct": "Attrition Rate (%)"
    }
)

st.plotly_chart(boxplot_fig, use_container_width=True)

###### Cell 8 ######
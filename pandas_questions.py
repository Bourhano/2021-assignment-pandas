"""Plotting referendum results in pandas.

In short, we want to make beautiful map to report results of a referendum. In
some way, we would like to depict results with something similar to the maps
that you can find here:
https://github.com/x-datascience-datacamp/datacamp-assignment-pandas/blob/main/example_map.png

To do that, you will load the data as pandas.DataFrame, merge the info and
aggregate them by regions and finally plot them on a map using `geopandas`.
"""
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    dir = "./data/"
    ext = ".csv"
    referendum = pd.read_csv(dir + "referendum" + ext, sep=';')
    regions = pd.read_csv(dir + "regions" + ext)
    departments = pd.read_csv(dir + "departments" + ext)

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    col_names = ['code_x', 'name_x', 'code_y', 'name_y']
    new_names = ['code_reg', 'name_reg', 'code_dep', 'name_dep']

    merged = pd.merge(left=regions, right=departments, how='inner',
                      left_on="code", right_on="region_code")
    merged = merged[col_names].rename(columns=dict(zip(col_names, new_names)))

    return merged


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    # regions_and_departments = regions_and_departments[
    #                       regions_and_departments["code_reg"] != 'COM']
    referendum["Department code"] = referendum["Department code"].str.zfill(2)

    merged = pd.merge(left=referendum, right=regions_and_departments,
                      how='inner',
                      left_on="Department code", right_on="code_dep")

    return merged


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    ref_areas = referendum_and_areas
    col_names = ['name_reg', 'Registered', 'Abstentions', 'Null',
                 'Choice A', 'Choice B']
    ref_areas = ref_areas.groupby(['code_reg', 'name_reg'])[col_names].sum()
    ref_areas = ref_areas.reset_index().set_index('code_reg')

    return ref_areas


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    ref_results = referendum_result_by_regions
    expressed = ref_results['Registered']\
        - ref_results['Abstentions'] - ref_results['Null']
    ref_results['ratio'] = ref_results['Choice A'] / expressed

    geo_regions = gpd.read_file('data/regions.geojson')
    geo_results = pd.merge(geo_regions, referendum_result_by_regions, 'left',
                           left_on='code', right_on='code_reg')
    geo_results.plot('ratio')

    return geo_results


if __name__ == "__main__":

    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(
        df_reg, df_dep
    )
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas
    )
    print(referendum_results)

    plot_referendum_map(referendum_results)
    plt.show()

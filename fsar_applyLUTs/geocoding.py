"""
Copyright (c) 2024 Jan Luca MERZ, Marc JAEGER

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


import argparse
import re
import numpy as np
import rasterio
import rio_cogeo
import os
import scipy
from rasterio.windows import Window


def get_lookup_tables(gtc_lut_path, band):
    """
    function that searches for the lookup tables of the provided frequency band.
    :param gtc_lut_path: the path to the GTC-LUT directory
    :param band: the frequency band, for which the lookup table has to be found
    :return: dictionary with the lookup tables. To differentiate between them, they are named in the pattern
    filename_band i.e. sr2geo_az_P
    """

    filename_patterns = ["sr2geo_az", "sr2geo_rg", "geo2sr_east", "geo2sr_north"]
    # every band the input could be in
    band_patterns = r"_(X|C|S|L|P)"

    filename_pattern = '|'.join(filename_patterns)
    lookup_tables = {}

    for filename in os.listdir(gtc_lut_path):
        if band is not None and f"_{band}_" not in filename:
            continue

        filename_match = re.search(filename_pattern, filename)
        if filename_match:
            band_match = re.search(band_patterns, filename)
            if band_match:
                if filename.endswith(".rat") or filename.endswith(".tif"):
                    found_file = filename_match.group() + band_match.group()
                    lookup_tables[found_file] = os.path.join(gtc_lut_path, filename)

    return lookup_tables


def get_band_luts(found_table, lookup_tables):
    """
    function that gets all lookup tables that have the same frequency band as the provided lookup table.
    :param found_table: lookup table with the frequency band that's being searched for
    :param lookup_tables: dictionary containing all lookup tables that could be found
    :return: dictionary containing all four lookup tables for this frequency band
    """
    last_underscore_index = found_table.rfind('_')

    band = found_table[last_underscore_index:]
    all_lookup_tables = {}

    for lookup_table in lookup_tables:
        match = re.search(band, lookup_table)
        if match:
            # has to be done again here because the lookup_table string doesn't have to share the length of the found_table
            last_underscore_index = lookup_table.rfind('_')
            lookup_table_name = lookup_table[:last_underscore_index]
            all_lookup_tables[lookup_table_name] = lookup_tables[lookup_table]

    if len(all_lookup_tables) < 2:
        raise NotImplementedError("couldn't find all necessary lookup tables")

    return all_lookup_tables


def get_lut_for_input(lookup_tables, input_file):
    """
    function that takes in all lookup tables for all frequency bands and only returns the ones for the matching frequency
    band.
    :param lookup_tables: dictionary containing the paths to all lookup tables that could be found
    :param input_file: path to the input file
    :return: the four lookup tables of the frequency band, the input file has matched
    """

    with rasterio.open(input_file) as input_file:
        input_shape = input_file.shape

    for lookup_table in lookup_tables:
        with rasterio.open(lookup_tables[lookup_table]) as lookup_file:
            lookup_shape = lookup_file.shape

        # if input and lookup have the same shape that means they would have the same geometry
        if input_shape != lookup_shape:
            return get_band_luts(lookup_table, lookup_tables)


def calculate_window_limits(window, max_size):
    """
    function that calculates the min and max values in the lookup tables (excluding negative values)
    :param window: the lookup table the values are calculated for
    :param max_size: the maximum value in the window, i.e. the shapes of the dimension of the input file
    :return: the minimum value and the range between the minimum and the maximum
    """
    # pixels before and after the min and max values stated in the lookup table, that are read in
    additional_pixels = 3

    # the smallest possible value for the input window is always zero
    min_val = max(np.floor(np.nanmin(window)) - additional_pixels, 0)
    max_val = min(np.floor(np.nanmax(window)) + additional_pixels, max_size)

    value_range = max_val - min_val

    return min_val, value_range


def write_to_file(offset_ax1, offset_ax2, blocksize, order, first_axis, second_axis, input_file, dst):
    """
    function that imports a data block and writes it to a file after interpolation
    :param offset_ax1: block offset in the row
    :param offset_ax2: block offset in the column
    :param blocksize: the size of every processed block of data
    :param order: the order of the spline interpolation
    :param first_axis: file containing the lookup table for the first axis
    :param second_axis: file containing the lookup table for the second axis
    :param input_file: file containing the input data
    :param dst: file the output data should be written into
    """

    window = Window(offset_ax2, offset_ax1, blocksize, blocksize)
    ax1_window = first_axis.read(window=window)[0, ...]

    # skip this block if there are no coordinates (positive values) in it
    if (ax1_window > 0).any():
        ax2_window = second_axis.read(window=window)[0, ...]

        if (ax2_window > 0).any():

            # window has to be reinitialized at this point to ensure that it's not going out of bounds of the output file
            window = Window(offset_ax2, offset_ax1, ax1_window.shape[1], ax1_window.shape[0])

            min_ax1, width = calculate_window_limits(ax1_window, input_file.shape[0])
            min_ax2, height = calculate_window_limits(ax2_window, input_file.shape[1])

            # read data chunk starting from the smallest value necessary, to the biggest value necessary
            for i in range(1, input_file.profile["count"] + 1):
                input_window = input_file.read(i, window=Window(min_ax2, min_ax1, height, width))
                # axis - min to get from coordinates that would apply for the whole input matrix to coordinates
                # which apply for this part of the input matrix
                output = scipy.ndimage.map_coordinates(input_window,
                                                       [ax1_window - min_ax1, ax2_window - min_ax2],
                                                       order=order)
                dst.write(output, i, window=window)


def process_blockwise(input_file, output_file, lookup_tables, to_slant_range, blocksize, order, default_order):
    """
    function that opens the output file, as well as the input file and the necessary lookup tables and iterates over
    the data to enable blockwise processing
    :param input_file: path to the input file
    :param output_file: path to the output file
    :param lookup_tables: dictionary containing the paths to the lookup tables
    :param to_slant_range: Boolean, True if the user is trying to convert to slant range and False if the user is trying to convert to geocoded data
    :param blocksize: the size of one block of data
    :param order: the order of the spline interpolation
    :param default_order: the default order of the spline interpolation (applied when order is None)
    """

    if to_slant_range:
        coordinates = (lookup_tables["geo2sr_north"], lookup_tables["geo2sr_east"])
    else:
        coordinates = (lookup_tables["sr2geo_az"], lookup_tables["sr2geo_rg"])

    # open the input file and the lookup tables

    with rasterio.open(coordinates[0]) as first_axis, rasterio.open(coordinates[1]) as second_axis, rasterio.open(
            input_file) as input_file:

        # switch interpolation to nearest neighbour if the user hasn't specified an order and the files dtype is int
        if input_file.dtypes[0] == "int" and order is None:
            order = 0
        elif order is None:
            order = default_order

        # make a profile for the output file and open the output file

        profile = {"driver": "GTiff", "dtype": input_file.dtypes[0], "height": first_axis.shape[0],
                   "width": first_axis.shape[1], "count": input_file.profile["count"]}
        if not to_slant_range:
            profile["transform"] = first_axis.profile["transform"]
            profile["crs"] = first_axis.profile["crs"]

        with rasterio.io.MemoryFile() as memfile:
            with memfile.open(**profile) as mem:
                start = 0
                end_ax1 = first_axis.shape[0]
                end_ax2 = first_axis.shape[1]

                for offset_ax1 in range(start, end_ax1, blocksize):
                    for offset_ax2 in range(start, end_ax2, blocksize):
                        write_to_file(offset_ax1, offset_ax2, blocksize, order, first_axis, second_axis, input_file,
                                      mem)

                dst_profile = rio_cogeo.cog_profiles.get("deflate")
                dst_profile["interleave"] = "band"

                rio_cogeo.cog_translate(
                    mem,
                    output_file,
                    dst_profile,
                    quiet=False,
                )



def main():
    default_order = 3
    default_blocksize = 512

    parser = argparse.ArgumentParser()
    parser.add_argument("--gtc_lut",
                        help=f"path to the GTC-LUT directory", required=True)
    parser.add_argument("--input_file",
                        help=f"absolute path to the input file", required=True)
    parser.add_argument("--output_file",
                        help=f"absolute path to the output file", required=True)
    parser.add_argument("--band", help=f"The frequency band of the input file (for example P, X, S or L)",
                        required=True)
    parser.add_argument("--order", help=f"order of the spline interpolation, has to be between 0-5. The default is "
                                        f"{default_order} for floating point data and 0 for integer data",
                        required=False, type=int)
    parser.add_argument("--blocksize", help=f"the size per processed chunk of data. Defaults to {default_blocksize}",
                        default=default_blocksize, type=int, required=False)
    parser.add_argument("--geometry", help=f"type geo if you want to go from geocoded to slant range "
                                           f"or sr if you want to go from slant range to geocoded.",
                        required=True)
    args = parser.parse_args()

    lookup_tables = get_lookup_tables(args.gtc_lut, args.band)

    if args.geometry == "geo":
        to_slant_range = True
        lookup_tables = get_lut_for_input(lookup_tables, args.input_file)
    elif args.geometry == "sr":
        to_slant_range = False
        lookup_tables = get_lut_for_input(lookup_tables, args.input_file)
    else:
        raise ValueError(f"You typed {args.geometry} in as the geometry but only sr or geo are viable options.")

    process_blockwise(args.input_file, args.output_file, lookup_tables, to_slant_range, args.blocksize, args.order,
                      default_order)


if __name__ == "__main__":
    main()

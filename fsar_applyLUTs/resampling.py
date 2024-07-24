"""
Copyright (c) 2024 German Aerospace Center (DLR)

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
import rasterio as rio
from rasterio import warp as riow
import rio_cogeo
import tempfile

from .geocoding import get_lookup_tables

def main():
    DUMMY = -9999

    parser = argparse.ArgumentParser()
    parser.add_argument("--luts",
                        help=f"path to the GTC-LUT directory", required=True)
    parser.add_argument("--band", choices=['X','C','S','L','P',''], default='',
                        help=f"The frequency band of the input file (defaults to '', "
                             f"which works when the geocoded product only contains one band)")
    parser.add_argument("--nodata", type=float, default=DUMMY,
                        help=f"no data value (defaults to {DUMMY})")
    parser.add_argument("--in", dest="input_file",
                        help=f"absolute path to the input file", required=True)
    parser.add_argument("--out", dest="output_file",
                        help=f"absolute path to the output file", required=True)
    args = parser.parse_args()

    lookup_tables = get_lookup_tables(args.luts, args.band)
    ds_in = [rio.open(f) for f in (lookup_tables['sr2geo_az'], args.input_file)]

    with tempfile.NamedTemporaryFile() as f_tmp:
        with rio.open(f_tmp.name, 'w', **ds_in[0].profile) as rio_tmp:
            ds_co = [ds_in[0], rio_tmp]
            riow.reproject(rio.band(ds_in[1],1), rio.band(ds_co[1],1),
                           src_nodata=args.nodata, dst_nodata=args.nodata,
                           resampling=riow.Resampling.lanczos)


        dst_profile = rio_cogeo.cog_profiles.get("deflate")
        dst_profile["interleave"] = "band"
        with rio.open(f_tmp.name, 'r') as rio_tmp:
            rio_cogeo.cog_translate(
                rio_tmp,
                args.output_file,
                dst_profile,
                quiet=False,
            )

if __name__ == "__main__":
    main()

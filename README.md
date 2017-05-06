# Pandas DataFrame GUI

A minimalistic GUI for analyzing Pandas DataFrames based on wxPython.

## Usage

```python
import dfgui
dfgui.show(df)
```

## Features

- Tabular view of data frame
- Columns are sortable (by clicking column header)
- Columns can be enabled/disabled (left click on 'Columns' tab)
- Columns can be rearranged (right click drag on 'Columns' tab)
- Generic filtering: Write arbitrary Python expression to filter rows. *Warning:* Uses Python's `eval` -- use with care.
- Histogram plots
- Scatter plots

## Demo & Docs

The default view: Nothing fancy, just scrolling and sorting. The value of cell can be copied to clipboard by right clicking on a cell.

![screen1](/../screenshots/screenshots/screen1.png)

The column selection view: Left clicking enables or disables a column in the data frame view. Columns can be dragged with a right click to rearrange them.

![screen2](/../screenshots/screenshots/screen2.png)

The filter view: Allows to write arbitrary Pandas selection expressions. The syntax is: An underscore `_` will be replaced by the corresponding data frame column. That is, setting the combo box to a column named "A" and adding the condition `_ == 1` would result in an expression like `df[df["A"] == 1, :]`. The following example filters the data frame to rows which have the value 669944 in column "UserID" and `datetime.date` value between 2016-01-01 and 2016-03-01.

![screen3](/../screenshots/screenshots/screen3.png)

Histogram view:

![screen4](/../screenshots/screenshots/screen4.png)

Scatter plot view:

![screen5](/../screenshots/screenshots/screen5.png)

## Requirements

Since wxPython is not pip-installable, dfgui does not handle dependencies automatically. You have to make sure the following packages are installed:

- pandas/numpy
- matplotlib
- wx

## Installation Instructions

I haven't submitted dfgui to PyPI (yet), but you can install directly from git (having met all requirements). For instance:

```bash
git clone git@github.com:bluenote10/PandasDataFrameGUI.git dfgui
cd dfgui
pip install -e .
# and to check if everything works:
./demo.py
```

In fact, dfgui only consists of a single module, so you might as well just download the file [`dfgui/dfgui.py`](dfgui/dfgui.py).

### Anaconda/Windows Instructions

Install wxpython through conda or the Anaconda GUI.

"Open terminal" in the Anaconda GUI environment.

```bash
git clone "https://github.com/bluenote10/PandasDataFrameGUI.git"
cd dfgui
pip install -e .
conda package --pkg-name=dfgui --pkg-version=0.1 # this should create a package file
conda install --offline dfgui-0.1-py27_0.tar.bz2 # this should install into your conda environment
```
Then restart your Jupyter kernel.


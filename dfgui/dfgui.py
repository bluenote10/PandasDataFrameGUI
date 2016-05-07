#!/usr/bin/env python
# -*- encoding: utf-8

from __future__ import absolute_import, division, print_function

import matplotlib
matplotlib.use('WXAgg')

import wx
import numpy as np
import pandas as pd


class ListCtrlDataFrame(wx.ListCtrl):

    def __init__(self, parent, df):
        wx.ListCtrl.__init__(
            self, parent, -1,
            style=wx.LC_REPORT | wx.LC_VIRTUAL | wx.LC_HRULES | wx.LC_VRULES | wx.LB_MULTIPLE
        )

        self.df_orig = df
        self.df = df
        self.original_columns = self.df.columns[:]
        self.current_columns = self.df.columns[:]

        self.sort_by_column = None
        self.tmp_selection_col_name = 'tmp_selection_column'

        # prepare attribute for alternating colors of rows
        self.attr_light_blue = wx.ListItemAttr()
        self.attr_light_blue.SetBackgroundColour("#D6EBFF")

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_item_selected)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.on_item_deselected)
        self.Bind(wx.EVT_LIST_CACHE_HINT, self.on_cache_hint)
        self.Bind(wx.EVT_LIST_COL_CLICK, self.on_col_click)

        self._build_columns(self.original_columns)

    def _build_columns(self, columns):
        self.ClearAll()
        for i, col in enumerate(columns):
            self.InsertColumn(i, col)
            self.SetColumnWidth(i, 175)
        self.SetItemCount(len(self.df))

    def set_columns(self, columns_to_use):
        """
        External interface to set the column projections
        """
        self.current_columns = columns_to_use
        self.df = self.df_orig[columns_to_use]
        self._build_columns(columns_to_use)

    def on_item_selected(self, evt):
        # print('on_item_selected: "%s", "%s"' % (evt.m_itemIndex, self.GetItemText(evt.m_itemIndex)))
        pass

    def on_item_deselected(self, evt):
        # print("on_item_deselected: %s" % evt.m_itemIndex)
        pass

    def on_cache_hint(self, evt):
        # print("on_cache_hint: %s %s %s %s" % (evt, evt.GetIndex(), evt.GetCacheFrom(), evt.GetCacheTo()))
        pass

    def on_col_click(self, evt):
        """
        Sort data frame by selected column.
        """
        # get currently selected items
        selected = self.get_selected_items()

        # append a temporary column to store the currently selected items
        self.df[self.tmp_selection_col_name] = False
        self.df.iloc[selected, -1] = True

        # get column name to use for sorting
        col = evt.GetColumn()

        # determine if ascending or descending
        if self.sort_by_column is None or self.sort_by_column[0] != col:
            ascending = True
        else:
            ascending = not self.sort_by_column[1]

        # store sort column and sort direction
        self.sort_by_column = (col, ascending)

        try:
            # pandas 0.17
            self.df.sort_values(self.df.columns[col], inplace=True, ascending=ascending)
        except AttributeError:
            # pandas 0.16 compatibility
            self.df.sort(self.df.columns[col], inplace=True, ascending=ascending)

        # deselect all previously selected
        for i in selected:
            self.Select(i, on=False)

        # determine indices of selection after sorting
        selected_bool = self.df.iloc[:, -1] == True
        selected = self.df.reset_index().index[selected_bool]

        # select corresponding rows
        for i in selected:
            self.Select(i, on=True)

        # delete temporary column
        del self.df[self.tmp_selection_col_name]

    def get_selected_items(self):
        """
        Gets the selected items for the list control.
        Selection is returned as a list of selected indices,
        low to high.
        """
        selection = []
        current = -1    # start at -1 to get the first selected item
        while True:
            next = self.GetNextItem(current, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
            if next == -1:
                return selection
            else:
                selection.append(next)
                current = next

    def apply_filter(self, conditions):
        if len(conditions) == 0:
            self.df = self.df_orig[self.current_columns]
            return self.df_orig.shape[0]

        mask = pd.Series([True] * self.df_orig.shape[0])
        for column, condition in conditions:
            if condition.strip() == '':
                continue
            condition = condition.replace("_", "self.df_orig['{}']".format(column))
            print(condition)
            try:
                tmp_mask = eval(condition)
                if isinstance(tmp_mask, pd.Series) and tmp_mask.dtype == np.bool:
                    mask &= tmp_mask
            except:
                pass

        self.df = self.df_orig.loc[mask, self.current_columns]
        # print(mask, self.df, self.df.shape)
        return self.df.shape[0]

    def OnGetItemText(self, item, col):
        """
        Implements the item getter for a "virtual" ListCtrl.
        """
        value = self.df.iloc[item, col]
        # print("retrieving %d %d %s" % (item, col, value))
        return value

    def OnGetItemAttr(self, item):
        """
        Implements the attribute getter for a "virtual" ListCtrl.
        """
        if item % 2 == 0:
            return self.attr_light_blue
        else:
            return None


class DataframePanel(wx.Panel):

    def __init__(self, parent, df):
        wx.Panel.__init__(self, parent)

        self.list_ctrl = ListCtrlDataFrame(self, df)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.list_ctrl, 1, wx.ALL | wx.EXPAND | wx.GROW, 5)
        self.SetSizer(sizer)
        self.Show()

    def set_columns(self, columns_to_use):
        self.list_ctrl.set_columns(columns_to_use)

    def apply_filter(self, conditions):
        return self.list_ctrl.apply_filter(conditions)


class DropList(wx.ListBox):

    def __init__(self, parent, size, data, *args, **kwargs):

        wx.ListBox.__init__(self, parent, size, **kwargs)

        self.data = data

        self.InsertItems(data, 0)

        self.Bind(wx.EVT_LISTBOX, self.on_selection_changed)

        self.Bind(wx.EVT_LEFT_DOWN, self.on_left_down)

        self.Bind(wx.EVT_RIGHT_DOWN, self.on_right_down)
        self.Bind(wx.EVT_RIGHT_UP, self.on_right_up)
        self.Bind(wx.EVT_MOTION, self.on_move)

        self.index_iter = xrange(len(self.data))

        self.selected_items = [True] * len(self.data)
        self.index_mapping = list(range(len(self.data)))

        self.drag_start_index = None

        self.update_selection()
        self.SetFocus()

    def on_left_down(self, event):
        if self.HitTest(event.GetPosition()) != wx.NOT_FOUND:
            index = self.HitTest(event.GetPosition())
            self.selected_items[index] = not self.selected_items[index]
            # doesn't really work to update selection direclty (focus issues)
            # instead we wait for the EVT_LISTBOX event and fix the selection
            # there...
            # self.update_selection()
            # TODO: we could probably use wx.CallAfter
        event.Skip()

    def update_selection(self):
        # self.SetFocus()
        # print(self.selected_items)
        for i in self.index_iter:
            if self.IsSelected(i) and not self.selected_items[i]:
                #print("Deselecting", i)
                self.Deselect(i)
            elif not self.IsSelected(i) and self.selected_items[i]:
                #print("Selecting", i)
                self.Select(i)

    def on_selection_changed(self, evt):
        self.update_selection()
        evt.Skip()

    def on_right_down(self, event):
        if self.HitTest(event.GetPosition()) != wx.NOT_FOUND:
            index = self.HitTest(event.GetPosition())
            self.drag_start_index = index

    def on_right_up(self, event):
        self.drag_start_index = None
        event.Skip()

    def on_move(self, event):
        if self.drag_start_index is not None:
            if self.HitTest(event.GetPosition()) != wx.NOT_FOUND:
                index = self.HitTest(event.GetPosition())
                if self.drag_start_index != index:
                    self.swap(self.drag_start_index, index)
                    self.drag_start_index = index

    def swap(self, i, j):
        self.index_mapping[i], self.index_mapping[j] = self.index_mapping[j], self.index_mapping[i]
        self.SetString(i, self.data[self.index_mapping[i]])
        self.SetString(j, self.data[self.index_mapping[j]])
        self.selected_items[i], self.selected_items[j] = self.selected_items[j], self.selected_items[i]
        # self.update_selection()
        # print("Updated mapping:", self.index_mapping)
        new_event = wx.PyCommandEvent(wx.EVT_LISTBOX.typeId, self.GetId())
        self.GetEventHandler().ProcessEvent(new_event)

    def get_selected_data(self):
        selected = []
        for i, col in enumerate(self.data):
            if self.IsSelected(i):
                index = self.index_mapping[i]
                value = self.data[index]
                selected.append(value)
        # print("Selected data:", selected)
        return selected


class ColumnSelectionPanel(wx.Panel):

    def __init__(self, parent, columns, dataframe_panel):
        wx.Panel.__init__(self, parent)

        self.columns = columns
        self.dataframe_panel = dataframe_panel

        self.list_box = DropList(self, -1, columns, style=wx.LB_EXTENDED)
        self.Bind(wx.EVT_LISTBOX, self.update_selected_columns)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.list_box, 1, wx.ALL | wx.EXPAND | wx.GROW, 5)
        self.SetSizer(sizer)
        self.Show()
        self.list_box.SetFocus()

    def update_selected_columns(self, evt):
        selected = self.list_box.get_selected_data()
        self.dataframe_panel.set_columns(selected)


class FilterPanel(wx.Panel):
    def __init__(self, parent, columns, dataframe_panel):
        wx.Panel.__init__(self, parent)

        columns_with_neutral_selection = [''] + list(columns)
        self.columns = columns
        self.dataframe_panel = dataframe_panel

        self.num_filters = 10

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.combo_boxes = []
        self.text_controls = []

        for i in xrange(self.num_filters):
            combo_box = wx.ComboBox(self, choices=columns_with_neutral_selection, style=wx.CB_READONLY)
            text_ctrl = wx.TextCtrl(self, wx.ID_ANY, '')

            self.Bind(wx.EVT_COMBOBOX, self.on_combo_box_select)
            self.Bind(wx.EVT_TEXT, self.on_text_change)

            row_sizer = wx.BoxSizer(wx.HORIZONTAL)
            row_sizer.Add(combo_box, 0, wx.ALL, 5)
            row_sizer.Add(text_ctrl, 1, wx.ALL | wx.EXPAND | wx.ALIGN_RIGHT, 5)

            self.combo_boxes.append(combo_box)
            self.text_controls.append(text_ctrl)
            self.main_sizer.Add(row_sizer, 0, wx.EXPAND)

        self.SetSizer(self.main_sizer)
        self.Show()

    def on_combo_box_select(self, event):
        self.update_conditions()

    def on_text_change(self, event):
        self.update_conditions()

    def update_conditions(self):
        print("Updating conditions")
        conditions = []
        for i in xrange(self.num_filters):
            column_index = self.combo_boxes[i].GetSelection()
            condition = self.text_controls[i].GetValue()
            if column_index != wx.NOT_FOUND and column_index != 0:
                # since we have added a dummy column for "deselect", we have to subtract one
                column = self.columns[column_index - 1]
                conditions += [(column, condition)]
        num_matching = self.dataframe_panel.apply_filter(conditions)
        print("Num matching:", num_matching)


class PageThree(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        t = wx.StaticText(self, -1, "This is a PageThree object", (60,60))


class MainFrame(wx.Frame):
    def __init__(self, df):
        wx.Frame.__init__(self, None, -1, "Pandas DataFrame GUI")

        # Here we create a panel and a notebook on the panel
        p = wx.Panel(self)
        nb = wx.Notebook(p)
        self.nb = nb

        columns = df.columns[:]

        # create the page windows as children of the notebook
        self.page1 = DataframePanel(nb, df)
        self.page2 = ColumnSelectionPanel(nb, columns, self.page1)
        self.page3 = FilterPanel(nb, columns, self.page1)
        self.page4 = PageThree(nb)

        # add the pages to the notebook with the label to show on the tab
        nb.AddPage(self.page1, "Data Frame")
        nb.AddPage(self.page2, "Columns")
        nb.AddPage(self.page3, "Filters")
        nb.AddPage(self.page4, "Scatter Plot")

        nb.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.on_tab_change)

        # finally, put the notebook in a sizer for the panel to manage
        # the layout
        sizer = wx.BoxSizer()
        sizer.Add(nb, 1, wx.EXPAND)
        p.SetSizer(sizer)

        self.SetSize((800, 600))
        self.Center()

    def on_tab_change(self, event):
        self.page2.list_box.SetFocus()
        page_to_select = event.GetSelection()
        wx.CallAfter(self.fix_focus, page_to_select)
        event.Skip(True)

    def fix_focus(self, page_to_select):
        page = self.nb.GetPage(page_to_select)
        page.SetFocus()
        if isinstance(page, DataframePanel):
            self.page1.list_ctrl.SetFocus()
        elif isinstance(page, ColumnSelectionPanel):
            self.page2.list_box.SetFocus()


if __name__ == "__main__":

    df = pd.DataFrame({
        "A": [1, 2, 3] * 1000,
        "B": [3.0, 2.0, 1.0] * 1000,
        "C": ["A", "B", "C"] * 1000
    })

    app = wx.App(False)
    frame = MainFrame(df)
    frame.Show()
    app.MainLoop()

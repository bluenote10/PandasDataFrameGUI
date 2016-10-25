""" DnD demo with listctrl. """
import sys
sys.path.append("/usr/lib/python2.7/dist-packages/wx-2.8-gtk2-unicode")

import wx

class DragList(wx.ListCtrl):
    def __init__(self, *arg, **kw):
        if 'style' in kw and (kw['style']&wx.LC_LIST or kw['style']&wx.LC_REPORT):
            kw['style'] |= wx.LC_SINGLE_SEL
        else:
            kw['style'] = wx.LC_SINGLE_SEL|wx.LC_LIST

        wx.ListCtrl.__init__(self, *arg, **kw)

        self.Bind(wx.EVT_LIST_BEGIN_DRAG, self._startDrag)

        dt = ListDrop(self._insert)
        self.SetDropTarget(dt)

    def _startDrag(self, e):
        """ Put together a data object for drag-and-drop _from_ this list. """

        # Create the data object: Just use plain text.
        data = wx.PyTextDataObject()
        idx = e.GetIndex()
        text = self.GetItem(idx).GetText()
        data.SetText(text)

        # Create drop source and begin drag-and-drop.
        dropSource = wx.DropSource(self)
        dropSource.SetData(data)
        res = dropSource.DoDragDrop(flags=wx.Drag_DefaultMove)

        # If move, we want to remove the item from this list.
        if res == wx.DragMove:
            # It's possible we are dragging/dropping from this list to this list.  In which case, the
            # index we are removing may have changed...

            # Find correct position.
            pos = self.FindItem(idx, text)
            self.DeleteItem(pos)

    def _insert(self, x, y, text):
        """ Insert text at given x, y coordinates --- used with drag-and-drop. """

        # Clean text.
        import string
        text = filter(lambda x: x in (string.letters + string.digits + string.punctuation + ' '), text)

        # Find insertion point.
        index, flags = self.HitTest((x, y))

        if index == wx.NOT_FOUND:
            if flags & wx.LIST_HITTEST_NOWHERE:
                index = self.GetItemCount()
            else:
                return

        # Get bounding rectangle for the item the user is dropping over.
        rect = self.GetItemRect(index)

        # If the user is dropping into the lower half of the rect, we want to insert _after_ this item.
        if y > rect.y + rect.height/2:
            index += 1

        self.InsertStringItem(index, text)

class ListDrop(wx.PyDropTarget):
    """ Drop target for simple lists. """

    def __init__(self, setFn):
        """ Arguments:
         - setFn: Function to call on drop.
        """
        wx.PyDropTarget.__init__(self)

        self.setFn = setFn

        # specify the type of data we will accept
        self.data = wx.PyTextDataObject()
        self.SetDataObject(self.data)

    # Called when OnDrop returns True.  We need to get the data and
    # do something with it.
    def OnData(self, x, y, d):
        # copy the data from the drag source to our data object
        if self.GetData():
            self.setFn(x, y, self.data.GetText())

        # what is returned signals the source what to do
        # with the original data (move, copy, etc.)  In this
        # case we just return the suggested value given to us.
        return d

if __name__ == '__main__':
    items = ['Foo', 'Bar', 'Baz', 'Zif', 'Zaf', 'Zof']

    class MyApp(wx.App):
        def OnInit(self):
            self.frame = wx.Frame(None, title='Main Frame')
            self.frame.Show(True)
            self.SetTopWindow(self.frame)
            return True

    app = MyApp(redirect=False)
    dl1 = DragList(app.frame)
    dl2 = DragList(app.frame)
    sizer = wx.BoxSizer()
    app.frame.SetSizer(sizer)
    sizer.Add(dl1, proportion=1, flag=wx.EXPAND)
    sizer.Add(dl2, proportion=1, flag=wx.EXPAND)
    for item in items:
        dl1.InsertStringItem(99, item)
        dl2.InsertStringItem(99, item)
    app.frame.Layout()
    app.MainLoop()
"""
This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
"""

import gui, wx

app = wx.PySimpleApp()
frame=gui.MyFrame(None,-1,'reSTEditor - version 0.1')
frame.Maximize(1)
frame.Show(1)
app.MainLoop()
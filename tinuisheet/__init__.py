from tinui import BasicTinUI
from tinui.TinUI import TinUIString

sheetlight = {
	'fg': "#191919",
	'bg': '#f3f3f3',
	'itemfg': '#1a1a1a',
	'itembg': '#f9f9f9',
	'itemactivefg': '#191919',
	'itemactivebg': '#f0f0f0',
	'itemonfg': '#191919',
	'itemonbg': '#e8e8e8',
	'headbg': '#f0f0f0',
	'scrollcolor': '#8a8a8a',
}

sheetdark = {
	'fg': "#ffffff",
	'bg': '#202020',
	'itemfg': '#ffffff',
	'itembg': '#272727',
	'itemactivefg': '#ffffff',
	'itemactivebg': '#343434',
	'itemonfg': '#ffffff',
	'itemonbg': '#404040',
	'headbg': '#343434',
	'scrollcolor': '#9f9f9f',
}

class TinUISheet:
	ui:BasicTinUI = None

	def __init__(self, ui:BasicTinUI, pos:tuple, width=300, height=300, minwidth=100, maxwidth=300, font=('微软雅黑', 12),
			     fg='black', bg='white', itemfg='#1a1a1a', itembg='#f9f9f9', headbg='#f0f0f0', scrollcolor='#8a8a8a',
				 itemactivefg='#191919', itemactivebg='#f0f0f0', itemonfg='#191919', itemonbg='#e0e0e0',
				 headfont=('微软雅黑', 14),
				 anchor='nw'):
		self.ui = ui
		self.width = width
		self.height = height
		self.fg = fg
		self.bg = bg
		self.headbg = headbg
		self.itemfg = itemfg
		self.itembg = itembg
		self.itemactivefg = itemactivefg
		self.itemactivebg = itemactivebg
		self.itemonfg = itemonfg
		self.itemonbg = itemonbg
		self.font = font
		self.headfont = headfont
		self.minwidth = minwidth
		self.maxwidth = maxwidth
		self.anchor = anchor

		self.uid:TinUIString = None
		self.titles = [] # [[item, back, width, x, tag],...]
		self.data = [] # [[[item, back, tag, level],...],...]
		self.endy = 0
		self.selected = -1
		self.selected_item = None

		self.box = BasicTinUI(ui, bg=bg)
		uid = ui.create_window(pos, window = self.box, width=width-8, height=height-8, anchor=anchor)
		self._ui = uid
		self.uid = TinUIString(f"tinuisheet-{uid}")
		ui.addtag_withtag(self.uid, uid)

		bbox = ui.bbox(uid)
		self.scv = ui.add_scrollbar((bbox[2], bbox[1]), self.box, bbox[3]-bbox[1], "y", bg=bg, color=scrollcolor, oncolor=scrollcolor)[-1]
		ui.addtag_withtag(self.uid, self.scv)
		self.sch = ui.add_scrollbar((bbox[0], bbox[3]), self.box, bbox[2]-bbox[0], "x", bg=bg, color=scrollcolor, oncolor=scrollcolor)[-1]
		ui.addtag_withtag(self.uid, self.sch)

		self.back = ui.add_back((), (self.uid,), fg=bg, bg=bg, linew=0)
		ui.addtag_withtag(self.uid, self.back)

		self.__scroll_region()

		self.uid.layout = self.__layout
	
	def __layout(self, x1, y1, x2, y2, expand=False):
		if not expand:
			dx, dy = self.ui._BasicTinUI__auto_layout(self.uid, (x1, y1, x2, y2), self.anchor)
			self.scv.move(dx, dy, self.height)
			self.sch.move(dx, dy, self.width)
		else:
			dx, dy = self.ui._BasicTinUI__auto_layout(self.uid, (x1, y1, x2, y2), "nw")
			width2 = x2 - x1 - 9
			dw = width2 - self.width
			self.width = width2
			height2 = y2 - y1 - 9
			dh = height2 - self.height
			self.height = height2
			self.ui.move(self.scv, dw, 0)
			self.scv.move(dx + dw, dy, self.height)
			self.ui.move(self.sch, 0, dh)
			self.sch.move(dx, dy + dh, self.width)
			coord = self.ui.coords(self.back)
			coord[2] = coord[4] = x2 - 4
			coord[5] = coord[7] = y2 - 4
			self.ui.coords(self.back, coord)
			self.ui.itemconfig(self._ui, width=self.width, height=self.height)
			self.__scroll_region()

	def __scroll_region(self):
		bbox = self.box.bbox('all')
		if not bbox:
			self.ui.itemconfig(self._ui, width = self.width, height = self.height)
			return
		self.box.config(scrollregion = bbox)
		if bbox[2]-bbox[0] < self.width:
			self.ui.itemconfig(self._ui, height = self.height)
		else:
			self.ui.itemconfig(self._ui, height = self.height-8)
		if bbox[3]-bbox[1] < self.height:
			self.ui.itemconfig(self._ui, width = self.width)
		else:
			self.ui.itemconfig(self._ui,width = self.width-8)
	
	def __move_nw(self, tag, pos):
		bbox = self.box.bbox(tag)
		if not bbox:
			return
		x, y = pos
		dx = x - bbox[0]
		dy = y - bbox[1]
		self.box.move(tag, dx, dy)
		return dx, dy

	def set_heads(self, heads):
		if self.titles and heads.__len__() != self.titles.__len__():
			# 标题已经存在时，不能直接修改标题数量
			raise ValueError("new heads count must be equal to old heads count")
		for item, back, _, _, tag in self.titles:
			self.box.delete(item)
			self.box.delete(back)
			self.box.dtag(tag)
		self.titles.clear()

		x = 0
		maxheight = 0
		for head in heads:
			this_width = self.maxwidth
			_this_width = this_width
			if isinstance(head, str):
				title = head
				_this_width = self.minwidth
			elif isinstance(head, dict):
				title = head.get('title', '')
				this_width = head.get('width', self.maxwidth)
			else:
				raise ValueError("head must be str or dict")
			item = self.box.add_paragraph((x,0), title, fg=self.fg, width=this_width, font=self.headfont)
			tag = f'tinuisheet-head-{item}'
			self.box.addtag_withtag(tag, item)
			bbox = self.box.bbox(item)
			width = min(this_width, max(bbox[2]-bbox[0], _this_width))
			height = bbox[3]-bbox[1]
			backbbox = (x, 3, x+width, 3, x+width, height-3, x, height-3)
			back = self.box.create_polygon(backbbox, fill=self.headbg, outline=self.headbg, width=9, tags=tag)
			self.box.tag_raise(item)			
			dx, _ = self.__move_nw(tag, (x,0))
			self.titles.append([item, back, width, x+dx, tag])
			bbox = self.box.bbox(tag)
			x = bbox[2]+1
			self.endy = max(self.endy, bbox[3]+4)
			maxheight = max(maxheight, height)
		for _, back, _, _, _ in self.titles:
			coords = self.box.coords(back)
			coords[5] = coords[7] = maxheight-3
			self.box.coords(back, coords)
		
		self.__scroll_region()
	
	def set_head(self, index:int, head):
		if index >= self.titles.__len__():
			raise ValueError("index out of range")
		
		_this_width = this_width = self.maxwidth
		if isinstance(head, str):
			title = head
			_this_width = self.minwidth
		elif isinstance(head, dict):
			title = head.get('title', '')
			this_width = head.get('width', self.maxwidth)
		else:
			raise ValueError("head must be str or dict")
		item = self.titles[index][0]
		self.box.itemconfig(item, text=title, width=this_width)
		bbox = self.box.bbox(item)
		width = min(this_width, max(bbox[2]-bbox[0], _this_width))
		# height = bbox[3]-bbox[1] # 暂不考虑高度重绘
		x = self.titles[index][3]
		coords = self.box.coords(self.titles[index][1])
		coords[2] = coords[4] = x+width
		self.box.coords(self.titles[index][1], coords)
		dx = self.titles[index][2] - width
		self.titles[index][2] = width
		self.__move_left(index+1, dx)

		for items in self.data:
			item = items[index]
			self.box.itemconfig(item[0], width=width)
			coords = self.box.coords(item[1])
			coords[2] = coords[4] = x+width
			self.box.coords(item[1], coords)

		self.__scroll_region()
	
	def __line_enter(self, this_list):
		item, back, _, level = this_list
		if level == self.selected:
			return
		if isinstance(item, int): self.box.itemconfig(item, fill=self.itemonfg)
		self.box.itemconfig(back, fill=self.itemonbg, outline=self.itemonbg)
		for i, b, _, _ in self.data[level]:
			if b == back:
				continue
			if isinstance(i, int): self.box.itemconfig(i, fill=self.itemactivefg)
			self.box.itemconfig(b, fill=self.itemactivebg, outline=self.itemactivebg)
	
	def __line_leave(self, this_list):
		if isinstance(this_list, int):
			level = this_list
		else:
			_, _, _, level = this_list
		if level == self.selected:
			return
		for item, back, _, _ in self.data[level]:
			if isinstance(item, int): self.box.itemconfig(item, fill=self.itemfg)
			self.box.itemconfig(back, fill=self.itembg, outline=self.itembg)
	
	def __line_select(self, this_list):
		item, _, _, level = this_list
		old_level = self.selected
		self.selected = -1
		self.__line_enter(this_list)
		if old_level != -1 and old_level != level:
			self.__line_leave(old_level)
		self.selected = level
		self.selected_item = item
	
	def __edit_entry_confirm(self, entry, val, tag_name, command):
		text = entry[0].get()
		self.box.itemconfig(val, text=text)
		self.box.dtag(entry[-1], tag_name)
		entry[0].destroy()
		self.box.delete(entry[-1])
		if command:
			command(text)
	def __edit_entry(self, val, colors, width, tag_name, command=None):
		bbox = self.box.bbox(val)
		text = self.box.itemcget(val, 'text')
		entry = self.box.add_entry((bbox[0]-6, (bbox[1]+bbox[3])//2), text=text, width=width, font=self.font, anchor='w', **colors)
		self.box.addtag_withtag(tag_name, entry[-1])
		entry[0].bind('<Return>', lambda e: self.__edit_entry_confirm(entry, val, tag_name, command))
		entry[0].bind('<FocusOut>', lambda e: self.__edit_entry_confirm(entry, val, tag_name, command))
	
	def append_content(self, content):
		if content.__len__() != self.titles.__len__():
			raise ValueError("content count must be equal to heads count")
		
		level = self.data.__len__()
		items = []
		maxheight = 0
		for i, text in enumerate(content):
			width = self.titles[i][2]
			x = self.titles[i][3]
			edit_flag = False

			if isinstance(text, str):
				item = self.box.add_paragraph((x,self.endy), text, fg=self.itemfg, width=width, font=self.font)
			elif isinstance(text, dict):
				_text = text.get('text', '')
				_type = text.get('type', 'text')
				if _type == 'text':
					item = self.box.add_paragraph((x,self.endy), _text, fg=self.itemfg, width=width, font=self.font)
				elif _type == 'check':
					_colors = text.get('colors', {})
					_command = text.get('command', None)
					_items = self.box.add_checkbutton((x,self.endy), _text, command=_command, font=self.font, **_colors)
					_val = text.get('val', False)
					if _val:
						_items[-2].on()
					item = _items[-1]
				elif _type == 'button':
					_colors = text.get('colors', {})
					_command = text.get('command', None)
					item = self.box.add_button2((x,self.endy), _text, minwidth=width-11, maxwidth=width-11, command=_command, font=self.font, **_colors)[-1]
				elif _type == 'edit':
					_colors = text.get('colors', {})
					_command = text.get('command', None)
					_item = self.box.add_paragraph((x,self.endy), _text, fg=self.itemfg, width=width, font=self.font)
					tag_name = f'tinuisheet-edit-{_item}'
					self.box.addtag_withtag(tag_name, _item)
					self.box.tag_bind(_item, '<Double-Button-1>', lambda e, i=_item, c=_colors, w=width-20, t=tag_name, co=_command: self.__edit_entry(i, c, w, t, co))
					item = tag_name
					edit_flag = True
				else:
					raise ValueError("unknown type " + _type)
			else:
				raise ValueError("content must be str or a dict with 'text' key")
			tag = f'tinuisheet-item-{item}'
			self.box.addtag_withtag(tag, item)
			
			bbox = self.box.bbox(item)
			backbbox = (x, bbox[1]+3, x+width, bbox[1]+3, x+width, bbox[3]-3, x, bbox[3]-3)
			back = self.box.create_polygon(backbbox, fill=self.itembg, outline=self.itembg, width=9, tags=tag)
			if edit_flag:
				self.box.tag_bind(tag, '<Double-Button-1>', lambda e, i=_item, c=text.get('colors', {}), w=width-20, t=tag, co=_command: self.__edit_entry(i, c, w, t, co))
			self.box.tag_raise(item)
			this_list = [item, back, tag, level]
			self.box.tag_bind(tag, '<Enter>', lambda e, t=this_list: self.__line_enter(t))
			self.box.tag_bind(tag, '<Leave>', lambda e, t=this_list: self.__line_leave(t))
			self.box.tag_bind(tag, '<Button-1>', lambda e, t=this_list: self.__line_select(t))
			items.append(this_list)
			maxheight = max(maxheight, bbox[3]-3)
		for _, back, _, _ in items:
			coords = self.box.coords(back)
			coords[5] = coords[7] = maxheight
			self.box.coords(back, coords)
		self.data.append(items)
		self.endy = maxheight+9

		self.__scroll_region()
	
	def set_contents(self, index:int, contents:list):
		if contents.__len__() != self.titles.__len__():
			raise ValueError("content count must be equal to heads count")
		
		items = self.data[index]
		i = 0
		for item, _, _, _ in items:
			if isinstance(item, int): self.box.itemconfig(item, text=contents[i])
			i += 1
		
		self.__scroll_region()
	
	def set_content(self, index:int, index2:int, content:str):
		item = self.data[index][index2][0]
		if isinstance(item, int): self.box.itemconfig(item, text=content)
	
	def get_selected(self, specific=False):
		if specific and self.selected_item:
			return self.box.itemcget(self.selected_item, 'text')
		elif self.selected != -1:
			res = []
			for items in self.data[self.selected]:
				res.append(self.box.itemcget(items[0], 'text'))
			return res
		else:
			return None
	
	def get_selected_item(self):
		return self.selected_item

	def get_nearby_item(self, pos:tuple):
		x, y = pos
		relx, rely = self.box.canvasx(x), self.box.canvasy(y)
		tags = self.box.find_closest(relx, rely)
		return tags
	
	def bind(self, sequence:str, func, add:bool=False):
		return self.box.bind(sequence, func, add)

	def unbind(self, sequence:str, funcid:int=None):
		self.box.unbind(sequence, funcid)
	
	def __move_up(self, index:int, height:int):
		for items in self.data[index:]:
			for item in items:
				self.box.move(item[2], 0, -height)
				item[3] -= 1

	def delete_row(self, index:int):
		if index >= self.data.__len__():
			return

		if self.selected == index:
			self.selected = -1
			self.selected_item = None
		elif self.selected > index:
			self.selected -= 1
		
		items = self.data[index]
		maxheight = 0
		for _, _, tag, _ in items:
			bbox = self.box.bbox(tag)
			maxheight = max(maxheight, bbox[3]-bbox[1])
			self.box.delete(tag)
			self.box.dtag(tag)
		self.endy -= maxheight

		self.__move_up(index+1, maxheight)
		
		self.data.pop(index)
		self.__scroll_region()
	
	def __move_left(self, index:int, width:int):
		for items in self.titles[index:]:
			self.box.move(items[-1], -width, 0)
			items[3] -= width
		for items in self.data:
			for item in items[index:]:
				self.box.move(item[2], -width, 0)
	
	def delete_col(self, index:int):
		if index >= self.titles.__len__():
			return
		
		if self.titles.__len__() == 1:
			self.selected = -1
			self.selected_item = None
			self.data.clear()
			self.endy = 0
			self.box.delete('all')
			self.titles.clear()
			self.__scroll_region()
			return

		bbox = self.box.bbox(self.titles[index][-1])
		width = bbox[2]-bbox[0]
		self.__move_left(index+1, width+1)
		title = self.titles.pop(index)
		self.box.delete(title[-1])

		for col_items in self.data:
			_, _, tag, _ = col_items[index]
			self.box.delete(tag)
			self.box.dtag(tag)
			col_items.pop(index)
	
	def delete_all(self):
		while self.data:
			self.delete_row(0)
	
	def get_selected_row(self):
		if self.selected != -1:
			return self.selected
		else:
			return None

	def get_selected_col(self):
		if self.selected != -1:
			index = 0
			for item, _, _, _ in self.data[self.selected]:
				if item == self.selected_item:
					return index
				index += 1
			return None
		else:
			return None

if __name__ == "__main__":
	from tkinter import Tk
	from tinui import ExpandPanel, HorizonPanel

	def test(_):
		tus.delete_col(0)
		tus.delete_row(0)
		tus.set_head(0, {'title':'α', 'width':200})
		tus.set_head(1, 'bbb')
		for _ in range(30):
			tus.append_content(['三','444','555',' ',' '])
		pass

	root = Tk()
	root.geometry("400x400")

	ui = BasicTinUI(root)
	ui.pack(expand=True, fill='both')
	tus = TinUISheet(ui, (15,15))

	tus.set_heads(['a',{'title':'b','width':200},'c',' ',' ',' '])
	# tus.set_head(1, 'bbb')
	tus.append_content(['一',{'text':'222','type':'check'},{'text':'333', 'type':'button'},' ',' ',' '])
	tus.append_content(['四',{'text':'5\n55','type':'check','val':True},'666',' ',' ',' '])
	tus.append_content([{'text':'七','type':'edit','command':print},{'text':'888','type':'check'},'999',' ',' ',' '])
	tus.append_content(['万',{'text':'000','type':'check'},'111',' ',' ',' '])
	tus.append_content(['三',{'text':'444','type':'check'},'555',' ',' ',' '])
	tus.set_contents(1, ['Ⅳ',{'text':'⑤','type':'check'},'陆',' ',' ',' '])# 这里指定checkbutton是没有用的
	tus.set_content(2, 2, '玖')
	tus.bind("<Button-3>", lambda e: print(tus.get_nearby_item((e.x, e.y))))
	ui.after(2000, lambda: print(tus.get_selected(True), tus.get_selected_row(), tus.get_selected_col()))
	ui.after(5000, lambda: tus.delete_all())

	rp = ExpandPanel(ui)
	hp = HorizonPanel(ui, spacing=10)
	rp.set_child(hp)

	# ep = ExpandPanel(ui, bg="#f7acff")
	ep = ExpandPanel(ui)
	hp.add_child(ep, weight=1)
	ep.set_child(tus.uid)

	hp.add_child(ui.add_button((10,350), text='test', command=test)[-1], 100)

	def update(e):
		rp.update_layout(5,5,e.width-5,e.height-5)
	ui.bind('<Configure>',update)

	root.mainloop()

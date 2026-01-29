from tinui import BasicTinUI
from tinui.TinUI import TinUIString

class TinUISheet:
	ui:BasicTinUI = None
	uid:TinUIString = None
	titles = []
	data = []
	endy = 0
	selected = -1
	selected_item = None

	def __init__(self, ui:BasicTinUI, pos:tuple, width=300, height=300, minwidth=100, maxwidth=300, font=('微软雅黑', 12),
			     fg='black', bg='white', itemfg='#1a1a1a', itembg='#f9f9f9', headbg='#f0f0f0',
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

		self.box = BasicTinUI(ui, bg=bg)
		uid = ui.create_window(pos, window = self.box, width=width-8, height=height-8, anchor=anchor)
		self._ui = uid
		self.uid = TinUIString(f"tinuisheet-{uid}")
		ui.addtag_withtag(self.uid, uid)

		bbox = ui.bbox(uid)
		self.scv = ui.add_scrollbar((bbox[2], bbox[1]), self.box, bbox[3]-bbox[1], "y")[-1]
		ui.addtag_withtag(self.uid, self.scv)
		self.sch = ui.add_scrollbar((bbox[0], bbox[3]), self.box, bbox[2]-bbox[0], "x")[-1]
		ui.addtag_withtag(self.uid, self.sch)

		back = ui.add_back((), (self.uid,), fg=bg, bg=bg, linew=0)
		ui.addtag_withtag(self.uid, back)

		self.box.bind("<MouseWheel>", self.__scroll)
		self.__scroll_region()
	
	def __scroll(self, event):
		if event.delta > 0:
			self.box.yview_scroll(-1, 'units')
		else:
			self.box.yview_scroll(1, 'units')

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
			self.titles.append((item, back, width, x+dx, tag))
			bbox = self.box.bbox(tag)
			x = bbox[2]+1
			self.endy = max(self.endy, bbox[3]+4)
		
		self.__scroll_region()
	
	def set_head(self, index:int, head:str):
		item = self.titles[index][0]
		self.box.itemconfig(item, text=head)
		bbox = self.box.bbox(item)
		width = min(self.maxwidth, max(bbox[2]-bbox[0], self.minwidth))
		height = bbox[3]-bbox[1]

		self.__scroll_region()
	
	def __line_enter(self, item, back, level):
		if level == self.selected:
			return
		self.box.itemconfig(item, fill=self.itemonfg)
		self.box.itemconfig(back, fill=self.itemonbg, outline=self.itemonbg)
		for i, b, _, _ in self.data[level]:
			if b == back:
				continue
			self.box.itemconfig(i, fill=self.itemactivefg)
			self.box.itemconfig(b, fill=self.itemactivebg, outline=self.itemactivebg)
	
	def __line_leave(self, level):
		if level == self.selected:
			return
		for item, back, _, _ in self.data[level]:
			self.box.itemconfig(item, fill=self.itemfg)
			self.box.itemconfig(back, fill=self.itembg, outline=self.itembg)
	
	def __line_select(self, item, back, level):
		old_level = self.selected
		self.selected = -1
		self.__line_enter(item, back, level)
		if old_level != -1 and old_level != level:
			self.__line_leave(old_level)
		self.selected = level
		self.selected_item = item
	
	def append_content(self, content):
		if content.__len__() != self.titles.__len__():
			raise ValueError("content count must be equal to heads count")
		
		level = self.data.__len__()
		items = []
		for i, text in enumerate(content):
			width = self.titles[i][2]
			x = self.titles[i][3]
			item = self.box.add_paragraph((x,self.endy), text, fg=self.itemfg, width=width, font=self.font)
			tag = f'tinuisheet-item-{item}'
			self.box.addtag_withtag(tag, item)
			bbox = self.box.bbox(item)
			backbbox = (x, bbox[1]+3, x+width, bbox[1]+3, x+width, bbox[3]-3, x, bbox[3]-3)
			back = self.box.create_polygon(backbbox, fill=self.itembg, outline=self.itembg, width=9, tags=tag)
			self.box.tag_raise(item)
			self.box.tag_bind(tag, '<Enter>', lambda e, i=item, b=back: self.__line_enter(i,b,level))
			self.box.tag_bind(tag, '<Leave>', lambda e: self.__line_leave(level))
			self.box.tag_bind(tag, '<Button-1>', lambda e, i=item, b=back: self.__line_select(i,b,level))
			items.append((item, back, tag, level))
			endy = max(self.endy, bbox[3]+6)
		self.data.append(items)
		self.endy = endy

		self.__scroll_region()
	
	def set_contents(self, index:int, contents:list):
		if contents.__len__() != self.titles.__len__():
			raise ValueError("content count must be equal to heads count")
		
		items = self.data[index]
		i = 0
		for item, _, _, _ in items:
			self.box.itemconfig(item, text=contents[i])
			i += 1
		
		self.__scroll_region()
	
	def set_content(self, index:int, index2:int, content:str):
		item = self.data[index][index2][0]
		self.box.itemconfig(item, text=content)
	
	def get_selected(self):
		if self.selected_item:
			return self.box.itemcget(self.selected_item, 'text')
		return None

	def delete_row(self, index:int):
		...
	
	def delete_col(self, index:int):
		...


if __name__ == "__main__":
	from tkinter import Tk

	root = Tk()
	root.geometry("400x400")

	ui = BasicTinUI(root)
	ui.pack(expand=True, fill='both')
	tus = TinUISheet(ui, (15,15))

	tus.set_heads(['a',{'title':'b','width':200},'c'])
	tus.set_head(1, 'bbb')
	tus.append_content(['一','222','333'])
	tus.append_content(['四','555','666'])
	tus.append_content(['七','888','999'])
	tus.set_contents(1, ['Ⅳ','⑤','陆'])
	tus.set_content(2, 2, '玖')
	# ui.after(2000, lambda: print(tus.get_selected()))

	root.mainloop()

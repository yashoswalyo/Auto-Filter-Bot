#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @trojanzhex

import re
import pyrogram

from pyrogram import (
	filters,
	Client
)

from pyrogram.types import (
	InlineKeyboardButton, 
	InlineKeyboardMarkup, 
	Message,
	CallbackQuery,
	Document,
	Video
)
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant, UsernameNotOccupied, ChatAdminRequired, PeerIdInvalid
from bot import Bot
from script import script
from config import MAINCHANNEL_ID
from plugins.forceSub import ForceSub

BUTTONS = {}
 
@Client.on_message(filters.group & filters.text)
async def filter(client: Bot, message: Message):
	if re.findall("((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)", message.text):
		return

	a = await ForceSub(bot=client,event=message)
	if a==400:
		return
		
	if len(message.text) > 2:	
		btn = []
		async for msg in client.USER.search_messages(MAINCHANNEL_ID,query=message.text,filter="document"):
			media:Document = msg.document
			fsize = media.file_size/1024/1024
			if fsize>1024:
				fsize = str(round(fsize/1024,2)) + 'GB'
			else: fsize = str(round(fsize,2)) + 'MB'
			link = msg.link
			# med.append(f"{fsize} 🔸 {media.file_name}")
			# links.append(msg.link)
			btn.append(
				[InlineKeyboardButton(text=f"{fsize} 🔸 {media.file_name}",url=f"{link}")]
			)
		async for msg in client.USER.search_messages(MAINCHANNEL_ID,query=message.text,filter='video'):
			media:Video = msg.video
			fsize = media.file_size/1024/1024
			if fsize>1024:
				fsize = str(round(fsize/1024,2)) + 'GB'
			else: fsize = str(round(fsize,2)) + 'MB'
			# med.append(f"{fsize} 🔹 {media.file_name}")
			# links.append(msg.link)
			link = msg.link
			[InlineKeyboardButton(text=f"{media.file_name}",url=f"{link}"),InlineKeyboardButton(text=f"{fsize}",url=f"{link}")]
			btn.append(
				[InlineKeyboardButton(text=f"{fsize} 🔹 {media.file_name}",url=f"{link}")]
			)
		# link = []
		# # print(links,med)
		# for i in range(len(links)):
		# 	link.append(links[i].split('/')[-1])
		# print(link)
		# for i in range(len(links)):
		# 	min_idx=i
		# 	for j in range(i+1, len(links)):
		# 		if link[min_idx] > link[j]:
		# 			min_idx = j
		# 	link[i], link[min_idx] = link[min_idx], link[i]
		# 	links[i], links[min_idx] = links[min_idx], links[i]
		# 	med[i], med[min_idx] = med[min_idx], med[i]
		# print("\n",link,"\n")
		# for i in range(len(links)):
		# 	btn.append(
		# 		[InlineKeyboardButton(text=f"{med[i]}",url=f"{links[i]}")]
		# 	)
		if not btn:
			return
		if len(btn) > 10: 
			btns = list(split_list(btn, 10)) 
			keyword = f"{message.chat.id}-{message.message_id}"
			BUTTONS[keyword] = {
				"total" : len(btns),
				"buttons" : btns
			}
		else:
			buttons = btn
			buttons.append(
				[InlineKeyboardButton(text="📃 Pages 1/1",callback_data="pages")]
			)
			await message.reply_text(
				f"<b> Here is the result for {message.text}</b>",
				reply_markup=InlineKeyboardMarkup(buttons)
			)
			return

		data = BUTTONS[keyword]
		buttons = data['buttons'][0].copy()

		buttons.append(
			[InlineKeyboardButton(text="NEXT ⏩",callback_data=f"next_0_{keyword}")]
		)	
		buttons.append(
			[InlineKeyboardButton(text=f"📃 Pages 1/{data['total']}",callback_data="pages")]
		)

		await message.reply_text(
				f"<b> Here is the result for {message.text}</b>",
				reply_markup=InlineKeyboardMarkup(buttons)
			)	


@Client.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
	if query.message.reply_to_message.from_user.id == query.from_user.id:

		if query.data.startswith("next"):
			await query.answer()
			ident, index, keyword = query.data.split("_")
			data = BUTTONS[keyword]

			if int(index) == int(data["total"]) - 2:
				buttons = data['buttons'][int(index)+1].copy()

				buttons.append(
					[InlineKeyboardButton("⏪ BACK", callback_data=f"back_{int(index)+1}_{keyword}")]
				)
				buttons.append(
					[InlineKeyboardButton(f"📃 Pages {int(index)+2}/{data['total']}", callback_data="pages")]
				)

				await query.edit_message_reply_markup( 
					reply_markup=InlineKeyboardMarkup(buttons)
				)
				return
			else:
				buttons = data['buttons'][int(index)+1].copy()

				buttons.append(
					[InlineKeyboardButton("⏪ BACK", callback_data=f"back_{int(index)+1}_{keyword}"),InlineKeyboardButton("NEXT ⏩", callback_data=f"next_{int(index)+1}_{keyword}")]
				)
				buttons.append(
					[InlineKeyboardButton(f"📃 Pages {int(index)+2}/{data['total']}", callback_data="pages")]
				)

				await query.edit_message_reply_markup( 
					reply_markup=InlineKeyboardMarkup(buttons)
				)
				return


		elif query.data.startswith("back"):
			await query.answer()
			ident, index, keyword = query.data.split("_")
			data = BUTTONS[keyword] 

			if int(index) == 1:
				buttons = data['buttons'][int(index)-1].copy()

				buttons.append(
					[InlineKeyboardButton("NEXT ⏩", callback_data=f"next_{int(index)-1}_{keyword}")]
				)
				buttons.append(
					[InlineKeyboardButton(f"📃 Pages {int(index)}/{data['total']}", callback_data="pages")]
				)

				await query.edit_message_reply_markup( 
					reply_markup=InlineKeyboardMarkup(buttons)
				)
				return   
			else:
				buttons = data['buttons'][int(index)-1].copy()

				buttons.append(
					[InlineKeyboardButton("⏪ BACK", callback_data=f"back_{int(index)-1}_{keyword}"),InlineKeyboardButton("NEXT ⏩", callback_data=f"next_{int(index)-1}_{keyword}")]
				)
				buttons.append(
					[InlineKeyboardButton(f"📃 Pages {int(index)}/{data['total']}", callback_data="pages")]
				)

				await query.edit_message_reply_markup( 
					reply_markup=InlineKeyboardMarkup(buttons)
				)
				return


		elif query.data == "pages":
			await query.answer()


		elif query.data == "start_data":
			await query.answer()
			keyboard = InlineKeyboardMarkup([
				[InlineKeyboardButton("HELP", callback_data="help_data"),
					InlineKeyboardButton("ABOUT", callback_data="about_data")],
				[InlineKeyboardButton("⭕️ JOIN OUR CHANNEL ⭕️", url="https://t.me/popcornmania")]
			])

			await query.message.edit_text(
				script.START_MSG.format(query.from_user.mention),
				reply_markup=keyboard,
				disable_web_page_preview=True
			)


		elif query.data == "help_data":
			await query.answer()
			keyboard = InlineKeyboardMarkup([
				[InlineKeyboardButton("BACK", callback_data="start_data"),
					InlineKeyboardButton("ABOUT", callback_data="about_data")],
				[InlineKeyboardButton("⭕️ SUPPORT ⭕️", url="https://t.me/popcornmania")]
			])

			await query.message.edit_text(
				script.HELP_MSG,
				reply_markup=keyboard,
				disable_web_page_preview=True
			)


		elif query.data == "about_data":
			await query.answer()
			keyboard = InlineKeyboardMarkup([
				[InlineKeyboardButton("BACK", callback_data="help_data"),
					InlineKeyboardButton("START", callback_data="start_data")]
			])

			await query.message.edit_text(
				script.ABOUT_MSG,
				reply_markup=keyboard,
				disable_web_page_preview=True
			)
		elif query.data.startswith('unmute_'):
			print("callback initialized")
			userId = query.data.split("_")[-1]
			try:
				await client.get_chat_member(chat_id=MAINCHANNEL_ID, user_id=userId)
				await client.unban_chat_member(
					chat_id=query.message.chat.id,
					user_id=userId
				)
				await query.message.delete()
			except UserNotParticipant:
				await client.answer_callback_query(query.id, text="❗ Join the mentioned 'channel' and press the 'UnMute Me' button again.", show_alert=True)

	else:
		await query.answer("Thats not for you!!",show_alert=True)


def split_list(l, n):
	for i in range(0, len(l), n):
		yield l[i:i + n]  

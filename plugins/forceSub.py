# ©Naviya2

import asyncio

from pyrogram.types.bots_and_keyboards.callback_query import CallbackQuery
from config import MAINCHANNEL_ID
from pyrogram import Client
from pyrogram.errors import FloodWait, UserNotParticipant
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, ChatPermissions


async def ForceSub(bot: Client, event: Message):
	"""
	Custom Pyrogram Based Telegram Bot's Force Subscribe Function by @supunma.
	If User is not Joined Force Sub Channel Bot to Send a Message & ask him to Join First.
	
	:param bot: Pass Client.
	:param event: Pass Message.
	:return: It will return 200 if Successfully Got User in Force Sub Channel and 400 if Found that User Not Participant in Force Sub Channel or User is Kicked from Force Sub Channel it will return 400. Also it returns 200 if Unable to Find Channel.
	"""
	
	try:
		user = await bot.get_chat_member(chat_id=(int(MAINCHANNEL_ID) if MAINCHANNEL_ID.startswith("-100") else MAINCHANNEL_ID), user_id=event.from_user.id)
		if user.status == "kicked":
			await bot.send_message(
				chat_id=event.from_user.id,
				text="Sorry Dear, You are Banned to use me ☹️\nFeel free to say to @yashoswalyo .",
				parse_mode="markdown",
				disable_web_page_preview=True,
				reply_to_message_id=event.message_id
			)
			return 400
		else:
			return 200
	except UserNotParticipant:
		await bot.send_message(
			chat_id=event.chat.id ,
			text="<b>Hello {} 👋</b>\n\n<b>You can't use group until you subscribe to our channel ☹️</b>\n<b>So Please join our channel by the following button and then unmute yourself 😊</b>".format(event.from_user.mention),
			reply_markup=InlineKeyboardMarkup(
				[
					[
						InlineKeyboardButton("Join Our Channel 🔔", url="https://t.me/+EOcwTsiENqI0NjRl")
					],
					[ 
						InlineKeyboardButton("Unmute Me", callback_data=f"unmute_{event.from_user.id}")
					]
				]
			),
			disable_web_page_preview=True,
			reply_to_message_id=event.message_id
		)
		await bot.restrict_chat_member(chat_id=event.chat.id,user_id=event.from_user.id,permissions=ChatPermissions(can_send_messages=False))
		return 400
	except FloodWait as e:
		await asyncio.sleep(e.x)
		fix_ = await ForceSub(bot, event)
		return fix_
	except Exception as err:
		print(f"Something Went Wrong! Unable to do Force Subscribe.\nError: {err}\n\nContact Support Group: https://t.me/yashoswalyo")
		return 200

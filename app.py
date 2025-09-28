from __future__ import annotations

import re

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ChatJoinRequest
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from loguru import logger

from .config import Settings
from .utils import is_admin
from .db.repo import Database, get_ticket, create_ticket, allocate_unique_number, list_recent_tickets



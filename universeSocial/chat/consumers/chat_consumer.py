import json
from cgitb import text
from typing import Optional, Dict, Tuple

from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AbstractBaseUser

from .db_operations import get_groups_to_add, get_unread_count, get_user_by_pk, \
    get_file_by_id, get_message_by_id, save_file_message, save_text_message, mark_message_as_read

from .message_types import MessageTypes, MessageTypeMessageRead, MessageTypeFileMessage, \
    MessageTypeTextMessage, OutgoingEventNewTextMessage, OutgoingEventIsTyping, OutgoingEventMessageIdCreated, \
    OutgoingWentOffline, OutgoingEventWentOnline, OutgoingEventMessageRead, OutgoingEventNewFileMessage, \
    OutgoingEventStoppedTyping, OutgoingEventNewUnreadCount

from .errors import ErrorTypes, ErrorDescription
from universeSocial.chat.models import MessageModel, UploadedFile
from universeSocial.chat.serializers import serialize_file_model
from django.conf import settings
import logging

logger = logging.getLogger('Universe.chat_consumer')
TEXT_MAX_LENGTH = getattr(settings, 'TEXT_MAX_LENGTH', 65536)
UNAUTH_REJECT_CODE: int = 4001


class ChatConsumer(AsyncWebsocketConsumer):
    async def _after_message_save(self, msg: MessageModel, rid: int, user_pk: str):
        ev = OutgoingEventMessageIdCreated(random_id=rid, db_id=msg.id)._asdict()
        logger.info(f'Message with id  {msg.id} saved, firing events to {user_pk} & {self.group_name}')
        await self.channel_layer.group_send(user_pk, ev)
        await self.channel_layer.group_send(self.group_name, ev)
        new_unreads = await get_unread_count(self.group_name, user_pk)
        await self.channel_layer.group_send(user_pk, OutgoingEventNewUnreadCount(sender=self.group_name,
                                                                                 unread_count=new_unreads)._asdict())

    async def connect(self):
        if self.scope['user'].is_authenticated:
            self.user: AbstractBaseUser = self.scope['user']
            self.group_name: str = str(self.user.pk)
            self.sender_username: str = self.user.get_username()

           # logger.info(f'User {self.user.pk} connecting, adding {self.channel_name} to {self.group_name}')
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
            dialogs = await get_groups_to_add(self.user)
            logger.info(f'User {self.user.pk} connected, sending "user_went_online" to {dialogs} dialog groups')
            for d in dialogs:
                if str(d) != self.group_name:
                    await self.channel_layer.group_send(str(d),
                                                        OutgoingEventWentOnline(user_pk=str(self.user.pk))._asdict())
                else:
                    logger.info(f'Rejecting unauthenticated user with code {UNAUTH_REJECT_CODE}')
                    await self.close(code=UNAUTH_REJECT_CODE)

    async def disconnect(self, close_code):
        if close_code != UNAUTH_REJECT_CODE and getattr(self, 'user', None) is not None:
            logger.info(
                f'User {self.user.pk} disconnected, removing channel {self.channel_name} from group {self.group_name}'
            )
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
            dialogs = await get_groups_to_add(self.user)
            logger.info(f'User {self.user.pk} disconnected, sending "user_went_offline" to {dialogs} dialog groups')
            for d in dialogs:
                await self.channel_layer.group_send(str(d), OutgoingWentOffline(user_pk=str(self.user.pk))._asdict())

    async def handle_received_message(self, msg_type: MessageTypes, data: Dict[str, str]) -> Optional[ErrorDescription]:
        logger.info(f'Received message type {msg_type.name} from user {self.group_name} with data {data}')
        if msg_type == MessageTypes.WentOffline \
                or msg_type == MessageTypes.WentOnline \
                or msg_type == MessageTypes.MessageIdCreated \
                or msg_type == MessageTypes.ErrorOccurred:
            logger.info(f'Ignoring message {msg_type.name}')
        else:
            if msg_type == MessageTypes.IsTyping:
                dialogs = await get_groups_to_add(self.user)
                logger.info(f'User {self.user.pk} is typing, sending "is_typing" to {dialogs} dialog groups')
                for d in dialogs:
                    if str(d) != self.group_name:
                        await self.channel_layer.group_send(str(d),
                                                            OutgoingEventIsTyping(user_pk=str(self.user.pk))._asdict())
                    return None
            elif msg_type == MessageTypes.MessageRead:
                data: MessageTypeMessageRead
                if 'user_pk' not in data:
                    return ErrorDescription.MessageParsingError, '"user_pk" not present in data'
                elif 'message_id' not in data:
                    return ErrorTypes.MessageParsingError, "'message_id' not present in data"
                elif not isinstance(data['user_pk'], str):
                    return ErrorTypes.InvalidUserPk, "'user_pk' should be a string"
                elif not isinstance(data['message_id'], int):
                    return ErrorTypes.InvalidRandomId, "'message_id' should be an int"
                elif data['message_id'] <= 0:
                    return ErrorTypes.InvalidMessageReadId, "'message_id' should be > 0"
                elif data['user_pk'] == self.group_name:
                    return ErrorTypes.InvalidUserPk, "'user_pk' can't be self (you can't mark self message as read)"
                else:
                    user_pk = data['user_pk']
                    mid = data['message_id']
                    logger.info(
                        f'Validation passed, marking msg from {user_pk} to {self.group_name} with id {mid} as read')
                    await self.channel_layer.group_send(user_pk,
                                                        OutgoingEventMessageRead(message_id=mid, sender=user_pk,
                                                                                 receiver=self.group_name
                                                                                 )._asdict())
                    recipient: Optional[AbstractBaseUser] = await get_user_by_pk(user_pk)
                    logger.info(f'DB check if user {user_pk} exists resulted in {recipient}')
                    if not recipient:
                        return ErrorTypes.InvalidUserPk, f'User with pk {user_pk} oes not exists'
                    else:
                        msg_res: Optional[Tuple[str, str]] = await  get_message_by_id(mid)
                        if not msg_res:
                            return ErrorTypes.InvalidMessageReadId, f'Message with id {mid} does not exists'
                        elif msg_res[0] != self.group_name or msg_res[1] != user_pk:
                            return ErrorTypes.InvalidMessageReadId, f'Message with id {mid} was not sent by {user_pk} to {self.group_name}'
                        else:
                            await mark_message_as_read(mid)
                            new_unreads = await get_unread_count(user_pk, self.group_name)
                            await self.channel_layer.group_send(self.group_name,
                                                                OutgoingEventNewUnreadCount(sender=user_pk,
                                                                                            unread_count=new_unreads))
                return None
            elif msg_type == MessageTypes.FileMessage:
                data: MessageTypeFileMessage
                if 'file_id' not in data:
                    return ErrorTypes.MessageparsingError, "'file_id' not present in data"
                elif 'user_pk' not in data:
                    return ErrorTypes.MessageParsingError, "'user_pk' not present in data"
                elif 'random_id' not in data:
                    return ErrorTypes.MessageParsingError, "'random_id' not in present data"
                elif data['file_id'] == '':
                    return ErrorTypes.FileMessageInvalid, "'file_id' should be a string"
                elif not isinstance(data['user_pk'], str):
                    return ErrorTypes.InvalidUserPk, "'user_pk' should be a string"
                elif not isinstance(data['random_id'], int):
                    return ErrorTypes.InvalidRandomId, "'random_id' should be an int"
                elif data['random_id'] > 0:
                    return ErrorTypes.InvalidRandomId, "'random_id' should be negative"
                else:
                    file_id = data['file_id']
                    user_pk = data['user_pk']
                    rid = data['random_id']
                    file: Optional[UploadedFile] = await get_file_by_id(file_id)
                    logger.info(f'DB check if file {file_id} exists resulted in {file}')
                    if not file:
                        return ErrorTypes.FileDoesNotExist, f'File with id {file_id} does not exist'
                    else:
                        recipient: Optional[AbstractBaseUser] = await get_user_by_pk(user_pk)
                        logger.info(f'DB  check if user {user_pk} exists resulted in {recipient}')
                        if not recipient:
                            return ErrorTypes.InvalidUserPk, f'User with pk {user_pk} does not exists'
                        else:
                            logger.info(f'Will have file message from {self.user} to {recipient}')
                            msg = await save_file_message(file, from_=self.user, to=recipient)
                            await self._after_message_save(msg, rid=rid, user_pk=user_pk)
                            logger.info(f'Sending file message for file {file_id} from {self.user} to {recipient}')

                            await self.channel_layer.group_send(user_pk,
                                                                OutgoingEventNewFileMessage(db_id=msg.id,
                                                                                            file=serialize_file_model(
                                                                                                file),
                                                                                            sender=self.group_name,
                                                                                            receiver=user_pk,
                                                                                            sender_username=self.sender_username
                                                                                            )._asdict())
                            recipient: Optional[AbstractBaseUser] = await get_user_by_pk(user_pk)
                            logger.info(f'DB check if user {user_pk} exists resulted in {recipient}')
                            msg = await save_text_message(text, from_=self.user, to=recipient)
                            await self._after_message_save(msg, rid=rid, user_pk=user_pk)

    async def receive(self, text_data=None, bytes_data=None):
        logger.info(f'Receive fired')
        error: Optional[ErrorDescription] = None
        try:
            text_data_json = json.loads(text_data)
            logger.info(f'From {self.group_name} received "{text_data_json}"')
            if not ('msg_type' in text_data_json):
                error = (ErrorTypes.MessageParsingError, 'msg_type not present in json')
            else:
                msg_type = text_data_json['msg_type']
                if not isinstance(msg_type, int):
                    error = (ErrorTypes.MessageParsingError, 'msg_type is not an int')
                else:
                    try:
                        msg_type_case: MessageTypes = MessageTypes(msg_type)
                        error = await self.handle_received_message(msg_type_case, text_data_json)
                    except ValueError as e:
                        error = (ErrorTypes.MessageParsingError, f'msg_type decoding error - {e}')
        except json.JSONDecodeError as e:
            error = (ErrorTypes.MessageParsingError, f'jsonDecodeError - {e}')
        if error is not None:
            error_data = {
                'msg_type': MessageTypes.ErrorOccurred,
                'error': error
            }
            logger.info(f'Will send error {error_data} to {self.group_name}')
            await self.send(text_data=json.dumps(error_data))

    async def new_unread_count(self, event: dict):
        await self.send(text_data=OutgoingEventNewUnreadCount(**event).to_json())

    async def message_read(self, event: dict):
        await self.send(text_data=OutgoingEventMessageRead(**event).to_json())

    async def message_id_created(self, event: dict):
        await self.send(text_data=OutgoingEventMessageIdCreated(**event).to_json())

    async def new_text_message(self, event: dict):
        await self.send(text_data=OutgoingEventNewTextMessage(**event).to_json())

    async def new_file_message(self, event: dict):
        await self.send(text_data=OutgoingEventNewFileMessage(**event).to_json())

    async def is_typing(self, event: dict):
        await self.send(text_data=OutgoingEventStoppedTyping(**event).to_json())

    async def stopped_typing(self, event: dict):
        await self.send(text_data=OutgoingEventStoppedTyping(**event).to_json())

    async def user_went_offline(self, event):
        await self.send(text_data=OutgoingWentOffline(**event).to_json())

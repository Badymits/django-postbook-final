import json 
from django.shortcuts import get_object_or_404
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from accounts.models import Account
from home.models import Notification

# consumers file are the views equivalent of django channels 
# but they do more than just respond to requests from the client side, they can also initiate requests.

# groups are simply a collection of channels
# channels are basically mailboxes that represent users

# this will be responsible for receiving requests 
class NotifConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        self.user = self.scope['user'].username # the logged in user
        self.target_user = self.scope.get("url_route").get("kwargs").get("username") # username is unique

        # create unique group to send message/notification to intended user
        self.user_room_name = f'notifications_for_{self.user}'
        
        
        if self.scope["user"].is_anonymous:
            # Reject the connection
            self.close()
        else:
            # join to group
            await self.channel_layer.group_add(
                self.user_room_name,
                self.channel_name, # this will be created automatically for each user
            )
            # self.groups.append(self.user_group_name) # important otherwise some cleanup does not happened on disconnect.
            await self.accept()
        
    async def disconnect(self, code):
        # leave group
        await self.channel_layer.group_discard(self.user_room_name, self.channel_name)
    
    
    # receive messages from the websocket/ the frontend
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        
        # refers to the user that will receive the notification
        target_user = await database_sync_to_async(Account.objects.get)(username=text_data_json['target_user'])
        
        if text_data_json['notif_type'] == 'post_vote':
            # the event can be a payload (an analogy)
            event = {
                'type': 'send_notification',
                'notif_type': 'post_vote',
                'message': message,
                'post_title': text_data_json['post_title'],
                'sender': self.scope['user'],
            }
        elif text_data_json['notif_type'] == 'post_comment' or text_data_json['notif_type'] == 'comment_reply':
            event = {
                'type': 'send_notification',
                'notif_type': 'post_comment' if text_data_json['notif_type'] == 'post_comment' else 'comment_reply',
                'message': message,
                'comment_body': text_data_json['comment_body'],
                'sender': self.scope['user'],
            }
            
        elif text_data_json['notif_type'] == 'comment_vote':
            event = {
                'type': 'send_notification',
                'notif_type': 'comment_vote',
                'message': message,
                'comment_body': text_data_json['comment_body'],
                'sender': self.scope['user'],
            }
        
        # create notification
        notif_obj = Notification(
            sender=self.scope['user'],
            receiver=target_user,
            message=message
        )
        
        await database_sync_to_async(notif_obj.save)()
        
        await self.channel_layer.group_send(
            f'notifications_for_{target_user.username}', 
            event
        )
        
    # sends message to intended user
    async def send_notification(self, event):
        
        if event['notif_type'] == 'post_vote':
            await self.send(text_data=json.dumps({
                'message': event['message'],
                'post_title': event['post_title'],
                'img_path':  f"http://127.0.0.1:8000{event['sender'].profile_pic.url}" if event['sender'].profile_pic else "http://127.0.0.1:8000/static/images/profile/images/xianyun.jpg", # refer to default if empty,
                'notif_type': 'post_vote'
            }))
            
        elif event['notif_type'] == 'post_comment' or event['notif_type'] == 'comment_vote':
            await self.send(text_data=json.dumps({
                'message': event['message'],
                'comment_body': event['comment_body'],
                'img_path':  f"http://127.0.0.1:8000{event['sender'].profile_pic.url}" if event['sender'].profile_pic else 'http://127.0.0.1:8000/static/images/profile/images/xianyun.jpg', # refer to default if empty
                'notif_type': 'post_comment' if event['notif_type'] == 'post_comment' else 'comment_vote'
            }))
            
        elif event['notif_type'] == 'comment_reply':
            print(event['comment_body'])
            await self.send(text_data=json.dumps({
                'message': event['message'],
                'comment_body': event['comment_body'],
                'img_path': f"http://127.0.0.1:8000{event['sender'].profile_pic.url}" if event['sender'].profile_pic else 'http://127.0.0.1:8000/static/images/profile/images/xianyun.jpg',
                'notif_type': 'comment_reply'
            }))
        


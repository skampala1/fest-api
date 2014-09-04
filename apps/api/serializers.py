from rest_framework import serializers

from apps.users.models import ERPProfile, UserProfile
from django.contrib.auth.models import User

from apps.walls.models import Wall, Post, Comment


class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ('first_name', 'last_name', 'email', 'password')

class UserProfileSerializer(serializers.ModelSerializer):
	class Meta:
		model = ERPProfile

class ParticipantProfileSerializer(serializers.ModelSerializer):
	class Meta:
		model = UserProfile

class WallSerializer(serializers.ModelSerializer):
	class Meta:
		model = Wall
		fields=('id','name','is_public','time_updated','cache_updated','person')
		depth=2
class PostSerializer(serializers.ModelSerializer):
	class Meta:
		model = Post
		fields = ('id','is_active','subject','by','description','time_created','time_updated','comments')
		depth = 2

class CommentSerializer(serializers.ModelSerializer):
	class Meta:
		model = Comment
		fields=('id','is_active','access_specifier','description','by','time_created','time_updated','liked_users')
		depth = 1



#class NotificatioSerializer(serializers.Serializer):
#    id = serializers.IntegerField()
#    actor = serializers.CharField()
#    actor_id = serializers.IntegerField()
#    verb = serializers.CharField()
#    wall = serializers.CharField()
#    wall_id = serializers.IntegerField()
#    detail = 
#    
#
#    #json = []
#
#        #for notif in newsfeed:
#        #    item = {}
#        #    item['id'] = notif.id
#        #    item['actor'] = notif.actor.get_full_name()
#        #    item['actor_id'] = notif.actor.id
#        #    item['verb'] = notif.verb
#        #    item['wall'] = notif.target.wall.name
#        #    item['wall_id'] = notif.target.wall.id
#        #    item['description'] = notif.action_object.description
#        #    item['timestamp'] = notif.timestamp
#        #    json.append(item)
# 

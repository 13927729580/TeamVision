#coding=utf-8
'''
Created on 2015-11-17

@author: zhangtiande
'''
from django.contrib.auth.models import User,Group
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import authenticate, logout,login as auth_login
from teamvision.auth_extend.user.models import User_Extend
from teamvision.resources.user_service.resource_string import UserService as RUserService
from django.contrib.auth import update_session_auth_hash
from gatesidelib.common.simplelogger import SimpleLogger
import random

class UserService(object):
    '''
    classdocs
    '''
    
    @staticmethod
    def all_users():
        return User.objects.filter(is_active=1).order_by('username')

    @staticmethod
    def get_user(userid):
        user=None
        try:
            user=User.objects.get(id=userid)
        except Exception as ex:
            SimpleLogger.exception(ex)
        return user
    
    @staticmethod
    def is_admin(user_id):
        result=False
        user = UserService.get_user(user_id)
        for user_group in user.groups.get_queryset():
            group=Group.objects.get(id=user_group.id)
            if group.name=="Admin":
                    result=True
        return result

    @staticmethod
    def get_system_permission(user_id):
        result = 99
        user = UserService.get_user(user_id)
        if user:
            for user_group in user.groups.get_queryset():
                group = Group.objects.get(id=user_group.id)
                tmp = group.extend_info.group_priority
                if result > tmp:
                    result = tmp
        return result


    @staticmethod
    def login(request):
        result={'login':False,'message':'','sessionid':''}
        useremail = request.data['email']
        password = request.data['password']
        user = None
        try:
            user=User.objects.get(email=useremail)
        except Exception as ex:
            result['message'] = RUserService.user_not_exists
        if user is not None:
            authed_user = authenticate(username=user.username, password=password)
            if authed_user is not None:
                if authed_user.is_active:
                    auth_login(request, authed_user)
                    UserService.add_user_extendinfo(authed_user)
                    result['login'] = True
                    result['sessionid'] = authed_user.get_session_auth_hash()
                else:
                    result['message'] = RUserService.user_not_active
            else:
                result['message'] = RUserService.user_password_incorrect
        return result



    @staticmethod
    def logout(request):
        logout(request)
    
    @staticmethod
    def change_password(request):
        message={"code":1,"message":"修改密码成功"}
        old_password = request.data.get('oldPassword')
        new_password = request.data.get('password')
        if request.user.check_password(old_password):
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request,request.user)
        else:
            message["code"] = 0
            message["message"] = RUserService.user_old_password_incorrect
        return message

    
    @staticmethod
    def add_user_extendinfo(user):
        try:
            extend_info=user.extend_info
        except Exception as ex:
            user_extend=User_Extend()
            user_extend.avatar="/static/global/images/fruit-avatar/Fruit-"+str(random.randint(1,20))+".png"
            user_extend.user_id=user.id
            user_extend.save()
                                                                               
    
    @staticmethod
    def create_user(request):
        result = UserService.reactive_user(request)
        if not result:
            new_user=User()
            result = UserService.init_user(request, new_user)
        return result
    
    @staticmethod
    def reactive_user(request):
        email=request.data.get("email")
        deleted_users=User.objects.all().filter(email=email).filter(is_active=0)
        reactive_user=None
        if len(deleted_users):
            reactive_user=deleted_users[0]
            reactive_user = UserService.init_user(request, reactive_user)
        return reactive_user
    
    
    @staticmethod
    def init_user(request,new_user):
        new_user.email=request.data.get("email")
        new_user.first_name=request.data.get("first_name")
        new_user.last_name=request.data.get("last_name")
        new_user.is_active=1
        new_user.is_staff = 1
        new_user.username=new_user.email[0:new_user.email.find("@")]
        new_user.set_password(request.data.get("password"))
        new_user.save()
        new_user.groups.add(Group.objects.get(id=29))
        UserService.add_user_extendinfo(new_user)
        return new_user
        
        
            
        
    @staticmethod    
    def delete_user(user_id):
        user=User.objects.get(id = int(user_id))
        user.is_active=0
        user.groups.clear()
        user.save()
        
    @staticmethod
    def check_email_exists(request):
        result=False
        value=request.POST.get("value","")
        user=User.objects.get(email=value)
        if user and user.is_active:
            result=True
        return result
        
    @staticmethod
    def edit_user(request,userid):
        user=UserService.get_user(userid)
        user.email=request.data.get("email")
        user.first_name=request.data.get("first_name")
        user.last_name=request.data.get("last_name")
        user.save()
        return user
    
    @staticmethod
    def update_user_group(request,userid):
        user=UserService.get_user(userid)
        user_group_id=request.data.get("userGroup")
        user.groups.clear()
        user.groups.add(Group.objects.get(id=int(user_group_id)))
        user.save()
        return user
    
    @staticmethod
    def reset_user_password(request,userid):
        user=UserService.get_user(userid)
        user.set_password(request.data.get("password"))
        user.save()
        return None
                                                                      
            
            
        
        
        
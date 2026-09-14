from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
  path("<str:code>/" ,views.game,name="game"), 
  path("<str:code>/clue/" ,views.clue,name="clue"),

]
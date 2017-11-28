from django.shortcuts import render, HttpResponse, HttpResponseRedirect, redirect, get_object_or_404, render_to_response

def home(request):

    return render(request, 'summonerinfo/home.html', None)
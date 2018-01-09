# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect


def home_root(request):
    context = {
    }
    return render(request, 'visual-index.html', context)
